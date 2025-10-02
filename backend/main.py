from fastapi import FastAPI, HTTPException, UploadFile, File, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import hashlib
import hmac
import base64
import boto3
import json
import os
import pandas as pd
import numpy as np
from datetime import datetime
from io import StringIO
from dotenv import load_dotenv
from configs import SensorReadings, MachineData, ChatMessage
from retrivals import load_embeddings_from_file, search_query_in_embeddings
from BreakdownMaintenanceAdviceTool import BreakdownMaintenanceAdviceTool
from Orchestrator import Orchestrator
import uploads
from ml_predictor import get_predictor
from line_bot import get_line_notifier

# Load environment variables

from dotenv import load_dotenv

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

# LINE Bot users storage (replace with database in production)
line_users_store = {
    "users": [],  # List of LINE user IDs
    "alert_settings": {},  # User-specific alert settings
    "sent_alerts": {}  # Track sent alerts: {machine_id: {timestamp: alert_hash}}
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

def convert_sensor_names_to_tool_format(sensor_dict: dict) -> dict:
    """แปลงชื่อ field จาก frontend format เป็น tool format"""
    mapping = {
        "PowerMotor": "Power_Motor",
        "CurrentMotor": "Current_Motor",
        "SpeedMotor": "Speed_Motor",
        "SpeedRoller": "Speed_Roller",
        "TempBrassBearingDE": "Temperator_Brass_bearing_DE",
        "TempBearingMotorNDE": "Temperator_Bearing_Motor_NDE",
        "TempOilGear": "Temperator_Oil_Gear",
        "TempWindingMotorPhase_U": "Temperator_Winding_Motor_Phase_U",
        "TempWindingMotorPhase_V": "Temperator_Winding_Motor_Phase_V",
        "TempWindingMotorPhase_W": "Temperator_Winding_Motor_Phase_W",
        "Vibration": "Vibration"
    }
    return {mapping.get(k, k): v for k, v in sensor_dict.items()}

# API Endpoints
@app.get("/")
def read_root():
    return {"message": "Zero Breakdown Prediction API", "status": "running"}

@app.post("/api/upload-csv")
async def upload_csv(file: UploadFile = File(...), custom_name: Optional[str] = None):
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

        # Save as JSON file to disk - Local Path
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        CSV_DIR = os.path.join(backend_dir, "csv_data")
        os.makedirs(CSV_DIR, exist_ok=True)

        if custom_name:
            json_filename = f"{custom_name}.json"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_filename = f"factory_data_{timestamp}.json"

        json_filepath = os.path.join(CSV_DIR, json_filename)

        # Convert DataFrame to JSON with metadata
        json_data = {
            "metadata": {
                "filename": json_filename,
                "original_file": file.filename,
                "uploaded_at": datetime.now().isoformat(),
                "total_rows": len(df),
                "total_machines": len(machines),
                "date_range": date_range,
                "completeness": round(completeness, 2),
                "missing_values": int(missing_values),
                "custom_name": custom_name or f"factory_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            },
            "machines": machines,
            "data": json.loads(df.to_json(orient='records', date_format='iso'))
        }

        # Save to JSON file
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        # Store data globally
        uploaded_data_store["dataframe"] = df
        uploaded_data_store["machines"] = machines
        uploaded_data_store["metadata"] = {
            "total_rows": len(df),
            "total_machines": len(machines),
            "date_range": date_range,
            "completeness": round(completeness, 2),
            "missing_values": int(missing_values),
            "saved_file": json_filename,
            "filepath": json_filepath
        }

        return {
            "total_rows": len(df),
            "total_machines": len(machines),
            "machines": machines,
            "date_range": date_range,
            "saved_file": json_filename,
            "filepath": json_filepath,
            "data_quality": {
                "completeness": round(completeness, 2),
                "missing_values": int(missing_values)
            },
            "message": f"อัพโหลดและบันทึกข้อมูลเป็น JSON สำเร็จ: {json_filename}"
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

        # Auto-send LINE alert if there are warnings (ONCE per problem)
        if analysis['alerts']:
            # Calculate risk score
            risk_score = len(analysis['alerts']) * 15
            risk_level = "ต่ำ" if risk_score < 30 else "ปานกลาง" if risk_score < 60 else "สูง"

            # Create unique alert hash from alerts
            alert_hash = hashlib.md5(
                "|".join(sorted(analysis['alerts'])).encode('utf-8')
            ).hexdigest()

            # Check if we already sent this exact alert
            last_sent = line_users_store["sent_alerts"].get(machine_id, {})
            if last_sent.get("alert_hash") == alert_hash:
                print(f"⏭️  Skip duplicate alert for {machine_id} (already sent)")
            else:
                # Send LINE alert with repair instructions
                try:
                    line_notifier = get_line_notifier()
                    if line_notifier.is_configured() and line_users_store["users"]:
                        # Get detailed repair manual from RAG
                        repair_advice = "กรุณาตรวจสอบเครื่องจักร"
                        try:
                            backend_dir = os.path.dirname(os.path.abspath(__file__))
                            embeddings_file_path = os.path.join(backend_dir, "embeddings.json")
                            manuls_file_path = os.path.join(backend_dir, "manuls.txt")

                            embeddings = load_embeddings_from_file(embeddings_file_path)

                            with open(manuls_file_path, "r", encoding="utf-8") as file:
                                text_fitz = file.read()  # อ่านเนื้อหาทั้งหมดในไฟล์

                            # แบ่งข้อความตามบรรทัด
                            texts_strip = text_fitz.split("\n")  # หรือแบ่งตามพารากราฟได้

                            # กรองข้อความว่างออก
                            texts = [text for text in texts_strip if text.strip()]

                            # ตรวจสอบว่ามีการรับ query_text จาก request หรือไม่
                            query_text = "ปัญหาที่พบ: " + ", ".join(analysis['alerts'])

                            # ค้นหาคำถามใน embeddings
                            results = search_query_in_embeddings(query_text, embeddings, texts)

                            prompt = f"""คุณเป็นผู้เชี่ยวชาญด้านการซ่อมบำรุงเครื่องจักรโรงงานน้ำตาล โดยเฉพาะระบบ Feed Mill

คำถาม: {query_text}
โดยใช้เนื้อหาจาก: {results}

กรุณาตอบคำถามเกี่ยวกับการซ่อมบำรุงอย่างละเอียด รวมถึง:
ขั้นตอนการซ่อม
อุปกรณ์ที่ต้องใช้
ข้อควรระวัง
เวลาที่ใช้โดยประมาณ"""

                            # ส่งคำขอไปยังโมเดล qwen.qwen3-32b-v1:0 ผ่าน API
                            response_body = bedrock_runtime.converse(
                                modelId="qwen.qwen3-32b-v1:0",
                                messages=[
                                    {
                                        "role": "user",
                                        "content": [{"text": prompt}]
                                    }
                                ],
                                inferenceConfig={
                                    "maxTokens": 1024
                                }
                            )
                            repair_advice = response_body['output']['message']['content'][0]['text']
                        except Exception as e:
                            print(f"⚠️ RAG failed: {str(e)}")

                        messages = line_notifier.create_flex_alert_message(
                            machine_id=machine_id,
                            alerts=analysis['alerts'],
                            risk_score=risk_score,
                            risk_level=risk_level,
                            sensor_readings=sensor_data,
                            repair_advice=repair_advice
                        )

                        # Send to all users with alerts enabled
                        for user_id in line_users_store["users"]:
                            if line_users_store["alert_settings"].get(user_id, True):
                                line_notifier.send_push_message(user_id, messages)
                                print(f"📤 Auto-alert sent to LINE user: {user_id} for {machine_id}")

                        # Mark as sent
                        line_users_store["sent_alerts"][machine_id] = {
                            "alert_hash": alert_hash,
                            "timestamp": latest['Timestamp'].isoformat()
                        }
                except Exception as e:
                    print(f"⚠️ Failed to send auto LINE alert: {str(e)}")

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
        # แปลงชื่อ field ให้ตรงกับ tool format
        sensor_dict_for_tool = convert_sensor_names_to_tool_format(sensor_dict)
        analysis = maintenance_tool.analyze_sensors(sensor_dict_for_tool)

        # Generate maintenance advice using AWS Bedrock with RAG
        if analysis['alerts']:
            try:
                # Get the backend directory path
                backend_dir = os.path.dirname(os.path.abspath(__file__))
                embeddings_file_path = os.path.join(backend_dir, "embeddings.json")
                manuls_file_path = os.path.join(backend_dir, "manuls.txt")

                embeddings = load_embeddings_from_file(embeddings_file_path)

                with open(manuls_file_path, "r", encoding="utf-8") as file:
                    text_fitz = file.read()  # อ่านเนื้อหาทั้งหมดในไฟล์

                # แบ่งข้อความตามบรรทัด
                texts_strip = text_fitz.split("\n")  # หรือแบ่งตามพารากราฟได้

                # กรองข้อความว่างออก
                texts = [text for text in texts_strip if text.strip()]

                # ตรวจสอบว่ามีการรับ query_text จาก request หรือไม่
                query_text = f"ปัญหาเครื่องจักร {data.machine_type}: " + ", ".join(analysis['alerts'])

                # ค้นหาคำถามใน embeddings
                results = search_query_in_embeddings(query_text, embeddings, texts)

                prompt = f"""คุณเป็นผู้เชี่ยวชาญด้านการซ่อมบำรุงเครื่องจักรโรงงานน้ำตาล โดยเฉพาะระบบ Feed Mill

คำถาม: {query_text}
โดยใช้เนื้อหาจาก: {results}

ข้อมูล Sensor:
{json.dumps(sensor_dict, indent=2, ensure_ascii=False)}

ปัญหาที่พบ:
{chr(10).join(analysis['alerts'])}

ข้อมูลเปรียบเทียบค่าปกติของแต่ละ sensor:
- ค่าปกติของ PowerMotor อยู่ในช่วง 290-315 kW
- ค่าปกติของ CurrentMotor อยู่ในช่วง 280–320 Amp
- ค่าปกติของ TempBrassBearingDE อยู่ในช่วง < 75°C
- ค่าปกติของ SpeedMotor อยู่ในช่วง 1480–1495 rpm
- ค่าปกติของ TempOilGear อยู่ในช่วง < 65°C
- ค่าปกติของ TempBearingMotorNDE อยู่ในช่วง < 85°C
- ค่าปกติของ TempWindingMotorPhase_U/V/W อยู่ในช่วง < 105°C

กรุณาตอบคำถามเกี่ยวกับการซ่อมบำรุงอย่างละเอียด รวมถึง:
ขั้นตอนการซ่อม
อุปกรณ์ที่ต้องใช้
ข้อควรระวัง
เวลาที่ใช้โดยประมาณ"""

                # ส่งคำขอไปยังโมเดล qwen.qwen3-32b-v1:0 ผ่าน API
                response_body = bedrock_runtime.converse(
                    modelId="qwen.qwen3-32b-v1:0",
                    messages=[
                        {
                            "role": "user",
                            "content": [{"text": prompt}]
                        }
                    ],
                    inferenceConfig={
                        "maxTokens": 1024
                    }
                )
                maintenance_advice = response_body['output']['message']['content'][0]['text']

            except Exception as e:
                print(f"⚠️ RAG lookup failed: {str(e)}")
                maintenance_advice = f"เกิดข้อผิดพลาดในการค้นหาคู่มือ: {str(e)}"

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
        # แปลงชื่อ field ให้ตรงกับ tool format
        sensor_dict_for_tool = convert_sensor_names_to_tool_format(sensor_dict)
        analysis = maintenance_tool.analyze_sensors(sensor_dict_for_tool)

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

รหัสเครื่องจักรนี้คือ ABB M3BP355SMB4

โดยให้คำทำนายเกี่ยวกับ:
1. โอกาสที่เครื่องจักรจะเสียหาย
2. อายุการใช้งานโดยประมาณที่เหลืออยู่
3. ส่วนประกอบที่มีความเสี่ยงสูงสุด"""
        
        
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
        # prediction = response_body['content'][0]['text']
        # ส่งคำขอไปยังโมเดล qwen.qwen3-32b-v1:0 ผ่าน API
        response = bedrock_runtime.converse(
            modelId="qwen.qwen3-32b-v1:0",
            messages=[
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ],
            inferenceConfig={
                "maxTokens": 1024
            }
        )
        prediction = response['output']['message']['content'][0]['text']

        return {
            "machine_type": data.machine_type,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "prediction": prediction,
            "alerts": analysis['alerts']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/predict-ml-breakdown")
async def predict_ml_breakdown(data: MachineData):
    """ทำนายความเสี่ยงด้วย ML Model (pm_model_fullpipeline.py)"""
    try:
        sensor_dict = data.sensor_readings.model_dump()

        # Get ML predictor
        predictor = get_predictor()

        # Make prediction
        ml_result = predictor.predict_single(sensor_dict)

        # Add metadata
        ml_result["machine_type"] = data.machine_type
        ml_result["timestamp"] = data.timestamp

        return ml_result

    except Exception as e:
        import traceback
        print(f"Error in /api/predict-ml-breakdown: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/repair-manual")
async def get_repair_manual(request: ChatMessage):

    """ค้นหาคู่มือการซ่อม (ใช้ AI ตอบคำถาม)"""
    try:
        # Get the backend directory path
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        embeddings_file_path = os.path.join(backend_dir, "embeddings.json")
        manuls_file_path = os.path.join(backend_dir, "manuls.txt")

        embeddings = load_embeddings_from_file(embeddings_file_path)

        with open(manuls_file_path, "r", encoding="utf-8") as file:
            text_fitz = file.read()  # อ่านเนื้อหาทั้งหมดในไฟล์

        # แบ่งข้อความตามบรรทัด
        texts_strip = text_fitz.split("\n")  # หรือแบ่งตามพารากราฟได้

        # กรองข้อความว่างออก
        texts = [text for text in texts_strip if text.strip()]

        # ตรวจสอบว่ามีการรับ query_text จาก request หรือไม่
        query_text = request.message  # สมมติว่า message จาก request คือคำถามที่ต้องการค้นหา

        # ค้นหาคำถามใน embeddings
        results = search_query_in_embeddings(query_text, embeddings, texts)

        prompt = f"""คุณเป็นผู้เชี่ยวชาญด้านการซ่อมบำรุงเครื่องจักรโรงงานน้ำตาล โดยเฉพาะระบบ Feed Mill

คำถาม: {query_text}
โดยใช้เนื้อหาจาก: {results}

กรุณาตอบคำถามเกี่ยวกับการซ่อมบำรุงอย่างละเอียด รวมถึง:
ขั้นตอนการซ่อม
อุปกรณ์ที่ต้องใช้
ข้อควรระวัง
เวลาที่ใช้โดยประมาณ"""

        # ส่งคำขอไปยังโมเดล qwen.qwen3-32b-v1:0 ผ่าน API
        response_body = bedrock_runtime.converse(
            modelId="qwen.qwen3-32b-v1:0",
            messages=[
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ],
            inferenceConfig={
                "maxTokens": 1024
            }
        )
        manual_content = response_body['output']['message']['content'][0]['text']

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
        print(f"Received chat request: {request.message}")
        # Determine which function to use based on message
        messager = request.message
        Host_Agent = Orchestrator(messager)
        agent_response=Host_Agent.run(messager) 

        return {
            "message": request.message,
            "response": agent_response
        }
    except Exception as e:
        import traceback
        print(f"Error in /api/chat: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/orchestrator-chat")
async def orchestrator_chat(request: ChatMessage):
    """Orchestrator-based Chat - ใช้ Tool calling ผ่าน AWS Bedrock"""
    try:
        print(f"Received orchestrator chat request: {request.message}")

        # สร้าง Orchestrator instance และส่ง user input เข้าไป
        orchestrator = Orchestrator()

        # เรียกใช้ run() โดยส่ง user_input เข้าไป (ใช้ _get_user_input ภายใน)
        response_text = orchestrator.run(user_input=request.message)

        return {
            "message": request.message,
            "response": response_text,
            "tools_used": [],  # Orchestrator จะจัดการ tools ภายใน
            "stop_reason": "completed"
        }

    except Exception as e:
        import traceback
        print(f"Error in /api/orchestrator-chat: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# ===== Embeddings Management Endpoints =====

class RenameRequest(BaseModel):
    old_filename: str
    new_name: str

@app.post("/api/upload-pdf")
async def upload_pdf(file: UploadFile = File(...), custom_name: Optional[str] = None):
    """อัพโหลดไฟล์ PDF และสร้าง embeddings"""
    try:
        # Save temp PDF file
        import tempfile
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, file.filename)

        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Generate and save embeddings
        result = uploads.save_embedding(temp_path, custom_name)

        # Remove temp file
        os.remove(temp_path)

        return {
            "success": True,
            "message": "สร้าง embeddings สำเร็จ",
            **result
        }
    except Exception as e:
        import traceback
        print(f"Error in /api/upload-pdf: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/embeddings")
async def list_embeddings():
    """ดึงรายการไฟล์ embeddings ทั้งหมด"""
    try:
        files = uploads.list_embedding_files()
        return {
            "files": files,
            "total": len(files)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/embeddings/{filename}")
async def get_embedding_info(filename: str):
    """ดึงข้อมูลรายละเอียดของไฟล์ embedding"""
    try:
        info = uploads.get_embedding_file_info(filename)
        return info
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/embeddings/rename")
async def rename_embedding(request: RenameRequest):
    """เปลี่ยนชื่อไฟล์ embedding"""
    try:
        result = uploads.rename_embedding_file(request.old_filename, request.new_name)
        return {
            "success": True,
            "message": "เปลี่ยนชื่อไฟล์สำเร็จ",
            **result
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FileExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/embeddings/{filename}")
async def delete_embedding(filename: str):
    """ลบไฟล์ embedding"""
    try:
        result = uploads.delete_embedding_file(filename)
        return {
            "success": True,
            "message": "ลบไฟล์สำเร็จ",
            **result
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== LINE Bot Endpoints =====

def verify_line_signature(body: bytes, signature: str) -> bool:
    """Verify LINE webhook signature"""
    line_notifier = get_line_notifier()
    if not line_notifier.channel_secret:
        return False

    hash_digest = hmac.new(
        line_notifier.channel_secret.encode('utf-8'),
        body,
        hashlib.sha256
    ).digest()

    computed_signature = base64.b64encode(hash_digest).decode('utf-8')
    return hmac.compare_digest(signature, computed_signature)


@app.post("/api/line/webhook")
async def line_webhook(request: Request, x_line_signature: str = Header(None)):
    """LINE Bot Webhook endpoint"""
    try:
        body = await request.body()
        print(f"📥 Received webhook request")
        print(f"   Body length: {len(body)}")
        print(f"   Signature: {x_line_signature}")

        # Verify signature (disabled for testing)
        # if not verify_line_signature(body, x_line_signature or ""):
        #     raise HTTPException(status_code=400, detail="Invalid signature")

        # Parse JSON
        try:
            events_data = json.loads(body.decode('utf-8'))
            print(f"   Parsed JSON: {events_data}")
        except json.JSONDecodeError as je:
            print(f"⚠️ JSON decode error: {str(je)}")
            # Return OK for verification requests that might not have valid JSON
            return {"status": "ok"}

        # Handle events
        events_list = events_data.get('events', [])
        print(f"   Events count: {len(events_list)}")

        for event in events_list:
            print(f"   Event type: {event.get('type')}")

            if event['type'] == 'message' and event['message']['type'] == 'text':
                # Handle text message
                user_id = event['source']['userId']
                message_text = event['message']['text'].lower()

                # Add user to storage if not exists
                if user_id not in line_users_store["users"]:
                    line_users_store["users"].append(user_id)
                    print(f"✅ New LINE user registered: {user_id}")

                # Reply based on message
                line_notifier = get_line_notifier()

                if 'สถานะ' in message_text or 'status' in message_text:
                    # Send current machine status
                    if uploaded_data_store["dataframe"] is not None:
                        machines = uploaded_data_store["machines"]
                        reply = f"📊 สถานะเครื่องจักร\n\n"
                        reply += f"จำนวนเครื่อง: {len(machines)} เครื่อง\n"
                        reply += f"รายการ: {', '.join(machines[:5])}"
                        if len(machines) > 5:
                            reply += f" และอื่นๆ อีก {len(machines) - 5} เครื่อง"
                    else:
                        reply = "⚠️ ยังไม่มีข้อมูลเครื่องจักร"

                    line_notifier.send_push_message(user_id, [{"type": "text", "text": reply}])

                elif 'ช่วยเหลือ' in message_text or 'help' in message_text:
                    help_text = """🤖 คำสั่งที่ใช้ได้:

1️⃣ 'สถานะ' - ดูสถานะเครื่องจักร
2️⃣ 'แจ้งเตือน เปิด' - เปิดการแจ้งเตือน
3️⃣ 'แจ้งเตือน ปิด' - ปิดการแจ้งเตือน
4️⃣ 'ช่วยเหลือ' - แสดงคำสั่ง

ระบบจะแจ้งเตือนอัตโนมัติเมื่อเครื่องจักรมีความเสี่ยง"""

                    line_notifier.send_push_message(user_id, [{"type": "text", "text": help_text}])

                elif 'แจ้งเตือน' in message_text:
                    if 'เปิด' in message_text:
                        line_users_store["alert_settings"][user_id] = True
                        reply = "✅ เปิดการแจ้งเตือนแล้ว คุณจะได้รับแจ้งเตือนเมื่อเครื่องจักรมีความเสี่ยง"
                    elif 'ปิด' in message_text:
                        line_users_store["alert_settings"][user_id] = False
                        reply = "❌ ปิดการแจ้งเตือนแล้ว"
                    else:
                        status = "เปิด ✅" if line_users_store["alert_settings"].get(user_id, True) else "ปิด ❌"
                        reply = f"สถานะการแจ้งเตือน: {status}"

                    line_notifier.send_push_message(user_id, [{"type": "text", "text": reply}])

                else:
                    # Default welcome message
                    welcome_text = """สวัสดีครับ! 👋

ผมเป็นบอทแจ้งเตือนสถานะเครื่องจักร Zero Breakdown

พิมพ์ 'ช่วยเหลือ' เพื่อดูคำสั่งทั้งหมด"""

                    line_notifier.send_push_message(user_id, [{"type": "text", "text": welcome_text}])

            elif event['type'] == 'follow':
                # User added bot as friend
                user_id = event['source']['userId']
                if user_id not in line_users_store["users"]:
                    line_users_store["users"].append(user_id)
                    line_users_store["alert_settings"][user_id] = True
                    print(f"✅ New LINE friend: {user_id}")

        print("✅ Webhook processed successfully")
        return {"status": "ok"}

    except Exception as e:
        import traceback
        print(f"❌ Error in LINE webhook: {str(e)}")
        print(traceback.format_exc())
        # Return 200 OK even on error to prevent LINE from retrying
        return {"status": "error", "message": str(e)}


@app.post("/api/line/send-alert")
async def send_line_alert(machine_id: str, alerts: List[str], risk_score: int = 0,
                         risk_level: str = "ไม่ทราบ", user_id: Optional[str] = None):
    """ส่งแจ้งเตือนผ่าน LINE Bot"""
    try:
        line_notifier = get_line_notifier()

        if not line_notifier.is_configured():
            raise HTTPException(status_code=503, detail="LINE Bot not configured")

        # Create flex message
        messages = line_notifier.create_flex_alert_message(
            machine_id=machine_id,
            alerts=alerts,
            risk_score=risk_score,
            risk_level=risk_level
        )

        sent_count = 0

        if user_id:
            # Send to specific user
            if line_notifier.send_push_message(user_id, messages):
                sent_count = 1
        else:
            # Send to all users with alerts enabled
            for uid in line_users_store["users"]:
                if line_users_store["alert_settings"].get(uid, True):
                    if line_notifier.send_push_message(uid, messages):
                        sent_count += 1

        return {
            "success": True,
            "sent_to": sent_count,
            "message": f"ส่งแจ้งเตือนไปยัง {sent_count} ผู้ใช้"
        }

    except Exception as e:
        import traceback
        print(f"Error sending LINE alert: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/line/users")
async def get_line_users():
    """ดึงรายชื่อผู้ใช้ LINE Bot"""
    try:
        users_with_settings = []
        for user_id in line_users_store["users"]:
            users_with_settings.append({
                "user_id": user_id,
                "alerts_enabled": line_users_store["alert_settings"].get(user_id, True)
            })

        return {
            "total_users": len(line_users_store["users"]),
            "users": users_with_settings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/line/test-alert")
async def test_line_alert():
    """ทดสอบส่งแจ้งเตือนผ่าน LINE"""
    try:
        test_alerts = [
            "CurrentMotor ผิดปกติ: 350 A (เกินค่าปกติ)",
            "อุณหภูมิสูงกว่าปกติ: 92°C"
        ]

        result = await send_line_alert(
            machine_id="Feed Mill 1 (ทดสอบ)",
            alerts=test_alerts,
            risk_score=65,
            risk_level="สูง"
        )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)