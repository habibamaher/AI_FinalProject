'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Plus, RotateCcw, Menu, X, Loader2 } from 'lucide-react';
import { chatbotAPI, type Message } from '@/lib/api';
import MessageBubble from './components/MessageBubble';
import LoadingIndicator from './components/LoadingIndicator';

interface SessionMessage extends Message {
  id: string;
  sentiment?: 'positive' | 'negative' | 'neutral';
}

const getSentimentColor = (sentiment?: string) => {
  switch (sentiment) {
    case 'positive':
      return 'bg-green-100 text-green-700 border border-green-300';
    case 'negative':
      return 'bg-red-100 text-red-700 border border-red-300';
    default:
      return 'bg-gray-100 text-gray-700 border border-gray-300';
  }
};

const getSentimentEmoji = (sentiment?: string) => {
  switch (sentiment) {
    case 'positive':
      return '😊';
    case 'negative':
      return '😞';
    default:
      return '😐';
  }
};

export default function ChatPage() {
  const [messages, setMessages] = useState<SessionMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isInitializing, setIsInitializing] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const initializeSession = async () => {
      try {
        setIsInitializing(true);
        setError(null);
        const response = await chatbotAPI.startSession();

        if (response.success && response.session_id) {
          setSessionId(response.session_id);
          if (response.initial_message) {
            const msg: SessionMessage = {
              id: response.initial_message.id || String(Date.now()),
              text: String(response.initial_message.text || ''),
              sender: response.initial_message.sender || 'bot',
              timestamp: response.initial_message.timestamp || new Date().toISOString(),
              sentiment: response.initial_message.sentiment || 'neutral',
            };
            setMessages([msg]);
          }
        } else {
          setError('Failed to start session. Make sure backend is running on http://localhost:5000');
        }
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Failed to initialize chat. Make sure backend is running on http://localhost:5000';
        setError(errorMsg);
        console.error('Initialization error:', err);
      } finally {
        setIsInitializing(false);
      }
    };

    initializeSession();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (!isLoading && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isLoading]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!input.trim() || isLoading || !sessionId || isInitializing) return;

    const userMessage = input.trim();
    setInput('');
    setError(null);

    try {
      setIsLoading(true);

      const response = await chatbotAPI.sendMessage(sessionId, userMessage);

      if (response.success) {
        const userMsg: SessionMessage = {
          id: response.user_message.id || String(Date.now()),
          text: String(response.user_message.text || ''),
          sender: 'user',
          timestamp: response.user_message.timestamp || new Date().toISOString(),
          sentiment: response.user_message.sentiment || 'neutral',
        };

        const botMsg: SessionMessage = {
          id: response.bot_message.id || String(Date.now() + 1),
          text: String(response.bot_message.text || ''),
          sender: 'bot',
          timestamp: response.bot_message.timestamp || new Date().toISOString(),
          sentiment: response.bot_message.sentiment || 'neutral',
        };

        setMessages((prev) => [...prev, userMsg, botMsg]);
      } else {
        setError(response.error || 'Failed to send message');
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Error sending message';
      setError(errorMsg);
      console.error('Send message error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = async () => {
    try {
      setIsInitializing(true);
      setMessages([]);
      setError(null);
      const response = await chatbotAPI.startSession();

      if (response.success && response.session_id) {
        setSessionId(response.session_id);
        if (response.initial_message) {
          const msg: SessionMessage = {
            id: response.initial_message.id || String(Date.now()),
            text: String(response.initial_message.text || ''),
            sender: response.initial_message.sender || 'bot',
            timestamp: response.initial_message.timestamp || new Date().toISOString(),
            sentiment: response.initial_message.sentiment || 'neutral',
          };
          setMessages([msg]);
        }
      } else {
        setError('Failed to start new session');
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to start new session';
      setError(errorMsg);
      console.error('New chat error:', err);
    } finally {
      setIsInitializing(false);
    }
  };

  if (isInitializing && messages.length === 0) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-slate-100 to-blue-200">
        <div className="text-center">
          <div className="text-6xl mb-4 animate-bounce">💳</div>
          <p className="text-xl font-semibold text-gray-800">Sadeem</p>
          <p className="text-sm text-gray-600 mt-2">Initializing assistant...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gradient-to-br from-slate-100 to-blue-200 overflow-hidden">
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/40 z-40 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <div
        className={`${ sidebarOpen ? 'translate-x-0' : '-translate-x-full' } fixed md:relative w-64 h-screen bg-white border-r border-gray-200 flex flex-col z-50 md:z-0 transition-transform duration-200 md:transition-none shadow-lg md:shadow-none`}
      >
        <div className="p-4 border-b border-gray-200 flex items-center justify-between">
          <h1 className="text-xl font-bold text-blue-600">Sadeem</h1>
          <button onClick={() => setSidebarOpen(false)} className="md:hidden p-1 hover:bg-gray-100 rounded">
            <X size={20} />
          </button>
        </div>

        <button onClick={handleNewChat} className="m-4 flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-all font-medium shadow-md hover:shadow-lg">
          <Plus size={18} />
          New Chat
        </button>

        <div className="flex-1 overflow-y-auto p-4">
          <div className="space-y-2">
            <div className="px-3 py-2 rounded-lg bg-blue-50 text-sm text-gray-700 cursor-pointer hover:bg-blue-100 transition-colors">
              💬 Fuel Card Support
            </div>
            {sessionId && (
              <div className="text-xs text-gray-500 px-3 py-2 break-all">
                <span className="font-semibold">Session:</span> {sessionId.substring(0, 8)}...
              </div>
            )}
          </div>
        </div>

        <div className="p-4 border-t border-gray-200 text-xs text-gray-500">
          <p>🤖 RAG-Powered Assistant</p>
          <p>v4.0.0</p>
        </div>
      </div>

      <div className="flex-1 flex flex-col min-w-0">
        <div className="bg-white border-b border-gray-200 px-4 md:px-6 py-3 md:py-4 flex items-center justify-between shadow-sm">
          <div className="flex items-center gap-3">
            <button onClick={() => setSidebarOpen(!sidebarOpen)} className="md:hidden p-2 hover:bg-gray-100 rounded-lg transition-colors">
              <Menu size={20} className="text-blue-600" />
            </button>
            <div>
              <h2 className="text-lg md:text-xl font-bold text-blue-900">💳 Sadeem Support</h2>
              <p className="text-xs md:text-sm text-gray-500">
                {isLoading ? 'Typing...' : error ? 'Connection Error' : 'Ready to help'}
              </p>
            </div>
          </div>
          <button onClick={handleNewChat} className="hidden sm:flex items-center gap-2 px-3 py-2 rounded-lg text-gray-600 hover:bg-gray-100 transition-colors text-sm" title="Start a new conversation">
            <RotateCcw size={16} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4">
          {error && (
            <div className="mx-auto max-w-2xl rounded-lg bg-red-50 border border-red-200 p-4 text-red-700 text-sm">
              ⚠️ {error}
            </div>
          )}

          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full text-center">
              <div>
                <div className="text-4xl mb-4">💳</div>
                <h3 className="text-xl font-semibold text-gray-800 mb-2">Welcome to Sadeem!</h3>
                <p className="text-gray-600 max-w-sm">
                  I'm your AI-powered customer support assistant for Sadeem Fuel Card. Ask me anything about features,
                  fees, how to apply, and more!
                </p>
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-xs md:max-w-md lg:max-w-lg xl:max-w-2xl`}>
                  <MessageBubble message={message} />
                  {message.sentiment && (
                    <div className={`text-xs mt-2 px-3 py-1 rounded-full inline-block font-medium ${getSentimentColor(message.sentiment)}`}>
                      {getSentimentEmoji(message.sentiment)} {message.sentiment}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}

          {isLoading && (
            <div className="flex justify-start">
              <LoadingIndicator />
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="border-t border-gray-200 bg-white px-4 md:px-6 py-3 md:py-4 shadow-lg">
          <form onSubmit={handleSendMessage} className="max-w-4xl mx-auto">
            <div className="flex gap-2 md:gap-3">
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about Sadeem Fuel Card..."
                disabled={isLoading || isInitializing || !sessionId}
                className="flex-1 px-3 md:px-4 py-2 md:py-3 rounded-lg border border-gray-300 bg-white text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent disabled:opacity-50 disabled:bg-gray-50 text-sm md:text-base transition-colors"
              />
              <button
                type="submit"
                disabled={isLoading || isInitializing || !input.trim() || !sessionId}
                className="px-3 md:px-4 py-2 md:py-3 rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all disabled:bg-gray-400 flex items-center gap-2 font-medium text-sm md:text-base shadow-md hover:shadow-lg"
              >
                {isLoading ? (
                  <Loader2 size={18} className="animate-spin" />
                ) : (
                  <Send size={18} />
                )}
                <span className="hidden xs:inline">Send</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
