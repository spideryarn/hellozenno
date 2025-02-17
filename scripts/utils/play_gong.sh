#!/bin/bash

# Configuration
SOUND_FILE="/Users/greg/Dropbox/conf/sounds/dutifully-notification-tone.mp3"
MAX_VOLUME=50  # Maximum allowed volume percentage
REQUIRED_VOLUME=30  # Volume to set before playing

# Function to get current system volume (0-100)
get_current_volume() {
    osascript -e 'output volume of (get volume settings)'
}

# Function to set system volume (0-100)
set_volume() {
    osascript -e "set volume output volume $1"
}

# Main script
main() {
    # Check if afplay is available
    if ! command -v afplay >/dev/null 2>&1; then
        echo "Error: afplay command not found. This script requires macOS."
        exit 1
    fi
    
    # Check if sound file exists
    if [ ! -f "$SOUND_FILE" ]; then
        echo "Error: Sound file not found at: $SOUND_FILE"
        exit 1
    fi
    
    # Get current volume
    current_volume=$(get_current_volume)
    
    # Store original volume to restore later
    original_volume=$current_volume
    
    # Check if current volume is too high
    if [ "$current_volume" -gt "$MAX_VOLUME" ]; then
        echo "Current volume ($current_volume%) is too high. Adjusting..."
        set_volume $REQUIRED_VOLUME
    fi
    
    # Play the sound
    echo "Playing notification sound..."
    afplay "$SOUND_FILE"
    
    # Restore original volume if it was changed
    if [ "$current_volume" -gt "$MAX_VOLUME" ]; then
        set_volume $original_volume
        echo "Restored original volume"
    fi
}

# Run the main function
main
