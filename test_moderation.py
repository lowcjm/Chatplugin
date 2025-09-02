"""
Unit tests for the Chat Moderation Plugin

Run with: python -m pytest test_moderation.py -v
"""

import unittest
import tempfile
import json
import os
from datetime import datetime, timedelta
from chat_moderation_plugin import ChatModerationPlugin, ModerationAction, ViolationType
from moderation_api import ModerationAPI


class TestChatModerationPlugin(unittest.TestCase):
    """Test cases for the core moderation plugin"""
    
    def setUp(self):
        """Set up test environment"""
        self.plugin = ChatModerationPlugin()
        
    def test_profanity_detection(self):
        """Test profanity filter functionality"""
        # Test basic profanity
        has_profanity, words = self.plugin.check_profanity("This is a damn test")
        self.assertTrue(has_profanity)
        self.assertIn("damn", words)
        
        # Test clean message
        has_profanity, words = self.plugin.check_profanity("This is a clean message")
        self.assertFalse(has_profanity)
        self.assertEqual(words, [])
        
        # Test character substitution
        has_profanity, words = self.plugin.check_profanity("This is d@mn annoying")
        self.assertTrue(has_profanity)
        
    def test_spam_detection(self):
        """Test spam detection"""
        user_id = "test_user"
        
        # Add some messages to history
        user = self.plugin.get_user_status(user_id)
        user.recent_messages = ["hello", "world", "test"]
        
        # Test repetitive message
        is_spam = self.plugin.check_spam(user_id, "hello")
        self.assertTrue(is_spam)
        
        # Test unique message
        is_spam = self.plugin.check_spam(user_id, "unique message here")
        self.assertFalse(is_spam)
        
        # Test repetitive words within message
        is_spam = self.plugin.check_spam(user_id, "spam spam spam spam spam")
        self.assertTrue(is_spam)
        
    def test_caps_abuse_detection(self):
        """Test caps abuse detection"""
        # Test excessive caps
        is_abuse = self.plugin.check_caps_abuse("THIS IS ALL CAPS MESSAGE")
        self.assertTrue(is_abuse)
        
        # Test normal message
        is_abuse = self.plugin.check_caps_abuse("This is a normal message")
        self.assertFalse(is_abuse)
        
        # Test short message (should be ignored)
        is_abuse = self.plugin.check_caps_abuse("OK")
        self.assertFalse(is_abuse)
        
    def test_user_status_creation(self):
        """Test user status creation and retrieval"""
        user_id = "new_user"
        
        # First access should create user
        user = self.plugin.get_user_status(user_id)
        self.assertEqual(user.user_id, user_id)
        self.assertFalse(user.is_muted)
        self.assertFalse(user.is_banned)
        
        # Second access should return same user
        user2 = self.plugin.get_user_status(user_id)
        self.assertEqual(user, user2)
        
    def test_moderation_actions(self):
        """Test applying moderation actions"""
        user_id = "test_user"
        
        # Test mute
        success = self.plugin.apply_moderation_action(
            user_id, ModerationAction.MUTE, 300, "Test mute"
        )
        self.assertTrue(success)
        
        user = self.plugin.get_user_status(user_id)
        self.assertTrue(user.is_muted)
        self.assertIsNotNone(user.mute_until)
        
        # Test ban
        success = self.plugin.apply_moderation_action(
            user_id, ModerationAction.BAN, 3600, "Test ban"
        )
        self.assertTrue(success)
        
        user = self.plugin.get_user_status(user_id)
        self.assertTrue(user.is_banned)
        self.assertIsNotNone(user.ban_until)
        
    def test_message_moderation(self):
        """Test complete message moderation workflow"""
        user_id = "test_user"
        
        # Test clean message
        result = self.plugin.moderate_message(user_id, "Hello everyone!")
        self.assertTrue(result["allowed"])
        self.assertEqual(result["violations"], [])
        
        # Test profanity
        result = self.plugin.moderate_message(user_id, "This is damn annoying")
        self.assertEqual(result["violations"], ["profanity"])
        self.assertIn("warn", result["actions_taken"])
        
        # Test spam
        user = self.plugin.get_user_status(user_id)
        user.recent_messages = ["spam message"]
        result = self.plugin.moderate_message(user_id, "spam message")
        self.assertIn("spam", result["violations"])
        
    def test_violation_recording(self):
        """Test violation recording and history"""
        user_id = "test_user"
        
        # Record a violation
        self.plugin.record_violation(
            user_id, ViolationType.PROFANITY, "test message", ModerationAction.WARN
        )
        
        # Check violation was recorded
        violations = self.plugin.get_user_violations(user_id)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0]["violation_type"], "profanity")
        
        # Check user violation count
        user = self.plugin.get_user_status(user_id)
        self.assertEqual(user.violation_count, 1)
        
    def test_cleanup_expired_punishments(self):
        """Test cleanup of expired mutes and bans"""
        user_id = "test_user"
        user = self.plugin.get_user_status(user_id)
        
        # Set expired mute
        user.is_muted = True
        user.mute_until = datetime.now() - timedelta(seconds=1)
        
        # Set expired ban
        user.is_banned = True
        user.ban_until = datetime.now() - timedelta(seconds=1)
        
        # Run cleanup
        self.plugin.cleanup_expired_punishments()
        
        # Check punishments were removed
        self.assertFalse(user.is_muted)
        self.assertFalse(user.is_banned)
        self.assertIsNone(user.mute_until)
        self.assertIsNone(user.ban_until)
        
    def test_statistics(self):
        """Test moderation statistics"""
        # Add some test data
        self.plugin.record_violation(
            "user1", ViolationType.PROFANITY, "test", ModerationAction.WARN
        )
        self.plugin.record_violation(
            "user2", ViolationType.SPAM, "test", ModerationAction.MUTE
        )
        
        stats = self.plugin.get_moderation_stats()
        
        self.assertEqual(stats["total_violations"], 2)
        self.assertIn("profanity", stats["violation_types"])
        self.assertIn("spam", stats["violation_types"])


