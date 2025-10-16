from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
import openai
from pinecone import Pinecone
import os
import tempfile
from dotenv import load_dotenv
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import jwt
import time

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Alrah AI API", description="Arabic Religious Library Query API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Explicitly allow OPTIONS
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],  # Expose all headers
)

class TextQuery(BaseModel):
    text: str

class TTSRequest(BaseModel):
    text: str

class LiveKitTokenRequest(BaseModel):
    user_id: str
    user_name: str = "User"
    room_name: str = "alrah-ai-room"

class LiveKitTokenResponse(BaseModel):
    token: str
    livekit_url: str
    room_name: str

class QueryResponse(BaseModel):
    response: str
    transcription: str = None

class AlrahAI:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        self.index = pc.Index(os.getenv('PINECONE_INDEX_NAME'))
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    async def search_and_respond(self, query_text: str) -> str:
        # Run embedding and search in parallel
        embedding_task = asyncio.create_task(self._get_embedding(query_text))
        
        embedding = await embedding_task
        
        # Query Pinecone
        results = await asyncio.get_event_loop().run_in_executor(
            self.executor, self._query_pinecone, embedding
        )
        
        # Build context (reduced size for faster processing)
        context_texts = []
        for match in results.matches[:5]:  # Reduced from 10 to 5
            if match.score > 0.3:
                context_texts.append(match.metadata.get('text', ''))
        
        if not context_texts:
            context_texts = [match.metadata.get('text', '') for match in results.matches[:2]]  # Reduced from 3 to 2
        
        context_text = "\n".join(context_texts) if context_texts else "لا توجد معلومات متاحة في قاعدة البيانات"
        if len(context_text) > 2000:  # Reduced from 4000 to 2000
            context_text = context_text[:2000] + "..."
        
        # Generate response with shorter system prompt
        system_prompt = """أنت مساعد ذكي متخصص في مكتبة الرحيق المختوم للشيخ محمد اليعقوبي. أجب باللغة العربية الفصحى بأسلوب علمي مختصر ومفيد."""
        
        response = await asyncio.get_event_loop().run_in_executor(
            self.executor, self._generate_response, system_prompt, context_text, query_text
        )
        
        return response.choices[0].message.content
    
    async def _get_embedding(self, text: str):
        return await asyncio.get_event_loop().run_in_executor(
            self.executor, self._create_embedding, text
        )
    
    def _create_embedding(self, text: str):
        return self.openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        ).data[0].embedding
    
    def _query_pinecone(self, embedding):
        return self.index.query(
            vector=embedding,
            top_k=5,  # Reduced from 10 to 5
            include_metadata=True,
            include_values=False
        )
    
    def _generate_response(self, system_prompt, context_text, query_text):
        return self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"السياق: {context_text}\n\nالسؤال: {query_text}"}
            ],
            max_tokens=300,  # Reduced from 500 to 300
            temperature=0.7  # Added for faster processing
        )
    
    def _transcribe_audio(self, file_path):
        with open(file_path, 'rb') as audio_file:
            return self.openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="ar"
            )

# Initialize AI instance
ai = AlrahAI()

@app.post("/query/text", response_model=QueryResponse)
async def query_text(query: TextQuery):
    try:
        response = await ai.search_and_respond(query.text)
        return QueryResponse(response=response)
    except Exception as e:
        logger.error(f"Error processing text query: {e}")
        raise HTTPException(status_code=500, detail="خطأ في معالجة الاستعلام")

@app.post("/query/voice", response_model=QueryResponse)
async def query_voice(file: UploadFile = File(...)):
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file.flush()
            
            # Transcribe audio in executor
            transcript = await asyncio.get_event_loop().run_in_executor(
                ai.executor, ai._transcribe_audio, temp_file.name
            )
            
            # Get response
            response = await ai.search_and_respond(transcript.text)
            
            # Cleanup
            os.unlink(temp_file.name)
            
            return QueryResponse(response=response, transcription=transcript.text)
            
    except Exception as e:
        logger.error(f"Error processing voice query: {e}")
        raise HTTPException(status_code=500, detail="خطأ في معالجة الرسالة الصوتية")

