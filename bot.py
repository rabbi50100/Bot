import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import time

# ⚠️ আপনার টোকেনটি এখানে বসান (অবশ্যই সঠিক টোকেন দিবেন)
TOKEN = "8691161840:AAE-TXRoPpq5gwweVQBuILQANRQLk8PjV7c"
bot = telebot.TeleBot(TOKEN)

# ==================== Database Setup ====================
try:
    conn = sqlite3.connect('bot_data.db', check_same_thread=False)
    cursor = conn.cursor()

    # আগের ডাটাবেসের সাথে যেন ঝামেলা না হয়, তাই টেবিলের নাম users_v2 দেওয়া হলো
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users_v2 (
            user_id INTEGER PRIMARY KEY,
            status INTEGER DEFAULT 0,
            last_start_time REAL DEFAULT 0
        )
    ''')
    conn.commit()
    print("✅ Database Connected Successfully!")
except Exception as e:
    print(f"❌ Database Error: {e}")


# ==================== Keyboards ====================
def get_initial_keyboard():
    """Watch Ad এবং Confirm বাটন"""
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🔗 Watch Ad", url="https://www.profitablecpmratenetwork.com/uv78x22pja?key=f3ffba790fbb2ff3c308626730a2c9b3"),
        InlineKeyboardButton("✅ I Completed Ad", callback_data="check_completed")
    )
    return markup

def get_video_keyboard():
    """মুভি নেওয়ার বাটন"""
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎥 Get Video / মুভি নিন", callback_data="send_movie"))
    return markup


# ==================== Handlers ====================
@bot.message_handler(commands=['start'])
def start(message):
    try:
        user_id = message.from_user.id
        current_time = time.time()

        # ইউজারের ডাটা সেভ করা হচ্ছে
        cursor.execute("INSERT OR REPLACE INTO users_v2 (user_id, status, last_start_time) VALUES (?, 0, ?)", (user_id, current_time))
        conn.commit()

        bot.send_photo(
            message.chat.id,
            photo="https://dn721906.ca.archive.org/0/items/kis-kisko-pyaar-karoon/images%20%283%29.jpeg",
            caption="⚠️ প্রথমে **Watch Ad** বাটনে ক্লিক করে অন্তত **15 সেকেন্ড** অ্যাডটি দেখুন।\n\n"
                    "অ্যাড দেখা শেষ হলে **✅ I Completed Ad** বাটনে ক্লিক করুন।\n\n"
                    "*(ফাঁকি দেওয়ার চেষ্টা করলে মুভি পাবেন না!)*",
            reply_markup=get_initial_keyboard(),
            parse_mode="Markdown"
        )
        print(f"User {user_id} started the bot.") # টার্মিনালে দেখার জন্য
        
    except Exception as e:
        print(f"❌ Error in /start command: {e}")


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    try:
        user_id = call.from_user.id
        current_time = time.time()

        if call.data == "check_completed":
            cursor.execute("SELECT last_start_time FROM users_v2 WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()

            if result:
                time_passed = current_time - result[0]

                # ১৫ সেকেন্ড চেক
                if time_passed < 15:
                    remaining_time = int(15 - time_passed)
                    bot.answer_callback_query(
                        call.id, 
                        f"❌ আপনি ফাঁকি দিচ্ছেন! অ্যাড না দেখেই ক্লিক করেছেন।\n\nদয়া করে লিংকে ক্লিক করুন এবং আরও {remaining_time} সেকেন্ড পর Confirm করুন।", 
                        show_alert=True
                    )
                else:
                    bot.answer_callback_query(call.id, "✅ ভেরিফিকেশন সফল!")
                    
                    cursor.execute("UPDATE users_v2 SET status = 1 WHERE user_id = ?", (user_id,))
                    conn.commit()

                    bot.edit_message_caption(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        caption="✅ **অ্যাড দেখা সম্পন্ন হয়েছে!**\n\nএখন নিচের বাটন থেকে আপনার মুভি নিন 👇",
                        reply_markup=get_video_keyboard(),
                        parse_mode="Markdown"
                    )
            else:
                 bot.answer_callback_query(call.id, "❌ দয়া করে আগে /start টাইপ করুন।", show_alert=True)

        elif call.data == "send_movie":
            cursor.execute("SELECT status FROM users_v2 WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()

            if result and result[0] == 1:
                try:
                    bot.copy_message(
                        chat_id=call.message.chat.id,
                        from_chat_id="@HD_Movieindia", 
                        message_id=305,
                        caption="🎉 ধন্যবাদ! এই নিন আপনার মুভি।\n\nআবার মুভি নিতে চাইলে /start করুন।"
                    )
                    bot.answer_callback_query(call.id, "✅ মুভি পাঠানো হয়েছে!")
                    
                    cursor.execute("UPDATE users_v2 SET status = 0 WHERE user_id = ?", (user_id,))
                    conn.commit()
                    
                except Exception as e:
                    print(f"❌ Channel Error: {e}")
                    bot.answer_callback_query(call.id, "❌ মুভি পাঠাতে সমস্যা হয়েছে। বটকে চ্যানেলের এডমিন করা আছে কিনা চেক করুন।", show_alert=True)
            else:
                bot.answer_callback_query(call.id, "❌ আপনি এখনো অ্যাড ভেরিফাই করেননি!", show_alert=True)

    except Exception as e:
         print(f"❌ Error in callback: {e}")

print("🤖 Bot is starting... Please wait.")
bot.infinity_polling()
