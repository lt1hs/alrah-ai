import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import openai
from pinecone import Pinecone
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArabicVoiceBot:
    def __init__(self):
        # Initialize APIs
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        self.index = pc.Index(os.getenv('PINECONE_INDEX_NAME'))
        
    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            # Send typing indicator and processing message
            await update.message.chat.send_action(action="typing")
            processing_msg = await update.message.reply_text("جار التحليل...")
            
            # Download voice message
            voice_file = await update.message.voice.get_file()
            
            with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as temp_file:
                await voice_file.download_to_drive(temp_file.name)
                
                # Transcribe with OpenAI Whisper (supports .ogg directly)
                await update.message.chat.send_action(action="typing")
                with open(temp_file.name, 'rb') as audio_file:
                    transcript = self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language="ar"
                    )
                
                # Get embedding for the transcribed text
                await update.message.chat.send_action(action="typing")
                embedding_response = self.openai_client.embeddings.create(
                    model="text-embedding-3-small",
                    input=transcript.text
                )
                
                # Query Pinecone
                await update.message.chat.send_action(action="typing")
                results = self.index.query(
                    vector=embedding_response.data[0].embedding,
                    top_k=10,
                    include_metadata=True,
                    include_values=False
                )
                
                # Debug: log the search results
                logger.info(f"Transcribed text: {transcript.text}")
                logger.info(f"Found {len(results.matches)} matches")
                for i, match in enumerate(results.matches):
                    logger.info(f"Match {i+1}: Score={match.score}, Text={match.metadata.get('text', '')[:100]}...")
                
                # Build context from Pinecone results (use lower threshold for Arabic)
                context_texts = []
                for match in results.matches:
                    if match.score > 0.3:  # Lower threshold for Arabic content
                        context_texts.append(match.metadata.get('text', ''))
                
                # If no good matches, try all top results
                if not context_texts:
                    context_texts = [match.metadata.get('text', '') for match in results.matches[:3]]
                
                # Truncate context to fit token limits
                context_text = "\n".join(context_texts) if context_texts else "لا توجد معلومات متاحة في قاعدة البيانات"
                if len(context_text) > 4000:  # Keep context under ~4000 chars to leave room for system prompt
                    context_text = context_text[:4000] + "..."
                
                # Generate response with OpenAI
                await update.message.chat.send_action(action="typing")
                system_prompt = """أنت مساعد ذكي متخصص في مكتبة الرحيق المختوم، المكتبة الرقمية الشاملة لمؤلفات سماحة المرجع الديني الشيخ محمد اليعقوبي (دام ظله).

أنت خبير في:
- التفسير والفقه والأصول والرجال واللغة والأدب والتاريخ
- العقائد الإسلامية وولاية أهل البيت (عليهم السلام)
- القضايا المعاصرة: التربية، الأخلاق، الاجتماع، الاقتصاد، السياسة
- الشخصية الإسلامية والتنمية البشرية
- القضايا الحسينية والفاطمية والمهدوية
- المنبر الحسيني وصلاة الجمعة ودور المسجد

مهمتك:
1. الإجابة باللغة العربية الفصحى بأسلوب علمي رصين
2. الاستناد حصرياً إلى المحتوى المتوفر في قاعدة البيانات
3. تقديم إجابات شاملة ومفصلة مع الاستشهاد بالنصوص الأصلية
4. إذا لم تجد معلومات كافية، اذكر ذلك بوضوح واقترح البحث في مواضيع ذات صلة

أسلوبك: علمي، محترم، واضح، يليق بمقام المرجعية الدينية."""
                
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"السياق المتوفر: {context_text}\n\nالسؤال: {transcript.text}"}
                    ],
                    max_tokens=500
                )
                
                # Convert response to speech
                await update.message.chat.send_action(action="record_voice")
                speech_response = self.openai_client.audio.speech.create(
                    model="tts-1",
                    voice="alloy",
                    input=response.choices[0].message.content
                )
                
                # Save audio to temporary file
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as audio_file:
                    speech_response.stream_to_file(audio_file.name)
                    
                    # Send voice message
                    with open(audio_file.name, 'rb') as voice:
                        await update.message.reply_voice(voice=voice)
                    
                    # Delete processing message
                    await processing_msg.delete()
                    
                    # Cleanup audio file
                    os.unlink(audio_file.name)
                
                # Cleanup
                os.unlink(temp_file.name)
                
        except Exception as e:
            logger.error(f"Error processing voice: {e}")
            # Delete processing message if it exists
            try:
                await processing_msg.delete()
            except:
                pass
            await update.message.reply_text("عذراً، حدث خطأ في معالجة الرسالة الصوتية")

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            await update.message.chat.send_action(action="typing")
            
            # Get embedding for the text
            embedding_response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=update.message.text
            )
            
            # Query Pinecone
            await update.message.chat.send_action(action="typing")
            results = self.index.query(
                vector=embedding_response.data[0].embedding,
                top_k=10,
                include_metadata=True,
                include_values=False
            )
            
            # Build context from Pinecone results
            context_texts = []
            for match in results.matches:
                if match.score > 0.3:
                    context_texts.append(match.metadata.get('text', ''))
            
            if not context_texts:
                context_texts = [match.metadata.get('text', '') for match in results.matches[:3]]
            
            # Truncate context to fit token limits
            context_text = "\n".join(context_texts) if context_texts else "لا توجد معلومات متاحة في قاعدة البيانات"
            if len(context_text) > 4000:  # Keep context under ~4000 chars to leave room for system prompt
                context_text = context_text[:4000] + "..."
            
            # Generate response with OpenAI
            await update.message.chat.send_action(action="typing")
            system_prompt = """أنت مساعد ذكي متخصص في مكتبة الرحيق المختوم، المكتبة الرقمية الشاملة لمؤلفات سماحة المرجع الديني الشيخ محمد اليعقوبي (دام ظله).

أنت خبير في:
- التفسير والفقه والأصول والرجال واللغة والأدب والتاريخ
- العقائد الإسلامية وولاية أهل البيت (عليهم السلام)
- القضايا المعاصرة: التربية، الأخلاق، الاجتماع، الاقتصاد، السياسة
- الشخصية الإسلامية والتنمية البشرية
- القضايا الحسينية والفاطمية والمهدوية
- المنبر الحسيني وصلاة الجمعة ودور المسجد

مهمتك:
1. الإجابة باللغة العربية الفصحى بأسلوب علمي رصين
2. الاستناد حصرياً إلى المحتوى المتوفر في قاعدة البيانات
3. تقديم إجابات شاملة ومفصلة مع الاستشهاد بالنصوص الأصلية
4. إذا لم تجد معلومات كافية، اذكر ذلك بوضوح واقترح البحث في مواضيع ذات صلة

أسلوبك: علمي، محترم، واضح، يليق بمقام المرجعية الدينية."""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"السياق المتوفر: {context_text}\n\nالسؤال: {update.message.text}"}
                ],
                max_tokens=500
            )
            
            await update.message.reply_text(response.choices[0].message.content)
                
        except Exception as e:
            logger.error(f"Error processing text: {e}")
            await update.message.reply_text("عذراً، حدث خطأ في معالجة الرسالة")

def main():
    bot = ArabicVoiceBot()
    
    app = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()
    app.add_handler(MessageHandler(filters.VOICE, bot.handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_text))
    
    app.run_polling()

if __name__ == '__main__':
    main()
