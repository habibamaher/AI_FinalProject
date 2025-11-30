"""
Emotion-Aware Response Adapter for Sadeem AI Chatbot

Adapts bot responses based on detected user emotion to provide
more empathetic and contextually appropriate interactions.
"""

import logging
from typing import Dict, List, Optional
import google.generativeai as genai

logger = logging.getLogger(__name__)


class EmotionResponseAdapter:
    """
    Middleware that adjusts bot responses based on user emotion.
    
    Emotion-specific behaviors:
    - Happy: Upbeat, concise, maintains positive energy
    - Neutral: Professional, clear, factual
    - Confused: Step-by-step, asks clarifying questions, provides examples
    - Frustrated: Empathetic, solution-focused, offers escalation
    - Sad: Supportive, encouraging, gentle
    """
    
    def __init__(self, gemini_model=None):
        """
        Initialize emotion response adapter
        
        Args:
            gemini_model: Google Generative AI model instance
        """
        self.gemini_model = gemini_model
        
        # Track frustration patterns for escalation
        self.frustration_tracker = {}
        
        logger.info("✓ Emotion response adapter initialized")
    
    def adjust_response_based_on_emotion(
        self,
        emotion_label: str,
        base_answer: str,
        user_message: str,
        conversation_context: Optional[Dict] = None
    ) -> str:
        """
        Adjust response based on detected emotion
        
        Args:
            emotion_label: Detected emotion (Happy, Neutral, Confused, Frustrated, Sad)
            base_answer: Original response from RAG pipeline
            user_message: Original user message
            conversation_context: Optional context (session history, etc.)
            
        Returns:
            Adjusted response with appropriate tone and content
        """
        if not self.gemini_model:
            logger.warning("Gemini model not available, returning base answer")
            return base_answer
        
        try:
            # Get emotion-specific prompt
            system_prompt = self._get_emotion_prompt(emotion_label, conversation_context)
            
            # Build full prompt
            full_prompt = f"""{system_prompt}

User's Message: "{user_message}"
Detected Emotion: {emotion_label}

Base Answer (from knowledge base):
{base_answer}

Your Task:
Rewrite the base answer to match the user's emotional state. Keep the factual information but adjust the tone, structure, and approach based on the emotion guidelines above.

Adjusted Response:"""

            # Generate adapted response
            response = self.gemini_model.generate_content(full_prompt)
            adapted_answer = response.text.strip()
            
            # Add emotion-specific enhancements
            final_answer = self._add_emotion_enhancements(
                adapted_answer,
                emotion_label,
                user_message,
                conversation_context
            )
            
            logger.info(f"Response adapted for {emotion_label} emotion")
            return final_answer
            
        except Exception as e:
            logger.error(f"Error adapting response: {e}")
            # Fallback to base answer with simple prefix
            return self._simple_emotion_prefix(emotion_label) + base_answer
    
    def _get_emotion_prompt(self, emotion: str, context: Optional[Dict] = None) -> str:
        """Get emotion-specific system prompt"""
        
        prompts = {
            'Happy': """You are Sadeem, a friendly Fuel Card assistant. The user is in a HAPPY/POSITIVE mood.

Guidelines:
- Match their positive energy with an upbeat, friendly tone
- Keep responses concise and efficient (they're satisfied, don't over-explain)
- Use positive language and affirmations
- Be warm but professional
- 2-3 sentences maximum""",

            'Neutral': """You are Sadeem, a professional Fuel Card assistant. The user is in a NEUTRAL/CALM mood.

Guidelines:
- Use clear, professional, factual tone
- Be direct and informative
- Focus on accuracy and completeness
- Avoid unnecessary emotion or flair
- 2-4 sentences, well-structured""",

            'Confused': """You are Sadeem, a patient and helpful Fuel Card assistant. The user is CONFUSED/UNCERTAIN.

Guidelines:
- Break down information into simple, clear steps
- Use numbered lists or bullet points when helpful
- Provide concrete examples
- Ask a clarifying question at the end to ensure understanding
- Be patient and reassuring
- Avoid jargon, explain technical terms
- 3-5 sentences with clear structure""",

            'Frustrated': """You are Sadeem, an empathetic and solution-focused Fuel Card assistant. The user is FRUSTRATED/ANGRY.

Guidelines:
- START with acknowledgment of their frustration (e.g., "I understand this is frustrating...")
- Be direct and solution-oriented - get to the point quickly
- Offer specific, actionable steps
- Show empathy but don't over-apologize
- If this seems like a recurring issue, suggest escalation or alternative solutions
- 2-4 sentences, focused on resolution""",

            'Sad': """You are Sadeem, a supportive and encouraging Fuel Card assistant. The user is SAD/DISAPPOINTED.

Guidelines:
- Use a gentle, supportive tone
- Acknowledge their feelings briefly
- Provide reassurance while still being helpful
- Be encouraging and positive about finding a solution
- Avoid being overly cheerful (be genuine)
- 3-4 sentences, warm and understanding"""
        }
        
        # Check for repeated frustration
        if emotion == 'Frustrated' and context:
            session_id = context.get('session_id')
            if session_id:
                frustration_count = self.frustration_tracker.get(session_id, 0) + 1
                self.frustration_tracker[session_id] = frustration_count
                
                if frustration_count >= 2:
                    prompts['Frustrated'] += "\n\nIMPORTANT: This user has been frustrated multiple times. Offer to escalate to a human representative or provide alternative contact methods."
        
        return prompts.get(emotion, prompts['Neutral'])
    
    def _add_emotion_enhancements(
        self,
        answer: str,
        emotion: str,
        user_message: str,
        context: Optional[Dict]
    ) -> str:
        """Add emotion-specific enhancements to the answer"""
        
        # For Confused users, ensure there's a clarifying question
        if emotion == 'Confused' and '?' not in answer:
            clarifying_questions = [
                "\n\nDoes this help clarify things, or would you like me to explain any specific part in more detail?",
                "\n\nIs there a specific aspect you'd like me to break down further?",
                "\n\nDo you have any questions about these steps?"
            ]
            # Pick based on message length to add variety
            question_idx = len(user_message) % len(clarifying_questions)
            answer += clarifying_questions[question_idx]
        
        # For Frustrated users with repeated frustration, add escalation
        if emotion == 'Frustrated' and context:
            session_id = context.get('session_id')
            if session_id and self.frustration_tracker.get(session_id, 0) >= 2:
                if 'contact' not in answer.lower() and 'representative' not in answer.lower():
                    answer += "\n\nIf you'd prefer, I can provide contact information for our customer service team who can assist you directly."
        
        # For Sad users, add gentle encouragement
        if emotion == 'Sad' and len(answer.split()) > 20:
            if not any(word in answer.lower() for word in ['help', 'here', 'support']):
                answer += " I'm here to help make this easier for you."
        
        return answer
    
    def _simple_emotion_prefix(self, emotion: str) -> str:
        """Simple emotion-aware prefix as fallback"""
        prefixes = {
            'Happy': "Great to hear from you! ",
            'Neutral': "",
            'Confused': "Let me help clarify that. ",
            'Frustrated': "I understand this is frustrating. ",
            'Sad': "I'm sorry you're experiencing this. "
        }
        return prefixes.get(emotion, "")
    
    def reset_frustration_tracker(self, session_id: str):
        """Reset frustration tracking for a session"""
        if session_id in self.frustration_tracker:
            del self.frustration_tracker[session_id]
    
    def get_frustration_level(self, session_id: str) -> int:
        """Get current frustration count for a session"""
        return self.frustration_tracker.get(session_id, 0)