@app.options("/{path:path}")
async def options_handler(path: str):
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.get("/")
async def root():
    return {"message": "Alrah AI API is running"}

@app.post("/tts")
async def text_to_speech(request: TTSRequest):
    try:
        # Convert text directly to speech without processing as question
        speech_response = ai.openai_client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=request.text
        )
        
        # Return audio as response
        audio_content = speech_response.content
        return Response(
            content=audio_content,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=tts.mp3"}
        )
        
    except Exception as e:
        logger.error(f"Error in TTS: {e}")
        raise HTTPException(status_code=500, detail="خطأ في تحويل النص إلى صوت")

@app.post("/query/text/audio")
async def query_text_audio(query: TextQuery):
    try:
        response_text = ai.search_and_respond(query.text)
        
        # Convert response to speech
        speech_response = ai.openai_client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=response_text
        )
        
        # Return audio as response
        audio_content = speech_response.content
        return Response(
            content=audio_content,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=response.mp3"}
        )
        
    except Exception as e:
        logger.error(f"Error processing text to audio: {e}")
        raise HTTPException(status_code=500, detail="خطأ في معالجة الاستعلام الصوتي")

@app.post("/query/voice/audio")
async def query_voice_audio(file: UploadFile = File(...)):
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file.flush()
            
            # Transcribe audio
            with open(temp_file.name, 'rb') as audio_file:
                transcript = ai.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="ar"
                )
            
            # Get response
            response_text = ai.search_and_respond(transcript.text)
            
            # Convert response to speech
            speech_response = ai.openai_client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=response_text
            )
            
            # Cleanup
            os.unlink(temp_file.name)
            
            # Return audio as response
            audio_content = speech_response.content
            return Response(
                content=audio_content,
                media_type="audio/mpeg",
                headers={"Content-Disposition": "attachment; filename=response.mp3"}
            )
            
    except Exception as e:
        logger.error(f"Error processing voice to audio: {e}")
        raise HTTPException(status_code=500, detail="خطأ في معالجة الرسالة الصوتية")

@app.post("/livekit/token", response_model=LiveKitTokenResponse)
async def generate_livekit_token(request: LiveKitTokenRequest):
    try:
        api_key = os.getenv('LIVEKIT_API_KEY')
        api_secret = os.getenv('LIVEKIT_API_SECRET')
        livekit_url = os.getenv('LIVEKIT_URL', 'wss://your-livekit-server.com')
        
        if not api_key or not api_secret:
            raise HTTPException(status_code=500, detail="LiveKit credentials not configured")
        
        # Generate JWT token for LiveKit
        now = int(time.time())
        payload = {
            'iss': api_key,
            'sub': request.user_id,
            'name': request.user_name,
            'iat': now,
            'exp': now + 3600,  # 1 hour expiry
            'video': {
                'room': request.room_name,
                'roomJoin': True,
                'roomAdmin': False,
                'canPublish': True,
                'canSubscribe': True
            }
        }
        
        token = jwt.encode(payload, api_secret, algorithm='HS256')
        
        return LiveKitTokenResponse(
            token=token,
            livekit_url=livekit_url,
            room_name=request.room_name
        )
        
    except Exception as e:
        logger.error(f"Error generating LiveKit token: {e}")
        raise HTTPException(status_code=500, detail="خطأ في إنشاء رمز الاتصال")

@app.get("/livekit/status")
async def livekit_status():
    return {
        "livekit_configured": bool(os.getenv('LIVEKIT_API_KEY') and os.getenv('LIVEKIT_API_SECRET')),
        "livekit_url": os.getenv('LIVEKIT_URL', 'Not configured'),
        "agent_running": "Check agent service separately"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        timeout_keep_alive=30
    )
