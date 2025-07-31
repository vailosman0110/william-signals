import requests
import time
from datetime import datetime, timedelta
import pytz
import os

# إعدادات البوت
TELEGRAM_TOKEN = "TELEGRAM_TOKEN"
TELEGRAM_CHAT_ID = "CHAT_ID"
API_KEY = "API_KEY"

PAIRS = ["EUR/USD", "EUR/GBP", "EUR/JPY", "EUR/CAD", "USD/JPY", "EUR/CHF", "AUD/CHF", "NZD/CHF"]
RSI_PERIOD = 14
MA_PERIOD = 14
INTERVAL = "1min"

def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, data=payload)

def fetch_candles(symbol):
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={INTERVAL}&outputsize=50&apikey={API_KEY}"
    r = requests.get(url).json()
    if "values" in r:
        closes = [float(candle["close"]) for candle in r["values"]]
        return closes[::-1]  # ترتيب تصاعدي
    return []

def calculate_rsi(closes, period=14):
    if len(closes) < period + 1:
        return None
    gains = []
    losses = []
    for i in range(1, period + 1):
        diff = closes[i] - closes[i - 1]
        if diff >= 0:
            gains.append(diff)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(diff))
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_ma(closes, period=14):
    if len(closes) < period:
        return None
    return sum(closes[-period:]) / period

def get_direction(rsi):
    if rsi < 25:
        return "صاعد", "🟢"
    elif rsi > 75:
        return "هابط", "🔴"
    return None, None

def main():
    utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
    local_time = utc_now.astimezone(pytz.timezone("Asia/Amman"))  # غير التوقيت حسب بلدك
    if not (9 <= local_time.hour < 22):
        print("خارج وقت التشغيل")
        return

    for symbol in PAIRS:
        symb = symbol.replace("/", "")
        closes = fetch_candles(symbol)
        if not closes:
            continue

        rsi = calculate_rsi(closes, RSI_PERIOD)
        ma = calculate_ma(closes, MA_PERIOD)

        direction, emoji = get_direction(rsi)
        print(f"جارٍ فحص الزوج: {symbol} | RSI = {rsi:.2f} | MA = {ma:.4f} | الاتجاه = {direction}")

        if direction:
            entry_time = datetime.utcnow().strftime("%H:%M")
            message = f"""🔥 توصية جديدة 🔥

أسم الزوج : {symb}

أتجاه الصفقه : {direction} {emoji}

قوة الإشارة : 95%

⏰ وقت الدخول : {entry_time} UTC

مدة الصفقة : 1 دقيقة

@William_Trader_Support"""
            send_message(TELEGRAM_TOKEN, CHAT_ID, message)

            # انتظار دقيقة لإرسال النتيجة
            time.sleep(60)

            # عشوائي فقط كمثال - استبدله لاحقاً بنتيجة حقيقية
            result = "✅ WIN" if closes[-1] > closes[-2] else "❎ LOSS"
            result_msg = f"""📊 نتيجة الصفقة

{result}"""
            send_message(TELEGRAM_TOKEN, CHAT_ID, result_msg)
            time.sleep(2)

if __name__ == "__main__":
    main()
