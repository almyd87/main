import telebot
from telebot import types
import sqlite3

TOKEN = "7869769364:AAGWDK4orRgxQDcjfEHScbfExgIt_Ti8ARs"
ADMIN_ID = 6964741705
WALLET_ID = "1125130202"

bot = telebot.TeleBot(TOKEN)

# إنشاء قاعدة البيانات
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, balance INTEGER DEFAULT 0, referred_by INTEGER)")
conn.commit()

# 🔘 بدء البوت
@bot.message_handler(commands=['start'])
def start(msg):
    user_id = msg.from_user.id
    username = msg.from_user.username or "بدون اسم"
    args = msg.text.split()

    # تحقق إذا كان مستخدم جديد
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    if not cursor.fetchone():
        referred_by = int(args[1]) if len(args) > 1 and args[1].isdigit() else None
        cursor.execute("INSERT INTO users (id, username, referred_by) VALUES (?, ?, ?)", (user_id, username, referred_by))

        if referred_by:
            cursor.execute("UPDATE users SET balance = balance + 1 WHERE id=?", (referred_by,))
            bot.send_message(referred_by, f"🎉 تمت إضافة 1¢ إلى رصيدك لإحالتك صديق جديد!")

        conn.commit()

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📤 شارك رابط الدعوة", callback_data="share"))
    markup.add(types.InlineKeyboardButton("💰 شراء الاستراتيجيات", callback_data="buy"))
    markup.add(types.InlineKeyboardButton("💳 المحفظة", callback_data="wallet"))
    bot.send_message(user_id, "👋 مرحبًا بك في بوت التداول الاحترافي.\nاختر أحد الخيارات 👇", reply_markup=markup)

# 🎯 مشاركة رابط الدعوة
@bot.callback_query_handler(func=lambda call: call.data == "share")
def share(call):
    user_id = call.from_user.id
    ref_link = f"https://t.me/pocketoptiondars_bot?start={user_id}"
    bot.send_message(user_id, f"🔗 رابط الدعوة الخاص بك:\n{ref_link}\n\n👥 كل من ينضم عبرك تحصل على 1¢ روبل!")

# 💰 شراء الاستراتيجيات
@bot.callback_query_handler(func=lambda call: call.data == "buy")
def buy_strategy(call):
    user_id = call.from_user.id
    cursor.execute("SELECT balance FROM users WHERE id=?", (user_id,))
    result = cursor.fetchone()
    if result and result[0] >= 5:
        cursor.execute("UPDATE users SET balance = balance - 5 WHERE id=?", (user_id,))
        conn.commit()
        bot.send_message(user_id, "📚 تم إرسال الاستراتيجيات بنجاح! ✅\n\n👇 إليك الدروس:")
        send_lessons(user_id)
    else:
        bot.send_message(user_id, "❌ تحتاج إلى 5¢ على الأقل لشراء الاستراتيجيات.\n📤 قم بدعوة أصدقائك لزيادة الرصيد.")

# 💳 عرض المحفظة
@bot.callback_query_handler(func=lambda call: call.data == "wallet")
def wallet(call):
    bot.send_message(call.from_user.id, f"💼 عنوان محفظة الدفع:\n`{WALLET_ID}`\n\n📋 اضغط مطولًا لنسخ العنوان.", parse_mode="Markdown")

# 📚 إرسال الدروس التعليمية (عند الشراء)
def send_lessons(user_id):
    lessons = [
        "🟢 الدرس 1: ما هو التداول في Pocket Option؟\n\n📘 شرح كامل: التداول في المنصة يعتمد على التوقع إذا كان السعر سيرتفع أو ينخفض خلال فترة زمنية قصيرة.",
        "🟢 الدرس 2: الفرق بين الشراء والبيع\n\n🔼 شراء = تتوقع صعود السعر\n🔽 بيع = تتوقع هبوط السعر",
        "🟢 الدرس 3: إدارة رأس المال\n\n💡 لا تخاطر بأكثر من 5% من رصيدك في أي صفقة.",
        # أضف باقي الدروس حسب الحاجة...
    ]
    for lesson in lessons:
        bot.send_message(user_id, lesson)

# 💡 شرح أي زر يتم ضغطه
@bot.callback_query_handler(func=lambda call: True)
def explain_buttons(call):
    explanations = {
        "share": "📤 شارك هذا الرابط مع أصدقائك لتحصل على 1¢ عن كل إحالة ناجحة.",
        "buy": "💰 قم بشراء استراتيجيات تداول متقدمة بعد جمع 5¢.",
        "wallet": "💳 هذا هو عنوان محفظتك لتحويل رسوم الاشتراك أو الدفع."
    }
    if call.data in explanations:
        bot.send_message(call.from_user.id, f"ℹ️ توضيح:\n{explanations[call.data]}")

# ✅ تشغيل البوت
print("✅ Bot is running...")
bot.infinity_polling()
