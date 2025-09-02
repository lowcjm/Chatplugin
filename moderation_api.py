"""
Chat Moderation Plugin API

A simple API interface for the chat moderation plugin that can be integrated
into various chat platforms (Discord, Slack, Teams, etc.)
"""

from typing import Dict, List, Optional
from chat_moderation_plugin import ChatModerationPlugin, ModerationAction, ViolationType
import json


class ModerationAPI:
    """API wrapper for the chat moderation plugin"""
    
    def __init__(self, config_file: str = "config.json"):
        """Initialize the moderation API with configuration"""
        self.plugin = ChatModerationPlugin(config_file)
        
    def moderate_message(self, user_id: str, message: str, channel_id: str = None,
                        user_roles: List[str] = None) -> Dict:
        """
        Moderate a single message
        
        Args:
            user_id: Unique identifier for the user
            message: The message content to moderate
            channel_id: Optional channel identifier
            user_roles: Optional list of user roles (for bypassing moderation)
            
        Returns:
            Dictionary with moderation result
        """
        # Check if user has bypass permissions
        if user_roles and self._has_bypass_permission(user_roles):
            return {
                "allowed": True,
                "reason": "User has bypass permissions",
                "violations": [],
                "actions_taken": []
            }
            
        return self.plugin.moderate_message(user_id, message, channel_id)
        
    def get_user_status(self, user_id: str) -> Dict:
        """Get current status of a user"""
        user = self.plugin.get_user_status(user_id)
        return {
            "user_id": user.user_id,
            "is_muted": user.is_muted,
            "is_banned": user.is_banned,
            "mute_until": user.mute_until.isoformat() if user.mute_until else None,
            "ban_until": user.ban_until.isoformat() if user.ban_until else None,
            "violation_count": user.violation_count
        }
        
    def apply_manual_action(self, user_id: str, action: str, duration: int = 300,
                          reason: str = "", moderator_id: str = None) -> bool:
        """
        Manually apply a moderation action
        
        Args:
            user_id: Target user
            action: Action to take (warn, mute, kick, ban)
            duration: Duration in seconds (for mute/ban)
            reason: Reason for the action
            moderator_id: ID of the moderator taking action
            
        Returns:
            True if action was applied successfully
        """
        try:
            mod_action = ModerationAction(action)
            success = self.plugin.apply_moderation_action(user_id, mod_action, duration, reason)
            
            if success and moderator_id:
                # Log manual action
                self.plugin.logger.info(f"Manual action by {moderator_id}: {action} on {user_id} - {reason}")
                
            return success
        except ValueError:
            return False
            
    def get_violations(self, user_id: str = None, days: int = 7) -> List[Dict]:
        """Get violation history"""
        if user_id:
            return self.plugin.get_user_violations(user_id, days)
        else:
            # Return all violations from the last N days
            from datetime import datetime, timedelta
            cutoff = datetime.now() - timedelta(days=days)
            return [
                {
                    "user_id": v.user_id,
                    "violation_type": v.violation_type.value,
                    "message": v.message,
                    "timestamp": v.timestamp.isoformat(),
                    "action_taken": v.action_taken.value,
                    "moderator": v.moderator
                }
                for v in self.plugin.violations
                if v.timestamp > cutoff
            ]
            
    def get_stats(self) -> Dict:
        """Get moderation statistics"""
        return self.plugin.get_moderation_stats()
        
    def update_config(self, config_updates: Dict) -> bool:
        """Update configuration dynamically"""
        try:
            # Merge updates with existing config
            def deep_update(base_dict, update_dict):
                for key, value in update_dict.items():
                    if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                        deep_update(base_dict[key], value)
                    else:
                        base_dict[key] = value
                        
            deep_update(self.plugin.config, config_updates)
            
            # Save updated config
            with open("config.json", "w") as f:
                json.dump(self.plugin.config, f, indent=2)
                
            self.plugin.logger.info("Configuration updated successfully")
            return True
        except Exception as e:
            self.plugin.logger.error(f"Failed to update configuration: {e}")
            return False
            
    def cleanup(self):
        """Clean up expired punishments"""
        self.plugin.cleanup_expired_punishments()
        
    def add_profanity_words(self, words: List[str]) -> bool:
        """Add words to the profanity filter"""
        try:
            for word in words:
                self.plugin.profanity_words.add(word.lower())
            self.plugin.load_profanity_filter()  # Reload patterns
            return True
        except Exception as e:
            self.plugin.logger.error(f"Failed to add profanity words: {e}")
            return False
            
    def remove_profanity_words(self, words: List[str]) -> bool:
        """Remove words from the profanity filter"""
        try:
            for word in words:
                self.plugin.profanity_words.discard(word)
            self.plugin.load_profanity_filter()  # Reload patterns
            return True
        except Exception as e:
            self.plugin.logger.error(f"Failed to remove profanity words: {e}")
            return False
            
    def whitelist_user(self, user_id: str) -> bool:
        """Add user to whitelist (bypass moderation)"""
        try:
            if "bypass_users" not in self.plugin.config["whitelist"]:
                self.plugin.config["whitelist"]["bypass_users"] = []
            
            if user_id not in self.plugin.config["whitelist"]["bypass_users"]:
                self.plugin.config["whitelist"]["bypass_users"].append(user_id)
                return True
            return False
        except Exception as e:
            self.plugin.logger.error(f"Failed to whitelist user {user_id}: {e}")
            return False
            
    def remove_from_whitelist(self, user_id: str) -> bool:
        """Remove user from whitelist"""
        try:
            if "bypass_users" in self.plugin.config["whitelist"]:
                if user_id in self.plugin.config["whitelist"]["bypass_users"]:
                    self.plugin.config["whitelist"]["bypass_users"].remove(user_id)
                    return True
            return False
        except Exception as e:
            self.plugin.logger.error(f"Failed to remove user {user_id} from whitelist: {e}")
            return False
            
    def _has_bypass_permission(self, user_roles: List[str]) -> bool:
        """Check if user has permission to bypass moderation"""
        if not self.plugin.config["whitelist"]["enabled"]:
            return False
            
        moderator_roles = self.plugin.config["whitelist"]["moderator_roles"]
        return any(role in moderator_roles for role in user_roles)


