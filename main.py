import os
import random
import discord
from discord.ext import commands, tasks
from datetime import datetime, time
from dotenv import load_dotenv
from keep_alive import keep_alive
import asyncio

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Expanded Athkar Database
ATHKAR_DB = {
    "morning": [
        "أَعُوذُ بِاللَّهِ مِنَ الشَّيْطَانِ الرَّجِيمِ: اللّهُ لاَ إِلَـهَ إِلاَّ هُوَ الْحَيُّ الْقَيُّومُ...",
        "سُبْحَانَ اللَّهِ وَبِحَمْدِهِ: مائة مرة",
        "لا إله إلا الله وحده لا شريك له... عشر مرات",
        "اللهم بك أصبحنا وبك أمسينا...",
        "حَسْبِيَ اللّهُ لا إِلَـهَ إِلاَّ هُوَ عَلَيْهِ تَوَكَّلْتُ..."
    ],
    "evening": [
        "أَعُوذُ بِاللَّهِ مِنَ الشَّيْطَانِ الرَّجِيمِ...",
        "سُبْحَانَ اللَّهِ وَبِحَمْدِهِ: مائة مرة",
        "أمسينا وأمسى الملك لله...", "اللهم بك أمسينا وبك أصبحنا...",
        "حَسْبِيَ اللّهُ لا إِلَـهَ إِلاَّ هُوَ..."
    ],
    "random": [
        "سبحان الله وبحمده سبحان الله العظيم", "لا حول ولا قوة إلا بالله",
        "أستغفر الله العظيم", "اللهم صل على محمد وعلى آل محمد"
    ]
}


async def send_with_retry(channel, content, max_retries=3):
    """Send message with retry logic"""
    for attempt in range(max_retries):
        try:
            await channel.send(content)
            return True
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(5)
    return False


@bot.command()
async def athkar(ctx, time_of_day=None):
    """Get random athkar! Usage: !athkar [morning/evening/random]"""
    try:
        if not time_of_day or time_of_day.lower() not in ATHKAR_DB:
            time_of_day = "random"

        selected = random.choice(ATHKAR_DB[time_of_day.lower()])
        await ctx.send(f"📿 {selected}")
    except Exception as e:
        print(f"Command error: {e}")


@tasks.loop(time=time(6, 0))  # 6 AM
async def morning_athkar():
    print("Executing morning athkar...")
    for channel_id in [1103385833832206426]:  # Your channel ID
        try:
            channel = bot.get_channel(channel_id)
            if channel:
                await send_with_retry(channel, "🌅 أذكار الصباح:")
                for thikr in random.sample(ATHKAR_DB["morning"], 3):
                    await send_with_retry(channel, thikr)
        except Exception as e:
            print(f"Morning athkar error: {e}")


@tasks.loop(time=time(18, 0))  # 6 PM
async def evening_athkar():
    print("Executing evening athkar...")
    for channel_id in [1103385833832206426]:  # Your channel ID
        try:
            channel = bot.get_channel(channel_id)
            if channel:
                await send_with_retry(channel, "🌇 أذكار المساء:")
                for thikr in random.sample(ATHKAR_DB["evening"], 3):
                    await send_with_retry(channel, thikr)
        except Exception as e:
            print(f"Evening athkar error: {e}")


@tasks.loop(minutes=30)
async def status_check():
    """Regular status updates"""
    print(f"Bot status: Connected to {len(bot.guilds)} servers")
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening, name="!athkar for reminders"))


@bot.event
async def on_ready():
    print(f"{bot.user.name} is ready!")
    morning_athkar.start()
    evening_athkar.start()
    status_check.start()
    # Don't start keep_alive here since it's not a task


@bot.event
async def on_error(event, *args, **kwargs):
    print(f"Error in {event}: {args} {kwargs}")


# Start the web server
keep_alive()

# Start the bot
try:
    bot.run(os.getenv("DISCORD_BOT_TOKEN", ""))
except Exception as e:
    print(f"Fatal error: {e}")
    # Consider adding automatic restart logic here
