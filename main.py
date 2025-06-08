# main.py
# A wonderful Telegram bot for those, whose kids have a hard time remembering to inform the adults when the fridge runs out of stuff
# https://trello.com/b/aFgKUuiH/kaupastabot

# ====================Imports====================

from telegram import Update
from telegram import BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import sqlite3
import os
import auth

BOT_TOKEN = os.environ.get(auth.API_key)
user_add_mode = set()

# ====================SQLite====================

# list database
kaupasta_conn = sqlite3.connect("kaupasta.db", check_same_thread=False)
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
scoreboard_conn = sqlite3.connect("scoreboard.db", check_same_thread=False)
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

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    await update.message.reply_text(
        f"Hei {user}! Jos jokin on jääkaapista loppu, lisää se listalle kirjoittamalla /add <asia>."
    )

# /add command
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    item = " ".join(context.args)
    item = item.lower()
    if not item:
        await update.message.reply_text("Käyttö: /add juusto")
        return
    user = update.effective_user.first_name

    kaupasta_curs.execute("SELECT 1 FROM items WHERE name = ?", (item,))
    if kaupasta_curs.fetchone():
        item = item.capitalize()
        await update.message.reply_text(f"Kuules nyt {user}! {item} on jo listalla!")
        return

    kaupasta_curs.execute("INSERT INTO items (name, added_by) VALUES (?, ?)", (item, user))
    kaupasta_conn.commit()
    scoreboard_curs.execute("SELECT points FROM scores WHERE user = ?", (user,))
    row = scoreboard_curs.fetchone()

    if row:
        scoreboard_curs.execute("UPDATE scores SET points = points + 1 WHERE user = ?", (user,))
    else:
        scoreboard_curs.execute("INSERT INTO scores (user, points) VALUES (?, 1)", (user,))
    scoreboard_conn.commit()

    await update.message.reply_text(f"Lisätty listalle: {item}")

# /list command
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
async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kaupasta_curs.execute("DELETE FROM items")
    kaupasta_conn.commit()
    await update.message.reply_text("Lista tyhjennetty 🧹")

# /scoreboard
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
        BotCommand("start","Käynnistä botti"),
        BotCommand("add","Lisää asioita ostoslistalle"),
        BotCommand("list","Näytä ostoslista"),
        BotCommand("clear","Tyhjennä ostoslista"),
        BotCommand("scoreboard","Näytä pistetaulukko"),
    ])

# Regisgtering the commands
app = ApplicationBuilder().token(auth.API_key).post_init(setup).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("add", add))
app.add_handler(CommandHandler("list", list))
app.add_handler(CommandHandler("clear", clear))
app.add_handler(CommandHandler("scoreboard", scoreboard))

# Run the polling
app.run_polling()