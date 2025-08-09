import os
import json
import random
import asyncio
import discord
from discord.ext import commands

TOKEN = os.environ.get("BOT_TOKEN")  # Set in Replit Secrets
XP_FILE = "xp.json"
MODERATOR_ROLE = os.environ.get("MOD_ROLE")  # Optional: set a role name for mods in Secrets

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)

# ---------- XP Storage ----------
def load_xp():
    if not os.path.exists(XP_FILE):
        return {"users": {}}
    with open(XP_FILE, "r") as f:
        return json.load(f)

def save_xp(data):
    with open(XP_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_xp(user_id, amount):
    data = load_xp()
    uid = str(user_id)
    users = data.setdefault("users", {})
    users[uid] = users.get(uid, 0) + amount
    save_xp(data)

def get_xp(user_id):
    data = load_xp()
    return data.get("users", {}).get(str(user_id), 0)

def is_mod(ctx):
    if MODERATOR_ROLE:
        role = discord.utils.get(ctx.guild.roles, name=MODERATOR_ROLE)
        if role and role in ctx.author.roles:
            return True
    return ctx.author.guild_permissions.administrator

# ---------- Games ----------
TRIVIA_QUESTIONS = [
    {
        "q": "What is the capital of France?",
        "options": ["Paris", "Berlin", "Madrid", "Rome"],
        "answer": 0,
        "points": 10
    },
    {
        "q": "Which language is primarily used for Android app development?",
        "options": ["Swift", "Kotlin", "Ruby", "C#"],
        "answer": 1,
        "points": 8
    },
    {
        "q": "2 + 2 * 2 = ?",
        "options": ["6", "8", "4", "10"],
        "answer": 0,
        "points": 6
    },
]

TYPING_CHALLENGES = [
    "I love building bots!",
    "Quick brown fox jumps over the lazy dog.",
    "Type this sentence exactly to win XP."
]

typing_sessions = {}  # channel_id -> {"text": str, "expires": timestamp, "points": int}

# ---------- Commands ----------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def xp(ctx, member: discord.Member = None):
    target = member or ctx.author
    await ctx.send(f"{target.display_name} has {get_xp(target.id)} XP.")

@bot.command()
async def award(ctx, member: discord.Member, points: int):
    if not is_mod(ctx):
        await ctx.send("Only moderators can award XP.")
        return
    add_xp(member.id, points)
    await ctx.send(f"Gave {points} XP to {member.display_name}. They now have {get_xp(member.id)} XP.")

@bot.command()
async def game(ctx):
    menu = "🎮 **Choose a game:**\n1️⃣ Trivia\n2️⃣ Typing Challenge\n3️⃣ Dice Roll"
    await ctx.send(menu)

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for("message", check=check, timeout=20)
        if msg.content == "1":
            await start_trivia(ctx)
        elif msg.content == "2":
            await start_typing(ctx)
        elif msg.content == "3":
            value = random.randint(1, 6)
            points = value * 2
            add_xp(ctx.author.id, points)
            await ctx.send(f"🎲 You rolled {value} — +{points} XP!")
        else:
            await ctx.send("Invalid choice.")
    except asyncio.TimeoutError:
        await ctx.send("You took too long to choose a game.")

async def start_trivia(ctx):
    q = random.choice(TRIVIA_QUESTIONS)
    options = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(q["options"])])
    await ctx.send(f"❓ {q['q']}\n{options}")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for("message", check=check, timeout=15)
        if msg.content.isdigit() and int(msg.content) - 1 == q["answer"]:
            add_xp(ctx.author.id, q["points"])
            await ctx.send(f"✅ Correct! +{q['points']} XP.")
        else:
            await ctx.send("❌ Incorrect!")
    except asyncio.TimeoutError:
        await ctx.send("⏳ Time's up!")

async def start_typing(ctx):
    text = random.choice(TYPING_CHALLENGES)
    points = 8
    typing_sessions[ctx.channel.id] = {
        "text": text,
        "expires": asyncio.get_event_loop().time() + 25,
        "points": points
    }
    await ctx.send(f"⌨️ Type this exactly within 25 seconds:\n\n{text}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Typing challenge
    session = typing_sessions.get(message.channel.id)
    if session:
        if asyncio.get_event_loop().time() > session["expires"]:
            typing_sessions.pop(message.channel.id, None)
        elif message.content.strip() == session["text"]:
            add_xp(message.author.id, session["points"])
            await message.channel.send(f"🎯 {message.author.display_name} typed it correctly! +{session['points']} XP.")
            typing_sessions.pop(message.channel.id, None)

    # Mention response
    if bot.user in message.mentions:
        await message.channel.send("👋 You mentioned me! Use `/game`, `/xp`, or `/award`.")

    await bot.process_commands(message)

bot.run(TOKEN)