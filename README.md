# 🔧 Zero Breakdown Prediction System

ระบบ Agentic AI สำหรับทำนายและวิเคราะห์การเสียหายของเครื่องจักรโรงงานน้ำตาล

## ✨ ฟีเจอร์หลัก

### 1. 📊 ทำนาย Zero Breakdown ของเครื่องจักร
- วิเคราะห์ข้อมูลจาก 10 sensors แบบ real-time
- ระบบแจ้งเตือนตามเกณฑ์ที่กำหนด (ปกติ/เสี่ยง/เสียหาย)
- ทำนายความเสี่ยงและอายุการใช้งานที่เหลือ
- ให้คำแนะนำการซ่อมบำรุงโดย AI

**Sensors ที่รองรับ:**
- PowerMotor (kW)
- CurrentMotor (Amp)
- TempBrassBearingDE (°C)
- SpeedMotor (rpm)
- SpeedRoller (rpm)
- TempOilGear (°C)
- TempBearingMotorNDE (°C)
- TempWindingMotorPhase U/V/W (°C)
- Vibration (mm/s)

### 2. 💰 คำนวณ ROI (Return on Investment)
- เปรียบเทียบต้นทุนการซ่อมในช่วงเวลาต่างๆ
- คำนวณผลกระทบจากการสูญเสียประสิทธิภาพ
- วิเคราะห์ความคุ้มค่าของการซ่อม
- แนะนำช่วงเวลาที่เหมาะสมในการซ่อม

**ตัวอย่างการใช้งาน:**
- เปรียบเทียบการซ่อมที่สุขภาพเครื่องจักร 70% vs 50%
- คำนวณเงินที่ประหยัดได้จากการซ่อมตอนนี้
- วิเคราะห์ผลตอบแทนต่อการลงทุน (ROI %)

### 3. 📖 คู่มือการซ่อม
- ค้นหาวิธีการซ่อมและข้อมูลทางเทคนิค
- ตอบคำถามโดย AI ที่เชื่อมต่อกับ AWS Bedrock
- แสดงขั้นตอนการซ่อมอย่างละเอียด
- ให้คำแนะนำอุปกรณ์และข้อควรระวัง

### 4. 💬 Chat AI Agent
- ระบบ AI ที่จัดการคำถามอัตโนมัติ
- แยกประเภทคำถามและเลือกฟังก์ชันที่เหมาะสม
- รองรับภาษาไทย
- ตอบคำถามแบบ real-time

## 🏗️ สถาปัตยกรรมระบบ

```
┌─────────────────────────────────────┐
│   React Frontend (Vite)             │
│   - Chat Interface                  │
│   - Sensor Analysis UI              │
│   - ROI Calculator UI               │
│   - Repair Manual UI                │
└──────────────┬──────────────────────┘
               │ HTTP (axios)
               │ Port 5173 → 8000
               ↓
┌─────────────────────────────────────┐
│   Python FastAPI Backend            │
│   - Sensor Threshold Analysis       │
│   - Breakdown Prediction Logic      │
│   - ROI Calculation Engine          │
│   - Chat Agent Routing              │
└──────────────┬──────────────────────┘
               │
               │ AWS Bedrock API
               ↓
┌─────────────────────────────────────┐
│   AWS Bedrock (Claude AI)           │
│   - Maintenance Advice Generation   │
│   - Breakdown Prediction            │
│   - ROI Analysis                    │
│   - Repair Manual Q&A               │
└─────────────────────────────────────┘
```

## 🚀 การติดตั้งและรัน

### ข้อกำหนดเบื้องต้น
- Node.js 20.x หรือสูงกว่า
- Python 3.9+
- AWS Account พร้อม Bedrock access
- AWS CLI configured

### 1. ติดตั้ง Backend (FastAPI)

```bash
cd backend

# สร้าง virtual environment
python -m venv venv

# เปิดใช้งาน virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# ติดตั้ง dependencies
pip install -r requirements.txt

# ตั้งค่า AWS credentials
# ตรวจสอบว่า AWS CLI configured แล้ว หรือตั้งค่า environment variables:
# export AWS_ACCESS_KEY_ID=your_key
# export AWS_SECRET_ACCESS_KEY=your_secret
# export AWS_DEFAULT_REGION=us-west-2

# รัน FastAPI server
python main.py
```

Backend จะทำงานที่: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### 2. ติดตั้ง Frontend (React)

```bash
cd zero-breakdown-app

# ติดตั้ง dependencies
npm install

# รัน development server
npm run dev
```

Frontend จะทำงานที่: `http://localhost:5173`

## 📡 API Endpoints

### 1. Sensor Analysis
```http
POST /api/analyze-sensors
Content-Type: application/json

{
  "timestamp": "2025-09-29T13:00:00+07:00",
  "machine_type": "Feed Mill 1",
  "sensor_readings": {
    "PowerMotor": 295,
    "CurrentMotor": 300,
    "TempBrassBearingDE": 65,
    "SpeedMotor": 1485,
    "SpeedRoller": 5.5,
    "TempOilGear": 60,
    "TempBearingMotorNDE": 70,
    "TempWindingMotorPhase_U": 100,
    "TempWindingMotorPhase_V": 98,
    "TempWindingMotorPhase_W": 97,
    "Vibration": 1.5
  }
}
```

