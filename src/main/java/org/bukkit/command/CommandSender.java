package org.bukkit.command;

/**
 * Minimal CommandSender stub for demonstration purposes.
 * In production, this would come from the Bukkit/Paper API dependency.
 */
public interface CommandSender {
    
    /**
     * Sends this sender a message.
     * 
     * @param message Message to be displayed
     */
    void sendMessage(String message);
    
    /**
     * Gets the name of this command sender.
     * 
     * @return Name of the sender
     */
    String getName();
    
    /**
     * Tests if this CommandSender has the given permission.
     * 
     * @param permission Permission to check
     * @return true if the sender has the permission, otherwise false
     */
    boolean hasPermission(String permission);
}