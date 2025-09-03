package org.bukkit.plugin.java;

import java.util.logging.Logger;
import java.util.HashMap;
import java.util.Map;
import org.bukkit.command.PluginCommand;

/**
 * Minimal JavaPlugin stub for demonstration purposes.
 * In production, this would come from the Bukkit/Paper API dependency.
 */
public abstract class JavaPlugin {
    
    private Logger logger;
    private Map<String, PluginCommand> commands = new HashMap<>();
    
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
    
    /**
     * Gets a command registered to this plugin.
     * @param name Name of the command to retrieve
     * @return PluginCommand if found, otherwise null
     */
    public PluginCommand getCommand(String name) {
        PluginCommand command = commands.get(name);
        if (command == null) {
            // Create command if not exists (simulated behavior)
            command = new PluginCommand(name);
            commands.put(name, command);
        }
        return command;
    }
}