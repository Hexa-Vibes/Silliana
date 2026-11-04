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


class TicketButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)


class TicketButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Create ticket",
            style=discord.ButtonStyle.primary
        )

    async def callback(self, interaction: discord.Interaction):
        log.info("create channel")


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def __create_button_view(self):
        button = TicketButton()
        buttonview = TicketButtonView()

        buttonview.add_item(button)

        return buttonview

    @app_commands.command(
        name="admin_ticket_message_create",
        description="Send the Message for ticket creation",
    )
    async def admin_ticket_message_create(
        self,
        interaction: discord.Interaction
    ):
        buttonview = await self.__create_button_view()

        try:
            await interaction.channel.send(
                content=MESSAGE_TEXT,
                view=buttonview
            )
        except Exception as e:
            log.error(e)


async def setup(bot: commands.Bot):
    await bot.add_cog(Tickets(bot))
