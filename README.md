# Alrah AI - Arabic Telegram Voice Bot

Arabic Telegram bot for querying مكتبة الرحيق المختوم (Sheikh Al-Yaqoubi's digital library) using voice and text messages.

## Features

- **Voice Message Processing**: Transcribes Arabic voice messages using OpenAI Whisper
- **Text Message Support**: Handles text queries directly
- **Semantic Search**: Uses Pinecone vector database for intelligent content search
- **Voice Responses**: Responds with synthesized Arabic voice messages
- **Real-time Indicators**: Shows typing/recording indicators during processing

## Setup

1. **Install Dependencies**:
   ```bash
   ./deploy.sh
   ```

2. **Configure Environment**:
   Copy `.env.example` to `.env` and fill in your API keys:
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   OPENAI_API_KEY=your_openai_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_INDEX_NAME=your_pinecone_index_name
   ```

3. **Run the Bot**:
   ```bash
   ./run_bot.sh
   ```

## Deployment

Deploy as a system service:
```bash
sudo cp alrah-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable alrah-bot.service
sudo systemctl start alrah-bot.service
```

## Usage

- Send voice messages in Arabic for voice responses
- Send text messages for text responses
- Bot searches the religious library and provides contextual answers

## Technology Stack

- **Python 3.8+**
- **python-telegram-bot**: Telegram Bot API
- **OpenAI**: Whisper (transcription), GPT-4o-mini (responses), TTS (voice synthesis)
- **Pinecone**: Vector database for semantic search
- **FFmpeg**: Audio processing
