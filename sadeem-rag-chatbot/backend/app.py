import os
import logging
import traceback
from datetime import datetime
from typing import Dict, List, Any
import uuid
import time

from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline
import chromadb
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

# Import new emotion modules
from analytics_logger import AnalyticsLogger
from translations import SADEEM_KB_AR, UI_TRANSLATIONS_AR, get_translation

# ============================================================================
# CONFIGURATION
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global components
chatbot_components = {}

# Configure Gemini - use environment variable or default key
GEMINI_API_KEY = os.getenv('GOOGLE_API_KEY', '')
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        logger.info("✓ Gemini API configured")
    except Exception as e:
        logger.warning(f"Could not configure Gemini: {e}")

# ============================================================================
# SADEEM KNOWLEDGE BASE
# ============================================================================

SADEEM_KB = {
    "general": {
        "keywords": ["sadeem", "what is", "service", "bapco", "tazweed", "about"],
        "documents": [
            "Sadeem is a smart fuel payment service provided by Bapco Tazweed",
            "It allows you to pay for fuel at petrol stations using a physical card or the BenefitPay app",
            "Sadeem replaced the old paper-based voucher systems with a digital solution",
            "It is designed for both individual and corporate customers to manage fuel spending",
            "You can use Sadeem at all Bapco Refining stations and private service stations in Bahrain"
        ]
    },
    "benefitpay": {
        "keywords": ["benefitpay", "mobile", "app", "digital", "recharge", "pay", "apple", "android", "google"],
        "documents": [
            "Sadeem is fully integrated with the BenefitPay mobile app",
            "You can download BenefitPay from the Apple App Store, Google Play Store, or for Android",
            "The app allows you to top up your Sadeem account digitally without visiting a branch",
            "You can use the BenefitPay app to pay directly at refueling stations",
            "No physical card is needed if you use the BenefitPay integration"
        ]
    },
    "topup": {
        "keywords": ["top up", "recharge", "balance", "add money", "website", "online"],
        "documents": [
            "You can top up your Sadeem account through the BenefitPay mobile app",
            "Sadeem cards can also be topped up via the official Sadeem website",
            "Top-ups are instant and allow you to use the credit immediately",
            "You can also view your transaction history and balance online"
        ]
    },
    "fees": {
        "keywords": ["fee", "cost", "charge", "price", "how much", "issuance", "renewal"],
        "documents": [
            "Card issuance and replacement fee: BD 3.300",
            "Annual renewal fee: BD 2.200 (automatically deducted from balance)",
            "Amendment of card restrictions (e.g., vehicle plate, limits): BD 1.100",
            "The card is valid for 3 years"
        ]
    },
    "features": {
        "keywords": ["feature", "benefit", "offer", "control", "limit", "restriction"],
        "documents": [
            "Secure cash-free fuel transactions",
            "Set fuel type restrictions (e.g., Jayyid or Mumtaz only)",
            "Set vehicle-specific limits using license plate numbers",
            "Manage household or fleet fuel consumption under one account",
            "Prevent unauthorized use with smart restrictions"
        ]
    },
    "formats": {
        "keywords": ["format", "prepaid", "credit", "type", "card"],
        "documents": [
            "Sadeem is available as a Prepaid card (for individuals and companies)",
            "Sadeem is also available as a Credit card (for qualified corporate customers)",
            "Both formats offer the same security and management features"
        ]
    }
}

# ============================================================================
# EMOTION DETECTION (Replaced old SentimentAnalyzer)
# ============================================================================
# Now using emotion_detector.py module for 5-emotion classification



# ============================================================================
# VECTOR STORE
# ============================================================================

