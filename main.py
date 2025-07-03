import telebot
from telebot import types
import requests
import json
import os
import time
import threading

# إعدادات البوت
TOKEN = "7869769364:AAGWDK4orRgxQDcjfEHScbfExgIt_Ti8ARs"
ADMIN_ID = 6964741705
bot = telebot.TeleBot(TOKEN)

# ملفات البيانات
CONFIG_FILE = "config.json"
USERS_FILE = "users.json"
SESSIONS = {}

# تحميل الإعدادات
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"price": "3", "wallet": "محفظة غير مضافة", "admin_password": "admin"}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def get_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_user(user_id, data):
    users = get_users()
    users[str(user_id)] = data
    save_users(users)

def get_main_menu(show_dev=False):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🔐 تسجيل الدخول", "🆕 إنشاء حساب")
    if show_dev:
        markup.add("🔐 ALMYD8710")
    return markup

def get_developer_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("👥 المستخدمين", "⚙️ الإعدادات", "🚫 خروج")
    return markup

# شاشة البدء
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    SESSIONS[user_id] = {}
    welcome = "👋 مرحباً بك في بوت توصيات التداول.\nاختر أحد الخيارات للمتابعة:"
    bot.send_message(user_id, welcome, reply_markup=get_main_menu(show_dev=(user_id == ADMIN_ID)))

# إنشاء حساب
@bot.message_handler(func=lambda m: m.text == "🆕 إنشاء حساب")
def register(message):
    bot.send_message(message.chat.id, "✏️ أرسل اسمك الكامل:")
    bot.register_next_step_handler(message, get_name)

def get_name(message):
    SESSIONS[message.chat.id]["name"] = message.text
    bot.send_message(message.chat.id, "📧 أرسل بريدك الإلكتروني:")
    bot.register_next_step_handler(message, get_email)

def get_email(message):
    SESSIONS[message.chat.id]["email"] = message.text
    bot.send_message(message.chat.id, "🔑 اختر كلمة مرور:")
    bot.register_next_step_handler(message, complete_registration)

def complete_registration(message):
    SESSIONS[message.chat.id]["password"] = message.text
    save_user(message.chat.id, {
        "name": SESSIONS[message.chat.id]["name"],
        "email": SESSIONS[message.chat.id]["email"],
        "password": message.text,
        "status": "pending"
    })
    bot.send_message(message.chat.id, "✅ تم إنشاء الحساب بنجاح!\n▶️ اضغط هنا للمتابعة.", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("▶️ اضغط هنا للمتابعة"))

# تسجيل الدخول
@bot.message_handler(func=lambda m: m.text == "🔐 تسجيل الدخول")
def login(message):
    bot.send_message(message.chat.id, "📧 أدخل بريدك الإلكتروني:")
    bot.register_next_step_handler(message, get_login_email)

def get_login_email(message):
    SESSIONS[message.chat.id] = {"login_email": message.text}
    bot.send_message(message.chat.id, "🔑 أدخل كلمة المرور:")
    bot.register_next_step_handler(message, verify_login)

def verify_login(message):
    email = SESSIONS[message.chat.id]["login_email"]
    password = message.text
    users = get_users()
    for uid, data in users.items():
        if data["email"] == email and data["password"] == password:
            SESSIONS[message.chat.id]["logged_in"] = True
            bot.send_message(message.chat.id, "✅ تم تسجيل الدخول بنجاح.\n▶️ اضغط هنا للمتابعة.", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("▶️ اضغط هنا للمتابعة"))
            return
    bot.send_message(message.chat.id, "❌ البريد الإلكتروني أو كلمة المرور غير صحيحة.")

