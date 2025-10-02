from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import boto3
import json
import os
import pandas as pd
import numpy as np
from datetime import datetime
from io import StringIO
from dotenv import load_dotenv
from configs import SensorReadings, MachineData, ChatMessage, ROIRequest
from BreakdownMaintenanceAdviceTool import BreakdownMaintenanceAdviceTool

# Load environment variables
load_dotenv()
app = FastAPI(title="MITR Phol_Zero Breakdown Prediction API")

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
maintenance_tool = BreakdownMaintenanceAdviceTool()

# In-memory data storage (replace with database in production)
uploaded_data_store = {
    "dataframe": None,
    "machines": [],
    "metadata": {}
}

def clean_sensor_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and organize sensor data"""
    # Remove duplicates
    df = df.drop_duplicates()

    # Handle missing values
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].median())

    # Remove outliers using IQR method
    for col in numeric_columns:
        if col not in ['Machine_ID']:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 3 * IQR
            upper_bound = Q3 + 3 * IQR
            df[col] = df[col].clip(lower_bound, upper_bound)

    return df

# API Endpoints
@app.get("/")
def read_root():
    return {"message": "Zero Breakdown Prediction API", "status": "running"}

@app.post("/api/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """อัพโหลดและประมวลผลไฟล์ CSV ข้อมูลเครื่องจักร"""
    try:
        # Read CSV file
        contents = await file.read()
        df = pd.read_csv(StringIO(contents.decode('utf-8')))

        # Validate required columns
        required_columns = [
            'Timestamp', 'Machine_ID', 'PowerMotor', 'CurrentMotor',
            'TempBrassBearingDE', 'SpeedMotor', 'TempOilGear',
            'TempBearingMotorNDE', 'TempWindingMotorPhase_U',
            'TempWindingMotorPhase_V', 'TempWindingMotorPhase_W', 'Vibration'
        ]

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"ไฟล์ CSV ขาดคอลัมน์: {', '.join(missing_columns)}"
            )

        # Clean data
        original_rows = len(df)
        df = clean_sensor_data(df)

        # Convert Timestamp to datetime
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])

        # Get machine list
        machines = sorted(df['Machine_ID'].unique().tolist())

        # Calculate data quality metrics
        missing_values = df.isnull().sum().sum()
        completeness = ((df.size - missing_values) / df.size) * 100

        # Get date range
        min_date = df['Timestamp'].min().strftime('%Y-%m-%d')
        max_date = df['Timestamp'].max().strftime('%Y-%m-%d')
        date_range = f"{min_date} ถึง {max_date}"

        # Store data globally
        uploaded_data_store["dataframe"] = df
        uploaded_data_store["machines"] = machines
        uploaded_data_store["metadata"] = {
            "total_rows": len(df),
            "total_machines": len(machines),
            "date_range": date_range,
            "completeness": round(completeness, 2),
            "missing_values": int(missing_values)
        }

        return {
            "total_rows": len(df),
            "total_machines": len(machines),
            "machines": machines,
            "date_range": date_range,
            "data_quality": {
                "completeness": round(completeness, 2),
                "missing_values": int(missing_values)
            },
            "message": "อัพโหลดและประมวลผลข้อมูลสำเร็จ"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/machines")
async def get_machines():
    """ดึงรายการเครื่องจักรที่มีข้อมูล"""
    try:
        if uploaded_data_store["dataframe"] is None:
            return {"machines": [], "message": "ยังไม่มีข้อมูล กรุณาอัพโหลดไฟล์ CSV ก่อน"}

        return {
            "machines": uploaded_data_store["machines"],
            "metadata": uploaded_data_store["metadata"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/machine-data/{machine_id}")
async def get_machine_data(machine_id: str, limit: int = 100):
    """ดึงข้อมูลล่าสุดของเครื่องจักร"""
    try:
        if uploaded_data_store["dataframe"] is None:
            raise HTTPException(status_code=404, detail="ยังไม่มีข้อมูล กรุณาอัพโหลดไฟล์ CSV ก่อน")

        df = uploaded_data_store["dataframe"]
        machine_df = df[df['Machine_ID'] == machine_id].sort_values('Timestamp', ascending=False).head(limit)

        if machine_df.empty:
            raise HTTPException(status_code=404, detail=f"ไม่พบข้อมูลของเครื่องจักร {machine_id}")

        # Get latest reading
        latest = machine_df.iloc[0]

        # Convert to sensor readings format
        sensor_data = {
            "PowerMotor": float(latest['PowerMotor']),
            "CurrentMotor": float(latest['CurrentMotor']),
            "TempBrassBearingDE": float(latest['TempBrassBearingDE']),
            "SpeedMotor": float(latest['SpeedMotor']),
            "SpeedRoller": float(latest.get('SpeedRoller', 5.5)),
            "TempOilGear": float(latest['TempOilGear']),
            "TempBearingMotorNDE": float(latest['TempBearingMotorNDE']),
            "TempWindingMotorPhase_U": float(latest['TempWindingMotorPhase_U']),
            "TempWindingMotorPhase_V": float(latest['TempWindingMotorPhase_V']),
            "TempWindingMotorPhase_W": float(latest['TempWindingMotorPhase_W']),
            "Vibration": float(latest['Vibration'])
        }

        # Analyze current status
        analysis = maintenance_tool.analyze_sensors(sensor_data)

        return {
            "machine_id": machine_id,
            "timestamp": latest['Timestamp'].isoformat(),
            "sensor_readings": sensor_data,
            "alerts": analysis['alerts'],
            "status_summary": analysis['status_summary'],
            "historical_count": len(machine_df)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze-sensors")
async def analyze_sensors(data: MachineData):
    """วิเคราะห์ข้อมูล sensor และให้คำแนะนำ"""
    try:
        sensor_dict = data.sensor_readings.model_dump()
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
        sensor_dict = data.sensor_readings.model_dump()
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
        response_body = bedrock_runtime.converse(
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

#------------ prompt นี้ รอ ทำ RAG--------------------------------

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
        response_body = bedrock_runtime.converse(
            modelId="qwen.qwen3-32b-v1:0",
            body=body
        )
        agent_response= response_body['output']['message']['content'][0]['text']
        # response = bedrock_runtime.invoke_model(
        #     modelId='us.anthropic.claude-3-haiku-20240307-v1:0',
        #     body=json.dumps({
        #         "anthropic_version": "bedrock-2023-05-31",
        #         "max_tokens": 1024,
        #         "messages": [
        #             {
        #                 "role": "user",
        #                 "content": prompt
        #             }
        #         ]
        #     })
        # )

        # response_body = json.loads(response['body'].read())
        # agent_response = response_body['content'][0]['text']

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