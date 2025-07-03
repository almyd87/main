import telebot
from telebot import types
import json
import os
import time
import threading
TOKEN = "7869769364:AAGWDK4orRgxQDcjfEHScbfExgIt_Ti8ARs" ADMIN_ID = 6964741705 bot = telebot.TeleBot(TOKEN)

USERS_FILE = "users.json" CONFIG_FILE = "config.json" SESSIONS = {}

Load or create default config

def load_config(): if os.path.exists(CONFIG_FILE): with open(CONFIG_FILE, "r") as f: return json.load(f) return {"price": "3", "wallet": "1125130202", "admin_password": "admin"}

def save_config(config): with open(CONFIG_FILE, "w") as f: json.dump(config, f)

def get_users(): if os.path.exists(USERS_FILE): with open(USERS_FILE, "r") as f: return json.load(f) return {}

def save_users(users): with open(USERS_FILE, "w") as f: json.dump(users, f)

def save_user(user_id, data): users = get_users() users[str(user_id)] = data save_users(users)

def get_main_menu(show_dev=False): markup = types.ReplyKeyboardMarkup(resize_keyboard=True) markup.row("🔐 تسجيل الدخول", "🆕 إنشاء حساب") markup.row("🤝 شارك واربح", "🛒 شراء الاستراتيجيات") if show_dev: markup.add("🔐 ALMYD8710") return markup

def get_user_balance(user_id): users = get_users() user = users.get(str(user_id), {}) return int(user.get("balance", 0))

def update_user_balance(user_id, delta): users = get_users() uid = str(user_id) if uid not in users: users[uid] = {} users[uid]["balance"] = users[uid].get("balance", 0) + delta save_users(users)

@bot.message_handler(commands=['start']) def start(message): SESSIONS[message.chat.id] = {} bot.send_message(message.chat.id, "👋 مرحباً بك! اختر أحد الخيارات للمتابعة:", reply_markup=get_main_menu(show_dev=(message.chat.id == ADMIN_ID)))

@bot.message_handler(func=lambda m: m.text == "🆕 إنشاء حساب") def register(message): bot.send_message(message.chat.id, "✏️ أرسل اسمك الكامل:") bot.register_next_step_handler(message, get_name)

def get_name(message): SESSIONS[message.chat.id]["name"] = message.text bot.send_message(message.chat.id, "📧 أرسل بريدك الإلكتروني:") bot.register_next_step_handler(message, get_email)

def get_email(message): SESSIONS[message.chat.id]["email"] = message.text bot.send_message(message.chat.id, "🔑 اختر كلمة مرور:") bot.register_next_step_handler(message, complete_registration)

def complete_registration(message): user_id = message.chat.id SESSIONS[user_id]["password"] = message.text save_user(user_id, { "name": SESSIONS[user_id]["name"], "email": SESSIONS[user_id]["email"], "password": message.text, "status": "pending", "balance": 0, "referred": [] }) bot.send_message(user_id, "✅ تم إنشاء الحساب بنجاح!\n▶️ اضغط هنا للمتابعة.", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("▶️ اضغط هنا للمتابعة"))

@bot.message_handler(func=lambda m: m.text == "🔐 تسجيل الدخول") def login(message): bot.send_message(message.chat.id, "📧 أدخل بريدك الإلكتروني:") bot.register_next_step_handler(message, get_login_email)

def get_login_email(message): SESSIONS[message.chat.id] = {"login_email": message.text} bot.send_message(message.chat.id, "🔑 أدخل كلمة المرور:") bot.register_next_step_handler(message, verify_login)

def verify_login(message): email = SESSIONS[message.chat.id]["login_email"] password = message.text users = get_users() for uid, data in users.items(): if data["email"] == email and data["password"] == password: SESSIONS[message.chat.id]["logged_in"] = True bot.send_message(message.chat.id, "✅ تم تسجيل الدخول بنجاح.\n▶️ اضغط هنا للمتابعة.", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("▶️ اضغط هنا للمتابعة")) return bot.send_message(message.chat.id, "❌ البريد الإلكتروني أو كلمة المرور غير صحيحة.")

@bot.message_handler(func=lambda m: m.text == "🤝 شارك واربح") def share_referral(message): link = f"https://t.me/{bot.get_me().username}?start={message.chat.id}" bot.send_message(message.chat.id, f"🔗 رابط الدعوة الخاص بك:\n{link}\n\n👥 كل شخص ينضم عبر رابطك، تربح 1¢ روبل.")

@bot.message_handler(commands=['start']) def handle_referral(message): if len(message.text.split()) > 1: ref_id = message.text.split()[1] if ref_id != str(message.chat.id): users = get_users() user = users.get(str(message.chat.id), {}) if ref_id not in user.get("referred", []): update_user_balance(ref_id, 1) user.setdefault("referred", []).append(ref_id) save_user(message.chat.id, user)

@bot.message_handler(func=lambda m: m.text == "🛒 شراء الاستراتيجيات") def buy_lessons(message): balance = get_user_balance(message.chat.id) if balance >= 5: update_user_balance(message.chat.id, -5) bot.send_message(message.chat.id, "🎓 شكراً لشرائك، سيتم الآن إرسال الاستراتيجيات:") send_lessons(message.chat.id) else: bot.send_message(message.chat.id, f"💰 رصيدك الحالي: {balance}¢ روبل\n❗ تحتاج إلى 5¢ روبل على الأقل.")

def send_lessons(user_id): for i in range(1, 11): with open(f"lessons/lesson{i}.txt", "r", encoding="utf-8") as f: bot.send_message(user_id, f.read())

print("✅ Bot is ready.") bot.infinity_polling()

