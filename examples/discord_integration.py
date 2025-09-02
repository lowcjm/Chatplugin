"""
Discord Bot Integration Example

This example shows how to integrate the chat moderation plugin with a Discord bot.
Requires discord.py: pip install discord.py
"""

import discord
from discord.ext import commands, tasks
import asyncio
import logging
import sys
import os

# Add parent directory to path to import moderation modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from moderation_api import ModerationAPI


class DiscordModerationBot(commands.Bot):
    """Discord bot with integrated moderation"""
    
    def __init__(self, command_prefix="!", config_file="config.json"):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(command_prefix=command_prefix, intents=intents)
        
        self.moderation_api = ModerationAPI(config_file)
        self.setup_logging()
        
        # Start periodic cleanup task
        self.cleanup_task.start()
        
    def setup_logging(self):
        """Setup logging for the bot"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('DiscordModerationBot')
        
    async def on_ready(self):
        """Called when bot is ready"""
        self.logger.info(f'{self.user} has connected to Discord!')
        
    async def on_message(self, message):
        """Handle incoming messages"""
        # Skip bot messages
        if message.author.bot:
            return
            
        # Get user information
        user_id = str(message.author.id)
        user_roles = [role.name for role in message.author.roles]
        channel_id = str(message.channel.id)
        
        # Moderate the message
        result = self.moderation_api.moderate_message(
            user_id=user_id,
            message=message.content,
            channel_id=channel_id,
            user_roles=user_roles
        )
        
        # Handle moderation result
        if not result["allowed"]:
            try:
                await message.delete()
                await self.handle_violation(message, result)
            except discord.errors.NotFound:
                pass  # Message already deleted
            except discord.errors.Forbidden:
                self.logger.warning("Missing permissions to delete message")
                
        # Process commands after moderation
        await self.process_commands(message)
        
    async def handle_violation(self, message, result):
        """Handle moderation violations"""
        user = message.author
        channel = message.channel
        violations = result.get("violations", [])
        actions = result.get("actions_taken", [])
        
        # Send warning for violations
        if violations:
            violation_text = ", ".join(violations)
            embed = discord.Embed(
                title="Message Moderated",
                description=f"Your message was removed for: {violation_text}",
                color=discord.Color.orange()
            )
            embed.set_footer(text="Please follow the server rules")
            
            try:
                await user.send(embed=embed)
            except discord.errors.Forbidden:
                # Send to channel if DM fails
                await channel.send(f"{user.mention}, your message was moderated for: {violation_text}", delete_after=10)
                
        # Apply Discord-specific actions
        if "mute" in actions:
            await self.apply_discord_mute(user, message.guild)
        elif "kick" in actions:
            await self.apply_discord_kick(user, message.guild, "Automated moderation")
        elif "ban" in actions:
            await self.apply_discord_ban(user, message.guild, "Automated moderation")
            
    async def apply_discord_mute(self, user, guild):
        """Apply Discord mute (requires muted role setup)"""
        muted_role = discord.utils.get(guild.roles, name="Muted")
        if muted_role:
            try:
                await user.add_roles(muted_role, reason="Automated moderation")
                self.logger.info(f"Muted user {user} in {guild}")
            except discord.errors.Forbidden:
                self.logger.warning(f"Missing permissions to mute {user}")
        else:
            self.logger.warning("Muted role not found in guild")
            
    async def apply_discord_kick(self, user, guild, reason):
        """Apply Discord kick"""
        try:
            await guild.kick(user, reason=reason)
            self.logger.info(f"Kicked user {user} from {guild}: {reason}")
        except discord.errors.Forbidden:
            self.logger.warning(f"Missing permissions to kick {user}")
            
    async def apply_discord_ban(self, user, guild, reason):
        """Apply Discord ban"""
        try:
            await guild.ban(user, reason=reason, delete_message_days=1)
            self.logger.info(f"Banned user {user} from {guild}: {reason}")
        except discord.errors.Forbidden:
            self.logger.warning(f"Missing permissions to ban {user}")
            
    @tasks.loop(minutes=5)
    async def cleanup_task(self):
        """Periodic cleanup of expired punishments"""
        self.moderation_api.cleanup()
        
        # Remove expired Discord mutes
        for guild in self.guilds:
            muted_role = discord.utils.get(guild.roles, name="Muted")
            if muted_role:
                for member in muted_role.members:
                    user_status = self.moderation_api.get_user_status(str(member.id))
                    if not user_status["is_muted"]:
                        try:
                            await member.remove_roles(muted_role, reason="Mute expired")
                            self.logger.info(f"Removed mute from {member}")
                        except discord.errors.Forbidden:
                            pass
                            
    @cleanup_task.before_loop
    async def before_cleanup(self):
        """Wait for bot to be ready before starting cleanup"""
        await self.wait_until_ready()


# Moderation Commands Cog
class ModerationCommands(commands.Cog):
    """Moderation commands for Discord"""
    
    def __init__(self, bot):
        self.bot = bot
        self.api = bot.moderation_api
        
    @commands.command(name="modstats")
    @commands.has_permissions(manage_messages=True)
    async def moderation_stats(self, ctx):
        """Display moderation statistics"""
        stats = self.api.get_stats()
        
        embed = discord.Embed(
            title="Moderation Statistics",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Total Violations", value=stats["total_violations"], inline=True)
        embed.add_field(name="Active Mutes", value=stats["active_mutes"], inline=True)
        embed.add_field(name="Active Bans", value=stats["active_bans"], inline=True)
        embed.add_field(name="Users Tracked", value=stats["total_users_tracked"], inline=True)
        
        if stats["violation_types"]:
            violation_text = "\n".join([f"{k}: {v}" for k, v in stats["violation_types"].items()])
            embed.add_field(name="Violation Types", value=violation_text, inline=False)
            
        await ctx.send(embed=embed)
        
    @commands.command(name="userinfo")
    @commands.has_permissions(manage_messages=True)
    async def user_info(self, ctx, user: discord.Member = None):
        """Get moderation info for a user"""
        if user is None:
            user = ctx.author
            
        user_status = self.api.get_user_status(str(user.id))
        violations = self.api.get_violations(str(user.id), days=30)
        
        embed = discord.Embed(
            title=f"Moderation Info: {user.display_name}",
            color=discord.Color.green() if not user_status["is_muted"] and not user_status["is_banned"] else discord.Color.red()
        )
        
        embed.add_field(name="Is Muted", value=user_status["is_muted"], inline=True)
        embed.add_field(name="Is Banned", value=user_status["is_banned"], inline=True)
        embed.add_field(name="Total Violations", value=user_status["violation_count"], inline=True)
        
        if user_status["mute_until"]:
            embed.add_field(name="Muted Until", value=user_status["mute_until"], inline=False)
        if user_status["ban_until"]:
            embed.add_field(name="Banned Until", value=user_status["ban_until"], inline=False)
            
        recent_violations = len(violations)
        embed.add_field(name="Recent Violations (30 days)", value=recent_violations, inline=True)
        
        await ctx.send(embed=embed)
        
    @commands.command(name="modmute")
    @commands.has_permissions(manage_messages=True)
    async def manual_mute(self, ctx, user: discord.Member, duration: int = 300, *, reason: str = "Manual moderation"):
        """Manually mute a user"""
        success = self.api.apply_manual_action(
            str(user.id), "mute", duration, reason, str(ctx.author.id)
        )
        
        if success:
            await self.bot.apply_discord_mute(user, ctx.guild)
            embed = discord.Embed(
                title="User Muted",
                description=f"{user.mention} has been muted for {duration} seconds",
                color=discord.Color.orange()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Failed to mute user")
            
    @commands.command(name="modunmute")
    @commands.has_permissions(manage_messages=True)
    async def manual_unmute(self, ctx, user: discord.Member):
        """Manually unmute a user"""
        # Remove from moderation system
        user_status = self.api.get_user_status(str(user.id))
        if user_status["is_muted"]:
            # Force unmute by setting mute_until to now
            self.api.plugin.users[str(user.id)].is_muted = False
            self.api.plugin.users[str(user.id)].mute_until = None
            
            # Remove Discord mute role
            muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
            if muted_role and muted_role in user.roles:
                await user.remove_roles(muted_role, reason=f"Unmuted by {ctx.author}")
                
            embed = discord.Embed(
                title="User Unmuted",
                description=f"{user.mention} has been unmuted",
                color=discord.Color.green()
            )
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send("User is not muted")


# Bot setup and run function
def run_discord_bot(token: str, config_file: str = "config.json"):
    """Run the Discord moderation bot"""
    bot = DiscordModerationBot(config_file=config_file)
    bot.add_cog(ModerationCommands(bot))
    
    try:
        bot.run(token)
    except discord.errors.LoginFailure:
        print("Invalid bot token")
    except KeyboardInterrupt:
        print("Bot stopped by user")


if __name__ == "__main__":
    import os
    
    # Get token from environment variable
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("Please set DISCORD_BOT_TOKEN environment variable")
        print("Usage: DISCORD_BOT_TOKEN=your_token_here python discord_integration.py")
        exit(1)
        
    run_discord_bot(token)