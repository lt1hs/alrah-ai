# Alrah AI - Arabic Voice Assistant Project
## Complete Documentation

### 📋 Project Overview

**Alrah AI** is a comprehensive Arabic voice assistant system that provides intelligent responses based on مكتبة الرحيق المختوم (Sheikh Al-Yaqoubi's digital library). The system supports multiple interaction methods including Telegram bot, REST API, and real-time voice conversations via LiveKit.

### 🎯 Key Features

- **Arabic Voice Recognition** - OpenAI Whisper with Arabic language support
- **Intelligent Responses** - GPT-4o-mini powered by Pinecone vector search
- **Text-to-Speech** - Natural Arabic voice synthesis
- **Multi-Platform Access** - Telegram, REST API, and LiveKit integration
- **Real-time Voice Chat** - WebRTC-based live conversations
- **Vector Search** - Semantic search through religious texts
- **CORS Support** - Cross-origin requests enabled

### 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Telegram Bot  │    │    REST API     │    │   LiveKit Web   │
│                 │    │                 │    │                 │
│ Voice Messages  │    │ HTTP Endpoints  │    │ Real-time Voice │
│ Text Messages   │    │ File Uploads    │    │ WebRTC Stream   │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │      Core AI Engine       │
                    │                           │
                    │ • OpenAI Whisper (STT)    │
                    │ • GPT-4o-mini (LLM)       │
                    │ • OpenAI TTS (Voice)      │
                    │ • Pinecone (Vector DB)    │
                    └───────────────────────────┘
```

### 📁 Project Structure

```
alrah-ai/
├── bot.py                    # Telegram bot implementation
├── api.py                    # FastAPI REST server
├── livekit_agent.py         # LiveKit voice agent
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
├── .env.example            # Environment template
├── deploy.sh               # System setup script
├── run_bot.sh              # Telegram bot launcher
├── run_api.sh              # API server launcher
├── run_livekit.sh          # LiveKit agent launcher
├── alrah-bot.service       # Systemd service for bot
├── alrah-api.service       # Systemd service for API
├── livekit-client.js       # LiveKit JavaScript library
├── working_livekit.html    # Web demo interface
├── https_server.py         # HTTPS development server
├── cert.pem / key.pem      # SSL certificates
├── README.md               # Project overview
├── API.md                  # API documentation
├── LIVEKIT.md              # LiveKit integration guide
├── WEB_APP_INTEGRATION.md  # Web app integration guide
└── project-doc.md          # This comprehensive documentation
```

## 🚀 Installation & Setup

### Prerequisites

- **Linux Server** (Ubuntu/Debian recommended)
- **Python 3.8+**
- **FFmpeg** for audio processing
- **OpenAI API Key**
- **Pinecone API Key**
- **Telegram Bot Token**
- **LiveKit Server** (optional, for real-time voice)

### Quick Installation

```bash
# Clone or navigate to project directory
cd /root/tel-projcets/alrah-ai

# Run setup script
./deploy.sh

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys

# Start services
sudo systemctl start alrah-bot.service
sudo systemctl start alrah-api.service
```

### Environment Configuration

```bash
# Required API Keys
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=your_pinecone_index_name

# Optional LiveKit Configuration
LIVEKIT_URL=wss://your-livekit-server.com
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
```

## 📡 API Documentation

### Base URL
```
http://your-server-ip:8000
```

### Authentication
No authentication required for current endpoints.

### Core Endpoints

#### 1. Health Check
```http
GET /
```
**Response:**
```json
{
  "message": "Alrah AI API is running"
}
```

#### 2. Text Query
```http
POST /query/text
Content-Type: application/json

{
  "text": "ما هو حكم الصلاة؟"
}
```
**Response:**
```json
{
  "response": "الصلاة واجبة على كل مسلم بالغ عاقل...",
  "transcription": null
}
```

#### 3. Voice Query
```http
POST /query/voice
Content-Type: multipart/form-data

file: [audio file - .ogg, .mp3, .wav, .m4a]
```
**Response:**
```json
{
  "response": "الصلاة واجبة على كل مسلم بالغ عاقل...",
  "transcription": "ما هو حكم الصلاة؟"
}
```

#### 4. Text Query with Audio Response
```http
POST /query/text/audio
Content-Type: application/json

{
  "text": "ما هو حكم الصلاة؟"
}
```
**Response:** MP3 audio file

#### 5. Voice Query with Audio Response
```http
POST /query/voice/audio
Content-Type: multipart/form-data

file: [audio file]
```
**Response:** MP3 audio file

#### 6. Text-to-Speech Only
```http
POST /tts
Content-Type: application/json

{
  "text": "النص المراد تحويله إلى صوت"
}
```
**Response:** MP3 audio file

### LiveKit Integration Endpoints

#### 7. Generate LiveKit Token
```http
POST /livekit/token
Content-Type: application/json

{
  "user_id": "user123",
  "user_name": "Ahmed",
  "room_name": "alrah-ai-room"
}
```
**Response:**
```json
{
  "token": "jwt_token_here",
  "livekit_url": "wss://your-livekit-server.com",
  "room_name": "alrah-ai-room"
}
```

#### 8. LiveKit Status
```http
GET /livekit/status
```
**Response:**
```json
{
  "livekit_configured": true,
  "livekit_url": "wss://your-livekit-server.com",
  "agent_running": "Check agent service separately"
}
```

### Error Responses

#### 400 Bad Request
```json
{
  "detail": "Invalid request format"
}
```

#### 500 Internal Server Error
```json
{
  "detail": "خطأ في معالجة الاستعلام"
}
```

## 🤖 Telegram Bot

### Features
- **Voice Message Processing** - Automatic transcription and intelligent responses
- **Text Message Support** - Direct text queries
- **Typing Indicators** - Shows bot activity during processing
- **Voice Responses** - AI responds with synthesized Arabic voice
- **Error Handling** - Graceful error messages in Arabic

### Usage
1. Start conversation with your bot
2. Send voice messages in Arabic
3. Send text messages for text responses
4. Bot searches the religious library and provides contextual answers

### Bot Commands
- Voice messages → Voice responses
- Text messages → Text responses
- Automatic language detection
- Context-aware responses

## 🌐 Web Integration

### LiveKit Real-time Voice

#### HTML Integration
```html
<!DOCTYPE html>
<html>
<head>
    <script src="./livekit-client.js"></script>
</head>
<body>
    <button id="connect">Connect to Voice Assistant</button>
    <script>
        // Your LiveKit integration code
    </script>
</body>
</html>
```

#### JavaScript Integration
```javascript
// Get token from API
const tokenResponse = await fetch('http://your-server:8000/livekit/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: 'user123' })
});

