from typing import Dict, List, Optional

# Sensor threshold analysis
class BreakdownMaintenanceAdviceTool:
    def analyze_sensors(self, sensor_data: Dict) -> Dict:
        alerts = []
    
        # PowerMotor thresholds (kW)
        power = sensor_data.get('PowerMotor', 0)
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
        current = sensor_data.get('CurrentMotor', 0)
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
        temp_brass = sensor_data.get('TempBrassBearingDE', 0)
        if temp_brass <= 75:
            status_brass = "ปกติ"
        elif 75 < temp_brass <= 85:
            status_brass = "ผิดปกติ"
            alerts.append(f"TempBrassBearingDE: มีสถานะเป็น{status_brass} มีค่า {temp_brass}°C คือ มีสิทธิ์ที่ระบบจะหล่อลื่นผิดปกติ")
        elif 85 < temp_brass <= 95:
            status_brass = "เสี่ยง"
            alerts.append(f"TempBrassBearingDE: มีสถานะเป็น{status_brass} มีค่า {temp_brass}°C คือ มีความเสี่ยงที่ระบบหล่อลื่นผิดปกติ")
        else:
            status_brass = "เสียหาย"
            alerts.append(f"TempBrassBearingDE: มีสถานะเป็น{status_brass} มีค่า {temp_brass}°C คือ มีความเสี่ยงที่ เครื่องหยุดทำงานโดยสมบูรณ์และมีความเสี่ยงที่แบริ่งสึก, จาระบีหมด, alignment ผิด")
        
        # Temperature sensors NDE (°C)
        temp_motor_nde = sensor_data.get('TempBearingMotorNDE', 0)
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
        speed_motor = sensor_data.get('SpeedMotor', 0)
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
        speed_roller = sensor_data.get('SpeedRoller',0)
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
        temp_oil = sensor_data.get('TempOilGear', 0)
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
        temp_u = sensor_data.get('TempWindingMotorPhase_U', 0)
        temp_v = sensor_data.get('TempWindingMotorPhase_V', 0)
        temp_w = sensor_data.get('TempWindingMotorPhase_W', 0)

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
            vib_status = "No Data"

        return {
            "alerts": alerts,
            "status_summary": {
                "power": status_power,
                "current": status_current,
                "temp_brass_de": status_brass,
                "temp_motor_nde": status_motor_nde,
                "speed_motor": status_speed,
                "speed_roller": status_speed_roller,    
                "temp_oil": status_oil,
                "temp_winding_u": status_temp_phase,
                "temp_winding_v": status_temp_phase,    
                "temp_winding_w": status_temp_phase,        
                "vibration": vib_status,    
          }
        }
