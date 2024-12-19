#!/bin/bash

# Function for fancy error printing
print_error() {
    echo "
╔════════════════════════════════════════════════════════════════╗
║                         🚫 ERROR 🚫                            ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  Cannot connect to Ollama at: $OLLAMA_BASE_URL                ║
║                                                                ║
║  Please check:                                                ║
║    1. Ollama is running                                       ║
║    2. The OLLAMA_BASE_URL is correct                         ║
║    3. The network connection is working                       ║
║                                                                ║
║  Error details:                                               ║
║  $1
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
"
    exit 1
}

# Check if OLLAMA_BASE_URL is set
if [ -n "$OLLAMA_BASE_URL" ]; then
    echo "Testing Ollama connection at: $OLLAMA_BASE_URL"
    
    # Try to connect to Ollama
    response=$(curl -s -w "\n%{http_code}" "$OLLAMA_BASE_URL/api/generate" \
        -H "Content-Type: application/json" \
        -d '{
            "model": "llama2",
            "prompt": "Why is the sky blue?"
        }' 2>&1)
    
    # Get the HTTP status code
    http_code=$(echo "$response" | tail -n1)
    # Get the response body
    body=$(echo "$response" | sed '$d')

    # Check if curl command was successful
    if [ $? -ne 0 ]; then
        print_error "Connection failed: $body"
    fi

    # Check if we got a successful response
    if [ "$http_code" -ne 200 ]; then
        print_error "HTTP Error $http_code: $body"
    fi

    echo "✅ Successfully connected to Ollama"
fi 