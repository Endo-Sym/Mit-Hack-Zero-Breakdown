from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import boto3
import json
import os
from datetime import datetime
from configs import SensorReadings, MachineData, ChatMessage, ROIRequest

app = FastAPI(title="Zero Breakdown Prediction API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AWS Bedrock client
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-west-2'
)

# Sensor threshold analysis
class BreakdownMaintenanceAdviceTool:
    def analyze_sensors(self, sensor_data: Dict) -> Dict:
        alerts = []

        # PowerMotor thresholds (kW)
        power = sensor_data.get('PowerMotor', 0)
        if 280 <= power <= 320:
            status_power = "ปกติ"
        elif (270 <= power < 280) or (320 < power <= 325):
            status_power = "เสี่ยง"
            alerts.append(f"PowerMotor: มีสถานะเป็นเสี่ยง มีค่า {power} kW")
        elif power < 260 or power > 360:
            status_power = "เสียหาย"
            alerts.append(f"PowerMotor: มีสถานะเป็นเสียหาย มีค่า {power} kW - ค่าผิดปกติมาก")
        else:
            status_power = "เสี่ยง"
            alerts.append(f"PowerMotor: มีค่า {power} kW อยู่ในระดับเสี่ยง")

        # CurrentMotor thresholds (Amp)
        current = sensor_data.get('CurrentMotor', 0)
        if 270 <= current <= 330:
            status_current = "ปกติ"
        elif (260 <= current < 270) or (330 < current <= 340):
            status_current = "เสี่ยง"
            alerts.append(f"CurrentMotor: มีสถานะเป็นเสี่ยง มีค่า {current} Amp")
        elif current < 240 or current > 360:
            status_current = "เสียหาย"
            alerts.append(f"CurrentMotor: มีสถานะเป็นเสียหาย มีค่า {current} Amp")
        else:
            status_current = "เสี่ยง"
            alerts.append(f"CurrentMotor: มีค่า {current} Amp อยู่ในระดับเสี่ยง")

        # Temperature sensors (°C)
        temp_brass = sensor_data.get('TempBrassBearingDE', 0)
        if temp_brass < 75:
            status_brass = "ปกติ"
        elif 75 <= temp_brass <= 85:
            status_brass = "เสี่ยง"
            alerts.append(f"TempBrassBearingDE: อุณหภูมิสูง {temp_brass}°C")
        else:
            status_brass = "เสียหาย"
            alerts.append(f"TempBrassBearingDE: อุณหภูมิสูงเกินไป {temp_brass}°C")

        temp_motor_nde = sensor_data.get('TempBearingMotorNDE', 0)
        if temp_motor_nde < 75:
            status_motor_nde = "ปกติ"
        elif 75 <= temp_motor_nde <= 85:
            status_motor_nde = "เสี่ยง"
            alerts.append(f"TempBearingMotorNDE: อุณหภูมิสูง {temp_motor_nde}°C")
        else:
            status_motor_nde = "เสียหาย"
            alerts.append(f"TempBearingMotorNDE: อุณหภูมิสูงเกินไป {temp_motor_nde}°C")

        # Speed Motor (rpm)
        speed_motor = sensor_data.get('SpeedMotor', 0)
        if 1470 <= speed_motor <= 1500:
            status_speed = "ปกติ"
        elif (1450 <= speed_motor < 1470) or (1500 < speed_motor <= 1510):
            status_speed = "เสี่ยง"
            alerts.append(f"SpeedMotor: ความเร็วผิดปกติเล็กน้อย {speed_motor} rpm")
        elif speed_motor == 0:
            status_speed = "เสียหาย"
            alerts.append(f"SpeedMotor: มอเตอร์หยุดทำงาน")
        else:
            status_speed = "เสี่ยง"
            alerts.append(f"SpeedMotor: ความเร็ว {speed_motor} rpm อยู่นอกช่วงปกติ")

        # TempOilGear (°C)
        temp_oil = sensor_data.get('TempOilGear', 0)
        if temp_oil < 65:
            status_oil = "ปกติ"
        elif 65 <= temp_oil <= 75:
            status_oil = "เสี่ยง"
            alerts.append(f"TempOilGear: อุณหภูมิน้ำมันเกียร์สูง {temp_oil}°C")
        else:
            status_oil = "เสียหาย"
            alerts.append(f"TempOilGear: อุณหภูมิน้ำมันเกียร์สูงเกินไป {temp_oil}°C")

        # Winding temperatures (°C)
        temp_u = sensor_data.get('TempWindingMotorPhase_U', 0)
        temp_v = sensor_data.get('TempWindingMotorPhase_V', 0)
        temp_w = sensor_data.get('TempWindingMotorPhase_W', 0)

        for phase, temp in [('U', temp_u), ('V', temp_v), ('W', temp_w)]:
            if temp < 115:
                continue
            elif 115 <= temp <= 125:
                alerts.append(f"TempWindingMotorPhase_{phase}: อุณหภูมิสูง {temp}°C")
            else:
                alerts.append(f"TempWindingMotorPhase_{phase}: อุณหภูมิสูงเกินไป {temp}°C")

        # Vibration (mm/s)
        vibration = sensor_data.get('Vibration')
        if vibration:
            if vibration < 0.71:
                vib_status = "ดีมาก"
            elif 0.71 <= vibration < 1.8:
                vib_status = "ดี"
            elif 1.8 <= vibration < 4.5:
                vib_status = "พอใช้"
                alerts.append(f"Vibration: การสั่นสะเทือน {vibration} mm/s อยู่ในระดับพอใช้")
            else:
                vib_status = "ไม่พอใช้"
                alerts.append(f"Vibration: การสั่นสะเทือนสูงเกินไป {vibration} mm/s")

        return {
            "alerts": alerts,
            "status_summary": {
                "power": status_power,
                "current": status_current,
                "temp_brass": status_brass,
                "temp_motor_nde": status_motor_nde,
                "speed": status_speed,
                "oil_temp": status_oil
            }
        }

