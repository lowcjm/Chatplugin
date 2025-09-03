package com.lowcjm.chatplugin.commands;

import com.lowcjm.chatplugin.ChatPlugin;
import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;

/**
 * Command handler for /clearchat
 */
public class ClearChatCommand implements CommandExecutor {
    
    private final ChatPlugin plugin;
    
    public ClearChatCommand(ChatPlugin plugin) {
        this.plugin = plugin;
    }
    
    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (!sender.hasPermission("chatplugin.clearchat")) {
            String noPermMessage = translateColorCodes(
                plugin.getConfig().getString("messages.no-permission", "&cYou don't have permission to use this command."));
            sender.sendMessage(noPermMessage);
            return true;
        }
        
        plugin.getChatManager().clearChat();
        sender.sendMessage("§aChat has been cleared for all players.");
        
        return true;
    }
    
    // Legacy method for demo compatibility
    public boolean handleCommand(CommandSender sender, String[] args) {
        return onCommand(sender, null, "clearchat", args);
    }
    
    private String translateColorCodes(String text) {
        if (text == null) return "";
        return text.replace("&", "§");
    }
}