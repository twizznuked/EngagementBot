import os
import json
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# --- CONFIG ---
MOD_IDS = [123456789]  # Replace with real Telegram user ID(s)
BOT_USERNAME = os.getenv("BOT_USERNAME", "YourBotUsername")  # Optional fallback

# --- XP DATA LOAD/SAVE ---
XP_FILE = "xp.json"
try:
    with open(XP_FILE, "r") as f:
        xp_data = json.load(f)
except:
    xp_data = {}

def save_xp():
    with open(XP_FILE, "w") as f:
        json.dump(xp_data, f)

# --- BOT FUNCTIONS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! I'm your engagement bot.")

async def handle_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if f"@{BOT_USERNAME.lower()}" in update.message.text.lower():
        await update.message.reply_text("Hi! Reply with 'game' to play or 'award' to give XP (mods only).")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.lower()
    username = update.effective_user.username or str(user_id)

    if text == "game":
        await update.message.reply_text(
            "Choose a game:\n1. Trivia 🤔\n2. Typing 📝\n3. Dice 🎲\n(Reply with 1, 2, or 3)"
        )
    elif text == "1":
        await update.message.reply_text("❓ Trivia game coming soon!")
    elif text == "2":
        await update.message.reply_text("⌨️ Typing challenge coming soon!")
    elif text == "3":
        await update.message.reply_text("🎲 Rolling a dice... (not implemented yet)")

    elif text.startswith("award"):
        parts = text.split()
        if len(parts) >= 3:
            if user_id not in MOD_IDS:
                await update.message.reply_text("🚫 Only mods can give XP.")
                return
            try:
                target_user = parts[1].replace("@", "")
                amount = int(parts[2])
                xp_data[target_user] = xp_data.get(target_user, 0) + amount
                save_xp()
                await update.message.reply_text(f"✅ Gave {amount} XP to @{target_user}!")
            except:
                await update.message.reply_text("⚠️ Invalid format or amount.")
        else:
            await update.message.reply_text("Format: award @username 10")

# --- MAIN APP ---
async def main():
    token = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & filters.Entity("mention"), handle_tag))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Webhook config
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g., from Render
    PORT = int(os.environ.get("PORT", 10000))
    await app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL,
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())