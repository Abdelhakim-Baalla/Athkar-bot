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


# Modified for testing - will run 10 seconds after startup instead of at 6 AM
@tasks.loop(seconds=10, count=1)  # Run once after 10 seconds
async def test_morning_athkar():
    print("Executing test morning athkar...")
    for channel_id in [1103385833832206426]:  # Update with your testing channel ID
        try:
            channel = bot.get_channel(channel_id)
            if channel:
                await send_with_retry(channel, "🧪 TEST: 🌅 أذكار الصباح:")
                for thikr in random.sample(ATHKAR_DB["morning"], 2):
                    await send_with_retry(channel, thikr)
            else:
                print(f"Channel with ID {channel_id} not found")
        except Exception as e:
            print(f"Test morning athkar error: {e}")


# Modified for testing - will run 20 seconds after startup instead of at 6 PM
@tasks.loop(seconds=20, count=1)  # Run once after 20 seconds
async def test_evening_athkar():
    print("Executing test evening athkar...")
    for channel_id in [1103385833832206426]:  # Update with your testing channel ID
        try:
            channel = bot.get_channel(channel_id)
            if channel:
                await send_with_retry(channel, "🧪 TEST: 🌇 أذكار المساء:")
                for thikr in random.sample(ATHKAR_DB["evening"], 2):
                    await send_with_retry(channel, thikr)
            else:
                print(f"Channel with ID {channel_id} not found")
        except Exception as e:
            print(f"Test evening athkar error: {e}")


@tasks.loop(minutes=1)
async def status_check():
    """Regular status updates"""
    print(f"Bot status: Connected to {len(bot.guilds)} servers")
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening, name="!athkar for reminders"))


@bot.event
async def on_ready():
    print(f"{bot.user.name} is ready!")
    test_morning_athkar.start()  # Start the test version instead
    test_evening_athkar.start()  # Start the test version instead
    status_check.start()


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