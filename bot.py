import json
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Replace this with your real Telegram user ID(s)
MOD_IDS = [7534506739]

# Load XP data from file
try:
    with open("xp.json", "r") as f:
        xp_data = json.load(f)
except:
    xp_data = {}

# Save XP data to file
def save_xp():
    with open("xp.json", "w") as f:
        json.dump(xp_data, f)

# Respond when bot is tagged
def handle_tag(update: Update, context: CallbackContext):
    message = update.message
    if f"@{context.bot.username}" in message.text:
        message.reply_text("Hi! Reply with 'game' to play or 'award' to give XP (mods only).")

# Handle messages like "game", "award", etc.
def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    text = update.message.text.lower()

    if text == "game":
        update.message.reply_text(
            "Choose a game:\n1. Trivia 🤔\n2. Typing 📝\n3. Dice 🎲\n(Reply with 1, 2, or 3)"
        )
    elif text == "1":
        update.message.reply_text("Trivia game coming soon!")
    elif text == "2":
        update.message.reply_text("Typing challenge coming soon!")
    elif text == "3":
        update.message.reply_text("Rolling a dice... 🎲")

    elif text.startswith("award") and user_id in MOD_IDS:
        parts = text.split()
        if len(parts) >= 3:
            try:
                username = parts[1].replace("@", "")
                xp = int(parts[2])
                xp_data[username] = xp_data.get(username, 0) + xp
                save_xp()
                update.message.reply_text(f"✅ Gave {xp} XP to @{username}!")
            except:
                update.message.reply_text("⚠️ Error giving XP.")
        else:
            update.message.reply_text("Format: award @username 10")

    elif text.startswith("award") and user_id not in MOD_IDS:
        update.message.reply_text("🚫 Only mods can give XP.")

# Start the bot
def main():
    import os
    TOKEN = os.getenv("BOT_TOKEN")
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Add handlers
    dp.add_handler(MessageHandler(Filters.text & Filters.entity("mention"), handle_tag))
    dp.add_handler(MessageHandler(Filters.text & (~Filters.command), handle_message))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