class VectorStore:
    def __init__(self):
        try:
            self.client = chromadb.PersistentClient(path="./chroma_db")
            self.collection = self._init_collection()
            logger.info("✓ Vector store initialized")
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            self.collection = None
    
    def _init_collection(self):
        """Initialize ChromaDB collection"""
        try:
            try:
                self.client.delete_collection(name="sadeem")
            except:
                pass
            
            collection = self.client.create_collection(name="sadeem")
            self._add_documents(collection)
            return collection
        except Exception as e:
            logger.error(f"Error initializing collection: {e}")
            return None
    
    def _add_documents(self, collection):
        """Add documents to vector store"""
        try:
            model = SentenceTransformer('all-MiniLM-L6-v2')
            
            doc_id = 0
            # Add English documents
            for category, data in SADEEM_KB.items():
                for text in data['documents']:
                    embedding = model.encode(text).tolist()
                    collection.add(
                        embeddings=[embedding],
                        documents=[text],
                        ids=[f"doc_en_{doc_id}"],
                        metadatas=[{"category": category, "language": "en"}]
                    )
                    doc_id += 1
            
            # Add Arabic documents
            ar_doc_id = 0
            for category, data in SADEEM_KB_AR.items():
                for text in data['documents']:
                    embedding = model.encode(text).tolist()
                    collection.add(
                        embeddings=[embedding],
                        documents=[text],
                        ids=[f"doc_ar_{ar_doc_id}"],
                        metadatas=[{"category": category, "language": "ar"}]
                    )
                    ar_doc_id += 1
            
            logger.info(f"✓ Added {doc_id} English and {ar_doc_id} Arabic documents to vector store")
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
    
    def search(self, query: str, k: int = 3, language: str = "en") -> List[str]:
        """Search for relevant documents"""
        if not self.collection:
            return []
        
        try:
            # Filter by language if provided
            where_filter = {"language": language} if language else None
            
            results = self.collection.query(
                query_texts=[query], 
                n_results=k,
                where=where_filter
            )
            
            if results and results['documents'] and results['documents'][0]:
                # Return documents (Gemini will translate if needed)
                return results['documents'][0]
            return []
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []


# ============================================================================
# RESPONSE GENERATOR WITH GEMINI (Combined with Emotion Detection)
# ============================================================================

