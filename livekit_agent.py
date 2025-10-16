import asyncio
import logging
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli
from livekit.plugins import openai, silero
import os
from dotenv import load_dotenv
from pinecone import Pinecone

# Load environment variables
load_dotenv()

logger = logging.getLogger("alrah-voice-assistant")

class AlrahAIAssistant:
    def __init__(self):
        # Initialize Pinecone
        pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        self.index = pc.Index(os.getenv('PINECONE_INDEX_NAME'))
        
        # Initialize OpenAI client for embeddings
        import openai as openai_client
        self.openai_client = openai_client.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    async def search_and_respond(self, query_text: str) -> str:
        # Get embedding
        embedding_response = await asyncio.get_event_loop().run_in_executor(
            None, self._get_embedding, query_text
        )
        
        # Query Pinecone
        results = await asyncio.get_event_loop().run_in_executor(
            None, self._query_pinecone, embedding_response
        )
        
        # Build context
        context_texts = []
        for match in results.matches[:3]:
            if match.score > 0.3:
                context_texts.append(match.metadata.get('text', ''))
        
        context_text = "\n".join(context_texts) if context_texts else "لا توجد معلومات متاحة"
        if len(context_text) > 1000:
            context_text = context_text[:1000] + "..."
        
        return f"بناءً على مكتبة الرحيق المختوم: {context_text}"
    
    def _get_embedding(self, text: str):
        return self.openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        ).data[0].embedding
    
    def _query_pinecone(self, embedding):
        return self.index.query(
            vector=embedding,
            top_k=3,
            include_metadata=True,
            include_values=False
        )

async def entrypoint(ctx: JobContext):
    # Initialize AI assistant
    ai_assistant = AlrahAIAssistant()
    
    # Connect to room
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    
    # Initialize components
    stt = openai.STT(language="ar")
    llm = openai.LLM(model="gpt-4o-mini")
    tts = openai.TTS(voice="alloy")
    
    # Send welcome message
    await tts.asynthesize("السلام عليكم، أنا مساعدك الذكي لمكتبة الرحيق المختوم. كيف يمكنني مساعدتك؟")
    
    # Listen for audio
    async for event in ctx.room.on("track_published"):
        if event.track.kind == "audio":
            # Transcribe audio
            transcript = await stt.recognize(event.track)
            
            if transcript.text:
                logger.info(f"User said: {transcript.text}")
                
                # Get enhanced context from Pinecone
                enhanced_context = await ai_assistant.search_and_respond(transcript.text)
                
                # Generate response
                response = await llm.chat(
                    messages=[
                        {"role": "system", "content": "أنت مساعد ذكي متخصص في مكتبة الرحيق المختوم للشيخ محمد اليعقوبي. أجب باللغة العربية الفصحى بأسلوب علمي مختصر."},
                        {"role": "user", "content": f"{enhanced_context}\n\nالسؤال: {transcript.text}"}
                    ]
                )
                
                # Synthesize and play response
                await tts.asynthesize(response.content)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