@bot.message_handler(func=lambda m: m.text == "▶️ اضغط هنا للمتابعة")
def continue_to_subscription(message):
    users = get_users()
    if str(message.chat.id) in users and users[str(message.chat.id)]["status"] == "accepted":
        bot.send_message(message.chat.id, "✅ اشتراكك مفعل! سيتم إرسال التوصيات تلقائيًا.")
    else:
        config = load_config()
        text = f"""
🔒 لا يمكنك استخدام البوت حتى يتم تفعيل اشتراكك.
💵 السعر: {config['price']} دولار
🏦 الدفع عبر Binance:
📍 المحفظة: {config['wallet']}
📸 أرسل صورة إثبات التحويل هنا.
"""
        if os.path.exists("payment_guide.png"):
            with open("payment_guide.png", "rb") as img:
                bot.send_photo(message.chat.id, img, caption=text)
        else:
            bot.send_message(message.chat.id, text)

# المطور
@bot.message_handler(func=lambda m: m.text == "🔐 ALMYD8710")
def developer_login(message):
    bot.send_message(message.chat.id, "🔑 أرسل كلمة المرور:")
    bot.register_next_step_handler(message, verify_developer)

def verify_developer(message):
    if message.text == load_config().get("admin_password", "admin"):
        bot.send_message(message.chat.id, "✅ تم الدخول كمدير.", reply_markup=get_developer_menu())
    else:
        bot.send_message(message.chat.id, "❌ كلمة مرور غير صحيحة.")

# لوحة التحكم
@bot.message_handler(func=lambda m: m.text == "👥 المستخدمين")
def list_users(message):
    users = get_users()
    msg = "📋 قائمة المستخدمين:\n"
    for uid, data in users.items():
        msg += f"- {data['name']} | {data['status']}\n"
    bot.send_message(message.chat.id, msg or "لا يوجد مستخدمين.")

@bot.message_handler(func=lambda m: m.text == "⚙️ الإعدادات")
def settings(message):
    config = load_config()
    msg = f"💵 السعر الحالي: {config['price']} دولار\n🏦 المحفظة: {config['wallet']}"
    bot.send_message(message.chat.id, msg)

# إثبات الدفع
@bot.message_handler(content_types=['photo'])
def handle_payment_proof(message):
    caption = f"🧾 إثبات دفع جديد من: @{message.from_user.username or 'غير معروف'}\n🆔 ID: {message.chat.id}"
    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=caption)
    bot.send_message(message.chat.id, "✅ تم إرسال الإثبات، سيتم مراجعته قريبًا.")

# توصيات تلقائية (EUR/USD)
def fetch_prices():
    url = "https://scanner.tradingview.com/forex/scan"
    payload = {"symbols": {"tickers": ["OANDA:EURUSD"]}, "columns": ["close"]}
    prices = []
    try:
        for _ in range(50):
            r = requests.post(url, json=payload, timeout=5)
            price = r.json()['data'][0]['d'][0]
            prices.append(price)
            time.sleep(0.05)
    except:
        return []
    return prices

def calc_ema(prices, period):
    k = 2 / (period + 1)
    ema = prices[0]
    for price in prices[1:]:
        ema = price * k + ema * (1 - k)
    return ema

def calc_rsi(prices, period=14):
    gains, losses = [], []
    for i in range(1, len(prices)):
        diff = prices[i] - prices[i - 1]
        gains.append(max(0, diff))
        losses.append(max(0, -diff))
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0: return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def generate_signal(prices):
    ema20 = calc_ema(prices[-20:], 20)
    ema50 = calc_ema(prices[-50:], 50)
    rsi = calc_rsi(prices, 14)
    signal = "🟡 انتظر"
    if ema20 > ema50 and rsi < 70:
        signal = "🟢 شراء (Call)"
    elif ema20 < ema50 and rsi > 30:
        signal = "🔴 بيع (Put)"
    return f"""
📊 توصية لحظية (EUR/USD)
EMA20: {round(ema20, 5)} | EMA50: {round(ema50, 5)}
RSI(14): {round(rsi, 2)}
🔔 التوصية: {signal}
"""

def send_signal():
    prices = fetch_prices()
    if len(prices) >= 50:
        users = get_users()
        for uid, data in users.items():
            if data.get("status") == "accepted":
                bot.send_message(int(uid), generate_signal(prices))

def scheduler():
    while True:
        send_signal()
        time.sleep(60)

threading.Thread(target=scheduler).start()

# تشغيل البوت
print("✅ Bot is running...")
bot.infinity_polling()
