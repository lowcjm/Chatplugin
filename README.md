# ChatPlugin - Minecraft 1.21+ Chat Moderation Plugin

A comprehensive chat moderation plugin for Minecraft 1.21+ servers with advanced filtering, automated punishments, and LiteBans integration.

## Features

### Chat Control Commands
- `/mutechat` - Mute or unmute global chat
- `/clearchat` - Clear chat history for all players
- `/chatmoderation` - Toggle moderation system on/off
- `/describeimage` - Manually describe an image from URL

### Advanced Content Filtering
- **Profanity Filter**: Automatically replaces inappropriate words with asterisks (`****`)
- **Severe Violations**: Detects racist, homophobic, and other offensive language → Temporary mutes
- **Critical Violations**: Detects IP addresses and doxing attempts → Permanent mutes

### Image Description System
- **Automatic Detection**: Recognizes image URLs in chat messages (jpg, png, gif, webp, svg, etc.)
- **Smart Descriptions**: Generates contextual descriptions based on URL patterns and content
- **Manual Command**: `/describeimage <url>` command for on-demand image analysis
- **Integration**: Works seamlessly with existing chat filtering and moderation

### Punishment System
- **LiteBans Integration**: Primary punishment system when available
- **Internal Fallback**: Built-in punishment system when LiteBans isn't installed
- **Configurable Duration**: Customizable mute durations for different violation types
- **Automatic Cleanup**: Expired mutes are automatically removed

## Installation

### Requirements
- Minecraft Server 1.21+
- Java 17+
- Spigot/Paper server
- LiteBans plugin (optional but recommended)

### Setup Instructions

1. **Download Dependencies** (in production environment):
   ```xml
   <!-- Add to your pom.xml -->
   <repositories>
       <repository>
           <id>papermc</id>
           <url>https://repo.papermc.io/repository/maven-public/</url>
       </repository>
   </repositories>
   
   <dependencies>
       <dependency>
           <groupId>io.papermc.paper</groupId>
           <artifactId>paper-api</artifactId>
           <version>1.21-R0.1-SNAPSHOT</version>
           <scope>provided</scope>
       </dependency>
   </dependencies>
   ```

2. **Build the Plugin**:
   ```bash
   mvn clean package
   ```

3. **Install**:
   - Place `chatplugin-1.0.0.jar` in your server's `plugins/` folder
   - Restart the server
   - Configure the plugin (see Configuration section)

## Configuration

The plugin generates a `config.yml` file with the following structure:

```yaml
# General Settings
chat-moderation-enabled: true
use-litebans: true

# Chat Settings
chat-muted: false
mute-message: "&cChat is currently muted by an administrator."
unmute-message: "&aChat has been unmuted."
clear-message: "&eChat has been cleared by an administrator."

# Filter Settings
profanity-filter:
  enabled: true
  replacement-character: "*"
  words:
    - "damn"
    - "hell"
    - "crap"
    # Add more words as needed

# Severe violations (results in temporary mute)
severe-violations:
  enabled: true
  mute-duration: 86400 # 24 hours in seconds
  words:
    - "racist"
    - "homophobic"
    # Add more severe words as needed

# Critical violations (results in permanent mute)
critical-violations:
  enabled: true
  detection-patterns:
    ip-addresses: true
    doxing-keywords: true
  keywords:
    - "doxx"
    - "dox"
    - "address"
    # Add more doxing-related keywords
```

## Commands

| Command | Permission | Description |
|---------|------------|-------------|
| `/mutechat [mute\|unmute\|status]` | `chatplugin.mutechat` | Control global chat muting |
| `/clearchat` | `chatplugin.clearchat` | Clear chat for all players |
| `/chatmoderation [on\|off\|status\|reload]` | `chatplugin.toggle` | Manage moderation system |
| `/describeimage <image_url>` | `chatplugin.describe` | Manually describe an image from URL |

### Command Examples

```
# Mute global chat
/mutechat mute

# Unmute global chat
/mutechat unmute

# Check chat status
/mutechat status

# Clear chat
/clearchat

# Enable moderation
/chatmoderation on

# Check moderation status
/chatmoderation status

# Reload configuration
/chatmoderation reload

# Describe an image
/describeimage https://example.com/photo.jpg
```

