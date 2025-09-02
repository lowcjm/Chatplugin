package com.lowcjm.chatplugin.managers;

import com.lowcjm.chatplugin.ChatPlugin;

import java.util.List;
import java.util.regex.Pattern;

public class FilterManager {
    
    private final ChatPlugin plugin;
    private List<String> profanityWords;
    private List<String> severeViolationWords;
    private List<String> doxingKeywords;
    private Pattern ipPattern;
    private String replacementChar;
    
    public FilterManager(ChatPlugin plugin) {
        this.plugin = plugin;
        loadFilters();
    }
    
    public void reloadFilters() {
        loadFilters();
    }
    
    private void loadFilters() {
        // Load profanity words
        this.profanityWords = plugin.getConfig().getStringList("profanity-filter.words");
        
        // Load severe violation words
        this.severeViolationWords = plugin.getConfig().getStringList("severe-violations.words");
        
        // Load doxing keywords
        this.doxingKeywords = plugin.getConfig().getStringList("critical-violations.keywords");
        
        // Set replacement character
        this.replacementChar = plugin.getConfig().getString("profanity-filter.replacement-character", "*");
        
        // IP address pattern (basic IPv4 detection)
        this.ipPattern = Pattern.compile("\\b(?:[0-9]{1,3}\\.){3}[0-9]{1,3}\\b");
    }
    
    public FilterResult filterMessage(String message) {
        if (!plugin.getConfig().getBoolean("chat-moderation-enabled", true)) {
            return new FilterResult(message, FilterType.ALLOWED, null);
        }
        
        String originalMessage = message;
        String filteredMessage = message.toLowerCase();
        
        // Check for critical violations first (IP addresses and doxing)
        if (plugin.getConfig().getBoolean("critical-violations.enabled", true)) {
            if (plugin.getConfig().getBoolean("critical-violations.detection-patterns.ip-addresses", true)) {
                if (ipPattern.matcher(message).find()) {
                    return new FilterResult(originalMessage, FilterType.CRITICAL_VIOLATION, "IP address detected");
                }
            }
            
            if (plugin.getConfig().getBoolean("critical-violations.detection-patterns.doxing-keywords", true)) {
                for (String keyword : doxingKeywords) {
                    if (filteredMessage.contains(keyword.toLowerCase())) {
                        return new FilterResult(originalMessage, FilterType.CRITICAL_VIOLATION, "Doxing keyword detected: " + keyword);
                    }
                }
            }
        }
        
        // Check for severe violations
        if (plugin.getConfig().getBoolean("severe-violations.enabled", true)) {
            for (String word : severeViolationWords) {
                // Use word boundary matching to avoid partial matches
                String wordPattern = "\\b" + Pattern.quote(word.toLowerCase()) + "\\b";
                if (Pattern.compile(wordPattern, Pattern.CASE_INSENSITIVE).matcher(filteredMessage).find()) {
                    return new FilterResult(originalMessage, FilterType.SEVERE_VIOLATION, "Severe language detected: " + word);
                }
            }
        }
        
        // Check for profanity and filter it
        if (plugin.getConfig().getBoolean("profanity-filter.enabled", true)) {
            boolean containsProfanity = false;
            String processedMessage = originalMessage;
            
            for (String word : profanityWords) {
                // Use word boundary matching to avoid partial matches
                String wordPattern = "\\b" + Pattern.quote(word) + "\\b";
                Pattern pattern = Pattern.compile(wordPattern, Pattern.CASE_INSENSITIVE);
                if (pattern.matcher(processedMessage).find()) {
                    containsProfanity = true;
                    // Replace the word with asterisks
                    String replacement = replacementChar.repeat(word.length());
                    processedMessage = pattern.matcher(processedMessage).replaceAll(replacement);
                }
            }
            
            if (containsProfanity) {
                return new FilterResult(processedMessage, FilterType.PROFANITY_FILTERED, null);
            }
        }
        
        return new FilterResult(originalMessage, FilterType.ALLOWED, null);
    }
    
    public static class FilterResult {
        private final String filteredMessage;
        private final FilterType type;
        private final String reason;
        
        public FilterResult(String filteredMessage, FilterType type, String reason) {
            this.filteredMessage = filteredMessage;
            this.type = type;
            this.reason = reason;
        }
        
        public String getFilteredMessage() {
            return filteredMessage;
        }
        
        public FilterType getType() {
            return type;
        }
        
        public String getReason() {
            return reason;
        }
    }
    
    public enum FilterType {
        ALLOWED,
        PROFANITY_FILTERED,
        SEVERE_VIOLATION,
        CRITICAL_VIOLATION
    }
}