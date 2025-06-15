
import requests

def send_telegram_alert(message, bot_token, chat_id):
    """
    Sends a message to a Telegram user or channel using Bot API.
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        print("✅ Alert sent to Telegram!")
    else:
        print(f"❌ Telegram Error: {response.status_code} - {response.text}")
