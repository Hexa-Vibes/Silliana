# (C) 2025 Hexa Vibes. Licensed under the MIT License.

import discord
import os
from discord.ext import commands, tasks
from logger import Logger

log = Logger("AIC")

class AiCheck(commands.Cog):

  def __init__(self, bot: commands.Bot):
    self.bot = bot
    self.api_key = os.getenv("SHL_API_KEY")

    if not self._validate_config():
      log.error("Invalid configuration. AI checks are disabled.")
      self.enabled = False
      return

    self.enabled = True

  def _validate_config(self) -> bool:
    """Validates the configuration and returns True if valid."""
    required_vars = [self.api_key]
    if not all(required_vars):
      log.warn("Missing required SHLabs API credentials")
      return False

    return True
