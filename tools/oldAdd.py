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