# Discord Bot Integration Example
class DiscordModerationBot:
    """Example Discord bot integration"""
    
    def __init__(self, config_file: str = "config.json"):
        self.api = ModerationAPI(config_file)
        
    async def on_message(self, message):
        """Handle incoming Discord message"""
        # Skip bot messages
        if message.author.bot:
            return
            
        user_id = str(message.author.id)
        user_roles = [role.name for role in message.author.roles]
        channel_id = str(message.channel.id)
        
        # Moderate the message
        result = self.api.moderate_message(
            user_id=user_id,
            message=message.content,
            channel_id=channel_id,
            user_roles=user_roles
        )
        
        # Handle moderation result
        if not result["allowed"]:
            await message.delete()
            
            if "warn" in result["actions_taken"]:
                await message.channel.send(f"{message.author.mention}, please watch your language!")
                
            elif "mute" in result["actions_taken"]:
                # Apply Discord mute (would need appropriate permissions)
                await message.channel.send(f"{message.author.mention} has been muted for violating chat rules.")
                
        return result


# Slack Bot Integration Example  
class SlackModerationBot:
    """Example Slack bot integration"""
    
    def __init__(self, config_file: str = "config.json"):
        self.api = ModerationAPI(config_file)
        
    def handle_message(self, event):
        """Handle incoming Slack message"""
        user_id = event.get("user")
        message = event.get("text", "")
        channel_id = event.get("channel")
        
        # Moderate the message
        result = self.api.moderate_message(
            user_id=user_id,
            message=message,
            channel_id=channel_id
        )
        
        # Handle moderation result
        if not result["allowed"]:
            # Delete message (would need appropriate API calls)
            # Send warning or apply restrictions
            pass
            
        return result


if __name__ == "__main__":
    # Example usage
    api = ModerationAPI()
    
    # Test the API
    print("=== Moderation API Test ===")
    
    # Test normal message
    result1 = api.moderate_message("user1", "Hello everyone!")
    print(f"Normal message: {result1}")
    
    # Test profanity
    result2 = api.moderate_message("user2", "This is a damn test")
    print(f"Profanity test: {result2}")
    
    # Test spam
    result3 = api.moderate_message("user3", "spam spam spam spam spam")
    print(f"Spam test: {result3}")
    
    # Get stats
    stats = api.get_stats()
    print(f"Stats: {stats}")
    
    # Manual action
    success = api.apply_manual_action("user4", "mute", 300, "Manual moderation", "mod1")
    print(f"Manual action success: {success}")