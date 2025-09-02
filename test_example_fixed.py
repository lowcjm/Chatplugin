#!/usr/bin/env python3
"""
Simple test script with temporary config to verify the chat moderation plugin functionality
"""

from chat_moderation_plugin import ChatModerationPlugin
from moderation_api import ModerationAPI
import json
import tempfile
import os

def test_clean_functionality():
    """Test with a fresh instance and clean messages"""
    print("=== Testing Chat Moderation Plugin ===\n")
    
    # Create temp config
    config_data = {
        "rules": {
            "profanity_filter": {
                "enabled": True,
                "action": "warn",
                "threshold": 1
            },
            "spam_detection": {
                "enabled": True,
                "action": "mute",
                "threshold": 3,
                "duration": 300
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
        },
        "whitelist": {
            "enabled": True,
            "moderator_roles": ["admin", "moderator"],
            "bypass_users": []
        }
    }
    
    # Create temporary config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        config_file = f.name
    
    try:
        # Create a fresh instance with proper config
        api = ModerationAPI(config_file)
        
        # Test 1: Clean message (should pass)
        print("Test 1: Clean message")
        result = api.moderate_message("user1", "Hello everyone, how are you today?")
        print(f"Message: 'Hello everyone, how are you today?'")
        print(f"Allowed: {result['allowed']}")
        print(f"Violations: {result['violations']}")
        print(f"Actions: {result['actions_taken']}")
        print()
        
        # Test 2: Profanity (should detect)
        print("Test 2: Profanity detection")
        result = api.moderate_message("user2", "This is a damn annoying test")
        print(f"Message: 'This is a damn annoying test'")
        print(f"Allowed: {result['allowed']}")
        print(f"Violations: {result['violations']}")
        print(f"Actions: {result['actions_taken']}")
        print()
        
        # Test 3: Repetitive spam (should detect after adding to history)
        print("Test 3: Repetitive spam")
        # First send a message, then repeat it
        api.moderate_message("user3", "buy now")
        result = api.moderate_message("user3", "buy now")  # Should detect as spam
        print(f"Message: 'buy now' (repeated)")
        print(f"Allowed: {result['allowed']}")
        print(f"Violations: {result['violations']}")
        print(f"Actions: {result['actions_taken']}")
        print()
        
        # Test 4: Caps abuse (should detect)
        print("Test 4: Caps abuse")
        result = api.moderate_message("user4", "THIS IS ALL CAPS AND VERY ANNOYING MESSAGE")
        print(f"Message: 'THIS IS ALL CAPS AND VERY ANNOYING MESSAGE'")
        print(f"Allowed: {result['allowed']}")
        print(f"Violations: {result['violations']}")
        print(f"Actions: {result['actions_taken']}")
        print()
        
        # Test 5: Another clean message (should pass)
        print("Test 5: Another clean message")
        result = api.moderate_message("user5", "Thanks for the help everyone!")
        print(f"Message: 'Thanks for the help everyone!'")
        print(f"Allowed: {result['allowed']}")
        print(f"Violations: {result['violations']}")
        print(f"Actions: {result['actions_taken']}")
        print()
        
        # Test 6: Bypass with moderator role
        print("Test 6: Moderator bypass")
        result = api.moderate_message("mod1", "This damn message should be allowed", user_roles=["admin"])
        print(f"Message: 'This damn message should be allowed' (admin role)")
        print(f"Allowed: {result['allowed']}")
        print(f"Reason: {result.get('reason', 'N/A')}")
        print()
        
        # Get overall stats
        print("=== Final Statistics ===")
        stats = api.get_stats()
        for key, value in stats.items():
            print(f"{key}: {value}")
            
    finally:
        # Clean up temp file
        os.unlink(config_file)

if __name__ == "__main__":
    test_clean_functionality()