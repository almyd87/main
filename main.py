import telebot
from telebot import types
import json
import os
import threading
import time

TOKEN = "7869769364:AAGWDK4orRgxQDcjfEHScbfExgIt_Ti8ARs"
ADMIN_ID = 6964741705
ADMIN_PASSWORD = "admin"

bot = telebot.TeleBot(TOKEN)

USERS_FILE = "users.json"
CONFIG_FILE = "config.json"
SESSIONS = {}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {
            "welcome_message": "👋 مرحبًا بك في بوت التوصيات.",
            "subscription_message": "💳 للاشتراك، أرسل إثبات الدفع إلى المحفظة التالية.",
            "subscription_price": "3",
            "wallet_address": "1125130202"
        }
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

config = load_config()

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

users = load_users()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🆕 إنشاء حساب", "🔐 تسجيل الدخول")
    if message.chat.id == ADMIN_ID:
        markup.add("🔐 ALMYD8710", "📥 طلبات الاشتراك")
    bot.send_message(message.chat.id, config["welcome_message"], reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🆕 إنشاء حساب")
def create_account(message):
    bot.send_message(message.chat.id, "📛 أرسل اسمك:")
    bot.register_next_step_handler(message, process_name)

def process_name(message):
    name = message.text
    bot.send_message(message.chat.id, "📧 أرسل بريدك الإلكتروني:")
    bot.register_next_step_handler(message, lambda m: process_email(m, name))

def process_email(message, name):
    email = message.text
    bot.send_message(message.chat.id, "🔑 أرسل كلمة المرور:")
    bot.register_next_step_handler(message, lambda m: save_new_user(m, name, email))

def save_new_user(message, name, email):
    password = message.text
    chat_id = str(message.chat.id)
    users[chat_id] = {
        "name": name,
        "email": email,
        "password": password,
        "subscribed": False,
        "accepted": False
    }
    save_users(users)
    SESSIONS[chat_id] = True  # ✅ تفعيل الجلسة مباشرة بعد التسجيل
    bot.send_message(message.chat.id, "✅ تم إنشاء الحساب.")
    show_subscription_prompt(message)
    

@bot.message_handler(func=lambda m: m.text == "🔐 تسجيل الدخول")
def login(message):
    bot.send_message(message.chat.id, "📧 أرسل بريدك الإلكتروني:")
    bot.register_next_step_handler(message, process_login_email)

def process_login_email(message):
    email = message.text
    bot.send_message(message.chat.id, "🔑 أرسل كلمة المرور:")
    bot.register_next_step_handler(message, lambda m: check_credentials(m, email))

def check_credentials(message, email):
    password = message.text
    chat_id = str(message.chat.id)
    for uid, data in users.items():
        if data["email"] == email and data["password"] == password:
            SESSIONS[chat_id] = True
            bot.send_message(message.chat.id, "✅ تم تسجيل الدخول.")
            if not data["subscribed"]:
                show_subscription_prompt(message)
            elif not data["accepted"]:
                bot.send_message(message.chat.id, "📩 بانتظار موافقة المطور.")
            else:
                bot.send_message(message.chat.id, "🎉 أنت مشترك! التوصيات ستصلك تلقائيًا.")
            return
    bot.send_message(message.chat.id, "❌ بيانات الدخول غير صحيحة.")

def show_subscription_prompt(message):
    markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, f"{config['subscription_message']}\n💰 السعر: {config['subscription_price']}$\n🏦 المحفظة: {config['wallet_address']}", reply_markup=markup)
    bot.send_message(message.chat.id, "📸 أرسل صورة إثبات الدفع:")
    bot.register_next_step_handler(message, handle_proof)

def handle_proof(message):
    chat_id = str(message.chat.id)
    if chat_id in users:
        users[chat_id]["subscribed"] = True
        users[chat_id]["proof_message_id"] = message.message_id
        users[chat_id]["proof_chat_id"] = message.chat.id
        save_users(users)
        bot.send_message(message.chat.id, "📩 تم استلام الإثبات. بانتظار موافقة المطور.")
        bot.send_message(ADMIN_ID, f"📥 طلب جديد من {users[chat_id]['name']} (ID: {chat_id})")
        if message.photo:
            bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)

@bot.message_handler(commands=['قبول'])
def accept_by_command(message):
    if message.chat.id != ADMIN_ID:
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "❌ الصيغة: /قبول chat_id")
        return
    uid = parts[1]
    if uid in users:
        users[uid]["accepted"] = True
        save_users(users)
        bot.send_message(uid, "✅ تم قبول اشتراكك!")
        bot.send_message(message.chat.id, f"✅ تم قبول المستخدم {uid}.")
    else:
        bot.send_message(message.chat.id, "❌ المستخدم غير موجود.")

@bot.message_handler(func=lambda m: m.text == "🔐 ALMYD8710")
def developer_login(message):
    bot.send_message(message.chat.id, "🔑 أدخل كلمة السر:")
    bot.register_next_step_handler(message, verify_admin_password)

