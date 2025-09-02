#!/usr/bin/env python3
"""
Simple test script to verify the chat moderation plugin functionality
"""

from chat_moderation_plugin import ChatModerationPlugin
from moderation_api import ModerationAPI
import json

def test_clean_functionality():
    """Test with a fresh instance and clean messages"""
    print("=== Testing Chat Moderation Plugin ===\n")
    
    # Create a fresh instance
    api = ModerationAPI()
    
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
    
    # Test 3: Repetitive spam (should detect)
    print("Test 3: Repetitive spam")
    result = api.moderate_message("user3", "buy now buy now buy now buy now")
    print(f"Message: 'buy now buy now buy now buy now'")
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

if __name__ == "__main__":
    test_clean_functionality()