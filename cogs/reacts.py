# (C) 2025 Hexa Vibes. Licensed under the MIT License.

import discord
from discord.ext import commands
from time import time
from os import getenv
from random import choice

"""
BWAA_STICKERIDS = getenv("BWAA_STICKERIDS").split(",")
MEOW_STICKERIDS = getenv("MEOW_STICKERIDS").split(",")
PLUH_STICKERIDS = getenv("PLUH_STICKERIDS").split(",")
FUMO_STICKERIDS = getenv("FUMO_STICKERIDS").split(",")
FUMO_GIFS = getenv("FUMO_GIFS").split(",")
"""
BWAA_STICKERIDS = [1296589336736698378, 1370067972592238612]
MEOW_STICKERIDS = [1222679517038903319]
PLUH_STICKERIDS = [1252392137392132210]
FUMO_STICKERIDS = ["1393228729697960077"]
FUMO_GIFS = ["https://chibisafe.crispy-caesus.eu/iZc8VAvsKtsA.gif", "https://chibisafe.crispy-caesus.eu/7uMePUKfjI21.gif", "https://chibisafe.crispy-caesus.eu/kvW9w5h6TvLf.gif", "https://chibisafe.crispy-caesus.eu/5DK1Jr3C5aHt.gif", "https://chibisafe.crispy-caesus.eu/sz7TDwpn495I.gif"]


class MessageReacts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_ts = 0

    async def reply_sticker(self, message, sticker_id):
        try:
            await message.reply(stickers=[await message.guild.fetch_sticker(sticker_id)])
        except discord.Forbidden:
            print(f"Not allowed to reply (Message ID: {message.id})")
            return
        except discord.HTTPException as e:
            print(
                f"HTTP Exception when replying (Message ID: {message.id}\n   {e}")
            return
        self.message_ts = time()

    async def reply_text(self, message, text):
        try:
            await message.reply(text)
        except discord.Forbidden:
            print(f"Not allowed to reply (Message ID: {message.id})")
            return
        except discord.HTTPException as e:
            print(
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
        terms = ["bwaa", "pluh", "fumo", "meow"]
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
            case "ban dami":  # regular messgae/embed
                pass
            case "fish":  # emoji reaction
                pass


async def setup(bot: commands.Bot):
    await bot.add_cog(MessageReacts(bot))
