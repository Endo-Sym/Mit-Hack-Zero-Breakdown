"""
LINE Bot integration for machine alert notifications
"""
import os
import requests
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

class LINENotifier:
    def __init__(self):
        self.channel_access_token = os.getenv('707da015cd3aaf14a09fd603f0365ca8', '')
        self.line_api_url = 'https://api.line.me/v2/bot/message'

    def is_configured(self) -> bool:
        """Check if LINE Bot is properly configured"""
        return bool(self.channel_access_token)

    def send_push_message(self, user_id: str, messages: List[Dict]) -> bool:
        """
        Send push message to specific user

        Args:
            user_id: LINE user ID
            messages: List of message objects

        Returns:
            bool: True if successful
        """
        if not self.is_configured():
            print("⚠️ LINE Bot not configured. Set LINE_CHANNEL_ACCESS_TOKEN in .env")
            return False

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.channel_access_token}'
        }

        data = {
            'to': user_id,
            'messages': messages
        }

        try:
            response = requests.post(
                f'{self.line_api_url}/push',
                headers=headers,
                json=data
            )

            if response.status_code == 200:
                print(f"✅ LINE message sent to {user_id}")
                return True
            else:
                print(f"❌ Failed to send LINE message: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"❌ Error sending LINE message: {str(e)}")
            return False

    def send_broadcast_message(self, messages: List[Dict]) -> bool:
        """
        Broadcast message to all friends

        Args:
            messages: List of message objects

        Returns:
            bool: True if successful
        """
        if not self.is_configured():
            print("⚠️ LINE Bot not configured. Set LINE_CHANNEL_ACCESS_TOKEN in .env")
            return False

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.channel_access_token}'
        }

        data = {
            'messages': messages
        }

        try:
            response = requests.post(
                f'{self.line_api_url}/broadcast',
                headers=headers,
                json=data
            )

            if response.status_code == 200:
                print("✅ LINE broadcast message sent")
                return True
            else:
                print(f"❌ Failed to send broadcast: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"❌ Error sending broadcast: {str(e)}")
            return False

    def create_alert_message(self, machine_id: str, alerts: List[str],
                           risk_score: int = 0, risk_level: str = "ไม่ทราบ") -> List[Dict]:
        """
        Create formatted alert message for LINE

        Args:
            machine_id: Machine identifier
            alerts: List of alert messages
            risk_score: Risk score (0-100)
            risk_level: Risk level text

        Returns:
            List of LINE message objects
        """
        # Determine emoji based on risk level
        emoji = "🔴" if risk_level == "สูง" else "🟡" if risk_level == "ปานกลาง" else "🟢"

        # Build alert text
        alert_text = f"{emoji} แจ้งเตือนเครื่องจักร!\n\n"
        alert_text += f"🏭 เครื่องจักร: {machine_id}\n"
        alert_text += f"⚠️ ระดับความเสี่ยง: {risk_level} ({risk_score}/100)\n\n"
        alert_text += f"📋 ปัญหาที่พบ:\n"

        for i, alert in enumerate(alerts, 1):
            alert_text += f"{i}. {alert}\n"

        alert_text += f"\n⏰ เวลา: {self._get_thai_datetime()}"
        alert_text += f"\n\n💡 กรุณาตรวจสอบเครื่องจักรโดยเร็วที่สุด"

        messages = [
            {
                'type': 'text',
                'text': alert_text
            }
        ]

        return messages

    def create_flex_alert_message(self, machine_id: str, alerts: List[str],
                                 risk_score: int = 0, risk_level: str = "ไม่ทราบ",
                                 sensor_readings: Dict = None) -> List[Dict]:
        """
        Create rich Flex Message for alert

        Args:
            machine_id: Machine identifier
            alerts: List of alert messages
            risk_score: Risk score (0-100)
            risk_level: Risk level text
            sensor_readings: Dictionary of sensor readings

        Returns:
            List of LINE Flex message objects
        """
        # Color based on risk level
        color = "#EF4444" if risk_level == "สูง" else "#FBBF24" if risk_level == "ปานกลาง" else "#10B981"

        # Build alert contents
        alert_contents = []
        for alert in alerts[:5]:  # Limit to 5 alerts
            alert_contents.append({
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "text",
                        "text": "•",
                        "color": color,
                        "flex": 0,
                        "weight": "bold"
                    },
                    {
                        "type": "text",
                        "text": alert,
                        "wrap": True,
                        "color": "#666666",
                        "size": "sm",
                        "flex": 1
                    }
                ],
                "spacing": "sm"
            })

        flex_message = {
            "type": "flex",
            "altText": f"⚠️ แจ้งเตือน: {machine_id} - {risk_level}",
            "contents": {
                "type": "bubble",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "⚠️ แจ้งเตือนเครื่องจักร",
                            "weight": "bold",
                            "color": "#FFFFFF",
                            "size": "lg"
                        }
                    ],
                    "backgroundColor": color
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": machine_id,
                                    "weight": "bold",
                                    "size": "xl",
                                    "color": "#1F2937"
                                },
                                {
                                    "type": "text",
                                    "text": f"ระดับความเสี่ยง: {risk_level}",
                                    "color": color,
                                    "weight": "bold",
                                    "margin": "md"
                                },
                                {
                                    "type": "text",
                                    "text": f"คะแนน: {risk_score}/100",
                                    "color": "#6B7280",
                                    "size": "sm",
                                    "margin": "xs"
                                }
                            ],
                            "margin": "none"
                        },
                        {
                            "type": "separator",
                            "margin": "xl"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "ปัญหาที่พบ:",
                                    "weight": "bold",
                                    "color": "#1F2937",
                                    "margin": "md"
                                }
                            ] + alert_contents
                        },
                        {
                            "type": "separator",
                            "margin": "xl"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": f"⏰ {self._get_thai_datetime()}",
                                    "color": "#9CA3AF",
                                    "size": "xs",
                                    "margin": "md"
                                },
                                {
                                    "type": "text",
                                    "text": "💡 กรุณาตรวจสอบเครื่องจักรโดยเร็วที่สุด",
                                    "color": "#6B7280",
                                    "size": "sm",
                                    "margin": "sm",
                                    "wrap": True
                                }
                            ]
                        }
                    ],
                    "spacing": "md"
                }
            }
        }

        return [flex_message]

    def _get_thai_datetime(self) -> str:
        """Get formatted Thai datetime string"""
        from datetime import datetime
        now = datetime.now()
        return now.strftime("%d/%m/%Y %H:%M:%S")


# Singleton instance
_line_notifier = None

def get_line_notifier() -> LINENotifier:
    """Get LINE notifier singleton"""
    global _line_notifier
    if _line_notifier is None:
        _line_notifier = LINENotifier()
    return _line_notifier