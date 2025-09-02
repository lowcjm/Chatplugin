"""
Chat Moderation Plugin

A comprehensive chat moderation system that provides:
- Profanity filtering
- Spam detection and prevention
- Rate limiting
- User management (mute, kick, ban)
- Configurable moderation rules
- Logging and reporting

Author: Copilot
License: MIT
"""

import re
import time
import json
import logging
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum


class ModerationAction(Enum):
    """Types of moderation actions"""
    WARN = "warn"
    MUTE = "mute"
    KICK = "kick"
    BAN = "ban"
    DELETE_MESSAGE = "delete_message"


class ViolationType(Enum):
    """Types of rule violations"""
    PROFANITY = "profanity"
    SPAM = "spam"
    RATE_LIMIT = "rate_limit"
    CAPS_ABUSE = "caps_abuse"
    REPETITIVE = "repetitive"
    INAPPROPRIATE_CONTENT = "inappropriate_content"


@dataclass
class ModerationRule:
    """Configuration for a moderation rule"""
    name: str
    enabled: bool = True
    action: ModerationAction = ModerationAction.WARN
    threshold: int = 1
    duration: int = 300  # seconds
    auto_escalate: bool = False


@dataclass
class UserViolation:
    """Record of a user violation"""
    user_id: str
    violation_type: ViolationType
    message: str
    timestamp: datetime
    action_taken: ModerationAction
    moderator: Optional[str] = None


@dataclass
class UserStatus:
    """Current status of a user"""
    user_id: str
    is_muted: bool = False
    is_banned: bool = False
    mute_until: Optional[datetime] = None
    ban_until: Optional[datetime] = None
    violation_count: int = 0
    last_message_time: float = 0
    recent_messages: List[str] = None
    
    def __post_init__(self):
        if self.recent_messages is None:
            self.recent_messages = []