class TestModerationAPI(unittest.TestCase):
    """Test cases for the API wrapper"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary config file
        self.config_data = {
            "rules": {
                "profanity_filter": {"enabled": True, "action": "warn"},
                "spam_detection": {"enabled": True, "action": "mute"},
                "rate_limiting": {"enabled": True, "max_messages_per_minute": 5},
                "caps_abuse": {"enabled": True, "max_caps_percentage": 50, "min_message_length": 10}
            },
            "whitelist": {
                "enabled": True,
                "moderator_roles": ["admin", "moderator"]
            },
            "escalation": {"enabled": True}
        }
        
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(self.config_data, self.temp_config)
        self.temp_config.close()
        
        self.api = ModerationAPI(self.temp_config.name)
        
    def tearDown(self):
        """Clean up test environment"""
        os.unlink(self.temp_config.name)
        
    def test_api_message_moderation(self):
        """Test API message moderation"""
        # Test normal message
        result = self.api.moderate_message("user1", "Hello world!")
        self.assertTrue(result["allowed"])
        
        # Test with moderator role (should bypass)
        result = self.api.moderate_message(
            "user2", "This has profanity damn", user_roles=["admin"]
        )
        self.assertTrue(result["allowed"])
        self.assertEqual(result["reason"], "User has bypass permissions")
        
    def test_api_manual_actions(self):
        """Test manual moderation actions via API"""
        user_id = "test_user"
        
        # Test valid action
        success = self.api.apply_manual_action(
            user_id, "mute", 300, "Manual test", "moderator1"
        )
        self.assertTrue(success)
        
        # Test invalid action
        success = self.api.apply_manual_action(
            user_id, "invalid_action", 300, "Test"
        )
        self.assertFalse(success)
        
    def test_api_user_status(self):
        """Test getting user status via API"""
        user_id = "test_user"
        
        # Apply a mute first
        self.api.apply_manual_action(user_id, "mute", 300, "Test")
        
        # Get status
        status = self.api.get_user_status(user_id)
        self.assertEqual(status["user_id"], user_id)
        self.assertTrue(status["is_muted"])
        
    def test_api_config_updates(self):
        """Test dynamic configuration updates"""
        updates = {
            "rules": {
                "profanity_filter": {
                    "enabled": False
                }
            }
        }
        
        success = self.api.update_config(updates)
        self.assertTrue(success)
        self.assertFalse(self.api.plugin.config["rules"]["profanity_filter"]["enabled"])
        
    def test_api_profanity_management(self):
        """Test adding/removing profanity words via API"""
        # Add words
        success = self.api.add_profanity_words(["badword1", "badword2"])
        self.assertTrue(success)
        self.assertIn("badword1", self.api.plugin.profanity_words)
        
        # Remove words
        success = self.api.remove_profanity_words(["badword1"])
        self.assertTrue(success)
        self.assertNotIn("badword1", self.api.plugin.profanity_words)
        
    def test_api_whitelist_management(self):
        """Test whitelist management via API"""
        user_id = "trusted_user"
        
        # Add to whitelist
        success = self.api.whitelist_user(user_id)
        self.assertTrue(success)
        
        # Try to add again (should return False)
        success = self.api.whitelist_user(user_id)
        self.assertFalse(success)
        
        # Remove from whitelist
        success = self.api.remove_from_whitelist(user_id)
        self.assertTrue(success)


class TestModerationIntegration(unittest.TestCase):
    """Integration tests for the moderation system"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.api = ModerationAPI()
        
    def test_escalation_workflow(self):
        """Test the complete escalation workflow"""
        user_id = "escalation_user"
        
        # Generate warnings to trigger escalation
        for i in range(4):  # More than the threshold
            result = self.api.moderate_message(user_id, f"This is damn message {i}")
            
        # Check that user was escalated to mute
        user_status = self.api.get_user_status(user_id)
        self.assertTrue(user_status["is_muted"])
        
    def test_rate_limiting_workflow(self):
        """Test rate limiting enforcement"""
        user_id = "rate_limit_user"
        
        # Send many messages quickly
        results = []
        for i in range(15):  # More than the limit
            result = self.api.moderate_message(user_id, f"Message {i}")
            results.append(result)
            
        # Later messages should be rate limited
        rate_limited = any("rate_limit" in r.get("violations", []) for r in results)
        self.assertTrue(rate_limited)
        
    def test_multiple_violations(self):
        """Test handling multiple violations in one message"""
        user_id = "multi_violation_user"
        
        # Message with multiple issues
        result = self.api.moderate_message(
            user_id, "THIS IS A DAMN CAPS SPAM SPAM SPAM MESSAGE"
        )
        
        # Should detect multiple violations
        violations = result.get("violations", [])
        self.assertGreater(len(violations), 1)


if __name__ == "__main__":
    # Run all tests
    unittest.main(verbosity=2)