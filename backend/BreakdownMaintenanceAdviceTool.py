from typing import Dict, List, Optional

# Sensor threshold analysis
class BreakdownMaintenanceAdviceTool:

    @staticmethod
    def get_tool_spec():
        return {
            "toolSpec": {
                "name": "Breakdown_Maintenance_Advice_Tool",
                "description": "Provide maintenance advice for machinery based on breakdown data.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "timestamp": {"type": "string", "description": "Timestamp when the data was sent (ISO 8601 format)"},
                            "machine_type": {"type": "string", "description": "Name of the machine (including Feed Mill 1, Feed Mill 2, Feed Mill 3,Feed Mill 4)"},
                            "sensor_readings": {
                                "type": "object",
                                "description": "Sensor data includes PowerMotor , CurrentMotor , TempBrassBearingDE ,TempBearingMotorNDE ,SpeedMotor , SpeedRoller , TempOilGear , TempWindingMotorPhase_U , TempWindingMotorPhase_V ,TempWindingMotorPhase_W ,Vibration"
                            }
                        },
                        "required": ["timestamp", "machine_type", "sensor_readings"]
                    }
                }
            }
        }

    def analyze_sensors(self, sensor_data: Dict) -> Dict:
        alerts = []
    
        # PowerMotor thresholds (kW)
        power = sensor_data.get('Power_Motor', 0)
        if 290 <= power <= 315:
            status_power = "ปกติ"
        elif (270 <= power < 290) or (315 < power <= 325):          
            status_power = "ผิดปกติ"
            alerts.append(f"PowerMotor: มีสถานะเป็น{status_power} มีค่า {power} kW คือ มีสิทธิ์ที่จะแรงดันตก หรือ phase loss")
        elif (260 <= power < 270) or (325 < power <= 330):
            status_power = "เสี่ยง"
            alerts.append(f"PowerMotor: มีสถานะเป็น{status_power} มีค่า {power} kW คือ มีความเสี่ยงที่แรงดันตก หรือ phase loss และ Cooling failure")
        else:
            status_power = "เสียหาย"
            alerts.append(f"PowerMotor: มีสถานะเป็น{status_power} มีค่า {power} kW คือ มีความเสี่ยงที่เครื่องหยุดทำงานโดยสมบูรณ์")


        # CurrentMotor thresholds (Amp)
        current = sensor_data.get('Current_Motor', 0)
        if 280 <= current <= 320:
            status_current = "ปกติ"
        elif (260 <= current < 280) or (320 < current <= 330):
            status_current = "ผิดปกติ"
            alerts.append(f"CurrentMotor: มีสถานะเป็น{status_current} มีค่า {current} Amp คือ มีสิทธิ์ที่จะโหลดเกิน, alignment ผิด, แบริ่งฝืด")
        elif (240 <= power < 260) or (330 < power <= 360):
            status_current = "เสี่ยง"
            alerts.append(f"CurrentMotor: มีสถานะเป็น{status_current} มีค่า {current} Amp คือ มีความเสี่ยงที่โหลดเกิน, alignment ผิด, แบริ่งฝืด และมีความเสี่ยงที่จะเกิดเป็น Overload และ Cooling failure")
        else:
            status_current = "เสียหาย"
            alerts.append(f"CurrentMotor: มีสถานะเป็น{status_current} มีค่า {current} Amp คือ มีความเสี่ยงที่เครื่องหยุดทำงานโดยสมบูรณ์")
        
        # Temperature sensors brassDE (°C)
        temp_brass_de = sensor_data.get('Temperator_Brass_bearing_DE', 0)
        if temp_brass_de <= 75:
            status_brass_de = "ปกติ"
        elif 75 < temp_brass_de <= 85:
            status_brass_de = "ผิดปกติ"
            alerts.append(f"TempBrassBearingDE: มีสถานะเป็น{status_brass_de} มีค่า {temp_brass_de}°C คือ มีสิทธิ์ที่ระบบจะหล่อลื่นผิดปกติ")
        elif 85 < temp_brass_de <= 95:
            status_brass_de = "เสี่ยง"
            alerts.append(f"TempBrassBearingDE: มีสถานะเป็น{status_brass_de} มีค่า {temp_brass_de}°C คือ มีความเสี่ยงที่ระบบหล่อลื่นผิดปกติ")
        else:
            status_brass_de = "เสียหาย"
            alerts.append(f"TempBrassBearingDE: มีสถานะเป็น{status_brass_de} มีค่า {temp_brass_de}°C คือ มีความเสี่ยงที่ เครื่องหยุดทำงานโดยสมบูรณ์และมีความเสี่ยงที่แบริ่งสึก, จาระบีหมด, alignment ผิด")
        

        # Temperature sensors brassNDE (°C)
        temp_brass_nde = sensor_data.get('Temperator_Brass_bearing_NDE', 0)
        if temp_brass_nde <= 75:
            status_brass_nde = "ปกติ"
        elif 75 < temp_brass_nde <= 85:
            status_brass_nde = "ผิดปกติ"
            alerts.append(f"TemperatorBrassbearingNDE: มีสถานะเป็น{status_brass_nde} มีค่า {temp_brass_nde}°C คือ มีสิทธิ์ที่ระบบจะหล่อลื่นผิดปกติ")
        elif 85 < temp_brass_nde <= 95:
            status_brass_nde = "เสี่ยง"
            alerts.append(f"TemperatorBrassbearingNDE: มีสถานะเป็น{status_brass_nde} มีค่า {temp_brass_nde}°C คือ มีความเสี่ยงที่ระบบหล่อลื่นผิดปกติ")
        else:
            status_brass_nde = "เสียหาย"
            alerts.append(f"TemperatorBrassbearingNDE: มีสถานะเป็น{status_brass_nde} มีค่า {temp_brass_nde}°C คือ มีความเสี่ยงที่ เครื่องหยุดทำงานโดยสมบูรณ์และมีความเสี่ยงที่แบริ่งสึก, จาระบีหมด, alignment ผิด")
        
        # Temperature sensors motorDE (°C)
        temp_motor_de = sensor_data.get('Temperator_Bearing_Motor_DE', 0)
        if temp_motor_de <= 75:
            status_motor_de = "ปกติ"
        elif 75 < temp_motor_de <= 85:
            status_motor_de = "ผิดปกติ"
            alerts.append(f"TempBrassBearingDE: มีสถานะเป็น{status_motor_de} มีค่า {temp_motor_de}°C คือ มีสิทธิ์ที่ระบบจะหล่อลื่นผิดปกติ")
        elif 85 < temp_motor_de <= 95:
            status_motor_de = "เสี่ยง"
            alerts.append(f"TempBrassBearingDE: มีสถานะเป็น{status_motor_de} มีค่า {temp_motor_de}°C คือ มีความเสี่ยงที่ระบบหล่อลื่นผิดปกติ")
        else:
            status_motor_de = "เสียหาย"
            alerts.append(f"TempBrassBearingDE: มีสถานะเป็น{status_motor_de} มีค่า {temp_motor_de}°C คือ มีความเสี่ยงที่ เครื่องหยุดทำงานโดยสมบูรณ์และมีความเสี่ยงที่แบริ่งสึก, จาระบีหมด, alignment ผิด")

        # Temperature sensors motorNDE (°C)
        temp_motor_nde = sensor_data.get('Temperator_Bearing_Motor_NDE', 0)
        if temp_motor_nde <= 75:
            status_motor_nde = "ปกติ"
        elif 75 < temp_motor_nde <= 85:
            status_motor_nde = "ผิดปกติ"
            alerts.append(f"TempBrassBearingDE: มีสถานะเป็น{status_motor_nde} มีค่า {temp_motor_nde}°C คือ มีสิทธิ์ที่ระบบจะหล่อลื่นผิดปกติ")
        elif 85 < temp_motor_nde <= 95:
            status_motor_nde = "เสี่ยง"
            alerts.append(f"TempBrassBearingDE: มีสถานะเป็น{status_motor_nde} มีค่า {temp_motor_nde}°C คือ มีความเสี่ยงที่ระบบหล่อลื่นผิดปกติ")
        else:
            status_motor_nde = "เสียหาย"
            alerts.append(f"TempBrassBearingDE: มีสถานะเป็น{status_motor_nde} มีค่า {temp_motor_nde}°C คือ มีความเสี่ยงที่ เครื่องหยุดทำงานโดยสมบูรณ์และมีความเสี่ยงที่แบริ่งสึก, จาระบีหมด, alignment ผิด")

        # Speed Motor (rpm)
        speed_motor = sensor_data.get('Speed_Motor', 0)
        if 1470 <= speed_motor <= 1500:
            status_speed = "ปกติ"
        elif (1450 <= speed_motor < 1470) or (1500 < speed_motor <= 1510):
            status_speed = "ผิดปกติ"
            alerts.append(f"SpeedMotor: มีสถานะเป็น{status_speed} มีค่า {speed_motor} rpm คือ ต้องตรวจสอบความเร็วที่สัมพันธ์กับspeed_roller_value")
        elif (1400 <= speed_motor < 1450) or (1510 < soeed_motor <= 1520):
            status_speed = "เสี่ยง"
            alerts.append(f"SpeedMotor: มีสถานะเป็น{status_speed} มีค่า {speed_motor} rpm คือ ต้องตรวจสอบความเร็วที่สัมพันธ์กับspeed_roller_value")
        else:
            status_speed = "เสียหาย"
            alerts.append(f"SpeedMotor: มีสถานะเป็น{status_speed} มีค่า {speed_motor} rpm คือ มีความเสี่ยงที่เครื่องหยุดทำงานโดยสมบูรณ์")
        
        # Speed Roller (rpm)
        speed_roller = sensor_data.get('Speed_Roller',0)
        calculated_speed_roller = speed_motor / 270

        normal_range = calculated_speed_roller
        abnormal_range_lower = normal_range * 0.95  # ค่าผิดปกติ: ±5% จากค่าปกติ
        abnormal_range_upper = normal_range * 1.05

        risk_range_lower = normal_range * 0.9  # ค่าความเสี่ยง: ±10% จากค่าปกติ
        risk_range_upper = normal_range * 1.1

        if speed_roller == 0:
            status_speed_roller = "เสียหาย"
            alerts.append(f"SpeedRoller:  มีสถานะเป็น{statustatus_speed_rollers_speed} มีค่า {spespeed_rollered_motor} rpm คือ มีความเสี่ยงที่โรลเลอร์หยุดหมุนและเครื่องหยุดทำงานโดยสมบูรณ์")
        elif speed_roller < risk_range_lower or speed_roller > risk_range_upper:
             status_speed_roller = "เสี่ยง"
             alerts.append(f"SpeedRoller:  มีสถานะเป็น{status_speed_roller} มีค่า {speed_roller} rpm คือ มีความเสี่ยงที่จะเกิด Chute jam โดย ปัญหาอาจจะเกิดมาจาก อ้อยติด, alignment roller ผิด,ความเร็วไม่สัมพันธ์")
        elif speed_roller < abnormal_range_lower or speed_roller > abnormal_range_upper:
             status_speed_roller = "ผิดปกติ"
             alerts.append(f"SpeedRoller:  มีสถานะเป็น{status_speed_roller} มีค่า {speed_roller} rpm คือ อาจจะเกิดจาก อ้อยติด, alignment roller ผิด, ความเร็วไม่สัมพันธ์")
        else:
             status_speed_roller = "ปกติ" 


        # TempOilGear (°C)
        temp_oil = sensor_data.get('Temperator_Oil_Gear', 0)
        if temp_oil < 65:
            status_oil = "ปกติ"
        elif 65 <= temp_oil <= 75:
            status_oil = "ผิดปกติ"
            alerts.append(f"TempOilGear: มีสถานะเป็น{status_oil} มีค่า {temp_oil}°C คือ มีสิทธิ์ที่ระบบจะหล่อลื่นผิดปกติ")
        elif 75 < temp_oil <= 85:
            status_oil = "เสี่ยง"
            alerts.append(f"TempOilGear: มีสถานะเป็น{status_oil} มีค่า {temp_oil}°C คือ มีความเสี่ยงที่ระบบหล่อลื่นผิดปกติ")
        else:
            status_oil = "เสียหาย"
            alerts.append(f"TempOilGear: มีสถานะเป็น{status_oil} มีค่า {temp_oil}°C คือ มีความเสี่ยงที่ เครื่องหยุดทำงานโดยสมบูรณ์")

        # Winding temperatures (°C)
        temp_u = sensor_data.get('Temperator_Winding_Motor_Phase_U', 0)
        temp_v = sensor_data.get('Temperator_Winding_Motor_Phase_V', 0)
        temp_w = sensor_data.get('Temperator_Winding_Motor_Phase_W', 0)

        for phase, temp in [('U', temp_u), ('V', temp_v), ('W', temp_w)]:
            if temp < 105:
                status_temp_phase = "ปกติ"
            elif 115 <= temp <= 125:
                status_temp_phase = "ผิดปกติ"
                alerts.append(f"TempWindingMotorPhase_{phase}: มีสถานะเป็น {status_temp_phase} มีค่า {temp}°C คือ มีสิทธิ์ที่จะโหลดเกิน, cooling fail, ฉนวนเสื่อม")
            elif 115 <= temp <= 125:
                status_temp_phase = "เสี่ยง"
                alerts.append(f"TempWindingMotorPhase_{phase}: มีสถานะเป็น{status_temp_phase} มีค่า {temp}°C คือ มีความเสี่ยงที่โหลดเกิน, cooling fail, ฉนวนเสื่อม")
            else:
                status_temp_phase = "เสียหาย"
                alerts.append(f"TempWindingMotorPhase_{phase}: มีสถานะเป็น{status_temp_phase} มีค่า {temp}°C คือ มีความเสี่ยงที่เครื่องหยุดทำงานโดยสมบูรณ์")

        # Vibration (mm/s)
        vibration = sensor_data.get('Vibration')
        if vibration:
            if vibration < 0.71:
                vib_status = "Very Good"
            elif 0.71 <= vibration < 1.8:
                vib_status = "Good"
            elif 1.8 <= vibration < 4.5:
                vib_status = "Satisfactory"
                alerts.append(f"Vibration: มีสถานะเป็น{vib_status} และมีการสั่นสะเทือน {vibration} mm/s อยู่ในระดับที่ควรตรวจสอบหรือซ่อมแซม")
            else:
                vib_status = "Unsatisfactory"
                alerts.append(f"Vibration: มีสถานะเป็น{vib_status} และมีการสั่นสะเทือนสูงเกินไป {vibration} mm/s อยู่ในระดับที่มีเสี่ยงต่อความเสียหาย ต้องหยุดเครื่อง")
        else:
            vib_status = "No information"

        return {
            "alerts": alerts,
            "status_summary": {
                "Power_Moto": status_power,
                "Current_Motor": status_current,
                "Temperator_Brass_bearing_DE": status_brass_de,
                "Temperator_Brass_bearing_NDE": status_brass_nde,
                "Temperator_Bearing_Motor_DE": status_motor_de,
                "Temperator_Bearing_Motor_NDE": status_motor_nde,
                "Speed_Motor": status_speed,
                "Speed_Roller": status_speed_roller,    
                "Temperator_Oil_Gear": status_oil,
                "Temperator_Winding_Motor_Phase_U": status_temp_phase,
                "Temperator_Winding_Motor_Phase_V": status_temp_phase,    
                "Temperator_Winding_Motor_Phase_W": status_temp_phase,        
                "Vibration": vib_status,    
          }
        }
