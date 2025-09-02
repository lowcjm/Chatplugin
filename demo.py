#!/usr/bin/env python3
"""
Final demonstration of the Chat Moderation Plugin functionality
"""

import json
import tempfile
import os
from moderation_api import ModerationAPI

def demo_chat_moderation():
    """Comprehensive demonstration of all features"""
    print("🔧 CHAT MODERATION PLUGIN DEMONSTRATION 🔧")
    print("=" * 50)
    
    # Create demo config
    config_data = {
        "rules": {
            "profanity_filter": {"enabled": True, "action": "warn"},
            "spam_detection": {"enabled": True, "action": "mute"},
            "rate_limiting": {"enabled": True, "max_messages_per_minute": 10},
            "caps_abuse": {"enabled": True, "max_caps_percentage": 70, "min_message_length": 10}
        },
        "escalation": {
            "enabled": True, 
            "warn_to_mute_threshold": 3,
            "mute_to_kick_threshold": 2,
            "kick_to_ban_threshold": 2
        },
        "whitelist": {"enabled": True, "moderator_roles": ["admin", "moderator"]}
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        config_file = f.name
    
    try:
        api = ModerationAPI(config_file)
        
        print("\n📋 TESTING CORE FEATURES:")
        print("-" * 30)
        
        # 1. Clean messages
        print("\n✅ Clean Message Test:")
        result = api.moderate_message("alice", "Hello everyone! How are you today?")
        print(f"   Message: 'Hello everyone! How are you today?'")
        print(f"   Allowed: {result['allowed']} | Violations: {result['violations']}")
        
        # 2. Profanity detection  
        print("\n🚫 Profanity Detection:")
        result = api.moderate_message("bob", "This damn thing is broken!")
        print(f"   Message: 'This damn thing is broken!'")
        print(f"   Allowed: {result['allowed']} | Violations: {result['violations']}")
        
        # 3. Spam detection
        print("\n🔁 Spam Detection:")
        api.moderate_message("charlie", "Check this out!")  # First message
        result = api.moderate_message("charlie", "Check this out!")  # Repeat = spam
        print(f"   Message: 'Check this out!' (repeated)")
        print(f"   Allowed: {result['allowed']} | Violations: {result['violations']}")
        
        # 4. Caps abuse
        print("\n📢 Caps Abuse Detection:")
        result = api.moderate_message("david", "THIS IS REALLY ANNOYING WHEN PEOPLE TYPE LIKE THIS")
        print(f"   Message: 'THIS IS REALLY ANNOYING...'")
        print(f"   Allowed: {result['allowed']} | Violations: {result['violations']}")
        
        # 5. Moderator bypass
        print("\n👮 Moderator Bypass:")
        result = api.moderate_message("admin_user", "This damn message is allowed", user_roles=["admin"])
        print(f"   Message: 'This damn message is allowed' (admin)")
        print(f"   Allowed: {result['allowed']} | Reason: {result.get('reason', 'N/A')}")
        
        print("\n📊 MANAGEMENT FEATURES:")
        print("-" * 30)
        
        # 6. Manual actions
        print("\n⚡ Manual Moderation:")
        success = api.apply_manual_action("troublemaker", "mute", 300, "Spamming chat", "moderator1")
        print(f"   Manual mute applied: {success}")
        
        # 7. User status
        print("\n👤 User Status Check:")
        status = api.get_user_status("troublemaker")
        print(f"   User 'troublemaker' muted: {status['is_muted']}")
        
        # 8. Statistics
        print("\n📈 System Statistics:")
        stats = api.get_stats()
        print(f"   Total violations: {stats['total_violations']}")
        print(f"   Active mutes: {stats['active_mutes']}")
        print(f"   Users tracked: {stats['total_users_tracked']}")
        
        # 9. Violation history
        print("\n📝 Violation History:")
        violations = api.get_violations(days=1)
        print(f"   Recent violations: {len(violations)} found")
        for v in violations[:3]:  # Show first 3
            print(f"   - {v['user_id']}: {v['violation_type']}")
        
        # 10. Configuration management
        print("\n⚙️  Dynamic Configuration:")
        config_update = {"rules": {"profanity_filter": {"enabled": False}}}
        success = api.update_config(config_update)
        print(f"   Config updated: {success}")
        
        # Test that profanity filter is now disabled
        result = api.moderate_message("test_user", "This damn test should pass now")
        print(f"   Profanity now ignored: {result['allowed']}")
        
        print("\n🎉 DEMONSTRATION COMPLETE!")
        print("=" * 50)
        print("\nThe Chat Moderation Plugin is fully functional with:")
        print("✅ Automated content filtering")
        print("✅ User management and escalation")
        print("✅ Real-time statistics and monitoring")
        print("✅ Platform integration capabilities")
        print("✅ Web interface and Discord bot examples")
        print("✅ Comprehensive API for custom integrations")
        
    finally:
        os.unlink(config_file)

if __name__ == "__main__":
    demo_chat_moderation()