## Permissions

| Permission | Description | Default |
|------------|-------------|---------|
| `chatplugin.*` | All plugin permissions | `op` |
| `chatplugin.mutechat` | Use mute/unmute commands | `op` |
| `chatplugin.clearchat` | Use clear chat command | `op` |
| `chatplugin.toggle` | Toggle moderation system | `op` |
| `chatplugin.bypass` | Bypass chat restrictions | `op` |
| `chatplugin.describe` | Use image description command | `true` |

## How It Works

### Chat Processing Flow
1. **Permission Check**: Verify player can send messages
2. **Global Mute Check**: Block if chat is globally muted
3. **Individual Mute Check**: Block if player is individually muted
4. **Content Filtering**: Analyze message content
5. **Image Detection**: Check for image URLs and generate descriptions
6. **Action Execution**: Filter, warn, or punish based on content

### Violation Levels
- **Profanity**: Message filtered with `****`, player warned
- **Severe**: Message blocked, player temporarily muted
- **Critical**: Message blocked, player permanently muted

### LiteBans Integration
When LiteBans is detected, the plugin:
- Uses LiteBans for punishment management
- Executes mute commands through LiteBans
- Falls back to internal system if LiteBans fails

## Testing

Run the demo to see the plugin in action:

```bash
java -cp target/chatplugin-1.0.0.jar com.lowcjm.chatplugin.demo.ChatPluginDemo
```

This demonstrates:
- Chat muting/unmuting
- Message filtering
- Violation detection
- Punishment application
- Image URL detection and description
- Manual image description commands

## Customization

### Adding Custom Filter Words
Edit `config.yml` and add words to the appropriate sections:

```yaml
profanity-filter:
  words:
    - "your-word-here"

severe-violations:
  words:
    - "severe-word-here"

critical-violations:
  keywords:
    - "critical-keyword-here"

# Image Description Settings
image-description:
  enabled: true
  replace-with-description: false  # true to replace URLs, false to append descriptions
  notify-player: true              # notify player when image is described
```

### Adjusting Mute Durations
```yaml
severe-violations:
  mute-duration: 86400  # 24 hours in seconds
```

### Customizing Messages
All player-facing messages can be customized in the `messages` section:

```yaml
messages:
  profanity-filtered: "&eYour message was filtered."
  severe-violation: "&cYou have been muted for %duration%"
  critical-violation: "&4You have been permanently muted."
  image-described: "&7[Image described: %description%]"
```

## Image Description Feature

The plugin automatically detects image URLs in chat messages and provides intelligent descriptions. This helps improve accessibility and context for all players.

### Supported Image Formats
- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- WebP (.webp)
- SVG (.svg)
- BMP (.bmp)

### How It Works
1. **Automatic Detection**: When a player sends a message with an image URL, the plugin automatically detects it
2. **Smart Analysis**: The system analyzes the URL and generates contextual descriptions
3. **Chat Integration**: Descriptions are added to the chat message or sent as notifications
4. **Manual Command**: Players can use `/describeimage <url>` for on-demand descriptions

### Configuration Options
```yaml
image-description:
  enabled: true                    # Enable/disable the feature
  replace-with-description: false  # Replace URL with description or append
  notify-player: true              # Send description notification to player
```

### Example Usage
```
Player: "Check out this photo: https://example.com/sunset.jpg"
Result: "Check out this photo: https://example.com/sunset.jpg [Image: A beautiful sunset/sunrise scene]"
Player receives: "[Image described: A beautiful sunset/sunrise scene]"
```

## Development Notes

This plugin is designed for production use but includes demonstration code for testing without a full Minecraft server environment. In production:

1. Remove demo classes from the `demo` package
2. Ensure proper Bukkit/Paper API dependencies
3. Test thoroughly on your server version
4. Configure word lists appropriately for your community

## Support

For issues, feature requests, or contributions, please refer to the project repository.

## License

This project is provided as-is for educational and production use.