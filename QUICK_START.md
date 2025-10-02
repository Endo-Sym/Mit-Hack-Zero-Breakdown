# Quick Start Guide - Zero Breakdown System

## 🚀 การเริ่มต้นใช้งานอย่างรวดเร็ว

### 1. Setup Environment

```bash
# ติดตั้ง dependencies
cd backend
pip install -r requirements.txt

cd ../zero-breakdown-app
npm install
```

### 2. ตั้งค่า Environment Variables

สร้างไฟล์ `backend/.env`:

```bash
# LINE Bot (ถ้าต้องการใช้การแจ้งเตือน)
LINE_CHANNEL_ACCESS_TOKEN=your_token_here
LINE_CHANNEL_SECRET=your_secret_here

# AWS Bedrock
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_DEFAULT_REGION=us-west-2
```

### 3. รัน Backend

```bash
cd backend
python main.py
```

Backend จะรันที่: `http://localhost:8000`

### 4. รัน Frontend

```bash
cd zero-breakdown-app
npm run dev
```

Frontend จะรันที่: `http://localhost:5173`

### 5. ทดสอบระบบ

#### 5.1 อัพโหลดข้อมูล CSV

1. ไปที่ http://localhost:5173
2. เลือกแท็บ "วิเคราะห์ข้อมูล Sensor"
3. อัพโหลดไฟล์ `sample_sensor_data.csv`
4. ระบบจะประมวลผลและบันทึกข้อมูล

#### 5.2 ดู Dashboard

1. ไปที่แท็บ "Dashboard"
2. เลือกเครื่องจักร
3. ดูกราฟแสดงค่า sensor พร้อมเส้นเกณฑ์แจ้งเตือน
4. ถ้าค่าเกินเกณฑ์จะมี alert banner สีแดง

#### 5.3 ทดสอบ LINE Bot (Optional)

```bash
# ติดตั้ง ngrok
ngrok http 8000

# ตั้งค่า webhook URL ใน LINE Developers:
# https://xxxx.ngrok.io/api/line/webhook

# ทดสอบส่งแจ้งเตือน
cd backend
python test_line_bot.py
```

## 📊 ฟีเจอร์หลัก

### 1. Dashboard
- แสดงข้อมูล sensor แบบเรียลไทม์
- กราฟพร้อมเส้นเกณฑ์แจ้งเตือน
- Alert banner เมื่อค่าผิดปกติ

### 2. การวิเคราะห์ข้อมูล
- อัพโหลด CSV
- วิเคราะห์ sensor
- ทำนายความเสี่ยง (ML Model)

### 3. LINE Bot
- รับแจ้งเตือนอัตโนมัติ
- ตรวจสอบสถานะเครื่องจักร
- เปิด/ปิดการแจ้งเตือน

### 4. AI Chat
- ถามคำถามเกี่ยวกับการซ่อมบำรุง
- ค้นหาคู่มือ
- รับคำแนะนำจาก AI

## 🔧 API Endpoints

### Machine Data
```bash
GET  /api/machines                 # รายการเครื่องจักร
GET  /api/machine-data/{id}        # ข้อมูลเครื่องจักร
POST /api/upload-csv               # อัพโหลด CSV
POST /api/analyze-sensors          # วิเคราะห์ sensor
POST /api/predict-ml-breakdown     # ทำนายด้วย ML
```

### LINE Bot
```bash
POST /api/line/webhook             # Webhook จาก LINE
POST /api/line/send-alert          # ส่งแจ้งเตือน
POST /api/line/test-alert          # ทดสอบแจ้งเตือน
GET  /api/line/users               # รายชื่อผู้ใช้
```

### AI Chat
```bash
POST /api/chat                     # Agentic AI Chat
POST /api/repair-manual            # คู่มือการซ่อม
```

## 📱 LINE Bot Commands

| คำสั่ง | คำอธิบาย |
|--------|----------|
| `สถานะ` | ดูสถานะเครื่องจักร |
| `แจ้งเตือน เปิด` | เปิดการแจ้งเตือน |
| `แจ้งเตือน ปิด` | ปิดการแจ้งเตือน |
| `ช่วยเหลือ` | แสดงคำสั่งทั้งหมด |

## ⚠️ Thresholds (เกณฑ์แจ้งเตือน)

### CurrentMotor
- ✅ Normal: 280-320 A
- ⚠️ Warning: < 280 หรือ > 320 A
- 🔴 Danger: < 240 หรือ > 360 A

### Temperature (TempBrassBearingDE)
- ✅ Normal: < 75°C
- ⚠️ Warning: 75-85°C
- 🚨 High: 85-95°C
- 🔴 Danger: > 95°C

## 🐛 Troubleshooting

### Backend ไม่รัน
```bash
# ตรวจสอบ port ว่าว่างหรือไม่
netstat -ano | findstr :8000

# Restart backend
cd backend
python main.py
```

### Frontend ไม่รัน
```bash
# ติดตั้ง dependencies ใหม่
cd zero-breakdown-app
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### LINE Bot ไม่ส่งแจ้งเตือน
1. ตรวจสอบ `.env` มี `LINE_CHANNEL_ACCESS_TOKEN` และ `LINE_CHANNEL_SECRET`
2. ตรวจสอบ ngrok รันอยู่
3. ตรวจสอบ webhook URL ใน LINE Console
4. ดู backend logs

## 📚 เอกสารเพิ่มเติม

- [LINE Bot Setup Guide](./LINE_BOT_SETUP.md) - คู่มือตั้งค่า LINE Bot แบบละเอียด
- [API Documentation](http://localhost:8000/docs) - FastAPI Swagger Docs

## 🎯 ขั้นตอนถัดไป

1. ✅ อัพโหลดข้อมูล CSV จริงของโรงงาน
2. ✅ ตั้งค่า LINE Bot และเพิ่มเพื่อน
3. ✅ ทดสอบการแจ้งเตือนอัตโนมัติ
4. ✅ Train ML Model ด้วยข้อมูลจริง (`pm_model_fullpipeline.py`)
5. ✅ Deploy ไปยัง production server

---

**Zero Breakdown System** - Predictive Maintenance for Sugar Mill Feed System