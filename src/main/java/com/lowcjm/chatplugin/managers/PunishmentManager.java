package com.lowcjm.chatplugin.managers;

import com.lowcjm.chatplugin.ChatPlugin;
import com.lowcjm.chatplugin.managers.ChatManager.SimulatedPlayer;

import java.io.File;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.TimeUnit;

public class PunishmentManager {
    
    private final ChatPlugin plugin;
    private final boolean useLiteBans;
    private final Map<UUID, Long> tempMutes; // UUID -> unmute timestamp
    private File punishmentsFile;
    
    public PunishmentManager(ChatPlugin plugin, boolean liteBansAvailable) {
        this.plugin = plugin;
        this.useLiteBans = liteBansAvailable && plugin.getConfig().getBoolean("use-litebans", true);
        this.tempMutes = new HashMap<>();
        
        if (!useLiteBans) {
            setupInternalSystem();
        }
        
        // Start cleanup task for expired mutes
        startCleanupTask();
    }
    
    private void setupInternalSystem() {
        punishmentsFile = new File(".", plugin.getConfig().getString("internal-punishments.data-file", "punishments.yml"));
        if (!punishmentsFile.exists()) {
            try {
                punishmentsFile.createNewFile();
            } catch (IOException e) {
                plugin.getLogger().severe("Could not create punishments.yml file: " + e.getMessage());
            }
        }
        loadPunishments();
    }
    
    public void applySeverePunishment(SimulatedPlayer player, String reason) {
        UUID playerUuid = player.getUniqueId();
        long duration = plugin.getConfig().getLong("severe-violations.mute-duration", 86400); // 24 hours default
        
        if (useLiteBans) {
            applyLiteBansMute(player, duration, reason);
        } else {
            applyInternalTempMute(playerUuid, duration);
        }
        
        // Notify player
        String message = translateColorCodes(
            plugin.getConfig().getString("messages.severe-violation", "&cYou have been muted for inappropriate language. Duration: %duration%"));
        message = message.replace("%duration%", formatDuration(duration));
        player.sendMessage(message);
        
        plugin.getLogger().info("Player " + player.getName() + " was muted for severe violation: " + reason);
    }
    
    public void applyCriticalPunishment(SimulatedPlayer player, String reason) {
        UUID playerUuid = player.getUniqueId();
        
        if (useLiteBans) {
            applyLiteBansPermanentMute(player, reason);
        } else {
            applyInternalPermanentMute(playerUuid);
        }
        
        // Notify player
        String message = translateColorCodes(
            plugin.getConfig().getString("messages.critical-violation", "&4You have been permanently muted for sharing personal information."));
        player.sendMessage(message);
        
        plugin.getLogger().warning("Player " + player.getName() + " was permanently muted for critical violation: " + reason);
    }
    
    private void applyLiteBansMute(SimulatedPlayer player, long durationSeconds, String reason) {
        // In production: Use LiteBans API
        // Try to dispatch command to LiteBans
        String command = String.format("mute %s %s %s", 
            player.getName(), 
            formatLiteBansDuration(durationSeconds),
            plugin.getConfig().getString("litebans.severe-mute-reason", "Inappropriate language (automated)"));
        
        if (plugin.getConfig().getBoolean("litebans.use-silent-punishments", true)) {
            command = "s" + command;
        }
        
        // In production: Bukkit.dispatchCommand(Bukkit.getConsoleSender(), command);
        plugin.getLogger().info("Would execute LiteBans command: " + command);
        
        // Fallback to internal system
        applyInternalTempMute(player.getUniqueId(), durationSeconds);
    }
    
    private void applyLiteBansPermanentMute(SimulatedPlayer player, String reason) {
        // In production: Use LiteBans API
        String command = String.format("mute %s -1 %s", 
            player.getName(), 
            plugin.getConfig().getString("litebans.critical-mute-reason", "Sharing personal information (automated)"));
        
        if (plugin.getConfig().getBoolean("litebans.use-silent-punishments", true)) {
            command = "s" + command;
        }
        
        // In production: Bukkit.dispatchCommand(Bukkit.getConsoleSender(), command);
        plugin.getLogger().info("Would execute LiteBans command: " + command);
        
        // Fallback to internal system
        applyInternalPermanentMute(player.getUniqueId());
    }
    
    private void applyInternalTempMute(UUID playerUuid, long durationSeconds) {
        long unmuteTime = System.currentTimeMillis() + (durationSeconds * 1000);
        tempMutes.put(playerUuid, unmuteTime);
        plugin.getChatManager().mutePlayer(playerUuid);
        savePunishments();
    }
    
    private void applyInternalPermanentMute(UUID playerUuid) {
        tempMutes.put(playerUuid, -1L); // -1 indicates permanent
        plugin.getChatManager().mutePlayer(playerUuid);
        savePunishments();
    }
    
    public boolean isPlayerMuted(UUID playerUuid) {
        if (useLiteBans) {
            // In production: Check LiteBans API
            // For now, also check internal system as fallback
        }
        
        if (tempMutes.containsKey(playerUuid)) {
            long unmuteTime = tempMutes.get(playerUuid);
            if (unmuteTime == -1) { // Permanent mute
                return true;
            }
            if (System.currentTimeMillis() < unmuteTime) {
                return true;
            } else {
                // Mute expired
                tempMutes.remove(playerUuid);
                plugin.getChatManager().unmutePlayer(playerUuid);
                savePunishments();
            }
        }
        
        return false;
    }
    
    private void startCleanupTask() {
        // In production: Use Bukkit scheduler
        // new BukkitRunnable() { ... }.runTaskTimerAsynchronously(plugin, 20L * 60L, 20L * 60L);
        
        // For demonstration, create a simple cleanup thread
        Thread cleanupThread = new Thread(() -> {
            while (true) {
                try {
                    Thread.sleep(60000); // Sleep for 1 minute
                    long currentTime = System.currentTimeMillis();
                    tempMutes.entrySet().removeIf(entry -> {
                        long unmuteTime = entry.getValue();
                        if (unmuteTime != -1 && currentTime >= unmuteTime) {
                            plugin.getChatManager().unmutePlayer(entry.getKey());
                            return true;
                        }
                        return false;
                    });
                    
                    if (!useLiteBans) {
                        savePunishments();
                    }
                } catch (InterruptedException e) {
                    break;
                }
            }
        });
        cleanupThread.setDaemon(true);
        cleanupThread.start();
    }
    
    public void savePunishments() {
        if (useLiteBans) return;
        
        // In production: Save to YAML file using Bukkit's configuration system
        plugin.getLogger().info("Saving " + tempMutes.size() + " punishment records");
    }
    
    private void loadPunishments() {
        // In production: Load from YAML file using Bukkit's configuration system
        plugin.getLogger().info("Loading punishment records from file");
    }
    
    private String formatDuration(long seconds) {
        long hours = TimeUnit.SECONDS.toHours(seconds);
        long minutes = TimeUnit.SECONDS.toMinutes(seconds) % 60;
        
        if (hours > 0) {
            return hours + " hour(s) and " + minutes + " minute(s)";
        } else {
            return minutes + " minute(s)";
        }
    }
    
    private String formatLiteBansDuration(long seconds) {
        long hours = TimeUnit.SECONDS.toHours(seconds);
        if (hours > 0) {
            return hours + "h";
        } else {
            long minutes = TimeUnit.SECONDS.toMinutes(seconds);
            return minutes + "m";
        }
    }
    
    private String translateColorCodes(String text) {
        if (text == null) return "";
        return text.replace("&", "§");
    }
}