def verify_admin_password(message):
    if message.text == ADMIN_PASSWORD:
        show_admin_panel(message)
    else:
        bot.send_message(message.chat.id, "❌ كلمة السر غير صحيحة.")

def show_admin_panel(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📝 تغيير الرسالة الترحيبية", "💳 تغيير رسالة الاشتراك")
    markup.add("💰 تغيير السعر", "🏦 تغيير المحفظة")
    markup.add("🚪 خروج")
    bot.send_message(message.chat.id, "🛠️ لوحة التحكم:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.chat.id == ADMIN_ID and m.text == "📝 تغيير الرسالة الترحيبية")
def change_welcome_msg(message):
    bot.send_message(message.chat.id, "✍️ أرسل الرسالة الجديدة:")
    bot.register_next_step_handler(message, save_welcome_msg)

def save_welcome_msg(message):
    config["welcome_message"] = message.text
    save_config(config)
    bot.send_message(message.chat.id, "✅ تم التحديث.")

@bot.message_handler(func=lambda m: m.chat.id == ADMIN_ID and m.text == "💳 تغيير رسالة الاشتراك")
def change_sub_msg(message):
    bot.send_message(message.chat.id, "✍️ أرسل رسالة الاشتراك:")
    bot.register_next_step_handler(message, save_sub_msg)

def save_sub_msg(message):
    config["subscription_message"] = message.text
    save_config(config)
    bot.send_message(message.chat.id, "✅ تم التحديث.")

@bot.message_handler(func=lambda m: m.chat.id == ADMIN_ID and m.text == "💰 تغيير السعر")
def change_price(message):
    bot.send_message(message.chat.id, "💲 السعر الجديد:")
    bot.register_next_step_handler(message, save_price)

def save_price(message):
    config["subscription_price"] = message.text
    save_config(config)
    bot.send_message(message.chat.id, "✅ تم تحديث السعر.")

@bot.message_handler(func=lambda m: m.chat.id == ADMIN_ID and m.text == "🏦 تغيير المحفظة")
def change_wallet(message):
    bot.send_message(message.chat.id, "🏦 المحفظة الجديدة:")
    bot.register_next_step_handler(message, save_wallet)

def save_wallet(message):
    config["wallet_address"] = message.text
    save_config(config)
    bot.send_message(message.chat.id, "✅ تم تحديث المحفظة.")

@bot.message_handler(func=lambda m: m.chat.id == ADMIN_ID and m.text == "🚪 خروج")
def exit_admin(message):
    bot.send_message(message.chat.id, "✅ تم الخروج.", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda m: m.chat.id == ADMIN_ID and m.text == "📥 طلبات الاشتراك")
def show_pending_requests(message):
    pending = [uid for uid, data in users.items() if data.get("subscribed") and not data.get("accepted")]
    if not pending:
        bot.send_message(message.chat.id, "لا يوجد طلبات اشتراك.")
        return
    markup = types.InlineKeyboardMarkup()
    for uid in pending:
        name = users[uid].get("name", uid)
        markup.add(types.InlineKeyboardButton(text=name, callback_data=f"review_{uid}"))
    bot.send_message(message.chat.id, "📋 الطلبات:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("review_"))
def review_request(call):
    uid = call.data.split("_")[1]
    user = users.get(uid)
    if not user:
        return
    chat_id = user.get("proof_chat_id")
    msg_id = user.get("proof_message_id")
    if chat_id and msg_id:
        try:
            bot.copy_message(call.message.chat.id, chat_id, msg_id)
        except:
            bot.send_message(call.message.chat.id, "❌ لم أتمكن من جلب الإثبات.")
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ قبول", callback_data=f"accept_{uid}"),
        types.InlineKeyboardButton("❌ رفض", callback_data=f"reject_{uid}")
    )
    bot.send_message(call.message.chat.id, f"🔍 طلب: {user['name']} (ID: {uid})", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("accept_"))
def accept_user_btn(call):
    uid = call.data.split("_")[1]
    if uid in users:
        users[uid]["accepted"] = True
        save_users(users)
        bot.send_message(uid, "✅ تم قبول اشتراكك!")
        bot.edit_message_text("✅ تم القبول.", call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_"))
def reject_user_btn(call):
    uid = call.data.split("_")[1]
    if uid in users:
        users[uid]["subscribed"] = False
        users[uid]["accepted"] = False
        save_users(users)
        bot.send_message(uid, "❌ تم رفض طلب الاشتراك.")
        bot.edit_message_text("❌ تم الرفض.", call.message.chat.id, call.message.message_id)

def send_recommendations():
    while True:
        for uid, data in users.items():
            if data.get("accepted"):
                try:
                    bot.send_message(uid, "📊 توصية جديدة: ⬆️ شراء أو ⬇️ بيع")
                except:
                    continue
        time.sleep(60)

threading.Thread(target=send_recommendations).start()

bot.infinity_polling()
