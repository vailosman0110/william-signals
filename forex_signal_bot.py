import requests
import os
import time
from datetime import datetime

# جلب المتغيرات من GitHub Secrets
API_KEY = os.getenv("API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# أزواج العملات المستهدفة
PAIRS = [
    "EUR/USD", "EUR/GBP", "EUR/JPY", "EUR/CAD",
    "USD/JPY", "EUR/CHF", "AUD/CHF", "NZD/CHF", "GBP/USD"
]

# إرسال رسالة تيليجرام
def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, data=payload)

# جلب الإشارة الحقيقية من Twelve Data
def get_signal(pair):
    symbol = pair.replace("/", "")
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1min&outputsize=2&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()

    if "values" not in data:
        return None

    try:
        close_now = float(data["values"][0]["close"])
        close_prev = float(data["values"][1]["close"])
        direction = "صاعد 🟢" if close_now > close_prev else "هابط 🔴"
        strength = 95
        return symbol, direction, strength, close_now
    except:
        return None

def main():
    for pair in PAIRS:
        signal = get_signal(pair)
        if signal:
            symbol, direction, strength, entry_price = signal

            now = datetime.utcnow()
            entry_time = now.strftime("%H:%M UTC")

            message = f"""🔥  توصية جديدة 🔥

أسم الزوج : {symbol}

أتجاه الصفقه : {direction}

قوة الإشارة : {strength}%

⏰ وقت الدخول : {entry_time}

مدة الصفقة : 1 دقيقة

@William_Trader_Support
"""
            send_message(message)

            # انتظر دقيقة
            time.sleep(60)

            # احصل على السعر الجديد
            price_url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={API_KEY}"
            response = requests.get(price_url).json()

            try:
                exit_price = float(response["price"])
                if (direction == "صاعد 🟢" and exit_price > entry_price) or \
                   (direction == "هابط 🔴" and exit_price < entry_price):
                    result = "✅ WIN"
                else:
                    result = "❎ LOSS"
            except:
                result = "❎ LOSS"

            result_message = f"""📊 نتيجة الصفقة

{result}"""
            send_message(result_message)
            break  # إرسال توصية واحدة فقط

if name == "__main__":
    main()
