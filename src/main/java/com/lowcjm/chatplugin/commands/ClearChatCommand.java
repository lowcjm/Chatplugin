package com.lowcjm.chatplugin.commands;

import com.lowcjm.chatplugin.ChatPlugin;
import com.lowcjm.chatplugin.commands.MuteChatCommand.CommandSender;

/**
 * Command handler for /clearchat
 * In production, this would implement CommandExecutor from Bukkit API
 */
public class ClearChatCommand {
    
    private final ChatPlugin plugin;
    
    public ClearChatCommand(ChatPlugin plugin) {
        this.plugin = plugin;
    }
    
    // In production: public boolean onCommand(CommandSender sender, Command command, String label, String[] args)
    public boolean handleCommand(CommandSender sender, String[] args) {
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
    
    private String translateColorCodes(String text) {
        if (text == null) return "";
        return text.replace("&", "§");
    }
}