class ChatModerationPlugin:
    """Main chat moderation plugin class"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.setup_logging()
        self.users: Dict[str, UserStatus] = {}
        self.violations: List[UserViolation] = []
        self.load_config(config_file)
        self.load_profanity_filter()
        
    def setup_logging(self):
        """Setup logging for moderation actions"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('moderation.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('ChatModeration')
        
    def load_config(self, config_file: Optional[str] = None):
        """Load configuration from file or use defaults"""
        default_config = {
            "rules": {
                "profanity_filter": {
                    "enabled": True,
                    "action": "warn",
                    "threshold": 1,
                    "auto_escalate": True
                },
                "spam_detection": {
                    "enabled": True,
                    "action": "mute",
                    "threshold": 3,
                    "duration": 300,
                    "auto_escalate": False
                },
                "rate_limiting": {
                    "enabled": True,
                    "max_messages_per_minute": 10,
                    "action": "mute",
                    "duration": 60
                },
                "caps_abuse": {
                    "enabled": True,
                    "max_caps_percentage": 70,
                    "min_message_length": 10,
                    "action": "warn"
                }
            },
            "escalation": {
                "enabled": True,
                "warn_to_mute_threshold": 3,
                "mute_to_kick_threshold": 2,
                "kick_to_ban_threshold": 2
            }
        }
        
        if config_file:
            try:
                with open(config_file, 'r') as f:
                    self.config = json.load(f)
            except FileNotFoundError:
                self.logger.warning(f"Config file {config_file} not found, using defaults")
                self.config = default_config
        else:
            self.config = default_config
            
    def load_profanity_filter(self):
        """Load profanity words list"""
        # Basic profanity list - in production, this would be loaded from a file
        self.profanity_words = {
            'damn', 'shit', 'fuck', 'bitch', 'asshole', 'bastard',
            'crap', 'piss', 'hell', 'ass', 'slut', 'whore'
        }
        
        # Create regex patterns for variations
        self.profanity_patterns = []
        for word in self.profanity_words:
            # Handle character substitutions (e.g., @ for a, 3 for e)
            pattern = word.replace('a', '[a@]').replace('e', '[e3]').replace('i', '[i1]').replace('o', '[o0]')
            self.profanity_patterns.append(re.compile(rf'\b{pattern}\b', re.IGNORECASE))
            
    def get_user_status(self, user_id: str) -> UserStatus:
        """Get or create user status"""
        if user_id not in self.users:
            self.users[user_id] = UserStatus(user_id=user_id)
        return self.users[user_id]
        
    def check_profanity(self, message: str) -> Tuple[bool, List[str]]:
        """Check message for profanity"""
        if not self.config["rules"]["profanity_filter"]["enabled"]:
            return False, []
            
        found_words = []
        for pattern in self.profanity_patterns:
            matches = pattern.findall(message)
            found_words.extend(matches)
            
        return len(found_words) > 0, found_words
        
    def check_spam(self, user_id: str, message: str) -> bool:
        """Check for spam patterns"""
        if not self.config["rules"]["spam_detection"]["enabled"]:
            return False
            
        user = self.get_user_status(user_id)
        
        # Check for repetitive messages
        if message in user.recent_messages:
            return True
            
        # Check for excessive repetition within message
        words = message.split()
        if len(words) > 3:
            unique_words = set(words)
            if len(unique_words) / len(words) < 0.3:  # Less than 30% unique words
                return True
        
        # Check for very short repetitive messages
        if len(words) <= 3 and len(set(words)) == 1 and len(words) > 1:
            return True
                
        return False
        
    def check_rate_limit(self, user_id: str) -> bool:
        """Check if user is exceeding rate limits"""
        if not self.config["rules"]["rate_limiting"]["enabled"]:
            return False
            
        user = self.get_user_status(user_id)
        current_time = time.time()
        
        # For simplicity, use recent messages count as a proxy for rate limiting
        # In a real implementation, you'd track timestamps more precisely
        max_per_minute = self.config["rules"]["rate_limiting"]["max_messages_per_minute"]
        
        # Consider rate limiting if user has sent too many recent messages
        # This is a simplified check - a real implementation would track exact timestamps
        if len(user.recent_messages) >= max_per_minute:
            # Check if messages were sent within the last minute (approximation)
            time_since_last = current_time - user.last_message_time
            if time_since_last < 60:  # Less than a minute since last message
                return True
        
        return False
        
    def check_caps_abuse(self, message: str) -> bool:
        """Check for excessive caps usage"""
        if not self.config["rules"]["caps_abuse"]["enabled"]:
            return False
            
        min_length = self.config["rules"]["caps_abuse"]["min_message_length"]
        if len(message) < min_length:
            return False
            
        caps_count = sum(1 for c in message if c.isupper())
        caps_percentage = (caps_count / len(message)) * 100
        
        max_caps = self.config["rules"]["caps_abuse"]["max_caps_percentage"]
        return caps_percentage > max_caps
        
    def apply_moderation_action(self, user_id: str, action: ModerationAction, 
                              duration: int = 300, reason: str = "") -> bool:
        """Apply a moderation action to a user"""
        user = self.get_user_status(user_id)
        current_time = datetime.now()
        
        try:
            if action == ModerationAction.MUTE:
                user.is_muted = True
                user.mute_until = current_time + timedelta(seconds=duration)
                self.logger.info(f"User {user_id} muted for {duration} seconds. Reason: {reason}")
                
            elif action == ModerationAction.BAN:
                user.is_banned = True
                user.ban_until = current_time + timedelta(seconds=duration)
                self.logger.info(f"User {user_id} banned for {duration} seconds. Reason: {reason}")
                
            elif action == ModerationAction.KICK:
                # Kick is temporary - just log it
                self.logger.info(f"User {user_id} kicked. Reason: {reason}")
                
            elif action == ModerationAction.WARN:
                self.logger.info(f"User {user_id} warned. Reason: {reason}")
                
            return True
        except Exception as e:
            self.logger.error(f"Failed to apply action {action} to user {user_id}: {e}")
            return False
            
    def record_violation(self, user_id: str, violation_type: ViolationType, 
                        message: str, action_taken: ModerationAction):
        """Record a violation for tracking and escalation"""
        violation = UserViolation(
            user_id=user_id,
            violation_type=violation_type,
            message=message,
            timestamp=datetime.now(),
            action_taken=action_taken
        )
        
        self.violations.append(violation)
        user = self.get_user_status(user_id)
        user.violation_count += 1
        
        # Check for escalation
        if self.config["escalation"]["enabled"]:
            self.check_escalation(user_id)
            
    def check_escalation(self, user_id: str):
        """Check if user violations warrant escalation"""
        user = self.get_user_status(user_id)
        recent_violations = [v for v in self.violations 
                           if v.user_id == user_id and 
                           v.timestamp > datetime.now() - timedelta(hours=24)]
        
        warn_count = len([v for v in recent_violations if v.action_taken == ModerationAction.WARN])
        mute_count = len([v for v in recent_violations if v.action_taken == ModerationAction.MUTE])
        kick_count = len([v for v in recent_violations if v.action_taken == ModerationAction.KICK])
        
        if warn_count >= self.config["escalation"]["warn_to_mute_threshold"]:
            self.apply_moderation_action(user_id, ModerationAction.MUTE, 300, "Escalation: too many warnings")
        elif mute_count >= self.config["escalation"]["mute_to_kick_threshold"]:
            self.apply_moderation_action(user_id, ModerationAction.KICK, reason="Escalation: too many mutes")
        elif kick_count >= self.config["escalation"]["kick_to_ban_threshold"]:
            self.apply_moderation_action(user_id, ModerationAction.BAN, 3600, "Escalation: too many kicks")
            
    def moderate_message(self, user_id: str, message: str, channel_id: str = None) -> Dict:
        """Main method to moderate a message"""
        user = self.get_user_status(user_id)
        current_time = time.time()
        
        # Check if user is currently banned or muted
        if user.is_banned and user.ban_until and datetime.now() < user.ban_until:
            return {
                "allowed": False,
                "action": "rejected",
                "reason": "User is banned",
                "ban_until": user.ban_until.isoformat()
            }
            
        if user.is_muted and user.mute_until and datetime.now() < user.mute_until:
            return {
                "allowed": False,
                "action": "rejected", 
                "reason": "User is muted",
                "mute_until": user.mute_until.isoformat()
            }
            
        violations = []
        actions_taken = []
        
        # Check profanity
        has_profanity, profane_words = self.check_profanity(message)
        if has_profanity:
            violations.append(ViolationType.PROFANITY)
            action = ModerationAction.WARN
            self.apply_moderation_action(user_id, action, reason=f"Profanity detected: {profane_words}")
            self.record_violation(user_id, ViolationType.PROFANITY, message, action)
            actions_taken.append(action.value)
            
        # Check spam (only after we have some message history)
        if len(user.recent_messages) > 0 and self.check_spam(user_id, message):
            violations.append(ViolationType.SPAM)
            action = ModerationAction.MUTE
            self.apply_moderation_action(user_id, action, 300, "Spam detected")
            self.record_violation(user_id, ViolationType.SPAM, message, action)
            actions_taken.append(action.value)
            
        # Check rate limiting (only if user has sent multiple messages)
        if len(user.recent_messages) >= 3 and self.check_rate_limit(user_id):
            violations.append(ViolationType.RATE_LIMIT)
            action = ModerationAction.MUTE
            self.apply_moderation_action(user_id, action, 60, "Rate limit exceeded")
            self.record_violation(user_id, ViolationType.RATE_LIMIT, message, action)
            actions_taken.append(action.value)
            
        # Check caps abuse
        if self.check_caps_abuse(message):
            violations.append(ViolationType.CAPS_ABUSE)
            action = ModerationAction.WARN
            self.apply_moderation_action(user_id, action, reason="Excessive caps usage")
            self.record_violation(user_id, ViolationType.CAPS_ABUSE, message, action)
            actions_taken.append(action.value)
            
        # Update user message tracking AFTER checks
        user.last_message_time = current_time
        user.recent_messages.append(message)
        if len(user.recent_messages) > 10:  # Keep only last 10 messages
            user.recent_messages.pop(0)
            
        # Determine if message should be allowed
        should_delete = any(v in [ViolationType.PROFANITY, ViolationType.SPAM] for v in violations)
        allowed = len(violations) == 0 or not should_delete
        
        return {
            "allowed": allowed,
            "violations": [v.value for v in violations],
            "actions_taken": actions_taken,
            "user_status": asdict(user)
        }
        
    def get_user_violations(self, user_id: str, days: int = 7) -> List[Dict]:
        """Get recent violations for a user"""
        cutoff = datetime.now() - timedelta(days=days)
        user_violations = [v for v in self.violations 
                          if v.user_id == user_id and v.timestamp > cutoff]
        
        return [{
            'user_id': v.user_id,
            'violation_type': v.violation_type.value,  # Convert enum to string
            'message': v.message,
            'timestamp': v.timestamp.isoformat(),
            'action_taken': v.action_taken.value,  # Convert enum to string
            'moderator': v.moderator
        } for v in user_violations]
        
    def cleanup_expired_punishments(self):
        """Clean up expired mutes and bans"""
        current_time = datetime.now()
        
        for user in self.users.values():
            if user.is_muted and user.mute_until and current_time >= user.mute_until:
                user.is_muted = False
                user.mute_until = None
                self.logger.info(f"Mute expired for user {user.user_id}")
                
            if user.is_banned and user.ban_until and current_time >= user.ban_until:
                user.is_banned = False
                user.ban_until = None
                self.logger.info(f"Ban expired for user {user.user_id}")
                
    def get_moderation_stats(self) -> Dict:
        """Get moderation statistics"""
        total_violations = len(self.violations)
        violation_types = {}
        
        for violation in self.violations:
            vtype = violation.violation_type.value
            violation_types[vtype] = violation_types.get(vtype, 0) + 1
            
        active_mutes = len([u for u in self.users.values() if u.is_muted])
        active_bans = len([u for u in self.users.values() if u.is_banned])
        
        return {
            "total_violations": total_violations,
            "violation_types": violation_types,
            "active_mutes": active_mutes,
            "active_bans": active_bans,
            "total_users_tracked": len(self.users)
        }


# Example usage and testing
if __name__ == "__main__":
    # Initialize the plugin
    moderator = ChatModerationPlugin()
    
    # Test messages
    test_messages = [
        ("user1", "Hello everyone!"),
        ("user2", "This is a damn test message"),
        ("user3", "HELLO EVERYONE I AM SHOUTING"),
        ("user4", "spam spam spam spam spam"),
        ("user5", "Normal message here")
    ]
    
    print("=== Chat Moderation Plugin Test ===")
    for user_id, message in test_messages:
        result = moderator.moderate_message(user_id, message)
        print(f"\nUser: {user_id}")
        print(f"Message: {message}")
        print(f"Result: {result}")
        
    print("\n=== Moderation Statistics ===")
    stats = moderator.get_moderation_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")