package org.bukkit.command;

/**
 * Minimal PluginCommand stub for demonstration purposes.
 * In production, this would come from the Bukkit/Paper API dependency.
 */
public class PluginCommand extends Command {
    private CommandExecutor executor;
    
    public PluginCommand(String name) {
        super(name);
    }
    
    /**
     * Sets the CommandExecutor to run when parsing this command.
     * 
     * @param executor New executor to run
     */
    public void setExecutor(CommandExecutor executor) {
        this.executor = executor;
    }
    
    /**
     * Gets the CommandExecutor associated with this command.
     * 
     * @return CommandExecutor object linked to this command
     */
    public CommandExecutor getExecutor() {
        return executor;
    }
    
    @Override
    public boolean execute(CommandSender sender, String commandLabel, String[] args) {
        if (executor != null) {
            return executor.onCommand(sender, this, commandLabel, args);
        }
        return false;
    }
}