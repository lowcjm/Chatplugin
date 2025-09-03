package org.bukkit.plugin;

import org.bukkit.event.Listener;

/**
 * Minimal PluginManager stub for demonstration purposes.
 * In production, this would come from the Bukkit/Paper API dependency.
 */
public interface PluginManager {
    /**
     * Registers all the events in the given listener class
     * @param listener Listener to register
     * @param plugin Plugin to register
     */
    void registerEvents(Listener listener, Plugin plugin);
}