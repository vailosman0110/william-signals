import requests
import time
import schedule
from datetime import datetime, timedelta
import os

API_KEY = os.getenv("cd2e95b15b4f4b5e8f6218a8e3537de4")
TELEGRAM_TOKEN = os.getenv("8428714955:AAGqTTMqxAitY_RF93XPP3mvGGu5PVZvr_8")
CHAT_ID = "@williamsignal0"

PAIRS = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD"]

active_trades = []

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print("❌ خطأ في الإرسال:", e)

def get_rsi_price(pair):
    try:
        url = f"https://api.twelvedata.com/indicator/rsi?symbol={pair}&interval=1min&time_period=14&apikey={API_KEY}"
        response = requests.get(url, timeout=10)
        data = response.json()
        if "values" in data and len(data["values"]) > 0:
            rsi = float(data["values"][0]["rsi"])
            price = float(data["values"][0]["close"])
            return rsi, price
        return None, None
    except:
        return None, None

def get_current_price(pair):
    try:
        url = f"https://api.twelvedata.com/price?symbol={pair}&apikey={API_KEY}"
        response = requests.get(url, timeout=10)
        data = response.json()
        return float(data["price"])
    except:
        return None

def check_signal_strength(rsi):
    if rsi <= 30:
        strength = int(85 + (30 - rsi) * 2)
        return min(strength, 100), "شراء 🟢", "صاعد 🟢"
    elif rsi >= 70:
        strength = int(85 + (rsi - 70) * 2)
        return min(strength, 100), "بيع 🔴", "هابط 🔴"
    return 0, None, None

def open_trade(pair, direction_emoji, direction_text, strength, entry_price):
    utc_time = datetime.utcnow().strftime("%H:%M UTC")
    message = f"""🔥 توصية جديدة 🔥

أسم الزوج : {pair}

أتجاه الصفقه : {direction_text}

قوة الإشارة : {strength}%

⏰ وقت الدخول : {utc_time}

مدة الصفقة : 1 دقيقة

@William_Trader_Support"""
    send_telegram(message)
    active_trades.append({
        "pair": pair,
        "direction": direction_emoji,
        "entry_price": entry_price,
        "open_time": datetime.utcnow()
    })

def check_active_trades():
    now = datetime.utcnow()
    completed = []
    for trade in active_trades:
        if now >= trade["open_time"] + timedelta(minutes=1):
            entry = trade["entry_price"]
            exit_price = get_current_price(trade["pair"])
            if exit_price:
                profit = (exit_price - entry) if trade["direction"] == "شراء 🟢" else (entry - exit_price)
                result = "WIN ✅" if profit > 0 else "LOSS ❎"
                emoji = "🟢" if profit > 0 else "🔴"
                pnl_text = f"{abs(profit * 10000):.1f} pip"
            else:
                result = "⚠️ تعذر الجنيس"
                emoji = ""
                pnl_text = ""
            result_msg = f"""📊 نتيجة الصفقة

الزوج: {trade['pair']}
الاتجاه: {trade['direction']}
النتيجة: {result} {emoji}
التغير: {pnl_text}
⏱ انتهت: {now.strftime('%H:%M UTC')}

@William_Trader_Support"""
            send_telegram(result_msg)
            completed.append(trade)
    for trade in completed:
        active_trades.remove(trade)

def scan_for_signals():
    print(f"🔍 فحص إشارات جديدة... {datetime.now().strftime('%H:%M:%S')}")
    for pair in PAIRS:
        rsi, price = get_rsi_price(pair)
        if rsi and price:
            strength, order_type, direction_text = check_signal_strength(rsi)
            if strength >= 85:
                open_trade(pair, order_type, direction_text, strength, price)

schedule.every(1).minutes.do(scan_for_signals)
schedule.every(30).seconds.do(check_active_trades)

scan_for_signals()

while True:
    schedule.run_pending()
    time.sleep(5)