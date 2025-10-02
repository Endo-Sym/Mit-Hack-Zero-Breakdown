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
                            "Power_Motor": {
                                "type": "float",
                                "description": "Power consumed by the motor (kW)."
                            },
                            "Current_Motor": {
                                "type": "float",
                                "description": "Current draw by the motor (A)."
                            },
                            "Temperator_Brass_bearing_DE": {
                                "type": "float",
                                "description": "Temperature of the brass bearing (°C)."
                            },
                            "Temperator_Brass_bearing_NDE": {
                                "type": "float",
                                "description": "Temperature of the brass bearing (°C)."
                            },
                            "Temperator_Bearing_Motor_DE": {
                                "type": "float",
                                "description": "Temperature of the motor bearing (°C)."
                            },
                            "Temperator_Bearing_Motor_NDE": {
                                "type": "float",
                                "description": "Temperature of the motor bearing (°C)."
                            },
                            "Speed_Motor": {
                                "type": "float",
                                "description": "Speed of the motor (rpm)."
                            },
                            "Speed_Roller": {
                                "type": "float",
                                "description": "Speed of the roller (rpm)."
                            },
                            "Temperator_Oil_Gear": {
                                "type": "float",
                                "description": "Temperature of the oil gear (°C)."
                            },
                            "Temperator_Winding_Motor_Phase_U": {
                                "type": "float",
                                "description": "Temperature of the winding motor (Phase U)."
                            },
                            "Temperator_Winding_Motor_Phase_V": {
                                "type": "float",
                                "description": "Temperature of the winding motor (Phase V)."
                            },
                            "Temperator_Winding_Motor_Phase_W": {
                                "type": "float",
                                "description": "Temperature of the winding motor (Phase W)."
                            },
                            "Vibration": {
                                "type": "float",
                                "description": "Vibration level of the machine (mm/s)."
                            }
                        },
                        "required": [
                            "Power_Motor", 
                            "Current_Motor", 
                            "Temperator_Brass_bearing_DE",
                            "Temperator_Brass_bearing_NDE",
                            "Temperator_Bearing_Motor_DE",
                            "Temperator_Bearing_Motor_NDE",
                            "Speed_Motor",
                            "Speed_Roller",
                            "Temperator_Oil_Gear",
                            "Temperator_Winding_Motor_Phase_U",
                            "Temperator_Winding_Motor_Phase_V",
                            "Temperator_Winding_Motor_Phase_W",
                            "Vibration"
                        ]
                    }
                }
            }
        }