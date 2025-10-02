"""
Test script for LINE Bot integration
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_line_bot_configured():
    """Test if LINE Bot is configured"""
    print("🧪 Testing LINE Bot Configuration...")

    response = requests.get(f"{BASE_URL}/api/line/users")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ LINE Bot configured")
        print(f"   Total users: {data['total_users']}")
        if data['total_users'] > 0:
            print(f"   Users: {json.dumps(data['users'], indent=2, ensure_ascii=False)}")
    else:
        print(f"❌ Error: {response.status_code}")

def test_send_alert():
    """Test sending alert to LINE"""
    print("\n🧪 Testing Send Alert...")

    payload = {
        "machine_id": "Feed Mill 1 (ทดสอบ)",
        "alerts": [
            "CurrentMotor: 350A เกินค่าปกติ (>320A)",
            "Temperature: 92°C สูงกว่าปกติ (>85°C)"
        ],
        "risk_score": 70,
        "risk_level": "สูง"
    }

    response = requests.post(
        f"{BASE_URL}/api/line/send-alert",
        params=payload
    )

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Alert sent successfully")
        print(f"   {json.dumps(data, indent=2, ensure_ascii=False)}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")

def test_quick_alert():
    """Test quick alert using test endpoint"""
    print("\n🧪 Testing Quick Alert (test endpoint)...")

    response = requests.post(f"{BASE_URL}/api/line/test-alert")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Test alert sent")
        print(f"   {json.dumps(data, indent=2, ensure_ascii=False)}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")

def test_machine_data_auto_alert():
    """Test automatic alert when checking machine data"""
    print("\n🧪 Testing Auto-Alert via Machine Data...")

    # First upload CSV data
    print("   Uploading test CSV...")
    csv_content = """Timestamp,Machine_ID,PowerMotor,CurrentMotor,TempBrassBearingDE,SpeedMotor,TempOilGear,TempBearingMotorNDE,TempWindingMotorPhase_U,TempWindingMotorPhase_V,TempWindingMotorPhase_W,Vibration
2025-01-15 08:00:00,Feed Mill 1,305.2,350.5,92.3,1485,58.7,72.1,95.2,94.8,95.5,1.2"""

    files = {'file': ('test_data.csv', csv_content, 'text/csv')}
    upload_response = requests.post(f"{BASE_URL}/api/upload-csv", files=files)

    if upload_response.status_code == 200:
        print("   ✅ CSV uploaded")

        # Get machine data (this should trigger auto-alert)
        print("   Checking machine data (should trigger alert)...")
        data_response = requests.get(f"{BASE_URL}/api/machine-data/Feed Mill 1")

        if data_response.status_code == 200:
            data = data_response.json()
            print(f"   ✅ Machine data retrieved")
            print(f"   Alerts found: {len(data['alerts'])}")
            for alert in data['alerts']:
                print(f"      - {alert}")
            print(f"   📤 Auto-alert should be sent to LINE users (check backend logs)")
        else:
            print(f"   ❌ Error getting machine data: {data_response.status_code}")
    else:
        print(f"   ❌ Error uploading CSV: {upload_response.status_code}")

if __name__ == "__main__":
    print("=" * 60)
    print("LINE Bot Integration Test")
    print("=" * 60)

    # Test 1: Check configuration
    test_line_bot_configured()

    # Test 2: Send manual alert
    test_send_alert()

    # Test 3: Use test endpoint
    test_quick_alert()

    # Test 4: Test auto-alert via machine data
    test_machine_data_auto_alert()

    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
    print("\n📝 Note:")
    print("   - Make sure backend is running (python main.py)")
    print("   - Make sure LINE Bot is configured in .env")
    print("   - Add your LINE Bot as friend and enable alerts")
    print("   - Check backend logs for alert sending status")