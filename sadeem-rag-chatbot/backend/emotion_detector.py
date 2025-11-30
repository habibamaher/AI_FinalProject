"""
5-Emotion Detection Module for Sadeem AI Chatbot

Detects user emotions from text messages:
- Happy / Positive
- Neutral / Calm
- Confused
- Frustrated / Angry
- Sad / Upset
"""

import logging
from typing import Dict, Optional
from transformers import pipeline
import google.generativeai as genai

logger = logging.getLogger(__name__)


class EmotionDetector:
    """
    5-emotion classifier using Hugging Face transformer model
    with Gemini API fallback for edge cases.
    """
    
    # Emotion mapping from 7-class model to our 5 target emotions
    EMOTION_MAPPING = {
        'joy': 'Happy',
        'neutral': 'Neutral',
        'surprise': 'Confused',  # Contextual interpretation
        'anger': 'Frustrated',
        'sadness': 'Sad',
        'fear': 'Confused',  # Map fear to confused (uncertainty)
        'disgust': 'Frustrated',  # Map disgust to frustrated
    }
    
    TARGET_EMOTIONS = ['Happy', 'Neutral', 'Confused', 'Frustrated', 'Sad']
    
    def __init__(self, use_gemini_fallback: bool = True, confidence_threshold: float = 0.3):
        """
        Initialize emotion detector
        
        Args:
            use_gemini_fallback: Whether to use Gemini API for low-confidence cases
            confidence_threshold: Minimum confidence to accept model prediction
        """
        self.confidence_threshold = confidence_threshold
        self.use_gemini_fallback = use_gemini_fallback
        self.emotion_pipeline = None
        self.gemini_model = None
        
        # Initialize Hugging Face emotion model
        try:
            logger.info("Loading emotion detection model...")
            self.emotion_pipeline = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                top_k=None  # Return all emotion scores
            )
            logger.info("✓ Emotion detection model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load emotion model: {e}")
            logger.warning("⚠ Emotion detection will use Gemini API only")
        
        # Initialize Gemini fallback if enabled
        if use_gemini_fallback:
            try:
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("✓ Gemini fallback enabled for emotion detection")
            except Exception as e:
                logger.warning(f"Gemini fallback not available: {e}")
    
    def detect_emotion(self, user_message: str) -> Dict:
        """
        Detect emotion from user message
        
        Args:
            user_message: The user's text message
            
        Returns:
            {
                    "Sad": 0.10
                }
            }
        """
        if not user_message or not user_message.strip():
            return self._default_emotion()
        
        # Try Hugging Face model first
        if self.emotion_pipeline:
            try:
                result = self._detect_with_hf_model(user_message)
                
                # If confidence is too low and Gemini is available, use fallback
                if result['confidence'] < self.confidence_threshold and self.use_gemini_fallback:
                    logger.info(f"Low confidence ({result['confidence']:.2f}), trying Gemini fallback")
                    gemini_result = self._detect_with_gemini(user_message)
                    if gemini_result:
                        return gemini_result
                
                return result
            except Exception as e:
                logger.error(f"Error in HF emotion detection: {e}")
        
        # Fallback to Gemini if HF model failed
        if self.use_gemini_fallback and self.gemini_model:
            try:
                return self._detect_with_gemini(user_message)
            except Exception as e:
                logger.error(f"Error in Gemini emotion detection: {e}")
        
        # Ultimate fallback: return neutral
        return self._default_emotion()
    
    def _detect_with_hf_model(self, text: str) -> Dict:
        """Detect emotion using Hugging Face model"""
        # Get predictions from model
        predictions = self.emotion_pipeline(text)[0]
        
        # Convert to our 5-emotion format
        emotion_scores = {emotion: 0.0 for emotion in self.TARGET_EMOTIONS}
        
        for pred in predictions:
            original_label = pred['label']
            score = pred['score']
            
            # Map to our target emotion
            target_emotion = self.EMOTION_MAPPING.get(original_label, 'Neutral')
            emotion_scores[target_emotion] += score
        
        # Normalize scores to sum to 1.0
        total = sum(emotion_scores.values())
        if total > 0:
            emotion_scores = {k: v/total for k, v in emotion_scores.items()}
        
        # Get dominant emotion
        dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])
        
        logger.info(f"Emotion detected: {dominant_emotion[0]} ({dominant_emotion[1]:.2f}) for '{text[:50]}...'")
        
        return {
            'label': dominant_emotion[0],
            'confidence': dominant_emotion[1],
            'scores': emotion_scores
        }
    
    def _detect_with_gemini(self, text: str) -> Optional[Dict]:
        """Detect emotion using Gemini API"""
        if not self.gemini_model:
            return None
        
        try:
            prompt = f"""Analyze the emotion in this message and classify it into exactly ONE of these 5 categories:
- Happy (positive, joyful, satisfied, grateful)
- Neutral (calm, informational, matter-of-fact)
- Confused (uncertain, puzzled, seeking clarification)
- Frustrated (angry, annoyed, impatient, irritated)
- Sad (disappointed, upset, discouraged, unhappy)

Message: "{text}"

Respond with ONLY the emotion label and a confidence score (0.0-1.0) in this exact format:
EMOTION: [label]
CONFIDENCE: [score]

Example:
EMOTION: Frustrated
CONFIDENCE: 0.85"""

            response = self.gemini_model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Parse response
            emotion_label = 'Neutral'
            confidence = 0.5
            
            for line in result_text.split('\n'):
                if line.startswith('EMOTION:'):
                    emotion_label = line.split(':', 1)[1].strip()
                elif line.startswith('CONFIDENCE:'):
                    try:
                        confidence = float(line.split(':', 1)[1].strip())
                    except:
                        confidence = 0.5
            
            # Validate emotion label
            if emotion_label not in self.TARGET_EMOTIONS:
                logger.warning(f"Invalid emotion from Gemini: {emotion_label}, defaulting to Neutral")
                emotion_label = 'Neutral'
            
            # Create score distribution (dominant emotion gets confidence, rest split remaining)
            scores = {e: (1 - confidence) / 4 for e in self.TARGET_EMOTIONS}
            scores[emotion_label] = confidence
            
            logger.info(f"Gemini emotion: {emotion_label} ({confidence:.2f})")
            
            return {
                'label': emotion_label,
                'confidence': confidence,
                'scores': scores
            }
        
        except Exception as e:
            logger.error(f"Gemini emotion detection failed: {e}")
            return None
    
    def _default_emotion(self) -> Dict:
        """Return default neutral emotion"""
        return {
            'label': 'Neutral',
            'confidence': 1.0,
            'scores': {
                'Happy': 0.0,
                'Neutral': 1.0,
                'Confused': 0.0,
                'Frustrated': 0.0,
                'Sad': 0.0
            }
        }
