package org.bukkit.event;

/**
 * Minimal EventHandler annotation stub for demonstration purposes.
 * In production, this would come from the Bukkit/Paper API dependency.
 */
public @interface EventHandler {
    /**
     * Define the priority of the event.
     * @return the priority
     */
    EventPriority priority() default EventPriority.NORMAL;
}