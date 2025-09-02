# Chat Moderation Plugin

A comprehensive, platform-agnostic chat moderation system that provides automated content filtering, user management, and configurable moderation rules. This plugin can be easily integrated into Discord bots, Slack apps, web chat systems, and other chat platforms.

## Features

### Core Moderation Features
- **Profanity Filtering**: Detects and filters inappropriate language with customizable word lists
- **Spam Detection**: Identifies repetitive messages and spam patterns
- **Rate Limiting**: Prevents message flooding with configurable limits
- **Caps Abuse Detection**: Detects excessive use of capital letters
- **User Management**: Automated muting, kicking, and banning capabilities
- **Escalation System**: Automatic escalation of repeated violations

### Advanced Features
- **Configurable Rules**: Fully customizable moderation rules and thresholds
- **Multiple Action Types**: Warn, mute, kick, ban, and delete message actions
- **Violation Tracking**: Complete history of user violations with timestamps
- **Whitelist Support**: Bypass moderation for trusted users and roles
- **Real-time Statistics**: Monitor moderation activity and trends
- **Plugin API**: Easy integration with existing chat platforms

## Quick Start

### Installation

1. Clone this repository:
```bash
git clone https://github.com/lowcjm/Chatplugin.git
cd Chatplugin
```

2. Install dependencies (optional, for specific integrations):
```bash
pip install -r requirements.txt
```

### Basic Usage

```python
from moderation_api import ModerationAPI

# Initialize the moderation system
moderator = ModerationAPI()

# Moderate a message
result = moderator.moderate_message(
    user_id="user123",
    message="Hello everyone!",
    user_roles=["member"]
)

print(f"Message allowed: {result['allowed']}")
print(f"Violations: {result['violations']}")
```

### Configuration

The system uses a JSON configuration file (`config.json`) to customize behavior:

```json
{
  "rules": {
    "profanity_filter": {
      "enabled": true,
      "action": "warn",
      "threshold": 1
    },
    "spam_detection": {
      "enabled": true,
      "action": "mute",
      "duration": 300
    },
    "rate_limiting": {
      "enabled": true,
      "max_messages_per_minute": 10
    }
  }
}
```

## Platform Integrations

### Discord Bot Integration

```python
from examples.discord_integration import DiscordModerationBot

# Set your bot token as environment variable
# DISCORD_BOT_TOKEN=your_token_here

bot = DiscordModerationBot()
bot.run()
```

### Web Interface

```python
from examples.web_interface import app

# Start the web interface
app.run(debug=True, port=5000)
```

Access the web interface at `http://localhost:5000` for:
- Real-time moderation dashboard
- User management interface
- Configuration management
- Message testing tools

## API Reference

### Core Classes

#### `ChatModerationPlugin`
The main moderation engine that handles all rule checking and enforcement.

```python
from chat_moderation_plugin import ChatModerationPlugin

plugin = ChatModerationPlugin("config.json")
result = plugin.moderate_message("user_id", "message content")
```

#### `ModerationAPI`
High-level API wrapper for easy integration.

```python
from moderation_api import ModerationAPI

api = ModerationAPI()

# Moderate message
result = api.moderate_message("user_id", "message")

# Apply manual action
api.apply_manual_action("user_id", "mute", 300, "Spam")

# Get user status
status = api.get_user_status("user_id")

# Get statistics
stats = api.get_stats()
```

### Key Methods

#### Message Moderation
```python
moderate_message(user_id, message, channel_id=None, user_roles=None)
```
Returns a dictionary with moderation results including violations detected and actions taken.

#### User Management
```python
apply_manual_action(user_id, action, duration=300, reason="", moderator_id=None)
get_user_status(user_id)
get_violations(user_id=None, days=7)
```

#### Configuration
```python
update_config(config_updates)
add_profanity_words(words)
remove_profanity_words(words)
whitelist_user(user_id)
```

## Configuration Options

### Profanity Filter
```json
{
  "profanity_filter": {
    "enabled": true,
    "action": "warn",
    "threshold": 1,
    "auto_escalate": true
  }
}
```

### Spam Detection
```json
{
  "spam_detection": {
    "enabled": true,
    "action": "mute",
    "threshold": 3,
    "duration": 300,
    "repetitive_threshold": 0.3
  }
}
```

### Rate Limiting
```json
{
  "rate_limiting": {
    "enabled": true,
    "max_messages_per_minute": 10,
    "action": "mute",
    "duration": 60
  }
}
```

### Escalation System
```json
{
  "escalation": {
    "enabled": true,
    "warn_to_mute_threshold": 3,
    "mute_to_kick_threshold": 2,
    "kick_to_ban_threshold": 2
  }
}
```

## Testing

Run the test suite to verify functionality:

```bash
python -m pytest test_moderation.py -v
```

Test specific features:
```bash
python chat_moderation_plugin.py  # Run built-in tests
python moderation_api.py          # Test API functionality
```

## Examples

### Discord Bot Commands
- `!modstats` - View moderation statistics
- `!userinfo @user` - Get user moderation info
- `!modmute @user 300 reason` - Manually mute a user
- `!modunmute @user` - Unmute a user

### Web Interface Features
- Real-time moderation dashboard
- User violation history
- Configuration management
- Message testing tools
- Statistics and analytics

## Logging

The system provides comprehensive logging of all moderation actions:

```python
# Logs are written to moderation.log by default
# Configure logging in config.json:
{
  "logging": {
    "enabled": true,
    "log_file": "moderation.log",
    "log_level": "INFO",
    "retention_days": 30
  }
}
```

## Security Considerations

- Store sensitive configuration (API tokens, webhooks) in environment variables
- Regularly update profanity word lists
- Review and audit moderation logs
- Implement proper access controls for administrative functions
- Use HTTPS for web interfaces in production

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or contributions:
- Create an issue on GitHub
- Check the documentation and examples
- Review the test cases for usage patterns

## Changelog

### v1.0.0
- Initial release with core moderation features
- Discord bot integration
- Web interface
- Comprehensive test suite
- API documentation