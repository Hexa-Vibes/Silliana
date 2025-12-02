# (C) 2025 Hexa Vibes. Licensed under the MIT License.

import discord
from discord.ext import commands
from time import time
from os import getenv
from random import choice
from logger import Logger

log = Logger("REACTS")

BWAA_STICKERIDS = getenv("BWAA_STICKERIDS").split(",")
MEOW_STICKERIDS = getenv("MEOW_STICKERIDS").split(",")
PLUH_STICKERIDS = getenv("PLUH_STICKERIDS").split(",")
FUMO_STICKERIDS = getenv("FUMO_STICKERIDS").split(",")
FUMO_GIFS = getenv("FUMO_GIFS").split(",")
GET_REAL_GIFS = getenv("GET_REAL_GIFS").split(",")

class MessageReacts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_ts = 0

    async def reply_sticker(self, message, sticker_id):
        try:
            await message.reply(stickers=[await message.guild.fetch_sticker(sticker_id)])
        except discord.Forbidden:
            log.error(f"Not allowed to reply (Message ID: {message.id})")
            return
        except discord.HTTPException as e:
            log.error(
                f"HTTP Exception when replying (Message ID: {message.id}\n   {e}")
            return
        self.message_ts = time()

    async def reply_text(self, message, text):
        try:
            await message.reply(text)
        except discord.Forbidden:
            log.error(f"Not allowed to reply (Message ID: {message.id})")
            return
        except discord.HTTPException as e:
            log.error(
                f"HTTP Exception when replying (Message ID: {message.id}\n   {e}")
            return
        self.message_ts = time()

    async def fumo_reaction(self, message):
        fumo_reacton_list = FUMO_STICKERIDS + FUMO_GIFS
        selected_reaction = choice(fumo_reacton_list)
        try:
            int(selected_reaction[0])
        except ValueError:
            # can't convert to number so it's a link -> gif
            await self.reply_text(message, selected_reaction)
            return

        # could convert so it's a number/ID -> sticker
        await self.reply_sticker(message, selected_reaction)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or (time() - self.message_ts < 15):
            return

        term = ""
        terms = ["bwaa", "pluh", "fumo", "get real", "meow"]
        text = message.content.lower()

        # parse implementation
        term = next((x for x in terms if x in text), False)
        if term == False:
            return

        match term:
            case "bwaa":  # sticker
                await self.reply_sticker(message, choice(BWAA_STICKERIDS))
            case "meow":  # sticker
                await self.reply_sticker(message, choice(MEOW_STICKERIDS))
            case "pluh":  # sticker
                await self.reply_sticker(message, choice(PLUH_STICKERIDS))
            case "fumo":  # sticker/gif
                await self.fumo_reaction(message)
            case "get real":
                await self.reply_text(message, choice(GET_REAL_GIFS))
            case "ban dami":  # regular messgae/embed
                pass
            case "fish":  # emoji reaction
                pass


async def setup(bot: commands.Bot):
    await bot.add_cog(MessageReacts(bot))
