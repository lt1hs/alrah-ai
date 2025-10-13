#!/bin/bash

# Install system dependencies
sudo apt update
sudo apt install -y python3 python3-pip python3-venv ffmpeg

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

echo "Setup complete. To run the bot:"
echo "source venv/bin/activate"
echo "python bot.py"