class ResponseGenerator:
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.arabic_kb = SADEEM_KB_AR
        try:
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            self.has_gemini = GEMINI_API_KEY != ''
            if self.has_gemini:
                logger.info("✓ Gemini API available for response generation")
            else:
                logger.warning("⚠ Gemini API key not configured")
        except Exception as e:
            logger.warning(f"Gemini not available: {e}")
            self.gemini_model = None
            self.has_gemini = False
    
    def generate(self, query: str, context: Dict = None, language: str = "en") -> tuple[str, str, float, bool]:
        """
        Generate response for query using Gemini, with integrated emotion detection.
        Returns: (response_text, emotion_label, emotion_confidence, request_rating)
        """
        query_lower = query.lower().strip()
        
        # Select knowledge base based on language
        kb = self.arabic_kb if language == "ar" else SADEEM_KB
        
        # Search for relevant documents (use appropriate KB)
        documents = self.vector_store.search(query, k=3, language=language)
        
        # Check if query is related to Sadeem
        is_sadeem_related = self._is_sadeem_question(query_lower)
        
        logger.info(f"Query: '{query}' | Sadeem-related: {is_sadeem_related} | Documents found: {len(documents)}")
        
        # Default values
        emotion_label = "Neutral"
        emotion_confidence = 0.0
        should_request_rating = self._is_closing_intent(query_lower)
        
        # If Gemini is available, use it for combined detection and generation
        if self.has_gemini:
            logger.info("Using Gemini for combined emotion detection and response generation")
            
            try:
                # Format documents
                formatted_docs = []
                for i, doc in enumerate(documents, 1):
                    formatted_docs.append(f"- {doc}")
                doc_text = "\n".join(formatted_docs)
                
                # Construct combined prompt
                if language == "ar":
                    prompt = f"""أنت سديم، مساعد ذكي ومتحمس لكروت الوقود من البحرين.
                    
سؤال العميل: "{query}"

معلومات ذات صلة:
{doc_text}

مهمتك (نفذها في خطوة واحدة):
1. حلل مشاعر العميل (سعيد، محايد، مرتبك، محبط، حزين).
2. جاوب على السؤال باللهجة البحرينية بناءً على المعلومات المتوفرة.
3. كيّف نبرتك حسب المشاعر (مثلاً: تعاطف مع المحبط، بسّط للمرتبك).

تنسيق الإجابة المطلوب (يجب الالتزام به بدقة):
EMOTION: [المشاعر]
CONFIDENCE: [0.0-1.0]
RESPONSE: [ردك هنا]

مثال:
EMOTION: Frustrated
CONFIDENCE: 0.9
RESPONSE: مسامحة على الإزعاج يا خوي. عشان تحل هالمشكلة...

الرد:"""
                else:
                    prompt = f"""You are Sadeem, a knowledgeable and enthusiastic Fuel Card assistant from Bahrain.

Customer Question: "{query}"

Related Information:
{doc_text}

Your Task (Execute in one step):
1. Analyze the customer's emotion (Happy, Neutral, Confused, Frustrated, Sad).
2. Answer the question using the provided information.
3. Adapt your tone based on the detected emotion (e.g., be empathetic if frustrated, clear if confused).

Required Output Format (Follow strictly):
EMOTION: [Emotion Label]
CONFIDENCE: [0.0-1.0]
RESPONSE: [Your response here]

Example:
EMOTION: Frustrated
CONFIDENCE: 0.9
RESPONSE: I understand your frustration and I'm here to help. To resolve this...

Response:"""

                response = self.gemini_model.generate_content(prompt)
                result_text = response.text.strip()
                
                # Parse the response
                response_text = ""
                for line in result_text.split('\n'):
                    if line.startswith('EMOTION:'):
                        emotion_label = line.split(':', 1)[1].strip()
                        # Map Arabic emotions back to English labels if needed
                        emotion_map = {
                            'سعيد': 'Happy', 'محايد': 'Neutral', 'مرتبك': 'Confused', 
                            'محبط': 'Frustrated', 'حزين': 'Sad'
                        }
                        emotion_label = emotion_map.get(emotion_label, emotion_label)
                    elif line.startswith('CONFIDENCE:'):
                        try:
                            emotion_confidence = float(line.split(':', 1)[1].strip())
                        except:
                            emotion_confidence = 0.5
                    elif line.startswith('RESPONSE:'):
                        response_text = line.split(':', 1)[1].strip()
                    elif response_text: # Append multi-line response
                        response_text += "\n" + line
                
                if not response_text:
                    # Fallback if parsing failed
                    response_text = result_text
                
                # Add rating request if needed
                if should_request_rating:
                    if language == "ar":
                        response_text += "\n\nلو عندك دقيقة، قيّم تجربتك معي! ⭐"
                    else:
                        response_text += "\n\nIf you have a moment, please rate your experience with me below! ⭐"
                
                return response_text.strip(), emotion_label, emotion_confidence, should_request_rating

            except Exception as e:
                logger.error(f"Error with Gemini combined call: {e}")
                traceback.print_exc()
                # Fallback to local logic below
        
        # Fallback logic (Gemini failed or not available)
        logger.info("Using fallback response logic")
        
        if is_sadeem_related and documents:
            response_text = self._build_fallback_response(documents, language)
        elif should_request_rating:
             if language == "ar":
                response_text = "شكراً على تواصلك معي! إذا تحتاج مساعدة بسديم مستقبلاً، أنا دايماً هني. يومك سعيد!"
             else:
                response_text = "Thank you for chatting with me! If you need help with Sadeem in the future, I'm always here. Have a great day!"
        else:
             response_text = self._build_fallback_response([], language)
             
        if should_request_rating:
            if language == "ar":
                response_text += "\n\nلو عندك دقيقة، قيّم تجربتك معي! ⭐"
            else:
                response_text += "\n\nIf you have a moment, please rate your experience with me below! ⭐"

        return response_text, emotion_label, emotion_confidence, should_request_rating
    
    def _is_sadeem_question(self, query_lower: str) -> bool:
        """Check if question is about Sadeem"""
        sadeem_keywords = [
            'sadeem', 'fuel', 'card', 'fee', 'feature', 'benefitpay', 'benefit pay',
            'restriction', 'format', 'prepaid', 'credit', 'apply', 'how much',
            'cost', 'charge', 'what', 'how', 'use', 'get', 'student', 'young',
            'vehicle', 'limit', 'bapco', 'good', 'best', 'work', 'available',
            'app', 'mobile', 'download', 'iphone', 'android', 'apple',
            'سديم', 'وقود', 'بترول', 'كرت', 'بطاقة', 'رسوم', 'ميزة', 'مميزات',
            'بنفت', 'تطبيق', 'قيود', 'حدود', 'مسبق', 'ائتمان', 'تقديم', 'كم',
            'سعر', 'تكلفة', 'وش', 'شنو', 'كيف', 'شلون', 'استخدام', 'طالب',
            'سيارة', 'مركبة', 'بابكو', 'تزويد', 'زين', 'تحميل', 'تنزيل', 'ايفون',
            'اندرويد', 'جوال', 'موبايل', 'تلفون', 'ابي', 'بغيت', 'عندي'
        ]
        return any(keyword in query_lower for keyword in sadeem_keywords)

    def _is_closing_intent(self, query_lower: str) -> bool:
        """Check if user is ending the conversation"""
        closing_keywords = ['thanks', 'thank you', 'thx', 'bye', 'goodbye', 'see you', 'great', 'helpful', 'done',
                           'شكرا', 'شكراً', 'مشكور', 'باي', 'مع السلامة', 'يعطيك العافية', 'تمام', 'زين']
        return any(keyword in query_lower for keyword in closing_keywords)
    
    def _build_fallback_response(self, documents: list, language: str = "en") -> str:
        """Build fallback response from documents"""
        if not documents:
            if language == "ar":
                return "أنا مساعد سديم! أقدر أساعدك في ميزات الكرت، الرسوم، التقديم، القيود، بنفت باي، وأكثر. وش تبي تعرف؟"
            return "I'm Sadeem's assistant! I can help with questions about card features, fees, how to apply, restrictions, BenefitPay integration, and more. What would you like to know?"
        
        # Combine documents into response more naturally
        response_text = documents[0]
        if not response_text.endswith('.'):
            response_text += "."
            
        if len(documents) > 1:
            # Add second point naturally
            second_point = documents[1]
            if second_point[0].isupper():
                second_point = second_point[0].lower() + second_point[1:]
            if language == "ar":
                response_text += f" كمان، {second_point}"
            else:
                response_text += f" Additionally, {second_point}"
            if not response_text.endswith('.'):
                response_text += "."
                
        if len(documents) > 2:
            if language == "ar":
                response_text += f" وبعد: {documents[2]}"
            else:
                response_text += f" Also worth noting: {documents[2]}"
        
        return response_text


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

