#!/bin/bash

# Install system dependencies
apt-get update
apt-get install -y ffmpeg

# Install Python dependencies
pip install -r requirements.txt

echo "Setup complete. Copy .env.example to .env and fill in your API keys."
