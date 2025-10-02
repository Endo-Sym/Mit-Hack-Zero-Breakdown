class BreakdownPredictionTool:
    @staticmethod
    def get_tool_spec():
        return {
            "toolSpec": {
                "name": "Breakdown_Prediction_Tool",
                "description": "Predicts the likelihood of machinery breakdown based on sensor data.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "vibration": {"type": "number", "description": "Vibration level of the machine."},
                            "temperature": {"type": "number", "description": "Temperature of the machine."},
                            "motor_status": {"type": "string", "description": "Status of the motor."},
                        },
                        "required": ["vibration", "temperature", "motor_status"]
                    }
                }
            }
        }
