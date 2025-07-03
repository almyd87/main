
# encoding: utf-8
import telebot
from telebot import types
import json
import os

TOKEN = "7869769364:AAGWDK4orRgxQDcjfEHScbfExgIt_Ti8ARs"
ADMIN_ID = 1125130202

bot = telebot.TeleBot(TOKEN)
CONFIG_FILE = "config.json"
USERS_FILE = "users.json"
ACCOUNTS_FILE = "accounts.json"
SESSIONS_FILE = "sessions.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

def load_data(file):
    if not os.path.exists(file):
        return {}
    with open(file, "r") as f:
        return json.load(f)

def get_main_menu(show_dev=False):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🆕 إنشاء حساب", "🔐 تسجيل الدخول")
    if show_dev:
        markup.add("🔐 ALMYD8710")
    return markup

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "👋 مرحباً بك في بوت التداو" 
   bot.send_message(message.chat.id, "📍 اختر أحد الخيارات التالية:", reply_markup=get_main_menu())
@bot.message_handler(func=lambda m: m.text == "🆕 إنشاء حساب")
def register_step1(message):
    bot.send_message(message.chat.id, "📛 أرسل اسمك الكامل:")
    bot.register_next_step_handler(message, register_step2)

def register_step2(message):
    name = message.text.strip()
    bot.send_message(message.chat.id, "📧 أرسل بريدك الإلكتروني:")
    bot.register_next_step_handler(message, register_step3, name)

def register_step3(message, name):
    email = message.text.strip()
    bot.send_message(message.chat.id, "🔑 أرسل كلمة المرور:")
    bot.register_next_step_handler(message, register_finish, name, email)

def register_finish(message, name, email):
    password = message.text.strip()
    accounts = load_data(ACCOUNTS_FILE)
    accounts[str(message.from_user.id)] = {"name": name, "email": email, "password": password}
    save_data(ACCOUNTS_FILE, accounts)

    sessions = load_data(SESSIONS_FILE)
    sessions[str(message.from_user.id)] = True
    save_data(SESSIONS_FILE, sessions)

    bot.send_message(message.chat.id, "✅ تم إنشاء الحساب بنجاح.
▶️ اضغط هنا للمتابعة.", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("▶️ اضغط هنا للمتابعة"))

@bot.message_handler(func=lambda m: m.text == "🔐 تسجيل الدخول")
def login_step1(message):
    bot.send_message(message.chat.id, "📧 أرسل بريدك الإلكتروني:")
    bot.register_next_step_handler(message, login_step2)

def login_step2(message):
    email = message.text.strip()
    bot.send_message(message.chat.id, "🔑 أرسل كلمة المرور:")
    bot.register_next_step_handler(message, login_finish, email)

def login_finish(message, email):
    password = message.text.strip()
    accounts = load_data(ACCOUNTS_FILE)
    sessions = load_data(SESSIONS_FILE)

    for uid, data in accounts.items():
        if data["email"] == email and data["password"] == password:
            sessions[str(message.from_user.id)] = True
            save_data(SESSIONS_FILE, sessions)
            bot.send_message(message.chat.id, "✅ تم تسجيل الدخول بنجاح.
▶️ اضغط هنا للمتابعة.", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("▶️ اضغط هنا للمتابعة"))
            return

    bot.send_message(message.chat.id, "❌ بيانات الدخول غير صحيحة.")

@bot.message_handler(func=lambda m: m.text == "▶️ اضغط هنا للمتابعة")
def continue_to_subscription(message):
    config = load_config()
    users = load_data(USERS_FILE)
    uid = str(message.from_user.id)

    if uid not in users:
        users[uid] = {"username": message.from_user.username or "لا يوجد", "status": "pending"}
        save_data(USERS_FILE, users)

    if users[uid]["status"] != "accepted":
        text = (
            "🔒 لا يمكنك استخدام البوت حتى يتم تفعيل اشتراكك.

"
            f"💵 قيمة الاشتراك: {config['price']} دولار أمريكي
"
            "🏦 الدفع عبر Binance
"
            f"📍 عنوان المحفظة:
{config['wallet']}

"
            "📸 بعد الدفع، أرسل صورة إثبات التحويل هنا."
        )
        if os.path.exists("payment_guide.png"):
            with open("payment_guide.png", "rb") as img:
                bot.send_photo(message.chat.id, img, caption=text)
        else:
            bot.send_message(message.chat.id, text)
    else:
        bot.send_message(message.chat.id, "✅ مرحباً بك! اشتراكك مفعل.")

@bot.message_handler(func=lambda m: m.text == "🔐 ALMYD8710")
def developer_login(message):
    bot.send_message(message.chat.id, "🔑 أرسل كلمة المرور:")
    bot.register_next_step_handler(message, verify_developer)

def verify_developer(message):
    config = load_config()
    if message.text == config.get("admin_password", "admin"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("👥 المستخدمين", "⚙️ الإعدادات", "🚫 خروج")
        bot.send_message(message.chat.id, "✅ تم تسجيل الدخول كمدير.", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "❌ كلمة المرور غير صحيحة.")

@bot.message_handler(func=lambda m: True)
def general(message):
    if str(message.from_user.id) == str(ADMIN_ID) and message.text == "/dev":
        bot.send_message(message.chat.id, "🔓 تم تفعيل زر المطور.", reply_markup=get_main_menu(show_dev=True))