### 2. Breakdown Prediction
```http
POST /api/predict-breakdown
Content-Type: application/json

{
  "timestamp": "2025-09-29T13:00:00+07:00",
  "machine_type": "Feed Mill 1",
  "sensor_readings": { ... }
}
```

### 3. ROI Calculation
```http
POST /api/calculate-roi
Content-Type: application/json

{
  "current_health_percentage": 70,
  "comparison_health_percentage": 50,
  "repair_cost": 50000,
  "daily_production_value": 100000
}
```

### 4. Repair Manual
```http
POST /api/repair-manual
Content-Type: application/json

{
  "message": "วิธีการเปลี่ยนน้ำมันเกียร์"
}
```

### 5. Chat Agent
```http
POST /api/chat
Content-Type: application/json

{
  "message": "ช่วยทำนายว่าเครื่องจักรจะเสียหายเมื่อไหร่"
}
```

## 🔧 Sensor Thresholds

| Sensor | ปกติ | เสี่ยง | เสียหาย |
|--------|------|--------|---------|
| PowerMotor (kW) | 280-320 | 270-280, 320-325 | <260, >360 |
| CurrentMotor (Amp) | 270-330 | 260-270, 330-340 | <240, >360 |
| TempBrassBearingDE (°C) | <75 | 75-85 | >95 |
| TempBearingMotorNDE (°C) | <75 | 75-85 | >95 |
| SpeedMotor (rpm) | 1470-1500 | 1450-1470, 1500-1510 | 0 |
| TempOilGear (°C) | <65 | 65-75 | >85 |
| TempWindingPhase (°C) | <115 | 115-125 | >125 |
| Vibration (mm/s) | <0.71 (ดีมาก), 0.71-1.8 (ดี) | 1.8-4.5 (พอใช้) | >4.5 (ไม่พอใช้) |

## 🎨 Technologies Used

### Frontend
- **React 18** - UI Library
- **Vite** - Build Tool
- **Axios** - HTTP Client
- **React Markdown** - Markdown Renderer

### Backend
- **FastAPI** - Web Framework
- **Pydantic** - Data Validation
- **Boto3** - AWS SDK
- **Uvicorn** - ASGI Server

### AI/ML
- **AWS Bedrock** - AI Service
- **Claude 3 Haiku** - Language Model
- **Rule-based Threshold System** - Sensor Analysis

## 📝 โครงสร้างโปรเจกต์

```
Mit-Hack-Zero-Breakdown/
├── backend/
│   ├── main.py                 # FastAPI application
│   └── requirements.txt        # Python dependencies
├── zero-breakdown-app/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.jsx
│   │   │   ├── ChatInterface.css
│   │   │   ├── SensorAnalysis.jsx
│   │   │   ├── SensorAnalysis.css
│   │   │   ├── ROICalculator.jsx
│   │   │   ├── ROICalculator.css
│   │   │   ├── RepairManual.jsx
│   │   │   └── RepairManual.css
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 🔐 การตั้งค่า AWS Bedrock

1. สร้าง AWS Account และเปิดใช้งาน Bedrock
2. Request access สำหรับ Claude 3 Haiku model
3. สร้าง IAM User พร้อม permissions:
   - `bedrock:InvokeModel`
   - `bedrock:InvokeModelWithResponseStream`
4. Configure AWS CLI:
```bash
aws configure
# ใส่ AWS Access Key ID
# ใส่ AWS Secret Access Key
# ใส่ Region: us-west-2
```

## ⚠️ ข้อควรระวัง

1. **AWS Bedrock Cost**: การใช้งาน Claude AI มีค่าใช้จ่าย ตรวจสอบ pricing ที่ AWS
2. **API Rate Limits**: Bedrock มี rate limits ตรวจสอบ quota
3. **Security**: ห้าม commit AWS credentials ลงใน Git
4. **CORS**: Backend ตั้งค่าให้รับ request จาก localhost:5173 เท่านั้น

## 🐛 Troubleshooting

### Backend ไม่สามารถเชื่อมต่อ AWS Bedrock
```bash
# ตรวจสอบ AWS credentials
aws sts get-caller-identity

# ตรวจสอบว่ามี access ถึง Bedrock
aws bedrock list-foundation-models --region us-west-2
```

### Frontend ไม่สามารถเชื่อมต่อ Backend
- ตรวจสอบว่า Backend กำลังรันอยู่ที่ port 8000
- ตรวจสอบ CORS settings ใน `backend/main.py`
- เปิด Browser Console เพื่อดู error messages

### Node version warning
- ระบบจะทำงานได้ถึงแม้จะมี warning เกี่ยวกับ Node version
- แนะนำให้ upgrade เป็น Node 20.19+ หรือ 22.12+ สำหรับการใช้งานจริง

## 📄 License

MIT License - ใช้งานได้อย่างอิสระ

## 👨‍💻 Authors

สร้างสำหรับ Mit-Hack Zero Breakdown Project

## 🙏 Acknowledgments

- AWS Bedrock สำหรับ AI capabilities
- Anthropic Claude สำหรับ language model
- ข้อมูลจาก `Nut_Function_Rag.ipynb` สำหรับ business logic