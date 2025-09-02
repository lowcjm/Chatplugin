package com.lowcjm.chatplugin.listeners;

import com.lowcjm.chatplugin.ChatPlugin;
import com.lowcjm.chatplugin.managers.FilterManager;
import com.lowcjm.chatplugin.managers.ImageDescriptionManager;
import com.lowcjm.chatplugin.managers.ChatManager.SimulatedPlayer;

/**
 * Chat listener for intercepting and filtering chat messages
 * In production, this would implement Bukkit's Listener interface and use @EventHandler
 */
public class ChatListener {
    
    private final ChatPlugin plugin;
    
    public ChatListener(ChatPlugin plugin) {
        this.plugin = plugin;
    }
    
    // In production, this would be annotated with @EventHandler(priority = EventPriority.HIGHEST)
    // and take AsyncPlayerChatEvent as parameter
    public void onPlayerChat(SimulatedPlayer player, String message, ChatEventWrapper event) {
        // Check if player can chat (bypass permission, chat muted, player muted)
        if (!plugin.getChatManager().canPlayerChat(player)) {
            event.setCancelled(true);
            player.sendMessage(plugin.getChatManager().getMuteMessage());
            return;
        }
        
        // Check if player is muted by punishment system
        if (plugin.getPunishmentManager().isPlayerMuted(player.getUniqueId())) {
            event.setCancelled(true);
            String muteMessage = translateColorCodes(
                plugin.getConfig().getString("messages.player-muted", "&cYou are currently muted and cannot send messages."));
            player.sendMessage(muteMessage);
            return;
        }
        
        // Filter the message
        FilterManager.FilterResult result = plugin.getFilterManager().filterMessage(message);
        
        // If the message passed filtering, check for images and add descriptions
        String finalMessage = message;
        if (result.getType() == FilterManager.FilterType.ALLOWED || 
            result.getType() == FilterManager.FilterType.PROFANITY_FILTERED) {
            
            // Use the filtered message if profanity was filtered
            String messageToAnalyze = result.getType() == FilterManager.FilterType.PROFANITY_FILTERED ? 
                result.getFilteredMessage() : message;
            
            // Analyze for images and add descriptions
            ImageDescriptionManager.ImageAnalysisResult imageResult = 
                plugin.getImageDescriptionManager().analyzeMessage(messageToAnalyze);
            
            if (imageResult.containsImage()) {
                finalMessage = imageResult.getProcessedMessage();
                
                // Notify that image was described
                if (plugin.getConfig().getBoolean("image-description.notify-player", true)) {
                    String notifyMessage = translateColorCodes(
                        plugin.getConfig().getString("messages.image-described", 
                        "&7[Image described: " + imageResult.getDescription() + "]"));
                    player.sendMessage(notifyMessage);
                }
            } else {
                finalMessage = messageToAnalyze;
            }
        }
        
        switch (result.getType()) {
            case ALLOWED:
                // Message is clean, set the final message (potentially with image descriptions)
                if (!finalMessage.equals(message)) {
                    event.setMessage(finalMessage);
                }
                break;
                
            case PROFANITY_FILTERED:
                // Replace message with filtered version (potentially with image descriptions)
                event.setMessage(finalMessage);
                
                // Notify player their message was filtered
                String filterMessage = translateColorCodes(
                    plugin.getConfig().getString("messages.profanity-filtered", "&eYour message contained inappropriate language and has been filtered."));
                player.sendMessage(filterMessage);
                break;
                
            case SEVERE_VIOLATION:
                // Cancel message and apply punishment
                event.setCancelled(true);
                plugin.getPunishmentManager().applySeverePunishment(player, result.getReason());
                break;
                
            case CRITICAL_VIOLATION:
                // Cancel message and apply permanent punishment
                event.setCancelled(true);
                plugin.getPunishmentManager().applyCriticalPunishment(player, result.getReason());
                break;
        }
    }
    
    private String translateColorCodes(String text) {
        if (text == null) return "";
        return text.replace("&", "§");
    }
    
    // Wrapper class to simulate Bukkit's event system
    public static class ChatEventWrapper {
        private boolean cancelled = false;
        private String message;
        
        public ChatEventWrapper(String message) {
            this.message = message;
        }
        
        public boolean isCancelled() { return cancelled; }
        public void setCancelled(boolean cancelled) { this.cancelled = cancelled; }
        public String getMessage() { return message; }
        public void setMessage(String message) { this.message = message; }
    }
}