maintenance_tool = BreakdownMaintenanceAdviceTool()

# API Endpoints
@app.get("/")
def read_root():
    return {"message": "Zero Breakdown Prediction API", "status": "running"}

@app.post("/api/analyze-sensors")
async def analyze_sensors(data: MachineData):
    """วิเคราะห์ข้อมูล sensor และให้คำแนะนำ"""
    try:
        sensor_dict = data.sensor_readings.dict()
        analysis = maintenance_tool.analyze_sensors(sensor_dict)

#------------ prompt นี้ รอ ทำ RAG--------------------------------
        # Generate maintenance advice using AWS Bedrock
        if analysis['alerts']:
            prompt = f"""วิเคราะห์ข้อมูล sensor ของเครื่องจักร {data.machine_type}:

ข้อมูล Sensor:
{json.dumps(sensor_dict, indent=2, ensure_ascii=False)}

แจ้งเตือน:
{chr(10).join(analysis['alerts'])}

กรุณาให้คำแนะนำการซ่อมบำรุงที่ชัดเจนและเป็นขั้นตอนจาก
คู่มือซ่อมบำรุงที่ถูกต้องสำหรับ ABB M3BP355SMB4:
        1. การหล่อลื่นแบริ่ง
        ใช้จาระบีชนิด Lithium-based เช่น Mobil Polyrex EM
        รอบการหล่อลื่น: ทุก 3,000–5,000 ชั่วโมง หรือเร็วกว่านั้นในสภาพแวดล้อมร้อน/ชื้น
        มีช่องเติมจาระบีที่ฝั่ง DE และ NDE

        2. การตรวจสอบฉนวน
        ใช้เมกโอห์มมิเตอร์วัดความต้านทานฉนวนก่อนใช้งาน
        ค่า IR ควรสูงกว่า 1 MΩ ต่อ kV

        3. การทำความสะอาด
        เป่าฝุ่นออกจากช่องระบายอากาศและใบพัดด้วยลมแห้ง
        ห้ามใช้น้ำแรงดันสูงหรือสารเคมีที่กัดกร่อน

        4. การตรวจสอบความร้อน
        ตรวจสอบอุณหภูมิขณะทำงานไม่ให้เกิน Class C (80°C rise)
        ใช้เซนเซอร์วัดอุณหภูมิที่ฝาครอบหรือแบริ่ง

        5. การตรวจสอบเสียงและการสั่นสะเทือน
        เสียงรบกวนไม่ควรเกิน 85 dB(A) ที่ระยะ 1 เมตร
        ตรวจสอบการสั่นด้วย vibration analyzer เพื่อป้องกันการสึกหรอของแบริ่ง

        6. การจัดการความชื้น
        ถ้ามอเตอร์ไม่ได้ใช้งานนาน ให้ใช้ฮีตเตอร์ภายในหรือจ่ายไฟเบาๆ เพื่อป้องกันความชื้นสะสม

        ข้อมูลเปรียบเทียบค่าปกติของแต่ละsensor:
        -ค่าปกติของ PowerMotor อยู่ในช่วง 290-315 kW
        -ค่าปกติของ CurrentMotor อยู่ในช่วง  280–320 Amp
        -ค่าปกติของ TempBrassBearingDE อยู่ในช่วง < 75 C
        -ค่าปกติของ SpeedMotor อยู่ในช่วง 1480–1495 rpm
        -ค่าปกติของ TempOilGear อยู่ในช่วง < 65 C
        -ค่าปกติของ TempBearingMotorNDE อยู่ในช่วง <85 C
        -ค่าปกติของ  TempWindingMotorPhase_U และ TempWindingMotorPhase_V และ TempWindingMotorPhase_W อยู่ในช่วง  <105 C
"""

            response = bedrock_runtime.invoke_model(
                modelId='us.anthropic.claude-3-haiku-20240307-v1:0',
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1024,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                })
            )

            response_body = json.loads(response['body'].read())
            maintenance_advice = response_body['content'][0]['text']
        else:
            maintenance_advice = "เครื่องจักรทำงานปกติ ไม่พบความผิดปกติ"

        return {
            "timestamp": data.timestamp,
            "machine_type": data.machine_type,
            "sensor_readings": sensor_dict,
            "alerts": analysis['alerts'],
            "status_summary": analysis['status_summary'],
            "recommended_action": maintenance_advice
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/predict-breakdown")
async def predict_breakdown(data: MachineData):
    """ทำนายความเสี่ยงของการพังของเครื่องจักร"""
    try:
        sensor_dict = data.sensor_readings.dict()
        analysis = maintenance_tool.analyze_sensors(sensor_dict)

        # Calculate risk score
        risk_score = len(analysis['alerts']) * 10
        risk_level = "ต่ำ" if risk_score < 30 else "ปานกลาง" if risk_score < 60 else "สูง"

        prompt = f"""ทำนายความเสี่ยงของการเสียหายของเครื่องจักร {data.machine_type}:

ข้อมูล Sensor:
{json.dumps(sensor_dict, indent=2, ensure_ascii=False)}

ปัญหาที่พบ:
{chr(10).join(analysis['alerts']) if analysis['alerts'] else 'ไม่พบปัญหา'}

คะแนนความเสี่ยง: {risk_score}/100
ระดับความเสี่ยง: {risk_level}

ให้คำทำนายเกี่ยวกับ:
1. โอกาสที่เครื่องจักรจะเสียหายใน 7 วันข้างหน้า
2. อายุการใช้งานโดยประมาณที่เหลืออยู่
3. ส่วนประกอบที่มีความเสี่ยงสูงสุด"""

        response = bedrock_runtime.invoke_model(
            modelId='us.anthropic.claude-3-haiku-20240307-v1:0',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1024,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        )

        response_body = json.loads(response['body'].read())
        prediction = response_body['content'][0]['text']

        return {
            "machine_type": data.machine_type,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "prediction": prediction,
            "alerts": analysis['alerts']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/calculate-roi")
async def calculate_roi(request: ROIRequest):
    """คำนวณ ROI ของการซ่อมบำรุงในช่วงเวลาต่างๆ"""
    try:
        # Calculate efficiency loss
        efficiency_current = request.current_health_percentage / 100
        efficiency_comparison = request.comparison_health_percentage / 100

        # Estimate days until breakdown
        days_until_breakdown_current = (100 - request.current_health_percentage) * 2
        days_until_breakdown_comparison = (100 - request.comparison_health_percentage) * 2

        # Production loss
        production_loss_current = request.daily_production_value * (1 - efficiency_current) * days_until_breakdown_current
        production_loss_comparison = request.daily_production_value * (1 - efficiency_comparison) * days_until_breakdown_comparison

        # ROI calculation
        savings = production_loss_comparison - production_loss_current
        roi_percentage = ((savings - request.repair_cost) / request.repair_cost) * 100 if request.repair_cost > 0 else 0

        prompt = f"""วิเคราะห์ ROI ของการซ่อมบำรุงเครื่องจักร:

        สถานการณ์ปัจจุบัน:
        - สุขภาพเครื่องจักร: {request.current_health_percentage}%
        - ประมาณการวันก่อนเสียหาย: {days_until_breakdown_current:.0f} วัน
        - การสูญเสียจากประสิทธิภาพลดลง: {production_loss_current:,.2f} บาท

        สถานการณ์เปรียบเทียบ (ถ้าซ่อมที่ {request.comparison_health_percentage}%):
        - ประมาณการวันก่อนเสียหาย: {days_until_breakdown_comparison:.0f} วัน
        - การสูญเสียจากประสิทธิภาพลดลง: {production_loss_comparison:,.2f} บาท

        ค่าใช้จ่ายในการซ่อม: {request.repair_cost:,.2f} บาท
        ผลตอบแทนจากการลงทุน (ROI): {roi_percentage:.2f}%

        กรุณาอธิบายผลการวิเคราะห์และให้คำแนะนำว่าควรซ่อมตอนไหนดีที่สุด"""
        
        body = json.dumps({
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 1024
        })

        # ส่งคำขอไปยังโมเดล qwen.qwen3-32b-v1:0 ผ่าน API
        response_body = client.converse(
            modelId="qwen.qwen3-32b-v1:0",
            body=body
        )
        analysis= response_body['output']['message']['content'][0]['text']

        return {
            "current_scenario": {
                "health_percentage": request.current_health_percentage,
                "days_until_breakdown": round(days_until_breakdown_current, 1),
                "production_loss": round(production_loss_current, 2)
            },
            "comparison_scenario": {
                "health_percentage": request.comparison_health_percentage,
                "days_until_breakdown": round(days_until_breakdown_comparison, 1),
                "production_loss": round(production_loss_comparison, 2)
            },
            "repair_cost": request.repair_cost,
            "savings": round(savings, 2),
            "roi_percentage": round(roi_percentage, 2),
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/repair-manual")
async def get_repair_manual(request: ChatMessage):
    """ค้นหาคู่มือการซ่อม (ใช้ AI ตอบคำถาม)"""
    try:
        prompt = f"""คุณเป็นผู้เชี่ยวชาญด้านการซ่อมบำรุงเครื่องจักรโรงงานน้ำตาล โดยเฉพาะระบบ Feed Mill

คำถาม: {request.message}

กรุณาตอบคำถามเกี่ยวกับการซ่อมบำรุงอย่างละเอียด รวมถึง:
1. ขั้นตอนการซ่อม
2. อุปกรณ์ที่ต้องใช้
3. ข้อควรระวัง
4. เวลาที่ใช้โดยประมาณ"""

        response = bedrock_runtime.invoke_model(
            modelId='us.anthropic.claude-3-haiku-20240307-v1:0',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2048,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        )

        response_body = json.loads(response['body'].read())
        manual_content = response_body['content'][0]['text']

        return {
            "question": request.message,
            "answer": manual_content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat_agent(request: ChatMessage):
    """Agentic AI Chat - จัดการคำถามและเลือกฟังก์ชันที่เหมาะสม"""
    try:
        # Determine which function to use based on message
        message_lower = request.message.lower()

        if any(word in message_lower for word in ['ทำนาย', 'พยากรณ์', 'predict', 'breakdown', 'เสียหาย']):
            function_type = "prediction"
        elif any(word in message_lower for word in ['roi', 'กำไร', 'ขาดทุน', 'คุ้มค่า', 'ผลตอบแทน']):
            function_type = "roi"
        elif any(word in message_lower for word in ['ซ่อม', 'repair', 'manual', 'คู่มือ', 'วิธี']):
            function_type = "repair_manual"
        else:
            function_type = "general"

        prompt = f"""คุณเป็น AI Agent ที่ช่วยจัดการระบบ Zero Breakdown Prediction

คำถาม/คำสั่งจากผู้ใช้: {request.message}

ประเภทคำถาม: {function_type}

กรุณาตอบคำถามหรือแนะนำผู้ใช้ว่าต้องใช้ฟังก์ชันใดในการทำงาน:
1. ฟังก์ชันทำนาย Zero Breakdown - สำหรับวิเคราะห์ sensor และทำนายการเสียหาย
2. ฟังก์ชันคำนวณ ROI - สำหรับคำนวณผลตอบแทนของการซ่อมในช่วงเวลาต่างๆ
3. ฟังก์ชันคู่มือการซ่อม - สำหรับค้นหาวิธีการซ่อมและข้อมูลทางเทคนิค"""

        response = bedrock_runtime.invoke_model(
            modelId='us.anthropic.claude-3-haiku-20240307-v1:0',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1024,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        )

        response_body = json.loads(response['body'].read())
        agent_response = response_body['content'][0]['text']

        return {
            "message": request.message,
            "detected_function": function_type,
            "response": agent_response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)