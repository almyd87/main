# main.py - بوت تيليجرام توصيات مع تسجيل دخول وتحليل لحظي
import telebot
from telebot import types
import json
import time
import threading
import os

TOKEN = "ضع_توكن_البوت_هنا"
ADMIN_ID = 1125130202
bot = telebot.TeleBot(TOKEN)

USERS_FILE = "users.json"
SESSIONS_FILE = "sessions.json"
CONFIG_FILE = "config.json"

def load_json(file):
    if not os.path.exists(file):
        return {}
    with open(file, "r") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

# إرسال رسالة ترحيبية
@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🆕 إنشاء حساب", "🔐 تسجيل الدخول")
    bot.send_message(message.chat.id, "👋 مرحبًا بك في بوت التداول.
يرجى اختيار أحد الخيارات:", reply_markup=markup)

# هنا تضيف باقي الأوامر: إنشاء حساب، تسجيل دخول، تحليل المؤشرات، إلخ

# تشغيل البوت
bot.polling()
