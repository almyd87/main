import telebot
from telebot import types
import json
import os
import requests
import time
import schedule
import threading

# --- إعدادات البوت ---
TOKEN = "7869769364:AAGWDK4orRgxQDcjfEHScbfExgIt_Ti8ARs"
PAIR = "EURUSD"
bot = telebot.TeleBot(TOKEN)

USERS_FILE = "users.json"
SESSIONS_FILE = "sessions.json"
user_states = {}

# --- تحميل/حفظ JSON ---
def load_json(file):
    if not os.path.exists(file):
        return {}
    with open(file, "r") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

# --- المؤشرات الفنية ---
def calc_ema(prices, period):
    ema = prices[0]
    k = 2 / (period + 1)
    for price in prices[1:]:
        ema = price * k + ema * (1 - k)
    return ema

def calc_rsi(prices, period=14):
    gains, losses = [], []
    for i in range(1, len(prices)):
        diff = prices[i] - prices[i - 1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0: return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calc_bollinger(prices, period=20):
    if len(prices) < period:
        return None, None
    sma = sum(prices[-period:]) / period
    std = (sum((p - sma) ** 2 for p in prices[-period:]) / period) ** 0.5
    return sma + 2 * std, sma - 2 * std

def fetch_data():
    url = "https://scanner.tradingview.com/forex/scan"
    payload = {
        "symbols": {"tickers": [f"OANDA:{PAIR}"], "query": {"types": []}},
        "columns": ["close"]
    }
    try:
        prices = []
        for _ in range(50):
            r = requests.post(url, json=payload, timeout=5)
            p = r.json()['data'][0]['d'][0]
            prices.append(p)
            time.sleep(0.05)
        return prices
    except Exception as e:
        print("❌ خطأ:", e)
        return []

def generate_signal(prices):
    ema20 = calc_ema(prices[-20:], 20)
    ema50 = calc_ema(prices[-50:], 50)
    rsi = calc_rsi(prices, 14)
    upper, lower = calc_bollinger(prices)
    current = prices[-1]

    if ema20 > ema50 and current > ema20 and rsi < 70:
        signal = "🟢 شراء (Call)"
    elif ema20 < ema50 and current < ema20 and rsi > 30:
        signal = "🔴 بيع (Put)"
    else:
        signal = "🟡 انتظار"

    return f"""
📊 توصية لحظية ({PAIR})
السعر الحالي: {round(current, 5)}
EMA20: {round(ema20, 5)} | EMA50: {round(ema50, 5)}
RSI(14): {round(rsi, 2)}
🔔 {signal}
"""

def send_to_all():
    prices = fetch_data()
    if len(prices) >= 50:
        msg = generate_signal(prices)
        sessions = load_json(SESSIONS_FILE)
        for uid in sessions:
            try:
                bot.send_message(uid, msg)
            except:
                pass

def run_schedule():
    schedule.every(60).seconds.do(send_to_all)
    while True:
        schedule.run_pending()
        time.sleep(1)

threading.Thread(target=run_schedule).start()

# --- أوامر تيليجرام ---
@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🆕 إنشاء حساب", "🔐 تسجيل الدخول")
    bot.send_message(
        message.chat.id,
        "👋 مرحباً بك في *بوت توصيات التداول*.\n\n"
        "يرجى اختيار أحد الخيارات:\n"
        "🆕 إنشاء حساب\n🔐 تسجيل الدخول",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: m.text in ["🆕 إنشاء حساب", "🔐 تسجيل الدخول"])
def handle_menu(m):
    if m.text == "🆕 إنشاء حساب":
        user_states[m.chat.id] = {"action": "create", "step": "name"}
        bot.send_message(m.chat.id, "📛 أدخل اسمك:")
    else:
        user_states[m.chat.id] = {"action": "login", "step": "email"}
        bot.send_message(m.chat.id, "📧 أدخل بريدك الإلكتروني:")

@bot.message_handler(func=lambda m: m.chat.id in user_states)
def handle_steps(m):
    state = user_states[m.chat.id]
    users = load_json(USERS_FILE)
    sessions = load_json(SESSIONS_FILE)

    if state["action"] == "create":
        if state["step"] == "name":
            state["name"] = m.text
            state["step"] = "email"
            bot.send_message(m.chat.id, "📧 أدخل بريدك الإلكتروني:")
        elif state["step"] == "email":
            if m.text in users:
                bot.send_message(m.chat.id, "❌ هذا البريد مسجل مسبقًا.")
                user_states.pop(m.chat.id)
                return
            state["email"] = m.text
            state["step"] = "password"
            bot.send_message(m.chat.id, "🔐 أدخل كلمة مرور:")
        elif state["step"] == "password":
            users[state["email"]] = {
                "name": state["name"],
                "password": m.text
            }
            save_json(USERS_FILE, users)
            sessions[str(m.chat.id)] = state["email"]
            save_json(SESSIONS_FILE, sessions)
            bot.send_message(m.chat.id, f"✅ تم إنشاء الحساب بنجاح، {state['name']}!")
            user_states.pop(m.chat.id)

    elif state["action"] == "login":
        if state["step"] == "email":
            state["email"] = m.text
            state["step"] = "password"
            bot.send_message(m.chat.id, "🔐 أدخل كلمة المرور:")
        elif state["step"] == "password":
            email = state["email"]
            if email not in users or users[email]["password"] != m.text:
                bot.send_message(m.chat.id, "❌ بيانات الدخول غير صحيحة.")
                user_states.pop(m.chat.id)
                return
            sessions[str(m.chat.id)] = email
            save_json(SESSIONS_FILE, sessions)
            bot.send_message(m.chat.id, f"✅ تسجيل دخول ناجح، مرحباً {users[email]['name']}!")
            user_states.pop(m.chat.id)

# --- تشغيل البوت ---
print("✅ البوت يعمل الآن...")
bot.infinity_polling()
