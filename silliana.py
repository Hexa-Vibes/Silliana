# (C) 2025 Hexa Vibes. Licensed under the MIT License.

import asyncio
import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
from logger import Logger

INTENTS = discord.Intents.default()
INTENTS.message_content = True
INTENTS.guilds = True
INTENTS.guild_messages = True

log = Logger("SILLIANA")

load_dotenv()

TOKEN = os.getenv("TOKEN")
APPID = os.getenv("APPID")

bot = commands.Bot(
    command_prefix=None,
    intents=INTENTS
)

@bot.event
async def on_ready():
    log.info("Silliana is logged in!")

    # Set the bot's presence
    activity = discord.Activity(
        name="👀 Stalking your submissions",
        type=discord.ActivityType.watching,
        # state="👀 Stalking your submissions"  # Optional: for more detail
    )
    await bot.change_presence(activity=activity)
    log.info("Bot presence set!")

    # Add persistent views
    from cogs.forms import SubmissionButton
    bot.add_view(SubmissionButton())

    # Sync slash commands automatically
    try:
        synced = await bot.tree.sync()
        log.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        log.error(f"Failed to sync commands: {e}")

async def main():
    await bot.load_extension("cogs.reacts")
    await bot.load_extension("cogs.forms")
    await bot.load_extension("cogs.twitch_notifications")

    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
