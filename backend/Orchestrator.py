import boto3
from typing import Dict
from configs import SupportedModels
from BreakdownMaintenanceAdviceTool import BreakdownMaintenanceAdviceTool
from BreakdownPredictionTool import BreakdownPredictionTool

AWS_REGION = "us-west-2"
MODEL_ID = SupportedModels.CLAUDE_HAIKU.value

SYSTEM_PROMPT = """
You are an assistant that provides maintenance advice and breakdown predictions using only the Breakdown_Maintenance_Advice_Tool, and Breakdown_Prediction_Tool.
- Always call Breakdown_Maintenance_Advice_Tool to provide maintenance advice based on sensor data.
- Always call Breakdown_Prediction_Tool to predict the likelihood of breakdowns based on sensor readings and machine data.
- Never generate or guess results on your own; always rely on the respective tools.
- Provide accurate and precise results based on the tool outputs.
- Never hallucinate data.
- Always respond in Thai language (ภาษาไทย).
"""

class Orchestrator:
    def __init__(self):
        self.system_prompt = [{"text": SYSTEM_PROMPT}]
        self.tool_config = {
            "tools": [
                BreakdownPredictionTool.get_tool_spec(),
                BreakdownMaintenanceAdviceTool.get_tool_spec()
            ]
        }
        self.bedrockRuntimeClient = boto3.client("bedrock-runtime", region_name=AWS_REGION)

    def run(self, user_input=None):
        """
        Run orchestrator with user input

        Args:
            user_input: Optional user input from UI/API. If None, uses _get_user_input()
        """
        conversation = []

        user_input = self._get_user_input(user_input)


        message = {"role": "user", "content": [{"text": user_input}]}
        conversation.append(message)
        bedrock_response = self._send_conversation_to_bedrock(conversation)
        response_text = self._process_model_response(bedrock_response, conversation)

        return response_text


    def _send_conversation_to_bedrock(self, conversation):
        return self.bedrockRuntimeClient.converse(
            modelId=MODEL_ID,
            messages=conversation,
            system=self.system_prompt,
            toolConfig=self.tool_config,
        )

    def _process_model_response(self, model_response, conversation):
        message = model_response["output"]["message"]
        conversation.append(message)

        if model_response["stopReason"] == "tool_use":
            return self._handle_tool_use(message, conversation)
        elif model_response["stopReason"] == "end_turn":
            response_text = message["content"][0]["text"]
            print("Model response: ", response_text)
            return response_text

    def _handle_tool_use(self, model_response, conversation):
        tool_results = []
        for content_block in model_response["content"]:
            if "text" in content_block:
                print(content_block["text"])  # Output model response

            if "toolUse" in content_block:
                tool_response = self._invoke_tool(content_block["toolUse"])
                tool_results.append({
                    "toolResult": {
                        "toolUseId": tool_response["toolUseId"],
                        "content": [{"json": tool_response["content"]}],
                    }
                })

        conversation.append({"role": "user", "content": tool_results})
        response = self._send_conversation_to_bedrock(conversation)
        return self._process_model_response(response, conversation)

    def _invoke_tool(self, payload):
        tool_name = payload["name"]
        if tool_name == "Breakdown_Prediction_Tool":
            input_data = payload["input"]
            response = BreakdownPredictionTool.analyze_sensors(input_data)
        elif tool_name == "Breakdown_Maintenance_Advice_Tool":
            input_data = payload.get("input", {})
            response = BreakdownMaintenanceAdviceTool.analyze_sensors(input_data)
        else:
            response = {"error": True, "message": f"Tool {tool_name} not found"}
        return {"toolUseId": payload["toolUseId"], "content": response}

    @staticmethod
    def _get_user_input(user_input):
        # This should be replaced with actual input handling (e.g., from a UI or a form)
        return user_input  