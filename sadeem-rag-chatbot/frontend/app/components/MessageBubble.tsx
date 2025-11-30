import React from 'react';
import { format } from 'date-fns';
import EmotionIndicator from './EmotionIndicator';
import RatingComponent from './RatingComponent';

interface MessageBubbleProps {
  message: {
    id: string;
    text: string;
    sender: 'user' | 'bot';
    timestamp: string;
    emotion?: string;
    emotion_confidence?: number;
    request_rating?: boolean;
  };
  sessionId?: string;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message, sessionId }) => {
  const isUser = message.sender === 'user';

  return (
    <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} mb-4 animate-fade-in`}>
      <div className={`flex items-end gap-2 max-w-[80%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>

        {/* Avatar */}
        <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${isUser ? 'bg-blue-600' : 'bg-emerald-600'
          }`}>
          {isUser ? '👤' : '🤖'}
        </div>

        {/* Message Content */}
        <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
          <div className={`px-4 py-3 rounded-2xl shadow-md ${isUser
            ? 'bg-blue-600 text-white rounded-tr-none'
            : 'bg-gray-800 text-gray-100 rounded-tl-none border border-gray-700'
            }`}>
            <p className="whitespace-pre-wrap leading-relaxed">{message.text}</p>
          </div>

          {/* Metadata Row */}
          <div className="flex items-center gap-2 mt-1 px-1">
            <span className="text-xs text-gray-500">
              {format(new Date(message.timestamp), 'h:mm a')}
            </span>

            {/* Emotion Indicator for User Messages */}
            {isUser && message.emotion && (
              <EmotionIndicator
                emotion={message.emotion}
                confidence={message.emotion_confidence}
              />
            )}
          </div>

          {/* Rating Component (Only for bot messages that request it) */}
          {!isUser && message.request_rating && sessionId && (
            <RatingComponent
              sessionId={sessionId}
              onRatingSubmitted={() => console.log('Rating submitted')}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;
