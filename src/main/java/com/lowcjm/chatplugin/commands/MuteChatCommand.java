package com.lowcjm.chatplugin.commands;

import com.lowcjm.chatplugin.ChatPlugin;
import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;

import java.util.Arrays;
import java.util.List;

/**
 * Command handler for /mutechat
 */
public class MuteChatCommand implements CommandExecutor {
    
    private final ChatPlugin plugin;
    
    public MuteChatCommand(ChatPlugin plugin) {
        this.plugin = plugin;
    }
    
    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (!sender.hasPermission("chatplugin.mutechat")) {
            String noPermMessage = translateColorCodes(
                plugin.getConfig().getString("messages.no-permission", "&cYou don't have permission to use this command."));
            sender.sendMessage(noPermMessage);
            return true;
        }
        
        if (args.length == 0) {
            // Toggle chat mute status
            boolean currentlyMuted = plugin.getChatManager().isChatMuted();
            plugin.getChatManager().setChatMuted(!currentlyMuted);
            
            String status = !currentlyMuted ? "muted" : "unmuted";
            sender.sendMessage("§aChat has been " + status + ".");
            return true;
        }
        
        if (args.length == 1) {
            String action = args[0].toLowerCase();
            
            switch (action) {
                case "mute":
                case "on":
                    if (plugin.getChatManager().isChatMuted()) {
                        sender.sendMessage("§eChat is already muted.");
                    } else {
                        plugin.getChatManager().setChatMuted(true);
                        sender.sendMessage("§aChat has been muted.");
                    }
                    return true;
                    
                case "unmute":
                case "off":
                    if (!plugin.getChatManager().isChatMuted()) {
                        sender.sendMessage("§eChat is already unmuted.");
                    } else {
                        plugin.getChatManager().setChatMuted(false);
                        sender.sendMessage("§aChat has been unmuted.");
                    }
                    return true;
                    
                case "status":
                    String status = plugin.getChatManager().isChatMuted() ? "muted" : "unmuted";
                    sender.sendMessage("§bChat is currently " + status + ".");
                    return true;
                    
                default:
                    sender.sendMessage("§cUsage: /mutechat [mute|unmute|status]");
                    return true;
            }
        }
        
        sender.sendMessage("§cUsage: /mutechat [mute|unmute|status]");
        return true;
    }
    
    // Legacy method for demo compatibility
    public boolean handleCommand(CommandSender sender, String[] args) {
        return onCommand(sender, null, "mutechat", args);
    }
    
    // In production: public List<String> onTabComplete(CommandSender sender, Command command, String alias, String[] args)
    public List<String> handleTabComplete(String[] args) {
        if (args.length == 1) {
            return Arrays.asList("mute", "unmute", "status");
        }
        return null;
    }
    
    private String translateColorCodes(String text) {
        if (text == null) return "";
        return text.replace("&", "§");
    }
}