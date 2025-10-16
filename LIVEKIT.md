# LiveKit Real-Time Voice Assistant

Real-time voice conversation with مكتبة الرحيق المختوم using LiveKit WebRTC technology.

## Features

- **Real-time voice conversation** - No delays, natural conversation flow
- **Arabic speech recognition** - Powered by OpenAI Whisper
- **Intelligent responses** - Enhanced with Pinecone vector search
- **Arabic text-to-speech** - Natural voice responses
- **WebRTC technology** - Low latency, high quality audio

## Setup

### 1. Install Dependencies
```bash
source venv/bin/activate
pip install livekit livekit-agents livekit-plugins-openai livekit-plugins-silero
```

### 2. LiveKit Server Options

**Option A: Use LiveKit Cloud (Recommended)**
1. Sign up at [livekit.io](https://livekit.io)
2. Create a new project
3. Get your API keys and server URL

**Option B: Self-hosted LiveKit Server**
```bash
# Using Docker
docker run --rm -p 7880:7880 -p 7881:7881 -p 7882:7882/udp \
  livekit/livekit-server --dev
```

### 3. Configure Environment
Add to your `.env` file:
```
LIVEKIT_URL=wss://your-livekit-server.com
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
```

### 4. Run the Voice Assistant
```bash
./run_livekit.sh
```

## Usage

### Web Client Integration
```html
<!DOCTYPE html>
<html>
<head>
    <title>Alrah AI Voice Assistant</title>
    <script src="https://unpkg.com/livekit-client/dist/livekit-client.umd.js"></script>
</head>
<body>
    <button id="connect">Connect to Voice Assistant</button>
    <button id="disconnect">Disconnect</button>
    
    <script>
        const connectBtn = document.getElementById('connect');
        const disconnectBtn = document.getElementById('disconnect');
        let room;

        connectBtn.addEventListener('click', async () => {
            room = new LiveKit.Room();
            
            await room.connect('wss://your-livekit-server.com', 'your-token');
            
            // Enable microphone
            await room.localParticipant.enableCameraAndMicrophone(false, true);
            
            console.log('Connected to Alrah AI Voice Assistant');
        });

        disconnectBtn.addEventListener('click', () => {
            if (room) {
                room.disconnect();
            }
        });
    </script>
</body>
</html>
```

### Mobile App Integration
```javascript
// React Native example
import { Room, connect } from 'livekit-client';

const connectToVoiceAssistant = async () => {
  const room = new Room();
  
  await room.connect('wss://your-livekit-server.com', token);
  
  // Enable microphone
  await room.localParticipant.enableCameraAndMicrophone(false, true);
  
  console.log('Connected to voice assistant');
};
```

## Architecture

```
User Voice Input → LiveKit WebRTC → Voice Assistant Agent
                                          ↓
                                   OpenAI Whisper (STT)
                                          ↓
                                   Pinecone Vector Search
                                          ↓
                                   GPT-4o-mini Response
                                          ↓
                                   OpenAI TTS → LiveKit WebRTC → User
```

## Benefits Over HTTP API

| Feature | HTTP API | LiveKit |
|---------|----------|---------|
| **Latency** | 2-5 seconds | 200-500ms |
| **Conversation Flow** | Turn-based | Natural, real-time |
| **Interruptions** | Not supported | Supported |
| **Audio Quality** | Compressed files | High-quality WebRTC |
| **Bandwidth** | High (full audio files) | Optimized streaming |
| **User Experience** | Choppy | Smooth, natural |

## Deployment

### Production Deployment
```bash
# Create systemd service for LiveKit agent
sudo cp livekit-agent.service /etc/systemd/system/
sudo systemctl enable livekit-agent.service
sudo systemctl start livekit-agent.service
```

### Scaling
- Multiple agent instances can run simultaneously
- LiveKit handles load balancing automatically
- Each conversation gets its own room

## Token Generation

For production, you'll need to generate JWT tokens:

```python
from livekit import api

# Generate token for client
token = api.AccessToken(api_key, api_secret) \
    .with_identity("user-id") \
    .with_name("User Name") \
    .with_grants(api.VideoGrants(room_join=True, room="room-name")) \
    .to_jwt()
```

## Monitoring

Check agent status:
```bash
# View logs
sudo journalctl -u livekit-agent.service -f

# Check room status
curl -H "Authorization: Bearer $LIVEKIT_API_KEY" \
     https://your-livekit-server.com/twirp/livekit.RoomService/ListRooms
```

## Integration with Existing Services

The LiveKit agent can run alongside your existing:
- ✅ Telegram Bot (port internal)
- ✅ REST API (port 8000)
- ✅ LiveKit Agent (WebRTC)

All three services can share the same Pinecone database and OpenAI resources.

## Cost Considerations

- **LiveKit Cloud**: Pay per minute of usage
- **Self-hosted**: Server costs only
- **OpenAI**: Same STT/TTS costs as HTTP API
- **Bandwidth**: More efficient than file uploads

## Next Steps

1. Set up LiveKit server (cloud or self-hosted)
2. Install dependencies and configure environment
3. Test with web client
4. Integrate into your application
5. Deploy to production

This gives you a modern, real-time voice interface for your Arabic AI library! 🎙️
