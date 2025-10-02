import boto3
from enum import Enum
from configs import SupportedModels
AWS_REGION = "us-west-2"



MODEL_ID = SupportedModels.CLAUDE_HAIKU.value

SYSTEM_PROMPT = """
You are an assistant that provides maintenance advice and breakdown predictions using only the Breakdown_Maintenance_Advice_Tool, and Breakdown_Prediction_Tool.
- Always call Breakdown_Maintenance_Advice_Tool to provide maintenance advice based on sensor data.
- Always call Breakdown_Prediction_Tool to predict the likelihood of breakdowns based on sensor readings and machine data.
- Never generate or guess results on your own; always rely on the respective tools.
- Provide accurate and precise results based on the tool outputs.
- Report times in Thailand timezone (Asia/Bangkok) for all outputs that involve timestamps.
- Never hallucinate data.
"""



class Orchestrator:
    def __init__(self):
        self.system_prompt = [{"text": SYSTEM_PROMPT}]
        self.tool_config = {"tools": [BreakdownMaintenanceAdviceTool.get_tool_spec(), TimeTool.get_tool_spec()]}
        self.bedrockRuntimeClient = boto3.client("bedrock-runtime", region_name=AWS_REGION)
