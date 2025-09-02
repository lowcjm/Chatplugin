package com.lowcjm.chatplugin.commands;

import com.lowcjm.chatplugin.ChatPlugin;

/**
 * Command to manually describe images
 * Usage: /describeimage <image_url>
 */
public class DescribeImageCommand {
    
    private final ChatPlugin plugin;
    
    public DescribeImageCommand(ChatPlugin plugin) {
        this.plugin = plugin;
    }
    
    // In production, this would implement CommandExecutor
    public boolean onCommand(CommandSender sender, String[] args) {
        if (!sender.hasPermission("chatplugin.describe")) {
            sender.sendMessage(translateColorCodes("&cYou don't have permission to use this command."));
            return true;
        }
        
        if (args.length != 1) {
            sender.sendMessage(translateColorCodes("&eUsage: /describeimage <image_url>"));
            return true;
        }
        
        String imageUrl = args[0];
        
        if (!plugin.getImageDescriptionManager().isImageUrl(imageUrl)) {
            sender.sendMessage(translateColorCodes("&cInvalid image URL format. Please provide a direct link to an image (jpg, png, gif, etc.)."));
            return true;
        }
        
        String description = plugin.getImageDescriptionManager().describeImageUrl(imageUrl);
        sender.sendMessage(translateColorCodes("&7Image Description: &f" + description));
        
        return true;
    }
    
    private String translateColorCodes(String text) {
        if (text == null) return "";
        return text.replace("&", "§");
    }
    
    // Interface to simulate CommandSender
    public interface CommandSender {
        void sendMessage(String message);
        boolean hasPermission(String permission);
        String getName();
    }
}