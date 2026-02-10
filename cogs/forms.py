# (C) 2025 Hexa Vibes. Licensed under the MIT License.

import discord
import os
import re
from discord.ext import commands
from discord import app_commands
from typing import Optional
from logger import Logger

log = Logger("FORMS")

#====================
# CONSTANTS
#====================
SUBMISSION_EMBED_COLOR = 0x00ff00
WELCOME_EMBED_COLOR = 0x9b59b6
ACCEPTED_COLOR = 0x3498db  
DENIED_COLOR = 0xe74c3c    
HOLD_COLOR = 0xf1c40f      
SUCCESS_MESSAGE = "Your submission has been received!"
ERROR_MESSAGE = "An error occurred while submitting your form."

#====================
# MODALS
#====================
# Rejection reason embed
class RejectionReasonModal(discord.ui.Modal, title='Rejection Reason'):
    def __init__(self, original_view, message):
        super().__init__()
        self.original_view = original_view
        self.message = message

    rejection_reason = discord.ui.TextInput(
        label='Why are you rejecting this submission?',
        placeholder='Enter the reason for rejection...',
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await self.original_view.handle_review(
            interaction, 
            "denied", 
            DENIED_COLOR, 
            rejection_reason=self.rejection_reason.value
        )

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
            color=SUBMISSION_EMBED_COLOR,
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
            text=f"Submitted by {interaction.user.display_name} (ID: {interaction.user.id})",
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
                # Create review buttons for the submission message
                review_buttons = SubmissionReviewButtons()
                await channel.send(embed=embed, view=review_buttons)
        except (ValueError, AttributeError) as e:
            log.error(f"Error sending to submission channel: {e}")
# Handle errors during form submission
    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        log.error(f"Form submission error: {error}")

        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(ERROR_MESSAGE, ephemeral=True)
            else:
                await interaction.followup.send(ERROR_MESSAGE, ephemeral=True)
        except Exception as e:
            print(f"Error sending error message: {e}")

#====================
# UI BUTTONS
#====================
# Posted button for accepted tracks
class PostedButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label='Mark as Posted',
        style=discord.ButtonStyle.primary,
        custom_id='mark_as_posted',
    )
    async def mark_posted(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        
        embed = interaction.message.embeds[0]
        
        
        if not embed.title.startswith("**POSTED**"):
            embed.title = f"**POSTED** - {embed.title}"
            
        
        button.disabled = True
        button.label = "Posted"
        
        
        await interaction.response.edit_message(embed=embed, view=self)
        await interaction.followup.send("Track marked as posted.", ephemeral=True)

# Submission button view
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

# Review buttons for submission management
class SubmissionReviewButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        # Get the channel IDs from environment variables
        self.accepted_channel_id = os.getenv("ACCEPTED_CHANNELID")
        self.rejected_channel_id = os.getenv("REJECTED_CHANNELID")
        self.held_channel_id = os.getenv("HELD_CHANNELID")

    @staticmethod
    def _extract_submitter_id(embed: discord.Embed) -> Optional[int]:
        footer_text = embed.footer.text if embed.footer else ""
        if not footer_text:
            return None

        match = re.search(r"\(ID:\s*(\d+)\)", footer_text)
        if not match:
            return None

        try:
            return int(match.group(1))
        except ValueError:
            return None

    @discord.ui.button(
        label='Accept',
        style=discord.ButtonStyle.success,
        custom_id='accept_submission',
    )
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.handle_review(interaction, "accepted", ACCEPTED_COLOR)

    @discord.ui.button(
        label='Deny',
        style=discord.ButtonStyle.danger,
        custom_id='deny_submission',
    )
    async def deny_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        
        modal = RejectionReasonModal(self, interaction.message)
        await interaction.response.send_modal(modal)

    @discord.ui.button(
        label='Hold for Questions',
        style=discord.ButtonStyle.secondary,
        custom_id='hold_submission',
    )
    async def hold_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.handle_review(interaction, "held for questions", HOLD_COLOR)

    async def handle_review(self, interaction: discord.Interaction, status: str, color: int, rejection_reason: str = None) -> None:
        # Update the embed with the review status
        embed = interaction.message.embeds[0]
        embed.color = color
        embed.title = f"📝 Submission {status.capitalize()}"
        
        
        status_value = f"{status.capitalize()} by {interaction.user.mention}"
        if rejection_reason and status == "denied":
            status_value += f"\nReason: {rejection_reason}"
            
        embed.add_field(
            name="Review Status",
            value=status_value,
            inline=False
        )
        
        
        for item in self.children:
            item.disabled = True
        
        response_sent = False
        
        # Handle accepted submissions
        if status == "accepted" and self.accepted_channel_id:
            try:
                
                accepted_channel = await interaction.client.fetch_channel(int(self.accepted_channel_id))
                if accepted_channel:
                    
                    accepted_embed = discord.Embed(
                        title=f"Accepted Track: {embed.fields[1].value}",  # Song name
                        description=f"By {embed.fields[0].value}",  # Artist name
                        color=ACCEPTED_COLOR,
                        timestamp=discord.utils.utcnow()
                    )
                    
                    
                    accepted_embed.add_field(name="Link", value=embed.fields[2].value, inline=False)  # Song link
                    accepted_embed.add_field(name="Genre", value=embed.fields[3].value, inline=True)  # Genre
                    accepted_embed.add_field(name="Socials", value=embed.fields[4].value, inline=True)  # Socials
                    

                    posted_view = PostedButton()
                    

                    await accepted_channel.send(embed=accepted_embed, view=posted_view)
                    
                    # Send confirmation to reviewer
                    if interaction.response.is_done():
                        await interaction.followup.send(
                            f"Submission accepted and moved to <#{self.accepted_channel_id}>. Original message will be deleted.", 
                            ephemeral=True
                        )
                    else:
                        await interaction.response.send_message(
                            f"Submission accepted and moved to <#{self.accepted_channel_id}>. Original message will be deleted.", 
                            ephemeral=True
                        )
                        response_sent = True
                    
                    # Delete the original message
                    await interaction.message.delete()
                    
                else:
                    # Send error message if the channel couldn't be found
                    if not response_sent:
                        if interaction.response.is_done():
                            await interaction.followup.send(
                                "Could not find the accepted submissions channel. The submission has been marked as accepted, but was not moved.",
                                ephemeral=True
                            )
                        else:
                            await interaction.response.send_message(
                                "Could not find the accepted submissions channel. The submission has been marked as accepted, but was not moved.",
                                ephemeral=True
                            )
                            response_sent = True
                            

                    await interaction.message.edit(embed=embed, view=None)
                    
            except (ValueError, AttributeError, discord.NotFound, discord.Forbidden) as e:
                print(f"Error moving accepted submission: {e}")
                if not response_sent:
                    if interaction.response.is_done():
                        await interaction.followup.send(
                            "An error occurred while moving the submission. The submission has been marked as accepted, but was not moved.",
                            ephemeral=True
                        )
                    else:
                        await interaction.response.send_message(
                            "An error occurred while moving the submission. The submission has been marked as accepted, but was not moved.",
                            ephemeral=True
                        )
                        response_sent = True
                        
                
                await interaction.message.edit(embed=embed, view=None)
        
        elif status == "denied" and self.rejected_channel_id:
            try:
                # Get the rejected channel
                rejected_channel = await interaction.client.fetch_channel(int(self.rejected_channel_id))
                if rejected_channel:
                    # Create a new embed for the rejected channel
                    rejected_embed = discord.Embed(
                        title=f"Rejected Track: {embed.fields[1].value}",  # Song name
                        description=f"By {embed.fields[0].value}",  # Artist name
                        color=DENIED_COLOR,
                        timestamp=discord.utils.utcnow()
                    )
                    
                    # Copy relevant fields
                    rejected_embed.add_field(name="Link", value=embed.fields[2].value, inline=False)  # Song link
                    rejected_embed.add_field(name="Genre", value=embed.fields[3].value, inline=True)  # Genre
                    rejected_embed.add_field(name="Socials", value=embed.fields[4].value, inline=True)  # Socials
                    
                    # Add rejection reason if provided
                    if rejection_reason:
                        rejected_embed.add_field(
                            name="Rejection Reason",
                            value=rejection_reason,
                            inline=False
                        )
                    
                    
                    rejected_embed.set_footer(
                        text=f"Rejected by: {interaction.user.display_name}",
                        icon_url=interaction.user.avatar.url if interaction.user.avatar else None
                    )
                    
                    # Send to the rejected channel
                    await rejected_channel.send(embed=rejected_embed)
                    
                    
                    if interaction.response.is_done():
                        await interaction.followup.send(
                            f"Submission rejected and moved to <#{self.rejected_channel_id}>. Original message will be deleted.", 
                            ephemeral=True
                        )
                    else:
                        await interaction.response.send_message(
                            f"Submission rejected and moved to <#{self.rejected_channel_id}>. Original message will be deleted.", 
                            ephemeral=True
                        )
                        response_sent = True
                    

                    await interaction.message.delete()
                    
                else:
                    
                    if not response_sent:
                        if interaction.response.is_done():
                            await interaction.followup.send(
                                "Could not find the rejected submissions channel. The submission has been marked as rejected, but was not moved.",
                                ephemeral=True
                            )
                        else:
                            await interaction.response.send_message(
                                "Could not find the rejected submissions channel. The submission has been marked as rejected, but was not moved.",
                                ephemeral=True
                            )
                            response_sent = True
                            

                    await interaction.message.edit(embed=embed, view=None)
                    
            except (ValueError, AttributeError, discord.NotFound, discord.Forbidden) as e:
                log.error(f"Error moving rejected submission: {e}")
                if not response_sent:
                    if interaction.response.is_done():
                        await interaction.followup.send(
                            "An error occurred while moving the submission. The submission has been marked as rejected, but was not moved.",
                            ephemeral=True
                        )
                    else:
                        await interaction.response.send_message(
                            "An error occurred while moving the submission. The submission has been marked as rejected, but was not moved.",
                            ephemeral=True
                        )
                        response_sent = True
                        
                
                await interaction.message.edit(embed=embed, view=None)
        # Handle held for questions submissions
        elif status == "held for questions" and self.held_channel_id:
            try:
                
                held_channel = await interaction.client.fetch_channel(int(self.held_channel_id))
                if held_channel:
                    # Create a new embed for the held channel
                    held_embed = discord.Embed(
                        title=f"Held Track: {embed.fields[1].value}",  # Song name
                        description=f"By {embed.fields[0].value}",  # Artist name
                        color=HOLD_COLOR,
                        timestamp=discord.utils.utcnow()
                    )
                    
                    # Copy relevant fields
                    held_embed.add_field(name="Link", value=embed.fields[2].value, inline=False)  # Song link
                    held_embed.add_field(name="Genre", value=embed.fields[3].value, inline=True)  # Genre
                    held_embed.add_field(name="Socials", value=embed.fields[4].value, inline=True)  # Socials
                    

                    held_embed.set_footer(
                        text=f"Held by: {interaction.user.display_name}",
                        icon_url=interaction.user.avatar.url if interaction.user.avatar else None
                    )
                    
                    
                    await held_channel.send(embed=held_embed)
                    
                    
                    if interaction.response.is_done():
                        await interaction.followup.send(
                            f"Submission held for questions and moved to <#{self.held_channel_id}>. Original message will be deleted.", 
                            ephemeral=True
                        )
                    else:
                        await interaction.response.send_message(
                            f"Submission held for questions and moved to <#{self.held_channel_id}>. Original message will be deleted.", 
                            ephemeral=True
                        )
                        response_sent = True
                    
                    # Delete the original message
                    await interaction.message.delete()
                    
                else:
                    
                    if not response_sent:
                        if interaction.response.is_done():
                            await interaction.followup.send(
                                "Could not find the held submissions channel. The submission has been marked as held for questions, but was not moved.",
                                ephemeral=True
                            )
                        else:
                            await interaction.response.send_message(
                                "Could not find the held submissions channel. The submission has been marked as held for questions, but was not moved.",
                                ephemeral=True
                            )
                            response_sent = True
                            

                    await interaction.message.edit(embed=embed, view=None)
                    
            except (ValueError, AttributeError, discord.NotFound, discord.Forbidden) as e:
                log.error(f"Error moving held submission: {e}")
                if not response_sent:
                    if interaction.response.is_done():
                        await interaction.followup.send(
                            "An error occurred while moving the submission. The submission has been marked as held for questions, but was not moved.",
                            ephemeral=True
                        )
                    else:
                        await interaction.response.send_message(
                            "An error occurred while moving the submission. The submission has been marked as held for questions, but was not moved.",
                            ephemeral=True
                        )
                        response_sent = True
                        
                
                await interaction.message.edit(embed=embed, view=None)
        else:
            # For submissions or if channel isn't set, just update the message
            # If this is called from the modal, interaction.response is already used
            if interaction.response.is_done():
                await interaction.message.edit(embed=embed, view=None)
                if not response_sent:
                    await interaction.followup.send(f"Submission has been marked as {status}.", ephemeral=True)
            else:
                await interaction.response.edit_message(embed=embed, view=None)
                await interaction.followup.send(f"Submission has been marked as {status}.", ephemeral=True)
        
        
        try:
            submitter_id = self._extract_submitter_id(embed)
            if not submitter_id:
                await interaction.followup.send("Could not determine the submitter to notify.", ephemeral=True)
                return

            submitter = await interaction.client.fetch_user(submitter_id)
            if submitter:
                
                notification_embed = discord.Embed(
                    title=f"Your Submission Status: {status.capitalize()}",
                    color=color,
                    timestamp=discord.utils.utcnow()
                )
                
                
                if status == "held for questions":
                    notification_embed.description = "Please contact Hexa Vibes in DMs for more information about your submission."
                elif status == "denied" and rejection_reason:
                    notification_embed.description = f"**Reason for rejection:**\n{rejection_reason}"
                elif status == "accepted":
                    notification_embed.description = "Congratulations! Your submission has been accepted."
                
                # Copy relevant information from the original embed
                for field in embed.fields[:5]:  
                    notification_embed.add_field(
                        name=field.name,
                        value=field.value,
                        inline=field.inline
                    )
                
                
                notification_embed.set_footer(
                    text=f"Reviewed by: {interaction.user.display_name}",
                    icon_url=interaction.user.avatar.url if interaction.user.avatar else None
                )
                
                await submitter.send(embed=notification_embed)
                await interaction.followup.send("Notification sent to the submitter.", ephemeral=True)
            else:
                await interaction.followup.send("Could not find the submitter to notify.", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("Could not send DM to the submitter (DMs closed or blocked).", ephemeral=True)
        except Exception as e:
            log.error(f"Error notifying submitter: {e}")
            await interaction.followup.send("Error notifying the submitter.", ephemeral=True)

#====================
# MAIN COG
#====================
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

#====================
# SETUP
#====================
# Setup function for the cog.
async def setup(bot: commands.Bot) -> None:
    # Add the persistent view for the Posted button
    bot.add_view(PostedButton())
    await bot.add_cog(Forms(bot))