const { token, livekit_url } = await tokenResponse.json();

// Connect to LiveKit
const room = new LivekitClient.Room();
await room.connect(livekit_url, token);
await room.localParticipant.enableCameraAndMicrophone(false, true);
```

### REST API Integration

#### JavaScript Example
```javascript
// Text query with audio response
const response = await fetch('http://your-server:8000/query/text/audio', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: 'ما هو حكم الصلاة؟' })
});
const audioBlob = await response.blob();
const audioUrl = URL.createObjectURL(audioBlob);
const audio = new Audio(audioUrl);
audio.play();
```

#### Python Example
```python
import requests

# Text query
response = requests.post(
    'http://your-server:8000/query/text',
    json={'text': 'ما هو حكم الصلاة؟'}
)
result = response.json()
print(result['response'])
```

## 🔧 System Services

### Service Management

#### Telegram Bot Service
```bash
# Start/Stop/Restart
sudo systemctl start alrah-bot.service
sudo systemctl stop alrah-bot.service
sudo systemctl restart alrah-bot.service

# View logs
sudo journalctl -u alrah-bot.service -f

# Enable auto-start
sudo systemctl enable alrah-bot.service
```

#### API Service
```bash
# Start/Stop/Restart
sudo systemctl start alrah-api.service
sudo systemctl stop alrah-api.service
sudo systemctl restart alrah-api.service

# View logs
sudo journalctl -u alrah-api.service -f

# Enable auto-start
sudo systemctl enable alrah-api.service
```

### Service Status Check
```bash
# Check all services
sudo systemctl status alrah-bot.service
sudo systemctl status alrah-api.service

# Check resource usage
ps aux | grep python
netstat -tlnp | grep :8000
```

## 🔒 HTTPS Setup

### Self-Signed Certificate (Development)
```bash
# Generate certificate
./create_ssl.sh

# Start HTTPS server
python3 https_server.py
```

### Production SSL (Let's Encrypt)
```bash
# Install certbot
sudo apt install certbot

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com

# Configure nginx/apache with certificate
```

### Cloudflare SSL (Recommended)
1. Point domain to server IP
2. Add domain to Cloudflare
3. Enable SSL in dashboard
4. Automatic HTTPS with no server changes

## 🎛️ Configuration Options

### Performance Tuning

#### API Server
- **Async Processing** - All OpenAI calls run asynchronously
- **Thread Pool** - 4 worker threads for concurrent requests
- **Context Optimization** - Reduced context size for faster responses
- **Token Limits** - 300 tokens max for quicker generation

#### Pinecone Search
- **Top-K Results** - Limited to 5 matches for speed
- **Similarity Threshold** - 0.3 for Arabic content
- **Context Truncation** - 2000 characters max

#### OpenAI Models
- **STT** - Whisper-1 with Arabic language specification
- **LLM** - GPT-4o-mini for fast, quality responses
- **TTS** - TTS-1 with "alloy" voice
- **Embeddings** - text-embedding-3-small

### System Prompt
The AI uses a specialized system prompt for مكتبة الرحيق المختوم:

```
أنت مساعد ذكي متخصص في مكتبة الرحيق المختوم للشيخ محمد اليعقوبي. 
أجب باللغة العربية الفصحى بأسلوب علمي مختصر ومفيد.
```

## 📊 Monitoring & Logs

### Log Locations
```bash
# Systemd service logs
sudo journalctl -u alrah-bot.service
sudo journalctl -u alrah-api.service

