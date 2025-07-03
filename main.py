import telebot
from telebot import types
import json
import os
import time
import threading

# ✅ بيانات البوت والمطور
TOKEN = "7869769364:AAGWDK4orRgxQDcjfEHScbfExgIt_Ti8ARs"
ADMIN_ID = 6964741705

# ✅ إنشاء البوت
bot = telebot.TeleBot(TOKEN)

# ✅ عند بدء المحادثة
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📊 التحليلات", "📚 الدروس", "💰 الاشتراك", "👤 حسابي")
    bot.send_message(message.chat.id, "مرحبًا بك في بوت التداول 📈\nاختر من القائمة:", reply_markup=markup)

# ✅ مثال لزر التحليلات
@bot.message_handler(func=lambda message: message.text == "📊 التحليلات")
def analysis(message):
    bot.send_message(message.chat.id, "📉 لا توجد تحليلات حاليًا، سيتم إضافتها لاحقًا.")

# ✅ زر الدروس
@bot.message_handler(func=lambda message: message.text == "📚 الدروس")
def lessons(message):
    bot.send_message(message.chat.id, "📘 سيتم إرسال جميع دروس التداول بعد الاشتراك.")

# ✅ الاشتراك
@bot.message_handler(func=lambda message: message.text == "💰 الاشتراك")
def subscribe(message):
    wallet_address = "0x3a5db3aec7c262017af9423219eb64b5eb6643d7"
    bot.send_message(
        message.chat.id,
        f"💵 الاشتراك الشهري: 3 USDT\n🎯 المحفظة: `{wallet_address}`\n\nأرسل صورة الدفع لتفعيل اشتراكك ✅",
        parse_mode="Markdown"
    )

# ✅ أي رسالة غير معروفة
@bot.message_handler(func=lambda message: True)
def fallback(message):
    bot.send_message(message.chat.id, "❓ لم أفهم طلبك. استخدم الأزرار في الأسفل.")

# ✅ تشغيل البوت
def run():
    print("🤖 Bot is running...")
    bot.infinity_polling()

if __name__ == '__main__':
    run()
