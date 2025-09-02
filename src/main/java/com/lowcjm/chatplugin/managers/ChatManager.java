package com.lowcjm.chatplugin.managers;

import com.lowcjm.chatplugin.ChatPlugin;

import java.util.HashSet;
import java.util.Set;
import java.util.UUID;

public class ChatManager {
    
    private final ChatPlugin plugin;
    private boolean chatMuted;
    private final Set<UUID> mutedPlayers;
    
    public ChatManager(ChatPlugin plugin) {
        this.plugin = plugin;
        this.chatMuted = plugin.getConfig().getBoolean("chat-muted", false);
        this.mutedPlayers = new HashSet<>();
    }
    
    public boolean isChatMuted() {
        return chatMuted;
    }
    
    public void setChatMuted(boolean muted) {
        this.chatMuted = muted;
        plugin.getConfig().set("chat-muted", muted);
        plugin.saveConfig();
        
        String message = muted ? 
            translateColorCodes(plugin.getConfig().getString("mute-message", "&cChat is currently muted by an administrator.")) :
            translateColorCodes(plugin.getConfig().getString("unmute-message", "&aChat has been unmuted."));
        
        // In production: Bukkit.broadcastMessage(message);
        System.out.println("[BROADCAST] " + message);
    }
    
    public boolean isPlayerMuted(UUID playerUuid) {
        return mutedPlayers.contains(playerUuid);
    }
    
    public void mutePlayer(UUID playerUuid) {
        mutedPlayers.add(playerUuid);
    }
    
    public void unmutePlayer(UUID playerUuid) {
        mutedPlayers.remove(playerUuid);
    }
    
    public boolean canPlayerChat(SimulatedPlayer player) {
        // Check if player has bypass permission
        if (player.hasPermission("chatplugin.bypass")) {
            return true;
        }
        
        // Check if chat is globally muted
        if (chatMuted) {
            return false;
        }
        
        // Check if player is individually muted
        if (isPlayerMuted(player.getUniqueId())) {
            return false;
        }
        
        return true;
    }
    
    public void clearChat() {
        // Send 100 empty lines to clear chat for all players
        String clearLines = "\n".repeat(100);
        // In production: Bukkit.broadcastMessage(clearLines);
        
        // Send clear message
        String clearMessage = translateColorCodes(
            plugin.getConfig().getString("clear-message", "&eChat has been cleared by an administrator."));
        // In production: Bukkit.broadcastMessage(clearMessage);
        System.out.println("[BROADCAST] " + clearMessage);
    }
    
    public String getMuteMessage() {
        if (chatMuted) {
            return translateColorCodes(
                plugin.getConfig().getString("messages.chat-muted-player", "&cYou cannot send messages while chat is muted."));
        } else {
            return translateColorCodes(
                plugin.getConfig().getString("messages.player-muted", "&cYou are currently muted and cannot send messages."));
        }
    }
    
    // Simple color code translation
    private String translateColorCodes(String text) {
        if (text == null) return "";
        return text.replace("&", "§");
    }
    
    // Simulated Player class for demonstration
    public static class SimulatedPlayer {
        private UUID uuid;
        private String name;
        
        public SimulatedPlayer(String name) {
            this.name = name;
            this.uuid = UUID.randomUUID();
        }
        
        public UUID getUniqueId() { return uuid; }
        public String getName() { return name; }
        public boolean hasPermission(String permission) { return false; }
        public void sendMessage(String message) { System.out.println("[" + name + "] " + message); }
    }
}