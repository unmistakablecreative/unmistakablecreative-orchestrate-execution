#!/bin/bash

# Ensure the script is called with at least 2 arguments
if [ "$#" -lt 2 ]; then
    echo "{\"error\": \"Usage: $0 \\\"Guest Name\\\" \\\"Episode Title\\\" [\\\"Custom Prompt\\\"]\"}"
    exit 1
fi

# Input arguments
GUEST_NAME="$1"
EPISODE_TITLE="$2"
CUSTOM_PROMPT="$3"

# Define paths
REMIX_FILE_PATH="/Users/srinirao/Dropbox/2. Areas of Responsibility/Unmistkable Creative/1.Podcast/Covers/Assets/remix1.png"
OUTPUT_PATH="/Users/srinirao/Dropbox/2. Areas of Responsibility/Unmistkable Creative/1.Podcast/Covers/Assets/${GUEST_NAME// /-}-bg.jpg"

# Ensure input image exists
if [ ! -f "$REMIX_FILE_PATH" ]; then
    echo "{\"error\": \"The input file '$REMIX_FILE_PATH' does not exist.\"}"
    exit 1
fi

# Construct the prompt
if [ -z "$CUSTOM_PROMPT" ]; then
    # Default prompt when no customization is provided
    PROMPT="A visually captivating background for a podcast titled '${EPISODE_TITLE}'. The guest name '${GUEST_NAME}' should appear in sleek, modern text beneath the title. Place the title in the top right corner using a bold, handwritten font. Use bright, abstract colors to convey positivity and growth."
else
    # Use the custom prompt if provided
    PROMPT="$CUSTOM_PROMPT"
fi

# Log the prompt being used
echo "{\"info\": \"Using prompt: $PROMPT\"}"

# Make API call to Ideogram
response=$(curl --http1.1 -X POST "https://api.ideogram.ai/remix" \
  -H "Api-Key: AhCi-JBN-jIeSLOlvm6WO4AX0wjt_Xj65Yvz7BhDujo_V6PsjANlTZm1M4o9aJr_L24Jl7kLfh2cKbzCfu9Oyg" \
  -F "image_request={\"prompt\":\"$PROMPT\",\"aspect_ratio\":\"ASPECT_1_1\",\"image_weight\":50,\"magic_prompt_option\":\"ON\",\"model\":\"V_2\",\"seed\":813926077}" \
  -F "image_file=@$REMIX_FILE_PATH" 2>/dev/null)

# Extract the image URL from the response
IMAGE_URL=$(echo "$response" | jq -r '.data[0].url')

# Download the image if the URL is valid
if [ "$IMAGE_URL" != "null" ] && [ -n "$IMAGE_URL" ]; then
    curl -o "$OUTPUT_PATH" "$IMAGE_URL" 2>/dev/null
    if [ -f "$OUTPUT_PATH" ]; then
        echo "{\"data\": [{\"url\": \"$IMAGE_URL\"}]}"
    else
        echo "{\"error\": \"Failed to save the background image to '$OUTPUT_PATH'.\"}"
        exit 1
    fi
else
    echo "{\"error\": \"Failed to retrieve image URL from API response.\"}"
    exit 1
fi
