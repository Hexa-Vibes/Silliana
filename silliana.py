# (C) 2025 Hexa Vibes. Licensed under the MIT License.

import asyncio
import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

INTENTS = discord.Intents.default()
INTENTS.message_content = True
INTENTS.guilds = True
INTENTS.guild_messages = True

load_dotenv()

TOKEN = os.getenv("TOKEN")
APPID = os.getenv("APPID")

bot = commands.Bot(
  command_prefix=None,
  intents=INTENTS
)

@bot.event
async def on_ready():
  print("Silliana is logged in!")

async def main():
  await bot.load_extension("cogs.reacts")

  await bot.start(TOKEN)

if __name__ == "__main__":
  asyncio.run(main())
