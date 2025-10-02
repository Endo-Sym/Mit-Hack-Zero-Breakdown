class BreakdownPredictionTool:
    @staticmethod
    def analyze_sensors(sensor_data):
        """
        วิเคราะห์และทำนายความเสี่ยงของการเสียหายของเครื่องจักร

        Args:
            sensor_data: dict ของข้อมูล sensor

        Returns:
            dict: ผลการวิเคราะห์และคำทำนาย
        """
        # คำนวณ risk score จากข้อมูล sensor
        risk_factors = []
        risk_score = 0

        # ตรวจสอบ PowerMotor
        power = sensor_data.get('Power_Motor', 0)
        if power < 260 or power > 330:
            risk_score += 30
            risk_factors.append("PowerMotor อยู่ในระดับเสี่ยงสูง")
        elif (260 <= power < 290) or (315 < power <= 330):
            risk_score += 15
            risk_factors.append("PowerMotor อยู่ในระดับผิดปกติ")

        # ตรวจสอบ CurrentMotor
        current = sensor_data.get('Current_Motor', 0)
        if current < 240 or current > 360:
            risk_score += 30
            risk_factors.append("CurrentMotor อยู่ในระดับเสี่ยงสูง")
        elif (240 <= current < 280) or (320 < current <= 360):
            risk_score += 15
            risk_factors.append("CurrentMotor อยู่ในระดับผิดปกติ")

        # ตรวจสอบอุณหภูมิ
        temp_brass_de = sensor_data.get('Temperator_Brass_bearing_DE', 0)
        if temp_brass_de > 95:
            risk_score += 25
            risk_factors.append("TempBrassBearingDE สูงเกินไป")
        elif temp_brass_de > 85:
            risk_score += 10

        # ตรวจสอบ Vibration
        vibration = sensor_data.get('Vibration', 0)
        if vibration > 4.5:
            risk_score += 30
            risk_factors.append("Vibration อยู่ในระดับอันตราย")
        elif vibration > 1.8:
            risk_score += 10

        # กำหนดระดับความเสี่ยง
        if risk_score >= 60:
            risk_level = "สูง"
            prediction = "เครื่องจักรมีความเสี่ยงสูงที่จะเสียหายภายใน 7 วัน ควรหยุดตรวจสอบทันที"
        elif risk_score >= 30:
            risk_level = "ปานกลาง"
            prediction = "เครื่องจักรมีความเสี่ยงปานกลาง ควรติดตามอย่างใกล้ชิดและวางแผนซ่อมบำรุง"
        else:
            risk_level = "ต่ำ"
            prediction = "เครื่องจักรทำงานปกติ มีความเสี่ยงต่ำ"

        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "prediction": prediction,
            "risk_factors": risk_factors,
            "sensor_summary": {
                "Power_Motor": power,
                "Current_Motor": current,
                "Temperator_Brass_bearing_DE": temp_brass_de,
                "Vibration": vibration
            }
        }
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
        
            
        