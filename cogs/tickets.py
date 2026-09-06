# (C) 2025 Hexa Vibes. Licensed under the MIT License.

from os import getenv

import discord
from discord import app_commands
from discord.ext import commands

from logger import Logger

log = Logger("TICKETS")

MESSAGE_TEXT = """
Create a ticket with the moderation team, by clicking the button below
"""

TICKET_CHANNELID = int(getenv("TICKET_CHANNELID"))


class TicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Create ticket", style=discord.ButtonStyle.primary)
    async def createTicket(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        log.info("create channel")


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="admin_ticket_message_create",
        description="Send the Message for ticket creation",
    )
    async def admin_ticket_message_create(self, interaction: discord.Interaction):
        await interaction.channel.send(MESSAGE_TEXT, view=TicketButton)


async def setup(bot: commands.Bot):
    await bot.add_cog(Tickets(bot))
