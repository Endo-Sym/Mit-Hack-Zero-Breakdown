# LINE Bot Setup Guide

## การตั้งค่า LINE Bot สำหรับระบบแจ้งเตือนเครื่องจักร

### 1. สร้าง LINE Bot Account

1. เข้าไปที่ [LINE Developers Console](https://developers.line.biz/console/)
2. Login ด้วย LINE account
3. Create a new provider (ถ้ายังไม่มี)
4. Create a new channel → เลือก **Messaging API**
5. กรอกข้อมูล:
   - Channel name: `Zero Breakdown Alert Bot`
   - Channel description: `แจ้งเตือนสถานะเครื่องจักร`
   - Category: เลือกที่เหมาะสม
6. กด **Create**

### 2. ดึง Credentials

#### Channel Access Token:
1. ไปที่แท็บ **Messaging API**
2. ส่วน **Channel access token** → กด **Issue**
3. คัดลอก token ที่ได้

#### Channel Secret:
1. ไปที่แท็บ **Basic settings**
2. ส่วน **Channel secret** → กด **Show** แล้วคัดลอก

### 3. ตั้งค่า Webhook

1. ไปที่แท็บ **Messaging API**
2. ส่วน **Webhook settings**:
   - **Webhook URL**: `https://your-domain.com/api/line/webhook`
     - สำหรับการทดสอบ ใช้ [ngrok](https://ngrok.com/): `ngrok http 8000`
     - URL จะเป็น: `https://xxxx.ngrok.io/api/line/webhook`
   - เปิด **Use webhook**: ON
   - เปิด **Webhook redelivery**: ON (optional)
3. กด **Verify** เพื่อทดสอบ webhook
4. ปิด **Auto-reply messages** (ไปที่ LINE Official Account Manager)

### 4. ตั้งค่า Environment Variables

สร้างไฟล์ `.env` ใน folder `backend/`:

```bash
# LINE Bot Configuration
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token_here
LINE_CHANNEL_SECRET=your_channel_secret_here

# AWS Configuration (ถ้ามี)
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_DEFAULT_REGION=us-west-2
```

### 5. รัน Backend Server

```bash
cd backend
python main.py
```

Server จะรันที่ `http://localhost:8000`

### 6. เชื่อมต่อกับ LINE Bot

#### วิธีที่ 1: ใช้ ngrok (สำหรับทดสอบ)

```bash
# Terminal ใหม่
ngrok http 8000
```

คัดลอก URL ที่ได้ (เช่น `https://xxxx.ngrok.io`) และใส่ใน Webhook URL:
```
https://xxxx.ngrok.io/api/line/webhook
```

#### วิธีที่ 2: Deploy to Production

Deploy backend ไปยัง server (AWS, GCP, Azure, etc.) แล้วใส่ URL จริง

### 7. เพิ่มเพื่อนกับ Bot

1. ไปที่แท็บ **Messaging API**
2. สแกน **QR code** ด้วย LINE app
3. เพิ่มเพื่อน
4. ส่งข้อความ "ช่วยเหลือ" เพื่อดูคำสั่งทั้งหมด

## API Endpoints

### 1. Webhook (รับข้อความจาก LINE)
```
POST /api/line/webhook
```

### 2. ส่งแจ้งเตือน
```bash
POST /api/line/send-alert
Content-Type: application/json

{
  "machine_id": "Feed Mill 1",
  "alerts": ["CurrentMotor ผิดปกติ", "อุณหภูมิสูงเกินไป"],
  "risk_score": 75,
  "risk_level": "สูง"
}
```

### 3. ทดสอบส่งแจ้งเตือน
```bash
POST /api/line/test-alert
```

### 4. ดูรายชื่อผู้ใช้
```bash
GET /api/line/users
```

## คำสั่ง LINE Bot

| คำสั่ง | คำอธิบาย |
|--------|----------|
| `สถานะ` | ดูสถานะเครื่องจักรทั้งหมด |
| `แจ้งเตือน เปิด` | เปิดการรับแจ้งเตือน |
| `แจ้งเตือน ปิด` | ปิดการรับแจ้งเตือน |
| `แจ้งเตือน` | ดูสถานะการแจ้งเตือนปัจจุบัน |
| `ช่วยเหลือ` | แสดงคำสั่งทั้งหมด |

## การแจ้งเตือนอัตโนมัติ

ระบบจะส่งแจ้งเตือนอัตโนมัติเมื่อ:
- CurrentMotor < 280A หรือ > 320A (Warning)
- CurrentMotor < 240A หรือ > 360A (Danger)
- Temperature > 75°C (Normal Max)
- Temperature > 85°C (Warning)
- Temperature > 95°C (Danger)

## ตัวอย่างการใช้งาน

### Python
```python
import requests

# ส่งแจ้งเตือน
response = requests.post('http://localhost:8000/api/line/send-alert', json={
    "machine_id": "Feed Mill 1",
    "alerts": ["CurrentMotor: 350A เกินค่าปกติ"],
    "risk_score": 60,
    "risk_level": "ปานกลาง"
})

print(response.json())
```

### cURL
```bash
curl -X POST http://localhost:8000/api/line/test-alert
```

## Troubleshooting

### 1. Webhook ไม่ทำงาน
- ตรวจสอบว่า ngrok รันอยู่
- ตรวจสอบ webhook URL ใน LINE Console
- ดู logs ของ backend

### 2. ไม่ได้รับข้อความ
- ตรวจสอบว่าเพิ่มเพื่อนกับ bot แล้ว
- ตรวจสอบ LINE_CHANNEL_ACCESS_TOKEN ถูกต้อง
- ดู backend logs

### 3. Signature verification failed
- ตรวจสอบ LINE_CHANNEL_SECRET ถูกต้อง
- ตรวจสอบว่า request มาจาก LINE จริง

## เพิ่มเติม

- [LINE Messaging API Documentation](https://developers.line.biz/en/docs/messaging-api/)
- [Flex Message Simulator](https://developers.line.biz/flex-simulator/)