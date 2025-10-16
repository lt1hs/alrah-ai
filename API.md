# Alrah AI API Documentation

REST API for querying مكتبة الرحيق المختوم (Sheikh Al-Yaqoubi's digital library) using text and voice inputs.

## Base URL
```
http://your-server-ip:8000
```

## Authentication
No authentication required.

## Endpoints

### 1. Health Check
**GET** `/`

Check if the API is running.

**Response:**
```json
{
  "message": "Alrah AI API is running"
}
```

### 2. Text Query
**POST** `/query/text`

Submit a text question in Arabic and get an AI-generated response based on the religious library.

**Request:**
```json
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

**cURL Example:**
```bash
curl -X POST "http://your-server:8000/query/text" \
     -H "Content-Type: application/json" \
     -d '{"text": "ما هو حكم الصلاة؟"}'
```

### 3. Voice Query
**POST** `/query/voice`

Upload an audio file (voice message) and get both transcription and AI response.

**Request:**
- Content-Type: `multipart/form-data`
- Field: `file` (audio file - supports .ogg, .mp3, .wav, .m4a)

**Response:**
```json
{
  "response": "الصلاة واجبة على كل مسلم بالغ عاقل...",
  "transcription": "ما هو حكم الصلاة؟"
}
```

**cURL Example:**
```bash
curl -X POST "http://your-server:8000/query/voice" \
     -F "file=@voice_message.ogg"
```

## Response Schema

### QueryResponse
| Field | Type | Description |
|-------|------|-------------|
| `response` | string | AI-generated response in Arabic |
| `transcription` | string | Voice transcription (null for text queries) |

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request format"
}
```

### 500 Internal Server Error
```json
{
  "detail": "خطأ في معالجة الاستعلام"
}
```

## Integration Examples

### JavaScript/Frontend
```javascript
// Text query
async function queryText(question) {
  const response = await fetch('http://your-server:8000/query/text', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: question })
  });
  return await response.json();
}

// Voice query
async function queryVoice(audioFile) {
  const formData = new FormData();
  formData.append('file', audioFile);
  
  const response = await fetch('http://your-server:8000/query/voice', {
    method: 'POST',
    body: formData
  });
  return await response.json();
}
```

### Python
```python
import requests

# Text query
def query_text(question):
    response = requests.post(
        'http://your-server:8000/query/text',
        json={'text': question}
    )
    return response.json()

# Voice query
def query_voice(audio_file_path):
    with open(audio_file_path, 'rb') as f:
        response = requests.post(
            'http://your-server:8000/query/voice',
            files={'file': f}
        )
    return response.json()
```

### PHP
```php
// Text query
function queryText($question) {
    $data = json_encode(['text' => $question]);
    $context = stream_context_create([
        'http' => [
            'method' => 'POST',
            'header' => 'Content-Type: application/json',
            'content' => $data
        ]
    ]);
    return json_decode(file_get_contents('http://your-server:8000/query/text', false, $context), true);
}
```

## Interactive Documentation

Visit `http://your-server:8000/docs` for interactive API documentation with:
- Live API testing interface
- Request/response examples
- Schema definitions

## OpenAPI Specification

Get the OpenAPI/Swagger specification at:
```
http://your-server:8000/openapi.json
```

## Rate Limits
No rate limits currently implemented.

## Supported Audio Formats
- OGG Vorbis (.ogg)
- MP3 (.mp3)
- WAV (.wav)
- M4A (.m4a)

## Language Support
- **Input**: Arabic text and voice
- **Output**: Arabic text responses

## Technology Stack
- **FastAPI**: Web framework
- **OpenAI Whisper**: Voice transcription
- **OpenAI GPT-4o-mini**: Response generation
- **Pinecone**: Vector database for semantic search
- **Python 3.8+**: Runtime environment

## Deployment
The API runs as a systemd service on Linux:
```bash
sudo systemctl status alrah-api.service
sudo systemctl restart alrah-api.service
sudo journalctl -u alrah-api.service -f
```

## Support
For issues or questions, check the service logs:
```bash
sudo journalctl -u alrah-api.service -f
```
