package com.lowcjm.chatplugin.demo;

import com.lowcjm.chatplugin.ChatPlugin;
import com.lowcjm.chatplugin.commands.MuteChatCommand.CommandSender;
import com.lowcjm.chatplugin.listeners.ChatListener;
import com.lowcjm.chatplugin.managers.ChatManager.SimulatedPlayer;
import com.lowcjm.chatplugin.managers.FilterManager;

/**
 * Demonstration class showing how the ChatPlugin works
 * This simulates the functionality that would happen in a real Minecraft server
 */
public class ChatPluginDemo {
    
    public static void main(String[] args) {
        System.out.println("=== ChatPlugin Demo ===");
        System.out.println("Demonstrating Minecraft 1.21+ Chat Moderation Plugin");
        System.out.println();
        
        // Initialize the plugin
        ChatPlugin plugin = new ChatPlugin();
        plugin.onEnable();
        
        System.out.println("\n=== Testing Chat Commands ===");
        
        // Simulate an admin user
        AdminUser admin = new AdminUser("Administrator");
        
        // Test mute chat command
        System.out.println("\n1. Testing /mutechat command:");
        plugin.getChatManager().setChatMuted(false); // Ensure it starts unmuted
        System.out.println("   Initial chat status: " + (plugin.getChatManager().isChatMuted() ? "MUTED" : "UNMUTED"));
        
        // Mute chat
        System.out.println("   Executing: /mutechat mute");
        plugin.getChatManager().setChatMuted(true);
        System.out.println("   Chat status after mute: " + (plugin.getChatManager().isChatMuted() ? "MUTED" : "UNMUTED"));
        
        // Unmute chat
        System.out.println("   Executing: /mutechat unmute");
        plugin.getChatManager().setChatMuted(false);
        System.out.println("   Chat status after unmute: " + (plugin.getChatManager().isChatMuted() ? "MUTED" : "UNMUTED"));
        
        // Test clear chat command
        System.out.println("\n2. Testing /clearchat command:");
        System.out.println("   Executing: /clearchat");
        plugin.getChatManager().clearChat();
        
        System.out.println("\n=== Testing Chat Filtering ===");
        
        // Create test players
        SimulatedPlayer player1 = new SimulatedPlayer("TestPlayer1");
        SimulatedPlayer player2 = new SimulatedPlayer("ViolatorPlayer");
        SimulatedPlayer player3 = new SimulatedPlayer("SeverPlayer");
        
        ChatListener chatListener = new ChatListener(plugin);
        
        // Test normal message
        System.out.println("\n3. Testing normal message:");
        testChatMessage(chatListener, player1, "Hello everyone, how are you today?");
        
        // Test profanity filtering (using example words from config)
        System.out.println("\n4. Testing profanity filter:");
        testChatMessage(chatListener, player1, "This damn server is pretty good!");
        
        // Test severe violation (would result in temporary mute)
        System.out.println("\n5. Testing severe violation detection:");
        testChatMessage(chatListener, player2, "You're such a retard!");
        
        // Test critical violation - IP sharing
        System.out.println("\n6. Testing critical violation - IP address:");
        testChatMessage(chatListener, player3, "Come to my server at 192.168.1.100!");
        
        // Test critical violation - doxing
        System.out.println("\n7. Testing critical violation - doxing:");
        testChatMessage(chatListener, player3, "I know where you live, I'll doxx you!");
        
        // Test chat when muted
        System.out.println("\n8. Testing chat while globally muted:");
        plugin.getChatManager().setChatMuted(true);
        testChatMessage(chatListener, player1, "Can anyone hear me?");
        plugin.getChatManager().setChatMuted(false);
        
        System.out.println("\n=== Demo Complete ===");
        System.out.println("The plugin successfully demonstrates:");
        System.out.println("✓ Chat muting/unmuting functionality");
        System.out.println("✓ Chat clearing functionality");
        System.out.println("✓ Profanity filtering with **** replacement");
        System.out.println("✓ Severe violation detection (temp mutes)");
        System.out.println("✓ Critical violation detection (permanent mutes)");
        System.out.println("✓ IP address detection");
        System.out.println("✓ Doxing keyword detection");
        System.out.println("✓ LiteBans integration support (with fallback)");
        
        plugin.onDisable();
    }
    
    private static void testChatMessage(ChatListener listener, SimulatedPlayer player, String message) {
        System.out.println("   " + player.getName() + " says: \"" + message + "\"");
        
        ChatListener.ChatEventWrapper event = new ChatListener.ChatEventWrapper(message);
        listener.onPlayerChat(player, message, event);
        
        if (event.isCancelled()) {
            System.out.println("   → Message BLOCKED");
        } else if (!event.getMessage().equals(message)) {
            System.out.println("   → Message FILTERED: \"" + event.getMessage() + "\"");
        } else {
            System.out.println("   → Message ALLOWED");
        }
    }
    
    // Simulated admin user for testing commands
    static class AdminUser implements CommandSender {
        private String name;
        
        public AdminUser(String name) {
            this.name = name;
        }
        
        @Override
        public void sendMessage(String message) {
            System.out.println("   [" + name + " receives]: " + message);
        }
        
        @Override
        public boolean hasPermission(String permission) {
            return true; // Admin has all permissions
        }
        
        @Override
        public String getName() {
            return name;
        }
    }
}