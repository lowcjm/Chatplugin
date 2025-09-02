package org.bukkit.plugin.java;

import java.util.logging.Logger;

/**
 * Minimal JavaPlugin stub for demonstration purposes.
 * In production, this would come from the Bukkit/Paper API dependency.
 */
public abstract class JavaPlugin {
    
    private Logger logger;
    
    public JavaPlugin() {
        this.logger = Logger.getLogger(this.getClass().getName());
    }
    
    /**
     * Called when the plugin is enabled
     */
    public void onEnable() {
        // Default implementation - can be overridden
    }
    
    /**
     * Called when the plugin is disabled
     */
    public void onDisable() {
        // Default implementation - can be overridden
    }
    
    /**
     * Gets the plugin's logger
     * @return the logger
     */
    public Logger getLogger() {
        return logger;
    }
}