# Application logs
tail -f /var/log/alrah-ai/bot.log
tail -f /var/log/alrah-ai/api.log
```

### Health Monitoring
```bash
# API health check
curl http://localhost:8000/

# LiveKit status
curl http://localhost:8000/livekit/status

# Service status
systemctl is-active alrah-bot.service
systemctl is-active alrah-api.service
```

### Performance Metrics
- **Response Time** - Typically 2-5 seconds for voice queries
- **Concurrent Users** - Supports multiple simultaneous requests
- **Memory Usage** - ~50MB per service
- **CPU Usage** - Moderate during AI processing

## 🔍 Troubleshooting

### Common Issues

#### "LiveKit library not loaded"
**Solution:** Copy `livekit-client.js` to your web app directory or use CDN fallback

#### "MediaDevices undefined"
**Solution:** Use HTTPS or localhost for microphone access

#### "Token generation failed"
**Solution:** Check LiveKit credentials in `.env` file

#### "Context length exceeded"
**Solution:** Already fixed - using GPT-4o-mini with 128k context window

#### "CORS blocked"
**Solution:** Already configured - API includes proper CORS headers

### Debug Commands
```bash
# Test API endpoints
curl -X POST "http://localhost:8000/query/text" \
     -H "Content-Type: application/json" \
     -d '{"text": "test"}'

# Check service logs
sudo journalctl -u alrah-api.service -n 50

# Test LiveKit token
curl -X POST "http://localhost:8000/livekit/token" \
     -H "Content-Type: application/json" \
     -d '{"user_id": "test"}'
```

## 🚀 Deployment

### Development Environment
```bash
# Local testing
./run_api.sh
./run_bot.sh

# HTTPS testing
python3 https_server.py
```

### Production Deployment
```bash
# Install as system services
sudo cp *.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable alrah-bot.service
sudo systemctl enable alrah-api.service
sudo systemctl start alrah-bot.service
sudo systemctl start alrah-api.service
```

### Docker Deployment (Optional)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "api.py"]
```

## 📈 Scaling Considerations

### Horizontal Scaling
- **Load Balancer** - Nginx/HAProxy for multiple API instances
- **Database** - Pinecone handles distributed vector search
- **Caching** - Redis for frequent queries
- **CDN** - CloudFlare for static assets

### Vertical Scaling
- **CPU** - More cores for concurrent processing
- **Memory** - 4GB+ recommended for production
- **Storage** - SSD for faster model loading
- **Network** - High bandwidth for voice processing

## 🔐 Security

### API Security
- **Rate Limiting** - Implement request throttling
- **Input Validation** - Sanitize all user inputs
- **HTTPS Only** - Force SSL in production
- **API Keys** - Secure storage of credentials

### Data Privacy
- **No Data Storage** - Queries not permanently stored
- **Encrypted Transit** - All API calls over HTTPS
- **Temporary Files** - Audio files automatically deleted
- **Compliance** - GDPR/privacy law considerations

## 📚 Additional Resources

### Documentation Files
- `README.md` - Project overview and quick start
- `API.md` - Detailed API reference
- `LIVEKIT.md` - LiveKit integration guide
- `WEB_APP_INTEGRATION.md` - Web application integration

### External Dependencies
- **OpenAI API** - https://platform.openai.com/docs
- **Pinecone** - https://docs.pinecone.io/
- **LiveKit** - https://docs.livekit.io/
- **Telegram Bot API** - https://core.telegram.org/bots/api

### Support & Community
- **GitHub Issues** - Report bugs and feature requests
- **Documentation** - Comprehensive guides included
- **API Testing** - Interactive docs at `/docs` endpoint

## 🎯 Future Enhancements

### Planned Features
- **Multi-language Support** - Additional Arabic dialects
- **Voice Cloning** - Custom voice synthesis
- **Advanced Analytics** - Usage statistics and insights
- **Mobile SDKs** - Native iOS/Android integration
- **Webhook Support** - Real-time notifications
- **Admin Dashboard** - Web-based management interface

### Technical Improvements
- **Caching Layer** - Redis for frequent queries
- **Database Integration** - PostgreSQL for user data
- **Monitoring** - Prometheus/Grafana metrics
- **CI/CD Pipeline** - Automated deployment
- **Load Testing** - Performance benchmarking
- **Security Audit** - Penetration testing

---

## 📞 Contact & Support

For technical support, feature requests, or integration assistance, please refer to the documentation files or create an issue in the project repository.

**Project Status:** ✅ Production Ready
**Last Updated:** October 2025
**Version:** 1.0.0

---

*This documentation covers the complete Alrah AI system. For specific integration examples, refer to the individual documentation files included in the project.*
