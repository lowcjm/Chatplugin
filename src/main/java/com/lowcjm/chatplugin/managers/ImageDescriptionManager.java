package com.lowcjm.chatplugin.managers;

import com.lowcjm.chatplugin.ChatPlugin;

import java.util.regex.Pattern;
import java.util.regex.Matcher;

/**
 * Manager for detecting and describing images shared in chat
 */
public class ImageDescriptionManager {
    
    private final ChatPlugin plugin;
    private Pattern imageUrlPattern;
    
    // Common image URL patterns
    private static final String IMAGE_URL_REGEX = 
        "(?i)\\b(?:https?://)(?:[^\\s<>\"]+\\.(?:jpg|jpeg|png|gif|bmp|webp|svg))(?:\\?[^\\s<>\"]*)?\\b";
    
    public ImageDescriptionManager(ChatPlugin plugin) {
        this.plugin = plugin;
        this.imageUrlPattern = Pattern.compile(IMAGE_URL_REGEX);
    }
    
    /**
     * Check if a message contains image URLs and generate descriptions
     */
    public ImageAnalysisResult analyzeMessage(String message) {
        if (!plugin.getConfig().getBoolean("image-description.enabled", true)) {
            return new ImageAnalysisResult(message, false, null);
        }
        
        Matcher matcher = imageUrlPattern.matcher(message);
        if (matcher.find()) {
            String imageUrl = matcher.group();
            String description = describeImage(imageUrl);
            
            // Replace the URL with description if enabled
            if (plugin.getConfig().getBoolean("image-description.replace-with-description", false)) {
                String processedMessage = message.replace(imageUrl, 
                    "[Image: " + description + "]");
                return new ImageAnalysisResult(processedMessage, true, description);
            } else {
                // Add description after the URL
                String processedMessage = message.replace(imageUrl, 
                    imageUrl + " [Image: " + description + "]");
                return new ImageAnalysisResult(processedMessage, true, description);
            }
        }
        
        return new ImageAnalysisResult(message, false, null);
    }
    
    /**
     * Generate a description for an image URL
     * In a real implementation, this would use an AI service or image analysis API
     */
    private String describeImage(String imageUrl) {
        // For demo purposes, provide mock descriptions based on URL patterns
        String urlLower = imageUrl.toLowerCase();
        
        if (urlLower.contains("cat") || urlLower.contains("kitten")) {
            return "A cute cat photo";
        } else if (urlLower.contains("dog") || urlLower.contains("puppy")) {
            return "A friendly dog picture";
        } else if (urlLower.contains("sunset") || urlLower.contains("sunrise")) {
            return "A beautiful sunset/sunrise scene";
        } else if (urlLower.contains("meme")) {
            return "A funny meme image";
        } else if (urlLower.contains("screenshot") || urlLower.contains("game")) {
            return "A game screenshot";
        } else if (urlLower.endsWith(".gif")) {
            return "An animated GIF";
        } else if (urlLower.endsWith(".png")) {
            return "A PNG image";
        } else if (urlLower.endsWith(".jpg") || urlLower.endsWith(".jpeg")) {
            return "A JPEG photo";
        } else {
            return "An image file";
        }
        
        // In production, this would make an API call to an image analysis service:
        // return callImageAnalysisAPI(imageUrl);
    }
    
    /**
     * Manually describe an image URL (for command usage)
     */
    public String describeImageUrl(String imageUrl) {
        if (!imageUrlPattern.matcher(imageUrl).matches()) {
            return "Invalid image URL format";
        }
        
        return describeImage(imageUrl);
    }
    
    /**
     * Check if a string is a valid image URL
     */
    public boolean isImageUrl(String url) {
        return imageUrlPattern.matcher(url).matches();
    }
    
    /**
     * Result of image analysis
     */
    public static class ImageAnalysisResult {
        private final String processedMessage;
        private final boolean containsImage;
        private final String description;
        
        public ImageAnalysisResult(String processedMessage, boolean containsImage, String description) {
            this.processedMessage = processedMessage;
            this.containsImage = containsImage;
            this.description = description;
        }
        
        public String getProcessedMessage() {
            return processedMessage;
        }
        
        public boolean containsImage() {
            return containsImage;
        }
        
        public String getDescription() {
            return description;
        }
    }
}