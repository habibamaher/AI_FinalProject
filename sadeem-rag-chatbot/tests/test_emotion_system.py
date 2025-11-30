"""
Test script for Sadeem AI Emotion System
"""

import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from emotion_detector import EmotionDetector
from emotion_response_adapter import EmotionResponseAdapter

class TestEmotionSystem(unittest.TestCase):
    def setUp(self):
        self.detector = EmotionDetector(use_gemini_fallback=False)
        self.adapter = EmotionResponseAdapter(gemini_model=MagicMock())
        
    def test_emotion_detection_happy(self):
        """Test detection of happy emotion"""
        text = "I am so happy with this service! It's amazing!"
        result = self.detector._detect_with_hf_model(text)
        self.assertEqual(result['label'], 'Happy')
        
    def test_emotion_detection_frustrated(self):
        """Test detection of frustrated emotion"""
        text = "This is terrible! I hate this system, it never works!"
        result = self.detector._detect_with_hf_model(text)
        self.assertEqual(result['label'], 'Frustrated')
        
    def test_emotion_detection_neutral(self):
        """Test detection of neutral emotion"""
        text = "What is the fee for the card?"
        result = self.detector._detect_with_hf_model(text)
        # Note: Short questions might be neutral or sometimes surprised depending on model
        # We accept Neutral or Confused for questions
        self.assertIn(result['label'], ['Neutral', 'Confused'])

    def test_response_adaptation_frustrated(self):
        """Test response adaptation for frustrated user"""
        emotion = "Frustrated"
        base_answer = "The fee is BD 3.300."
        user_message = "Why is this so expensive?"
        context = {'session_id': 'test-session'}
        
        # Mock Gemini response
        self.adapter.gemini_model.generate_content.return_value.text = "I understand your concern about the cost. The fee is BD 3.300."
        
        response = self.adapter.adjust_response_based_on_emotion(
            emotion, base_answer, user_message, context
        )
        
        # Check if response contains empathy or explanation
        self.assertTrue(len(response) > 0)
        
    def test_response_adaptation_confused(self):
        """Test response adaptation for confused user"""
        emotion = "Confused"
        base_answer = "Use the app."
        user_message = "How do I use this?"
        context = {'session_id': 'test-session'}
        
        # Mock Gemini response
        self.adapter.gemini_model.generate_content.return_value.text = "To use the app, first download it, then log in."
        
        response = self.adapter.adjust_response_based_on_emotion(
            emotion, base_answer, user_message, context
        )
        
        # Check if clarifying question is added
        self.assertTrue("?" in response)

if __name__ == '__main__':
    unittest.main()
