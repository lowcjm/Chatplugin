package com.lowcjm.chatplugin.commands;

import com.lowcjm.chatplugin.ChatPlugin;
import com.lowcjm.chatplugin.commands.MuteChatCommand.CommandSender;

import java.util.Arrays;
import java.util.List;

/**
 * Command handler for /chatmoderation
 * In production, this would implement CommandExecutor and TabCompleter from Bukkit API
 */
public class ChatModerationCommand {
    
    private final ChatPlugin plugin;
    
    public ChatModerationCommand(ChatPlugin plugin) {
        this.plugin = plugin;
    }
    
    // In production: public boolean onCommand(CommandSender sender, Command command, String label, String[] args)
    public boolean handleCommand(CommandSender sender, String[] args) {
        if (!sender.hasPermission("chatplugin.toggle")) {
            String noPermMessage = translateColorCodes(
                plugin.getConfig().getString("messages.no-permission", "&cYou don't have permission to use this command."));
            sender.sendMessage(noPermMessage);
            return true;
        }
        
        if (args.length == 0) {
            // Show current status
            boolean enabled = plugin.getConfig().getBoolean("chat-moderation-enabled", true);
            String status = enabled ? "enabled" : "disabled";
            sender.sendMessage("§bChat moderation is currently " + status + ".");
            sender.sendMessage("§7Use /chatmoderation [on|off] to toggle.");
            return true;
        }
        
        if (args.length == 1) {
            String action = args[0].toLowerCase();
            
            switch (action) {
                case "on":
                case "enable":
                case "true":
                    plugin.getConfig().set("chat-moderation-enabled", true);
                    plugin.saveConfig();
                    plugin.reloadPluginConfig();
                    sender.sendMessage("§aChat moderation has been enabled.");
                    return true;
                    
                case "off":
                case "disable":
                case "false":
                    plugin.getConfig().set("chat-moderation-enabled", false);
                    plugin.saveConfig();
                    plugin.reloadPluginConfig();
                    sender.sendMessage("§eChat moderation has been disabled.");
                    return true;
                    
                case "reload":
                    plugin.reloadPluginConfig();
                    sender.sendMessage("§aChat moderation configuration has been reloaded.");
                    return true;
                    
                case "status":
                    boolean enabled = plugin.getConfig().getBoolean("chat-moderation-enabled", true);
                    String status = enabled ? "enabled" : "disabled";
                    sender.sendMessage("§bChat moderation is currently " + status + ".");
                    
                    // Show additional info
                    sender.sendMessage("§7LiteBans integration: " + 
                        (plugin.isLiteBansAvailable() ? "§aAvailable" : "§cNot available"));
                    sender.sendMessage("§7Profanity filter: " + 
                        (plugin.getConfig().getBoolean("profanity-filter.enabled", true) ? "§aEnabled" : "§cDisabled"));
                    sender.sendMessage("§7Severe violations: " + 
                        (plugin.getConfig().getBoolean("severe-violations.enabled", true) ? "§aEnabled" : "§cDisabled"));
                    sender.sendMessage("§7Critical violations: " + 
                        (plugin.getConfig().getBoolean("critical-violations.enabled", true) ? "§aEnabled" : "§cDisabled"));
                    return true;
                    
                default:
                    sender.sendMessage("§cUsage: /chatmoderation [on|off|status|reload]");
                    return true;
            }
        }
        
        sender.sendMessage("§cUsage: /chatmoderation [on|off|status|reload]");
        return true;
    }
    
    // In production: public List<String> onTabComplete(CommandSender sender, Command command, String alias, String[] args)
    public List<String> handleTabComplete(String[] args) {
        if (args.length == 1) {
            return Arrays.asList("on", "off", "status", "reload");
        }
        return null;
    }
    
    private String translateColorCodes(String text) {
        if (text == null) return "";
        return text.replace("&", "§");
    }
}