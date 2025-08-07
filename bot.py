import os
import json
from aiohttp import web
from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
    CommandHandler,
)

# ✅ Replace this with your real mod Telegram user IDs
MOD_IDS = [123456789]

# ✅ XP file path
XP_FILE = "xp.json"

# ✅ Load XP data
def load_xp():
    if os.path.exists(XP_FILE):
        with open(XP_FILE, "r") as f:
            return json.load(f)
    return {}

# ✅ Save XP data
def save_xp(data):
    with open(XP_FILE, "w") as f:
        json.dump(data, f)

xp_data = load_xp()

# ✅ Handle tags like "@YourBot"
async def handle_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if f"@{context.bot.username.lower()}" in update.message.text.lower():
        await update.message.reply_text("Hi! Reply with 'game' to play or 'award' to give XP (mods only).")

# ✅ Handle text commands
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.lower()
    username = update.message.from_user.username

    if text == "game":
        await update.message.reply_text(
            "Choose a game:\n1. Trivia 🤔\n2. Typing 📝\n3. Dice 🎲\n(Reply with 1, 2, or 3)"
        )

    elif text == "1":
        await update.message.reply_text("🧠 Trivia game coming soon!")

    elif text == "2":
        await update.message.reply_text("⌨️ Typing challenge coming soon!")

    elif text == "3":
        await update.message.reply_text("🎲 Rolling a dice... *not implemented yet*")

    elif text.startswith("award"):
        if user_id not in MOD_IDS:
            await update.message.reply_text("🚫 Only mods can give XP.")
            return

        parts = text.split()
        if len(parts) >= 3:
            try:
                awarded_username = parts[1].replace("@", "")
                xp = int(parts[2])
                xp_data[awarded_username] = xp_data.get(awarded_username, 0) + xp
                save_xp(xp_data)
                await update.message.reply_text(f"✅ Gave {xp} XP to @{awarded_username}!")
            except:
                await update.message.reply_text("⚠️ Error giving XP. Format: award @username 10")
        else:
            await update.message.reply_text("⚠️ Format: award @username 10")

# ✅ Start bot with webhook
async def main():
    TOKEN = os.getenv("BOT_TOKEN")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & filters.Entity("mention"), handle_tag))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    async def handle(request):
        data = await request.json()
        update = Update.de_json(data, app.bot)
        await app.process_update(update)
        return web.Response()

    # ✅ Webhook setup
    webhook_app = web.Application()
    webhook_app.add_routes([web.post("/", handle)])

    await app.bot.set_webhook(url=WEBHOOK_URL)
    print("🔗 Webhook set!")

    runner = web.AppRunner(webhook_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 10000)
    await site.start()

    print("✅ Bot is running with webhook.")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()  # Safe fallback
    await app.updater.idle()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())