# (C) 2025 Hexa Vibes. Licensed under the MIT License.

import discord
import os
from discord.ext import commands
from discord import app_commands
from typing import Optional


# Constants
SUBMISSION_EMBED_COLOR = 0x00ff00
WELCOME_EMBED_COLOR = 0x9b59b6
SUCCESS_MESSAGE = "✅ Your submission has been received!"
ERROR_MESSAGE = "❌ An error occurred while submitting your form."

# Modal form for music submissions.
class SubmissionForm(discord.ui.Modal, title='🎵 Music Submission Form'):
    
    def __init__(self):
        super().__init__()

    # Form fields
    artist_name = discord.ui.TextInput(
        label='Artist Name',
        placeholder='Enter your name...',
        required=True,
        max_length=100
    )

    song_name = discord.ui.TextInput(
        label='Song Name',
        placeholder='Enter your song title...',
        required=True,
        max_length=100
    )

    song_link = discord.ui.TextInput(
        label='Song Link',
        placeholder='Enter the link to your song (YouTube, SoundCloud, etc.)...',
        required=True,
        max_length=200
    )

    genre = discord.ui.TextInput(
        label='Genre',
        placeholder='Enter the genre(s) of your song...',
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=500
    )
    
    socials = discord.ui.TextInput(
        label='Social Media',
        placeholder='Enter your social media links (Instagram, Twitter, etc.)...',
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=500
    )
# Handle form submission    
    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            embed = self._create_submission_embed(interaction)
            await self._send_to_submission_channel(interaction, embed)
            await interaction.response.send_message(SUCCESS_MESSAGE, ephemeral=True)
        except Exception as e:
            await self.on_error(interaction, e)
# Create the submission embed
    def _create_submission_embed(self, interaction: discord.Interaction) -> discord.Embed:
        embed = discord.Embed(
            title="📝 New Form Submission",
            color=0x00ff00,
            timestamp=interaction.created_at
        )
        
# Add form fields to embed
        embed.add_field(name="Artist", value=self.artist_name.value, inline=True)
        embed.add_field(name="Song", value=self.song_name.value, inline=True)
        embed.add_field(name="Link", value=self.song_link.value, inline=False)
        embed.add_field(name="Genre", value=self.genre.value, inline=False)
        embed.add_field(name="Socials", value=self.socials.value, inline=False)
        
# Set footer with submitter info
        avatar_url = interaction.user.avatar.url if interaction.user.avatar else None
        embed.set_footer(
            text=f"Submitted by {interaction.user.display_name}",
            icon_url=avatar_url
        )
        
        return embed
# Send the submission embed to the configured submission channel.
    async def _send_to_submission_channel(self, interaction: discord.Interaction, embed: discord.Embed) -> None:
        submission_channel_id = os.getenv("SUBMISSION_CHANNELID")
        if not submission_channel_id:
            return
            
        try:
            channel = interaction.guild.get_channel(int(submission_channel_id))
            if channel:
                await channel.send(embed=embed)
        except (ValueError, AttributeError) as e:
            print(f"Error sending to submission channel: {e}")
# Handle errors during form submission
    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        print(f"Form submission error: {error}")
        
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(ERROR_MESSAGE, ephemeral=True)
            else:
                await interaction.followup.send(ERROR_MESSAGE, ephemeral=True)
        except Exception as e:
            print(f"Error sending error message: {e}")


class SubmissionButton(discord.ui.View):
 
# Persistent view with submission button. 
    def __init__(self):
        super().__init__(timeout=None)
    
# Cog for handling music submission forms
    @discord.ui.button(
        label='📝 Submit Your Music',
        style=discord.ButtonStyle.primary,
        custom_id='submit_music_button'
    )
# Handle submission button click.
    async def submit_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.send_modal(SubmissionForm())


class Forms(commands.Cog):
    
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="send_submission", description="Send a music submission form to a channel")
    @app_commands.describe(channel="The channel to send the submission form to (defaults to current channel)")
    async def send_submission_form(
        self, 
        interaction: discord.Interaction, 
        channel: Optional[discord.TextChannel] = None
    ) -> None:
        # Check if user is the bot owner
        owner_id = os.getenv("OWNER_ID")
        if not owner_id or interaction.user.id != int(owner_id):
            await interaction.response.send_message(
                "❌ You don't have permission to use this command. Only the bot owner can use this command.",
                ephemeral=True
            )
            return
      
# Send the submission form embed with button to a channel.
        target_channel = channel or interaction.channel
        
        embed = self._create_welcome_embed(interaction)
        view = SubmissionButton()
        
        await target_channel.send(embed=embed, view=view)
        await interaction.response.send_message(
            f"✅ Submission form sent to {target_channel.mention}!", 
            ephemeral=True
        )

    def _create_welcome_embed(self, interaction: discord.Interaction) -> discord.Embed:
# Create the welcome embed for the submission form.
        embed = discord.Embed(
            title="Welcome to Music Submissions!",
            description="Ready to share your music with the world? This is the place to submit your tracks for consideration!",
            color=WELCOME_EMBED_COLOR,
            timestamp=interaction.created_at
        )
        
        embed.add_field(
            name="What to Submit",
            value="• Original music tracks\n• Collaborative works\n• Creative content",
            inline=True
        )
        
        embed.add_field(
            name="What We're Looking For",
            value="• Quality production\n• Unique sounds\n• Passionate artists\n• Creative expression",
            inline=True
        )
        
        embed.add_field(
            name="How to Submit",
            value="Click the button below to open our submission form. Fill out all the required information about your track and we'll review it!",
            inline=False
        )
        
# Set footer and thumbnail
        guild_icon = interaction.guild.icon.url if interaction.guild and interaction.guild.icon else None
        embed.set_footer(text="Ready to get started? Click the button below!", icon_url=guild_icon)
        
        return embed

# Setup function for the cog.
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Forms(bot))
