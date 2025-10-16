import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ContextTypes
import openai
from pinecone import Pinecone
import tempfile
from dotenv import load_dotenv
from chat_manager import ChatManager

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
        self.chat_manager = ChatManager()
        self.user_sessions = {}  # user_id -> current_session_id
        
    def _get_or_create_session(self, user_id: int) -> str:
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = self.chat_manager.create_session(user_id)
        return self.user_sessions[user_id]
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        welcome_text = """مرحباً بك في مكتبة الرحيق المختوم 📚

يمكنك:
• إرسال رسائل صوتية أو نصية للاستفسار
• استخدام /menu لإدارة المحادثات

أرسل رسالتك أو اضغط /menu للبدء"""
        
        keyboard = [
            [InlineKeyboardButton("📋 القائمة الرئيسية", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)

    async def menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("💬 محادثة جديدة", callback_data="new_chat")],
            [InlineKeyboardButton("📋 قائمة المحادثات", callback_data="list_chats")],
            [InlineKeyboardButton("❌ إغلاق القائمة", callback_data="close_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("اختر من القائمة:", reply_markup=reply_markup)
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        if query.data == "new_chat":
            session_id = self.chat_manager.create_session(user_id)
            self.user_sessions[user_id] = session_id
            await query.edit_message_text(f"✅ تم إنشاء محادثة جديدة\nرقم المحادثة: {session_id}")
            
        elif query.data == "list_chats":
            sessions = self.chat_manager.list_user_sessions(user_id)
            if not sessions:
                await query.edit_message_text("لا توجد محادثات محفوظة")
                return
            
            keyboard = []
            for session in sessions[:8]:  # Show max 8 sessions
                keyboard.append([InlineKeyboardButton(
                    f"📝 {session['session_id']} ({session['message_count']} رسالة)",
                    callback_data=f"load_{session['session_id']}"
                )])
            keyboard.append([InlineKeyboardButton("🔙 العودة للقائمة", callback_data="back_to_menu")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("اختر محادثة للتحميل:", reply_markup=reply_markup)
            
        elif query.data.startswith("load_"):
            session_id = query.data.replace("load_", "")
            if self.chat_manager._load_session(user_id, session_id):
                self.user_sessions[user_id] = session_id
                
                # Show session options
                keyboard = [
                    [InlineKeyboardButton("🗑️ حذف هذه المحادثة", callback_data=f"delete_{session_id}")],
                    [InlineKeyboardButton("🔙 العودة للقائمة", callback_data="back_to_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(f"✅ تم تحميل المحادثة: {session_id}", reply_markup=reply_markup)
            else:
                await query.edit_message_text("❌ المحادثة غير موجودة")
                
        elif query.data.startswith("delete_"):
            session_id = query.data.replace("delete_", "")
            if self.chat_manager.delete_session(user_id, session_id):
                if self.user_sessions.get(user_id) == session_id:
                    del self.user_sessions[user_id]
                await query.edit_message_text(f"✅ تم حذف المحادثة: {session_id}")
            else:
                await query.edit_message_text("❌ المحادثة غير موجودة")
                
        elif query.data == "back_to_menu":
            keyboard = [
                [InlineKeyboardButton("💬 محادثة جديدة", callback_data="new_chat")],
                [InlineKeyboardButton("📋 قائمة المحادثات", callback_data="list_chats")],
                [InlineKeyboardButton("❌ إغلاق القائمة", callback_data="close_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("اختر من القائمة:", reply_markup=reply_markup)
            
        elif query.data == "close_menu":
            await query.edit_message_text("تم إغلاق القائمة")

    async def new_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        session_id = self.chat_manager.create_session(user_id)
        self.user_sessions[user_id] = session_id
        await update.message.reply_text(f"تم إنشاء محادثة جديدة: {session_id}")
    
    async def load_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("يرجى تحديد رقم المحادثة: /load_chat <session_id>")
            return
        
        user_id = update.effective_user.id
        session_id = context.args[0]
        
        if self.chat_manager._load_session(user_id, session_id):
            self.user_sessions[user_id] = session_id
            await update.message.reply_text(f"تم تحميل المحادثة: {session_id}")
        else:
            await update.message.reply_text("المحادثة غير موجودة")
    
    async def list_chats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        sessions = self.chat_manager.list_user_sessions(user_id)
        
        if not sessions:
            await update.message.reply_text("لا توجد محادثات محفوظة")
            return
        
        message = "المحادثات المحفوظة:\n\n"
        for session in sessions[:10]:  # Show last 10 sessions
            message += f"🔹 {session['session_id']} - {session['message_count']} رسالة\n"
        
        await update.message.reply_text(message)
    
    async def delete_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("يرجى تحديد رقم المحادثة: /delete_chat <session_id>")
            return
        
        user_id = update.effective_user.id
        session_id = context.args[0]
        
        if self.chat_manager.delete_session(user_id, session_id):
            if self.user_sessions.get(user_id) == session_id:
                del self.user_sessions[user_id]
            await update.message.reply_text(f"تم حذف المحادثة: {session_id}")
        else:
            await update.message.reply_text("المحادثة غير موجودة")

    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            user_id = update.effective_user.id
            session_id = self._get_or_create_session(user_id)
            
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
                
                # Save user message to chat history
                self.chat_manager.add_message(user_id, session_id, "user", transcript.text)
                
                # Get chat history for context
                history = self.chat_manager.get_session_history(user_id, session_id)
                
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
                
                # Build context from Pinecone results
                context_texts = []
                for match in results.matches:
                    if match.score > 0.3:
                        context_texts.append(match.metadata.get('text', ''))
                
                if not context_texts:
                    context_texts = [match.metadata.get('text', '') for match in results.matches[:3]]
                
                context_text = "\n".join(context_texts) if context_texts else "لا توجد معلومات متاحة في قاعدة البيانات"
                if len(context_text) > 3000:
                    context_text = context_text[:3000] + "..."
                
                # Build chat history context
                history_context = ""
                if len(history) > 1:  # More than just current message
                    recent_history = history[-6:-1]  # Last 5 messages before current
                    history_context = "\n\nسياق المحادثة السابقة:\n"
                    for msg in recent_history:
                        role = "المستخدم" if msg["role"] == "user" else "المساعد"
                        history_context += f"{role}: {msg['content'][:100]}...\n"
                
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
5. راعي سياق المحادثة السابقة عند الإجابة

أسلوبك: علمي، محترم، واضح، يليق بمقام المرجعية الدينية."""
                
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"السياق المتوفر: {context_text}{history_context}\n\nالسؤال: {transcript.text}"}
                    ],
                    max_tokens=500
                )
                
                response_text = response.choices[0].message.content
                
                # Save assistant response to chat history
                self.chat_manager.add_message(user_id, session_id, "assistant", response_text)
                
                # Convert response to speech
                await update.message.chat.send_action(action="record_voice")
                speech_response = self.openai_client.audio.speech.create(
                    model="tts-1",
                    voice="alloy",
                    input=response_text
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
            try:
                await processing_msg.delete()
            except:
                pass
            await update.message.reply_text("عذراً، حدث خطأ في معالجة الرسالة الصوتية")

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            user_id = update.effective_user.id
            session_id = self._get_or_create_session(user_id)
            
            await update.message.chat.send_action(action="typing")
            
            # Save user message to chat history
            self.chat_manager.add_message(user_id, session_id, "user", update.message.text)
            
            # Get chat history for context
            history = self.chat_manager.get_session_history(user_id, session_id)
            
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
            
            context_text = "\n".join(context_texts) if context_texts else "لا توجد معلومات متاحة في قاعدة البيانات"
            if len(context_text) > 3000:
                context_text = context_text[:3000] + "..."
            
            # Build chat history context
            history_context = ""
            if len(history) > 1:  # More than just current message
                recent_history = history[-6:-1]  # Last 5 messages before current
                history_context = "\n\nسياق المحادثة السابقة:\n"
                for msg in recent_history:
                    role = "المستخدم" if msg["role"] == "user" else "المساعد"
                    history_context += f"{role}: {msg['content'][:100]}...\n"
            
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
5. راعي سياق المحادثة السابقة عند الإجابة

أسلوبك: علمي، محترم، واضح، يليق بمقام المرجعية الدينية."""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"السياق المتوفر: {context_text}{history_context}\n\nالسؤال: {update.message.text}"}
                ],
                max_tokens=500
            )
            
            response_text = response.choices[0].message.content
            
            # Save assistant response to chat history
            self.chat_manager.add_message(user_id, session_id, "assistant", response_text)
            
            await update.message.reply_text(response_text)
                
        except Exception as e:
            logger.error(f"Error processing text: {e}")
            await update.message.reply_text("عذراً، حدث خطأ في معالجة الرسالة")

def main():
    bot = ArabicVoiceBot()
    
    app = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()
    
    # Add command handlers
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CommandHandler("menu", bot.menu))
    app.add_handler(CommandHandler("new_chat", bot.new_chat))
    app.add_handler(CommandHandler("load_chat", bot.load_chat))
    app.add_handler(CommandHandler("list_chats", bot.list_chats))
    app.add_handler(CommandHandler("delete_chat", bot.delete_chat))
    
    # Add callback query handler for buttons
    app.add_handler(CallbackQueryHandler(bot.button_handler))
    
    # Add message handlers
    app.add_handler(MessageHandler(filters.VOICE, bot.handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_text))
    
    app.run_polling()

if __name__ == '__main__':
    main()
