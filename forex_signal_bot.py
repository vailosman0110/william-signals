import random
import time
import requests
from datetime import datetime

# بيانات وهمية للإشارات
pairs = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/CHF", "NZD/CHF", "EUR/JPY", "EUR/CAD", "EUR/GBP"]
directions = ["شراء 🔼", "بيع 🔻"]
results = ["✅ WIN", "💔 LOSS"]

# سحب البيانات من secrets
import os
API_KEY = os.getenv("API_KEY")
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_NAME = os.getenv("CHAT_ID")  # اسم القناة مع @

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL_NAME,
        "text": text,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=data)
    print("📤 تم إرسال الرسالة:", response.status_code)
    return response

# إنشاء إشارة وهمية
pair = random.choice(pairs)
direction = random.choice(directions)
strength = random.randint(85, 99)
entry_time = datetime.utcnow().strftime("%H:%M UTC")
duration = "1 دقيقة"

# إرسال التوصية
signal_message = f"""📈 توصية جديدة 🔥
زوج: {pair}
الاتجاه: {direction}
قوة الإشارة: {strength}%
📍 وقت الدخول: {entry_time}
المدة: {duration}
#WILLIAM_VIP"""

send_message(signal_message)

# انتظار دقيقة (مدة الصفقة)
print("⏱️ انتظار 60 ثانية...")
time.sleep(60)

# إرسال النتيجة الوهمية
result = random.choice(results)
result_message = f"""📊 نتيجة الصفقة
{result}"""
send_message(result_message)
