# Web App Integration Guide
## Real-time Voice Conversation with Arabic AI

This guide shows how to integrate real-time voice conversation into your web application using the Alrah AI system.

## Prerequisites

- ✅ **HTTPS Required** - Microphone access needs secure connection
- ✅ **Modern Browser** - Chrome, Firefox, Safari, Edge
- ✅ **API Server Running** - Your backend at `http://91.109.114.158:8000`

## Quick Setup

### 1. Include LiveKit Client

```html
<!-- Option A: Use your local copy -->
<script src="./livekit-client.js"></script>

<!-- Option B: Use CDN (if working) -->
<script src="https://unpkg.com/livekit-client@1.15.13/dist/livekit-client.umd.js"></script>
```

### 2. Basic HTML Structure

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Arabic AI Voice Assistant</title>
    <script src="./livekit-client.js"></script>
</head>
<body>
    <div id="status">Ready to connect</div>
    <button id="connect">🎙️ Start Voice Chat</button>
    <button id="disconnect" disabled>❌ End Chat</button>
    <div id="messages"></div>
</body>
</html>
```

### 3. JavaScript Integration

```javascript
const API_BASE = 'http://91.109.114.158:8000';
let room = null;
let connected = false;

// Get LiveKit token from your API
async function getToken(userId) {
    const response = await fetch(`${API_BASE}/livekit/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            user_id: userId,
            user_name: 'User',
            room_name: 'alrah-ai-room'
        })
    });
    return await response.json();
}

// Connect to voice assistant
async function connectVoiceAssistant() {
    try {
        // Get token
        const tokenData = await getToken('user_' + Date.now());
        
        // Create room
        room = new LivekitClient.Room({
            adaptiveStream: true,
            dynacast: true,
        });
        
        // Set up event listeners
        room.on(LivekitClient.RoomEvent.Connected, () => {
            console.log('Connected to voice assistant');
            connected = true;
            updateUI();
        });
        
        room.on(LivekitClient.RoomEvent.TrackSubscribed, (track, publication, participant) => {
            if (track.kind === LivekitClient.Track.Kind.Audio) {
                // Play AI voice response
                const audioElement = track.attach();
                audioElement.autoplay = true;
                document.body.appendChild(audioElement);
            }
        });
        
        room.on(LivekitClient.RoomEvent.Disconnected, () => {
            connected = false;
            updateUI();
        });
        
        // Connect to room
        await room.connect(tokenData.livekit_url, tokenData.token);
        
        // Enable microphone
        await room.localParticipant.enableCameraAndMicrophone(false, true);
        
    } catch (error) {
        console.error('Connection failed:', error);
        alert('Connection failed: ' + error.message);
    }
}

// Disconnect from voice assistant
function disconnectVoiceAssistant() {
    if (room && connected) {
        room.disconnect();
        room = null;
        connected = false;
        updateUI();
    }
}

// Update UI based on connection state
function updateUI() {
    const status = document.getElementById('status');
    const connectBtn = document.getElementById('connect');
    const disconnectBtn = document.getElementById('disconnect');
    
    if (connected) {
        status.textContent = 'Connected - Speak in Arabic!';
        connectBtn.disabled = true;
        disconnectBtn.disabled = false;
    } else {
        status.textContent = 'Ready to connect';
        connectBtn.disabled = false;
        disconnectBtn.disabled = true;
    }
}

// Event listeners
document.getElementById('connect').addEventListener('click', connectVoiceAssistant);
document.getElementById('disconnect').addEventListener('click', disconnectVoiceAssistant);
```

## Advanced Integration

### React Component Example

```jsx
import React, { useState, useEffect } from 'react';

const VoiceAssistant = () => {
    const [connected, setConnected] = useState(false);
    const [room, setRoom] = useState(null);
    const [status, setStatus] = useState('Ready');

    const connectVoice = async () => {
        try {
            setStatus('Connecting...');
            
            // Get token
            const response = await fetch('http://91.109.114.158:8000/livekit/token', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: 'user_' + Date.now() })
            });
            const tokenData = await response.json();
            
            // Create and connect room
            const newRoom = new LivekitClient.Room();
            
            newRoom.on(LivekitClient.RoomEvent.Connected, () => {
                setConnected(true);
                setStatus('Connected - Speak now!');
            });
            
            newRoom.on(LivekitClient.RoomEvent.TrackSubscribed, (track) => {
                if (track.kind === LivekitClient.Track.Kind.Audio) {
                    const audio = track.attach();
                    audio.autoplay = true;
                    document.body.appendChild(audio);
                }
            });
            
            await newRoom.connect(tokenData.livekit_url, tokenData.token);
            await newRoom.localParticipant.enableCameraAndMicrophone(false, true);
            
            setRoom(newRoom);
            
        } catch (error) {
            setStatus('Connection failed');
            console.error(error);
        }
    };

    const disconnect = () => {
        if (room) {
            room.disconnect();
            setRoom(null);
            setConnected(false);
            setStatus('Disconnected');
        }
    };

    return (
        <div>
            <h2>🎙️ Arabic AI Voice Assistant</h2>
            <p>Status: {status}</p>
            <button onClick={connectVoice} disabled={connected}>
                Connect
            </button>
            <button onClick={disconnect} disabled={!connected}>
                Disconnect
            </button>
        </div>
    );
};

export default VoiceAssistant;
```

### Vue.js Component Example

```vue
<template>
  <div>
    <h2>🎙️ Arabic AI Voice Assistant</h2>
    <p>Status: {{ status }}</p>
    <button @click="connect" :disabled="connected">Connect</button>
    <button @click="disconnect" :disabled="!connected">Disconnect</button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      connected: false,
      room: null,
      status: 'Ready'
    }
  },
  methods: {
    async connect() {
      try {
        this.status = 'Connecting...';
        
        // Get token
        const response = await fetch('http://91.109.114.158:8000/livekit/token', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id: 'user_' + Date.now() })
        });
        const tokenData = await response.json();
        
        // Connect to room
        this.room = new LivekitClient.Room();
        
        this.room.on(LivekitClient.RoomEvent.Connected, () => {
          this.connected = true;
          this.status = 'Connected - Speak now!';
        });
        
        this.room.on(LivekitClient.RoomEvent.TrackSubscribed, (track) => {
          if (track.kind === LivekitClient.Track.Kind.Audio) {
            const audio = track.attach();
            audio.autoplay = true;
            document.body.appendChild(audio);
          }
        });
        
        await this.room.connect(tokenData.livekit_url, tokenData.token);
        await this.room.localParticipant.enableCameraAndMicrophone(false, true);
        
      } catch (error) {
        this.status = 'Connection failed';
        console.error(error);
      }
    },
    
    disconnect() {
      if (this.room) {
        this.room.disconnect();
        this.room = null;
        this.connected = false;
        this.status = 'Disconnected';
      }
    }
  }
}
</script>
```

## Error Handling

```javascript
// Check browser support
function checkBrowserSupport() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Microphone access requires HTTPS or localhost');
    }
    
    if (typeof LivekitClient === 'undefined') {
        throw new Error('LiveKit library not loaded');
    }
    
    return true;
}

// Enhanced connection with error handling
async function connectWithErrorHandling() {
    try {
        checkBrowserSupport();
        await connectVoiceAssistant();
    } catch (error) {
        if (error.message.includes('HTTPS')) {
            alert('Please access this page via HTTPS for microphone access');
        } else if (error.message.includes('Permission')) {
            alert('Please allow microphone access in your browser');
        } else {
            alert('Connection failed: ' + error.message);
        }
    }
}
```

## Deployment Checklist

### Development
- ✅ Use `https://localhost:8443` for local testing
- ✅ Accept self-signed certificate warnings
- ✅ Allow microphone permissions

### Production
- ✅ Valid SSL certificate (Let's Encrypt or commercial)
- ✅ Domain name pointing to your server
- ✅ CORS properly configured
- ✅ Firewall allows HTTPS (port 443)

## API Endpoints Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/livekit/token` | POST | Get LiveKit connection token |
| `/livekit/status` | GET | Check LiveKit configuration |
| `/query/text` | POST | Text query (fallback) |
| `/query/voice` | POST | Voice file upload (fallback) |

## Testing Your Integration

1. **Open browser console** to see connection logs
2. **Test microphone access** - should see permission prompt
3. **Speak in Arabic** - should see audio activity
4. **Listen for responses** - AI should respond with voice
5. **Check network tab** - verify API calls succeed

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "MediaDevices undefined" | Use HTTPS or localhost |
| "LiveKit not defined" | Check script loading |
| "Token failed" | Verify API server running |
| "No audio response" | Check browser audio settings |
| "Connection timeout" | Check firewall/network |

## Example Files

- **Working Demo**: `https://91.109.114.158:8443/working_livekit.html`
- **API Documentation**: `http://91.109.114.158:8000/docs`
- **Source Code**: Available in your server directory

Your Arabic AI voice assistant is now ready for web app integration! 🚀
