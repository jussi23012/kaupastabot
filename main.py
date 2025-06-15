# main.py
# A wonderful Telegram bot for those, whose kids have a hard time remembering to inform the adults when the fridge runs out of stuff
# https://trello.com/b/aFgKUuiH/kaupastabot

# ====================Imports====================

from telegram import Update
from telegram import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from functools import wraps
import time
import sqlite3
import os
from tools import auth as auth
from tools import allowedUsers as WELCOME
from tools import banned as soosoo

BOT_TOKEN = os.environ.get(auth.API_key)
user_add_mode = set()
pending_destruction = set()
pending_reset = set()

# ====================Access====================

def restricted(func):
    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in WELCOME:
            await update.message.reply_text("Äp äp! Sinulla ei ole lupaa käyttää tätä bottia.")
            time.sleep(1)
            await update.message.reply_text("Ota yhteys järjestelmävalvojaan.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapped

# ====================SQLite====================

# list database
kaupasta_conn = sqlite3.connect("databases\\kaupasta.db", check_same_thread=False)
kaupasta_curs = kaupasta_conn.cursor()
kaupasta_curs.execute("""
        CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        added_by TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")
kaupasta_conn.commit()

# scoreboard database
scoreboard_conn = sqlite3.connect("databases\\scoreboard.db", check_same_thread=False)
scoreboard_curs = scoreboard_conn.cursor()
scoreboard_curs.execute("""
        CREATE TABLE IF NOT EXISTS scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT NOT NULL,
        points INTEGER DEFAULT 0
    )
""")
scoreboard_conn.commit()


# ====================Commands====================

# /id command (this is hidden from the menu)
async def id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text("ID:si on:")
    time.sleep(1)
    await update.message.reply_text(f"{user.id}")
    time.sleep(1)
    await update.message.reply_text(f"Ilmoita ID järjestelmänvalvojallesi.")


# /start command
@restricted
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    with open("logo.png", "rb") as photo:
        await update.message.reply_photo(photo)
    await update.message.reply_text(
        f"Hei {user}!\n\nLämpimästi tervetuloa käyttämään Kaupastabotia.\n\nJos jokin on jääkaapista loppu, lisää se listalle käyttämällä komentoa\n/add.")

# /add command
@restricted
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_add_mode.add(user_id)
    await update.message.reply_text("Kirjoita listalle lisättävät asiat yksi kerrallaan.")
    time.sleep(0.5)
    await update.message.reply_text("Kun olet valmis, kirjoita /done.")
    
# /done command
@restricted
async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id =  update.effective_user.id
    if user_id in user_add_mode:
        user_add_mode.remove(user_id)
        await update.message.reply_text("Olet poistunut lisäystilasta.")
    else:
        await update.message.reply_text("Et lisännyt listalle mitään.")

# /list command
@restricted
async def list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kaupasta_curs.execute("SELECT name, added_by, timestamp FROM items ORDER BY timestamp ASC")
    rows = kaupasta_curs.fetchall()

    if not rows:
        await update.message.reply_text("Ostoslista on tyhjä.")
        return
    
    message = "*Kaupasta 🛒:*\n\n"
    for i, (name, added_by, timestamp) in enumerate(rows,1):
        message += f"{i}. {name} _(lisännyt {added_by})_\n"

    await update.message.reply_text(message, parse_mode="Markdown")

# /clear command
@restricted
async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    pending_destruction.add(user_id)

    await update.message.reply_text("Oletko varma, että haluat tyhjentää listan?")
    time.sleep(1)
    await update.message.reply_text("Kirjoita KYLLÄ, jos haluat tyhjentää listan.")
    time.sleep(1)
    await update.message.reply_text("Peruuttaaksesi, kirjoita mitä tahansa muuta.")

# /emptyscoreboard
@restricted
async def clearscoreboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    pending_reset.add(user_id)

    await update.message.reply_text("Oletko varma, että haluat tyhjentää pistetaulukon?")
    time.sleep(1)
    await update.message.reply_text("Kirjoita KYLLÄ, jos haluat tyhjentää pistetaulukon.")
    time.sleep(1)
    await update.message.reply_text("Peruuttaaksesi, kirjoita mitä tahansa muuta.")

# /scoreboard
@restricted
async def scoreboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    scoreboard_curs.execute("SELECT user, points FROM scores ORDER BY points DESC LIMIT 10")
    rows = scoreboard_curs.fetchall()

    if not rows:
        await update.message.reply_text("Pistetaulukko on tyhjä.")
        return
    
    message = "*Pistetaulukko*\n\n"
    for i, (user, points) in enumerate(rows, 1):
        message += f"{i}. {user} - {points} point{'s' if points != 1 else ''}\n"
    
    await update.message.reply_text(message, parse_mode="Markdown")

# ====================Bot Stuff====================

async def setup(application):
    await application.bot.set_my_commands([
        # BotCommand("id","Hae käyttäjä-ID tunnistautumista varten."), # This doesn't really need to be visible. IYKYK
        # BotCommand("start","Käynnistä botti"), # We really dont need this in the menu either
        BotCommand("add","Lisää asioita ostoslistalle"),
        BotCommand("done","Lopeta asioiden lisääminen"),
        BotCommand("list","Näytä tekstimuotoinen ostoslista"),
        BotCommand("shop","Näytä interaktiivinen ostoslista"),
        BotCommand("clear","Tyhjennä ostoslista"),
        BotCommand("scoreboard","Näytä pistetaulukko"),
    ])

async def listButtons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kaupasta_curs.execute("SELECT id, name FROM items")
    items = kaupasta_curs.fetchall()

    if not items:
        await update.message.reply_text("Ostoslista on tyhjä.")
        return
    
    keyboard = [
        [InlineKeyboardButton(text=name, callback_data=str(item_id))]
        for item_id, name in items
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Kaupasta 🛒:\n\n" 
    # + "\n".join([name for _, name in items]) # we don't want to show the list twice
    ,
    reply_markup=reply_markup)

async def buttonHandler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if "session_scores" not in context.chat_data:
        context.chat_data["session_scores"] = {}


    item_id = query.data
    kaupasta_curs.execute("SELECT added_by, name FROM items WHERE id = ?", (item_id,))
    row = kaupasta_curs.fetchone()

    if not row:
        await query.edit_message_text("Ei löydy")
        return

    added_by, item_name = row

    if "session_scores" not in context.chat_data:
        context.chat_data["session_scores"] = {}

    session_scores = context.chat_data["session_scores"]
    session_scores[added_by] = session_scores.get(added_by, 0) + 1

    kaupasta_curs.execute("DELETE FROM items WHERE id = ?", (item_id,))
    kaupasta_conn.commit()

    scoreboard_curs.execute("SELECT points FROM scores where user = ?", (added_by,))
    score_row = scoreboard_curs.fetchone()

    if score_row:
        scoreboard_curs.execute("UPDATE scores SET points = points + 1 WHERE user = ?", (added_by,))
    else:
        scoreboard_curs.execute("INSERT INTO scores (user, points) VALUES (?, 1)", (added_by,))
    scoreboard_conn.commit()

    kaupasta_curs.execute("SELECT id, name FROM items ORDER BY timestamp")
    items = kaupasta_curs.fetchall()

    if not items:
        session_scores = context.chat_data.get("session_scores", {})
        if session_scores:
            score_lines = [f"{user} {points}p" for user, points in session_scores.items()]
            score_text = "Pisteitä jaettu:\n" + ", ".join(score_lines)
        else:
            score_text = "Pisteitä ei jaettu."

        context.chat_data["session_scores"] = {}

        await query.edit_message_text(
            f"Reipas! 🎉 Lista on tyhjä! \n\n{score_text} \n\nKokonaispisteet: /scoreboard"
        )
        return
    
    keyboard = [
        [InlineKeyboardButton(text=name, callback_data=str(item_id))]
        for item_id, name in items
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text="Päivitetty ostoslista 🛒:\n\n"
        # + "\n".join([name for _, name in items]) # we don't want to show the list twice
        ,
        reply_markup=reply_markup
    )


# handler for handling the stuff that gets added and removed to and from the list
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = update.effective_user.first_name
    text = update.message.text.strip()
    item = update.message.text.strip().lower()

    # clearning the list
    if user_id in pending_destruction:
        pending_destruction.remove(user_id)

        if text == "KYLLÄ":
            kaupasta_curs.execute("DELETE FROM items")
            kaupasta_conn.commit()
            await update.message.reply_text("Lista tyhjennetty 🧹")

        else:
            await update.message.reply_text("Lista ennallaan.")
        return
    
    # resetting the scoreboard
    if user_id in pending_reset:
        pending_reset.remove(user_id)

        if text == "KYLLÄ":
            scoreboard_curs.execute("DELETE FROM scores")
            scoreboard_conn.commit()
            await update.message.reply_text("Pistetaulukko resetoitu.")

        else:
            await update.message.reply_text("Pistetaulukkoa ei resetoitu.")
        return
    
    if any(badWord in item for badWord in soosoo):
        await update.message.reply_text(f"Soo soo {user}. Listalle ei lisätä asiattomuuksia.")
        return
    
    # add mode
    if user_id not in user_add_mode:
        return
    
    if not item or item.startswith("/"):
        return
    
    # duplicates
    kaupasta_curs.execute("SELECT 1 FROM items WHERE name = ?", (item,))
    if kaupasta_curs.fetchone():
        item = item.capitalize()
        await update.message.reply_text(f"Kuules nyt {user}! {item} on jo listalla!")
        return

    # adding stuff to the list and to the scoreboard
    kaupasta_curs.execute("INSERT INTO items (name, added_by) VALUES (?, ?)", (item, user))
    kaupasta_conn.commit()

    # This should be deprecated now that users get the points based on if the product they added gets bought
    # scoreboard_curs.execute("SELECT points FROM scores WHERE user = ?", (user,))
    # row = scoreboard_curs.fetchone()
    # if row:
    #     scoreboard_curs.execute("UPDATE scores SET points = points + 1 WHERE user = ?", (user,))
    # else:
    #     scoreboard_curs.execute("INSERT INTO scores (user, points) VALUES (?, 1)", (user,))
    # scoreboard_conn.commit()

    await update.message.reply_text(f"Lisätty listalle: {item}")

# Regisgtering the commands
app = ApplicationBuilder().token(auth.API_key).post_init(setup).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("id", id))
app.add_handler(CommandHandler("add", add))
app.add_handler(CommandHandler("done", done))
app.add_handler(CommandHandler("list", list))
app.add_handler(CommandHandler("clear", clear))
app.add_handler(CommandHandler("scoreboard", scoreboard))
app.add_handler(CommandHandler("clearscoreboard",clearscoreboard))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))
app.add_handler(CommandHandler("shop", listButtons)) 
app.add_handler(CallbackQueryHandler(buttonHandler))

# Run the polling
app.run_polling()