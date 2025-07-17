# (C) 2025 Hexa Vibes. Licensed under the MIT License.

import discord
from discord.ext import commands
from time import time
from os import getenv
from random import choice

STICKERID = getenv("STICKERID").split(",")

class MessageReacts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_ts = 0

    @commands.Cog.listener()
    async def on_message(self, message):
        if ("bwaa" in message.content.lower()) and (time() - self.message_ts >= 60):
            try:
                await message.reply(stickers=[await message.guild.fetch_sticker(choice(STICKERID))])
            except discord.Forbidden:
                print(f"Not allowed to reply to bwaa (Message ID: {message.id})")
            except discord.HTTPException as e:
                print(f"HTTP Exception when replying to bwaa (Message ID: {message.id}\n   {e}")
                return
            self.message_ts = time()

async def setup(bot: commands.Bot):
    await bot.add_cog(MessageReacts(bot))
