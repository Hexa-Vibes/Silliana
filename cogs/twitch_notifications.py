# (C) 2025 Hexa Vibes. Licensed under the MIT License.

import discord
import os
import requests
from discord import app_commands
from discord.ext import commands, tasks
from typing import Optional, Dict, Any


class TwitchNotifications(commands.Cog):
    """
    A cog that monitors Twitch streams and sends Discord notifications when the streamer goes live.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
        # Load environment variables
        self.client_id = os.getenv("TWITCH_CLIENT_ID")
        self.client_secret = os.getenv("TWITCH_CLIENT_SECRET")
        self.username = os.getenv("TWITCH_USERNAME")
        
        # Parse numeric environment variables with error handling
        try:
            self.notification_channel_id = int(os.getenv("TWITCH_NOTIFICATION_CHANNELID", "0"))
            self.owner_id = int(os.getenv("OWNER_ID", "0"))
        except ValueError:
            print("Error: Invalid channel ID or owner ID in environment variables")
            self.notification_channel_id = 0
            self.owner_id = 0
        
        # API related attributes
        self.access_token: Optional[str] = None
        self.headers: Dict[str, str] = {}
        
        # State management
        self.is_live = False
        
        # Validate configuration
        if not self._validate_config():
            print("Error: Invalid configuration. Stream monitoring will not start.")
            return
        
        # Start the background task
        self.check_stream_status.start()

    def _validate_config(self) -> bool:
        """Validates the configuration and returns True if valid."""
        required_vars = [self.client_id, self.client_secret, self.username]
        if not all(required_vars):
            print("Error: Missing required Twitch API credentials")
            return False
        
        if self.notification_channel_id == 0:
            print("Error: Invalid notification channel ID")
            return False
        
        return True

    def cog_unload(self):
        """Gracefully stop the task when the cog is unloaded."""
        self.check_stream_status.cancel()

    def _get_access_token(self) -> bool:
     
        try:
            response = requests.post(
                "https://id.twitch.tv/oauth2/token",
                params={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "client_credentials"
                },
                timeout=10
            )
            response.raise_for_status()
            
            self.access_token = response.json()["access_token"]
            self.headers = {
                "Client-ID": self.client_id,
                "Authorization": f"Bearer {self.access_token}"
            }
            
            print("Successfully obtained Twitch access token")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"Error obtaining Twitch access token: {e}")
            self.access_token = None
            self.headers = {}
            return False

    def _make_api_request(self) -> Optional[Dict[str, Any]]:
        """
        Makes a request to the Twitch API to check stream status.
        
        Returns:
            Optional[Dict]: API response data or None if failed
        """
        try:
            response = requests.get(
                f"https://api.twitch.tv/helix/streams?user_login={self.username}",
                headers=self.headers,
                timeout=10
            )
            
            # Handle token expiration
            if response.status_code == 401:
                print("Twitch access token expired. Refreshing...")
                if self._get_access_token():
                    response = requests.get(
                        f"https://api.twitch.tv/helix/streams?user_login={self.username}",
                        headers=self.headers,
                        timeout=10
                    )
                else:
                    return None
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error making Twitch API request: {e}")
            return None

    @tasks.loop(minutes=1)
    async def check_stream_status(self):
        """Checks the Twitch API every minute to monitor stream status."""
        # Ensure we have a valid access token
        if not self.access_token and not self._get_access_token():
            return
        
        # Make API request
        api_data = self._make_api_request()
        if api_data is None:
            return
        
        stream_data = api_data.get("data", [])
        
        # Handle stream state changes
        if stream_data:
            # Stream is LIVE
            if not self.is_live:
                self.is_live = True
                stream_info = stream_data[0]
                await self._send_live_notification(stream_info)
        else:
            # Stream is OFFLINE
            if self.is_live:
                print(f"{self.username} has gone offline")
                self.is_live = False

    async def _send_live_notification(self, stream_info: Dict[str, Any]):
        """
        Sends a live notification to the designated Discord channel.
        
        Args:
            stream_info: Dictionary containing stream information from Twitch API
        """
        channel = self.bot.get_channel(self.notification_channel_id)
        if not channel:
            print(f"Error: Notification channel with ID {self.notification_channel_id} not found")
            return

        print(f"{self.username} is live! Sending notification...")

        # Create embed
        embed = self._create_live_embed(stream_info)
        
        # Send notification
        await channel.send(
            content=f"Hey everyone, @here! **{self.username}** just went live!",
            embed=embed
        )

    def _create_live_embed(self, stream_info: Dict[str, Any]) -> discord.Embed:
        """
        Creates a Discord embed for the live notification.
        
        Args:
            stream_info: Dictionary containing stream information
            
        Returns:
            discord.Embed: Formatted embed for the notification
        """
        embed = discord.Embed(
            title=f"🔴 LIVE: {stream_info.get('title', 'No Title')}",
            url=f"https://twitch.tv/{self.username}",
            color=discord.Color.purple()
        )
        
        embed.set_author(
            name=f"{self.username} is now streaming!",
            url=f"https://twitch.tv/{self.username}"
        )
        
        embed.add_field(
            name="Game",
            value=stream_info.get('game_name', 'Not specified'),
            inline=True
        )
        
        embed.add_field(
            name="Viewers",
            value=stream_info.get('viewer_count', 'N/A'),
            inline=True
        )
        
        # Add thumbnail with cache-busting timestamp
        thumbnail_url = stream_info.get('thumbnail_url', '')
        if thumbnail_url:
            thumbnail_url = thumbnail_url.replace('{width}', '1280').replace('{height}', '720')
            embed.set_image(url=f"{thumbnail_url}?t={int(discord.utils.utcnow().timestamp())}")
        
        return embed

    # @app_commands.command(name="debug_twitch", description="Manually check Twitch stream status for debugging.")
    # async def debug_twitch(self, interaction: discord.Interaction):
    #     """An owner-only command to debug the Twitch API connection."""
    #     if interaction.user.id != self.owner_id:
    #         await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
    #         return
    #     
    #     await interaction.response.defer(ephemeral=True)
    #
    #     # Check for access token
    #     if not self.access_token:
    #         token_status = "No token found. Attempting to get one..."
    #         token_success = self._get_access_token()
    #         token_status += " Success!" if token_success else " Failed."
    #     else:
    #         token_status = "Access token is present."
    #
    #     # Perform API check
    #     api_data = self._make_api_request()
    #     if api_data is not None:
    #         api_status = "API call successful"
    #         stream_data = api_data.get("data", [])
    #     else:
    #         api_status = "API call failed"
    #         stream_data = []
    #
    #     # Build the debug message
    #     debug_message = (
    #         f"**Twitch Debug Report**\n"
    #         f"--------------------------\n"
    #         f"**Timestamp:** `{interaction.created_at.strftime('%Y-%m-%d %H:%M:%S')}`\n"
    #         f"**Token Status:** `{token_status}`\n"
    #         f"**API Status:** {api_status}\n"
    #         f"**Current `is_live` state:** `{self.is_live}`\n"
    #         f"**Stream Data found:** `{'Yes' if stream_data else 'No'}`\n\n"
    #     )
    #     
    #     if stream_data:
    #         debug_message += "**Decision:** Stream is **LIVE**. "
    #         if not self.is_live:
    #             debug_message += "Notification would be sent."
    #         else:
    #             debug_message += "Notification already sent, so no new one."
    #     else:
    #         debug_message += "**Decision:** Stream is **OFFLINE**. "
    #         if self.is_live:
    #              debug_message += "State would be updated to offline."
    #         else:
    #              debug_message += "No action needed."
    #
    #     # Send to notification channel
    #     channel = self.bot.get_channel(self.notification_channel_id)
    #     if channel:
    #         await channel.send(debug_message)
    #         await interaction.followup.send(f"Debug report sent to <#{self.notification_channel_id}>")
    #     else:
    #         await interaction.followup.send("Could not find the notification channel.")

    # @app_commands.command(name="debug_embed", description="Preview the live notification embed with mock data.")
    # async def debug_embed(self, interaction: discord.Interaction):
    #     """An owner-only command to preview the live notification embed."""
    #     if interaction.user.id != self.owner_id:
    #         await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
    #         return
    #     
    #     # Mock stream data for testing
    #     mock_stream_info = {
    #         "title": "Building an awesome Discord bot! Come hang out!",
    #         "game_name": "Software and Game Development",
    #         "viewer_count": 42,
    #         "thumbnail_url": "https://static-cdn.jtvnw.net/previews-ttv/live_user_{login}-{width}x{height}.jpg"
    #     }
    #     
    #     # Create the same embed as the live notification
    #     embed = self._create_live_embed(mock_stream_info)
    #     
    #     # Add mock thumbnail with username replacement
    #     thumbnail_url = mock_stream_info.get('thumbnail_url', '').replace('{login}', self.username.lower())
    #     if thumbnail_url:
    #         thumbnail_url = thumbnail_url.replace('{width}', '1280').replace('{height}', '720')
    #         embed.set_image(url=f"{thumbnail_url}?t={int(discord.utils.utcnow().timestamp())}")
    #     
    #     embed.set_footer(text="This is a preview with mock data for testing purposes.")
    #
    #     # Send to notification channel
    #     channel = self.bot.get_channel(self.notification_channel_id)
    #     if channel:
    #         await channel.send(
    #             content=f"**Debug Preview:** This is how the notification would look when **{self.username}** goes live:",
    #             embed=embed
    #         )
    #         await interaction.response.send_message(f"Debug embed sent to <#{self.notification_channel_id}>", ephemeral=True)
    #     else:
    #         await interaction.response.send_message("Could not find the notification channel.", ephemeral=True)

    @check_stream_status.before_loop
    async def before_check(self):
        """Ensures the bot is ready before starting the loop."""
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    """Standard setup function for cogs."""
    await bot.add_cog(TwitchNotifications(bot))