package org.bukkit.command;

/**
 * Minimal Command stub for demonstration purposes.
 * In production, this would come from the Bukkit/Paper API dependency.
 */
public abstract class Command {
    private final String name;
    
    protected Command(String name) {
        this.name = name;
    }
    
    /**
     * Returns the name of this command.
     * 
     * @return Name of this command
     */
    public String getName() {
        return name;
    }
    
    /**
     * Executes the command, returning its success.
     * 
     * @param sender Source object which is executing this command
     * @param commandLabel The exact command label typed by the user
     * @param args All arguments passed to the command, split via ' '
     * @return true if the command was successful, otherwise false
     */
    public abstract boolean execute(CommandSender sender, String commandLabel, String[] args);
}