class SessionManager:
    def __init__(self):
        self.sessions = {}
    
    def create_session(self) -> str:
        """Create new session"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            'created_at': datetime.now(),
            'messages': [],
            'rating': None
        }
        logger.info(f"✓ Session created: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Dict:
        """Get session"""
        return self.sessions.get(session_id)
    
    def add_message(self, session_id: str, message: Dict):
        """Add message to session"""
        if session_id in self.sessions:
            self.sessions[session_id]['messages'].append(message)
            
    def add_rating(self, session_id: str, rating: int):
        """Add rating to session"""
        if session_id in self.sessions:
            self.sessions[session_id]['rating'] = rating
            logger.info(f"Rating added for session {session_id}: {rating} stars")


# ============================================================================
# INITIALIZE
# ============================================================================

def initialize_components():
    """Initialize components"""
    global chatbot_components
    
    logger.info("🤖 Initializing Chatbot Components...")
    
    try:
        # Initialize vector store
        chatbot_components['vector_store'] = VectorStore()
        
        # Initialize response generator (now handles emotion detection too)
        chatbot_components['response_generator'] = ResponseGenerator(
            chatbot_components['vector_store']
        )
        
        # Initialize session manager
        chatbot_components['session_manager'] = SessionManager()
        
        # Initialize analytics logger
        chatbot_components['analytics_logger'] = AnalyticsLogger(
            log_file='analytics.jsonl',
            hash_messages=False,  # Set to True for privacy
            enabled=True
        )
        
        logger.info("✅ All components initialized!")
        return True
    except Exception as e:
        logger.error(f"❌ Initialization error: {e}")
        traceback.print_exc()
        return False


# ============================================================================
# API ROUTES
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})


@app.route('/api/info', methods=['GET'])
def api_info():
    return jsonify({
        'name': 'Sadeem RAG Chatbot with 5-Emotion AI',
        'version': '5.1.0',
        'description': 'Sadeem Fuel Card assistant with optimized RAG and single-pass emotion/response generation',
        'emotions': ['Happy', 'Neutral', 'Confused', 'Frustrated', 'Sad']
    })


@app.route('/api/session/start', methods=['POST'])
def start_session():
    try:
        session_id = chatbot_components['session_manager'].create_session()
        return jsonify({
            'success': True,
            'session_id': session_id,
            'initial_message': {
                'id': str(uuid.uuid4()),
                'text': "Hello! I'm Sadeem, your Fuel Card assistant. How can I help you today?",
                'sender': 'bot',
                'timestamp': datetime.now().isoformat(),
                'emotion': 'neutral'
            }
        }), 201
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/chat/message', methods=['POST', 'OPTIONS'])
def chat_message():
    if request.method == 'OPTIONS':
        return '', 200
    
    start_time = time.time()
    
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        message = data.get('message', '').strip()
        language = data.get('language', 'en')  # Default to English
        
        if not session_id or not message:
            return jsonify({'success': False, 'error': 'Missing data'}), 400
        
        sm = chatbot_components['session_manager']
        rg = chatbot_components['response_generator']
        analytics = chatbot_components.get('analytics_logger')
        
        # Generate response AND detect emotion in one go
        context = {
            'session_id': session_id,
            'session': sm.get_session(session_id)
        }
        
        response_text, emotion_label, emotion_confidence, request_rating = rg.generate(message, context, language)
        
        # User message (we log the detected emotion here for consistency with old format)
        user_message = {
            'id': str(uuid.uuid4()),
            'text': message,
            'sender': 'user',
            'timestamp': datetime.now().isoformat(),
            'emotion': emotion_label,
            'emotion_confidence': emotion_confidence,
            'emotion_scores': {emotion_label: emotion_confidence} # Simplified scores
        }
        sm.add_message(session_id, user_message)
        
        logger.info(f"User: '{message}' | Language: {language} | Emotion: {emotion_label} ({emotion_confidence:.2f})")
        
        bot_message = {
            'id': str(uuid.uuid4()),
            'text': response_text,
            'sender': 'bot',
            'timestamp': datetime.now().isoformat(),
            'emotion': 'neutral',  # Bot is always neutral
            'request_rating': request_rating
        }
        sm.add_message(session_id, bot_message)
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Log analytics
        if analytics:
            analytics.log_message(
                session_id=session_id,
                user_message=message,
                emotion_data={'label': emotion_label, 'confidence': emotion_confidence},
                response_time=response_time,
                bot_response=response_text,
                metadata={
                    'message_id': user_message['id'],
                    'response_id': bot_message['id'],
                    'request_rating': request_rating
                }
            )
        
        logger.info(f"Bot: '{response_text[:80]}...' | Response time: {response_time:.2f}s")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'user_message': {
                'id': user_message['id'],
                'text': user_message['text'],
                'sender': user_message['sender'],
                'timestamp': user_message['timestamp'],
                'emotion': user_message['emotion'],
                'emotion_confidence': user_message['emotion_confidence'],
                'emotion_scores': user_message['emotion_scores']
            },
            'bot_message': {
                'id': bot_message['id'],
                'text': bot_message['text'],
                'sender': bot_message['sender'],
                'timestamp': bot_message['timestamp'],
                'emotion': bot_message['emotion'],
                'request_rating': bot_message['request_rating']
            },
            'response_time_ms': round(response_time * 1000, 2)
        }), 200
    
    except Exception as e:
        logger.error(f"Error: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/session/<session_id>/rating', methods=['POST'])
def submit_rating(session_id):
    """Submit a rating for the session"""
    try:
        data = request.get_json()
        rating = data.get('rating')
        
        if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
            return jsonify({'success': False, 'error': 'Invalid rating'}), 400
            
        sm = chatbot_components['session_manager']
        sm.add_rating(session_id, rating)
        
        # Log rating to analytics
        analytics = chatbot_components.get('analytics_logger')
        if analytics:
            # We log it as a special system message or just update metadata?
            # For simplicity, let's just log it
            logger.info(f"Rating submitted for session {session_id}: {rating} stars")
            
        return jsonify({'success': True}), 200
    except Exception as e:
        logger.error(f"Error submitting rating: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/session/<session_id>/history', methods=['GET'])
def get_history(session_id):
    try:
        session = chatbot_components['session_manager'].get_session(session_id)
        if not session:
            return jsonify({'success': False, 'error': 'Not found'}), 404
        return jsonify({'session_id': session_id, 'messages': session['messages']}), 200
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/analytics/emotions', methods=['GET'])
def get_emotion_analytics():
    """Get emotion statistics from analytics logs"""
    try:
        analytics = chatbot_components.get('analytics_logger')
        if not analytics:
            return jsonify({'success': False, 'error': 'Analytics not enabled'}), 503
        
        # Get optional session_id filter
        session_id = request.args.get('session_id')
        
        # Get statistics
        stats = analytics.get_emotion_statistics(session_id=session_id)
        
        return jsonify({
            'success': True,
            'statistics': stats
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving analytics: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/analytics/recent', methods=['GET'])
def get_recent_analytics():
    """Get recent conversation logs"""
    try:
        analytics = chatbot_components.get('analytics_logger')
        if not analytics:
            return jsonify({'success': False, 'error': 'Analytics not enabled'}), 503
        
        limit = int(request.args.get('limit', 50))
        limit = min(limit, 200)  # Cap at 200
        
        logs = analytics.get_recent_logs(limit=limit)
        
        return jsonify({
            'success': True,
            'count': len(logs),
            'logs': logs
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving recent logs: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500



# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    logger.info("🚀 Starting Sadeem Chatbot API with 5-Emotion AI...")
    
    if initialize_components():
        logger.info("=" * 70)
        logger.info("✅ SADEEM CHATBOT WITH 5-EMOTION AI - READY!")
        logger.info("=" * 70)
        logger.info(f"API: http://localhost:5000")
        logger.info(f"Frontend: http://localhost:3000")
        logger.info(f"Emotions: Happy, Neutral, Confused, Frustrated, Sad")
        logger.info("=" * 70)
        
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=True)
    else:
        logger.error("Failed to initialize!")