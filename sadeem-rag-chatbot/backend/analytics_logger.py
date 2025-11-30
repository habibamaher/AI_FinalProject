"""
Analytics Logger for Sadeem AI Chatbot

Logs conversation analytics including emotions, response times,
and message metadata for insights and debugging.
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Optional
import hashlib

logger = logging.getLogger(__name__)


class AnalyticsLogger:
    """
    Lightweight analytics system that logs conversation data to JSON Lines format.
    
    Logs include:
    - Timestamp
    - Session ID
    - User message (optionally hashed for privacy)
    - Detected emotion and confidence
    - Response time
    - Message metadata
    """
    
    def __init__(
        self,
        log_file: str = "analytics.jsonl",
        hash_messages: bool = False,
        enabled: bool = True
    ):
        """
        Initialize analytics logger
        
        Args:
            log_file: Path to analytics log file (JSON Lines format)
            hash_messages: If True, hash user messages for privacy
            enabled: If False, disable logging
        """
        self.log_file = log_file
        self.hash_messages = hash_messages
        self.enabled = enabled
        
        if self.enabled:
            # Ensure log file exists
            if not os.path.exists(self.log_file):
                with open(self.log_file, 'w') as f:
                    pass  # Create empty file
            
            logger.info(f"✓ Analytics logger initialized (file: {log_file}, hashing: {hash_messages})")
        else:
            logger.info("Analytics logging disabled")
    
    def log_message(
        self,
        session_id: str,
        user_message: str,
        emotion_data: Dict,
        response_time: float,
        bot_response: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Log a message interaction
        
        Args:
            session_id: Session identifier
            user_message: User's message text
            emotion_data: Emotion detection result (label, confidence, scores)
            response_time: Time taken to generate response (seconds)
            bot_response: Bot's response (optional, can be hashed)
            metadata: Additional metadata to log
        """
        if not self.enabled:
            return
        
        try:
            # Prepare message data
            message_hash = None
            if self.hash_messages:
                message_hash = self._hash_text(user_message)
                user_message = f"[HASHED:{message_hash[:16]}]"
            
            # Build log entry
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'session_id': session_id,
                'user_message': user_message,
                'message_length': len(user_message) if not self.hash_messages else 0,
                'emotion': {
                    'label': emotion_data.get('label', 'Unknown'),
                    'confidence': round(emotion_data.get('confidence', 0.0), 3),
                    'scores': {
                        k: round(v, 3) for k, v in emotion_data.get('scores', {}).items()
                    }
                },
                'response_time_ms': round(response_time * 1000, 2),
                'metadata': metadata or {}
            }
            
            if bot_response and self.hash_messages:
                log_entry['bot_response_hash'] = self._hash_text(bot_response)[:16]
            
            # Append to log file (JSON Lines format)
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
            
            logger.debug(f"Logged analytics: {emotion_data.get('label')} emotion, {response_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to log analytics: {e}")
    
    def get_recent_logs(self, limit: int = 100) -> list:
        """
        Get recent log entries
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of log entries (most recent first)
        """
        if not self.enabled or not os.path.exists(self.log_file):
            return []
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Parse JSON lines and return most recent
            entries = []
            for line in reversed(lines[-limit:]):
                try:
                    entries.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
            
            return entries
            
        except Exception as e:
            logger.error(f"Failed to read analytics: {e}")
            return []
    
    def get_emotion_statistics(self, session_id: Optional[str] = None) -> Dict:
        """
        Get emotion statistics from logs
        
        Args:
            session_id: If provided, filter by session
            
        Returns:
            Statistics dictionary with emotion counts and averages
        """
        logs = self.get_recent_logs(limit=1000)
        
        # Filter by session if provided
        if session_id:
            logs = [log for log in logs if log.get('session_id') == session_id]
        
        if not logs:
            return {
                'total_messages': 0,
                'emotion_counts': {},
                'avg_response_time_ms': 0,
                'avg_confidence': 0
            }
        
        # Calculate statistics
        emotion_counts = {}
        total_response_time = 0
        total_confidence = 0
        
        for log in logs:
            emotion = log.get('emotion', {}).get('label', 'Unknown')
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            total_response_time += log.get('response_time_ms', 0)
            total_confidence += log.get('emotion', {}).get('confidence', 0)
        
        return {
            'total_messages': len(logs),
            'emotion_counts': emotion_counts,
            'emotion_percentages': {
                k: round(v / len(logs) * 100, 1) 
                for k, v in emotion_counts.items()
            },
            'avg_response_time_ms': round(total_response_time / len(logs), 2),
            'avg_confidence': round(total_confidence / len(logs), 3),
            'session_id': session_id
        }
    
    def _hash_text(self, text: str) -> str:
        """Hash text using SHA-256"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def clear_logs(self):
        """Clear all analytics logs (use with caution!)"""
        if self.enabled and os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                pass
            logger.info("Analytics logs cleared")
