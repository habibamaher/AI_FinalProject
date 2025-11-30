'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Plus, RotateCcw, Menu, X, Loader2, Zap, BarChart2 } from 'lucide-react';
import MessageBubble from './components/MessageBubble';
import LoadingIndicator from './components/LoadingIndicator';
import EmotionIndicator from './components/EmotionIndicator';
import LanguageToggle from './components/LanguageToggle';
import { t, Language } from './i18n/translations';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: string;
  emotion?: string;
  emotion_confidence?: number;
  emotion_scores?: Record<string, number>;
  request_rating?: boolean;
}

const API_URL = 'http://localhost:5000/api';

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const [isInitializing, setIsInitializing] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [error, setError] = useState<string>('');
  const [language, setLanguage] = useState<Language>('en');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Load language preference from localStorage
  useEffect(() => {
    const savedLanguage = localStorage.getItem('sadeem_language') as Language;
    if (savedLanguage) {
      setLanguage(savedLanguage);
    }
  }, []);

  // Save language preference to localStorage
  const handleLanguageChange = (newLanguage: Language) => {
    setLanguage(newLanguage);
    localStorage.setItem('sadeem_language', newLanguage);
  };

  // Calculate emotion statistics
  const emotionStats = () => {
    const userMessages = messages.filter(m => m.sender === 'user' && m.emotion);
    const total = userMessages.length;

    const counts = {
      Happy: userMessages.filter(m => m.emotion === 'Happy').length,
      Neutral: userMessages.filter(m => m.emotion === 'Neutral').length,
      Confused: userMessages.filter(m => m.emotion === 'Confused').length,
      Frustrated: userMessages.filter(m => m.emotion === 'Frustrated').length,
      Sad: userMessages.filter(m => m.emotion === 'Sad').length,
    };

    return { counts, total };
  };

  const stats = emotionStats();

  // Determine overall mood
  const getOverallMood = () => {
    if (stats.total === 0) return 'None';

    // Find dominant emotion
    const dominant = Object.entries(stats.counts).reduce((a, b) => a[1] > b[1] ? a : b);
    return dominant[0];
  };

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${API_URL}/session/start`, { method: 'POST' });
        const data = await res.json();
        if (data.success) {
          setSessionId(data.session_id);
          if (data.initial_message) {
            setMessages([{
              id: data.initial_message.id,
              text: data.initial_message.text,
              sender: data.initial_message.sender,
              timestamp: data.initial_message.timestamp,
              emotion: data.initial_message.emotion,
            }]);
          }
        }
      } catch (err) {
        setError('Failed to connect to backend');
      } finally {
        setIsInitializing(false);
      }
    })();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading || !sessionId) return;

    const userText = input.trim();
    setInput('');
    setIsLoading(true);
    setError('');

    try {
      const res = await fetch(`${API_URL}/chat/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, message: userText, language }),
      });
      const data = await res.json();

      if (data.success) {
        setMessages(prev => [...prev,
        {
          id: data.user_message.id,
          text: data.user_message.text,
          sender: 'user',
          timestamp: data.user_message.timestamp,
          emotion: data.user_message.emotion,
          emotion_confidence: data.user_message.emotion_confidence,
          emotion_scores: data.user_message.emotion_scores,
        },
        {
          id: data.bot_message.id,
          text: data.bot_message.text,
          sender: 'bot',
          timestamp: data.bot_message.timestamp,
          emotion: data.bot_message.emotion,
          request_rating: data.bot_message.request_rating,
        }
        ]);
      } else {
        setError(data.error || 'Failed to process message');
      }
    } catch (err) {
      setError('Failed to send message');
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = async () => {
    try {
      const res = await fetch(`${API_URL}/session/start`, { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        setSessionId(data.session_id);
        if (data.initial_message) {
          setMessages([{
            id: data.initial_message.id,
            text: data.initial_message.text,
            sender: data.initial_message.sender,
            timestamp: data.initial_message.timestamp,
            emotion: data.initial_message.emotion,
          }]);
        }
      }
    } catch (err) {
      setError('Failed to start new session');
    }
  };

  if (isInitializing) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-blue-800">
        <div className="text-center">
          <div className="text-7xl mb-4 animate-bounce">⚡</div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 via-blue-400 to-magenta-400 bg-clip-text text-transparent mb-2">Sadeem</h1>
          <p className="text-sm text-cyan-300 mt-2">Powered by 5-Emotion AI</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 overflow-hidden" dir={language === 'ar' ? 'rtl' : 'ltr'}>
      {sidebarOpen && <div className="fixed inset-0 bg-black/50 z-40 md:hidden" onClick={() => setSidebarOpen(false)} />}

      <div className={`${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} fixed md:relative w-72 h-screen bg-gradient-to-b from-slate-800 to-slate-900 border-r border-blue-500/30 flex flex-col z-50 md:z-0 transition-transform duration-200 md:transition-none shadow-2xl overflow-y-auto`}>

        <div className="p-6 border-b border-blue-500/30 bg-gradient-to-r from-blue-600/20 to-magenta-600/20">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-400 to-magenta-500 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <span className="text-white font-bold text-lg">⚡</span>
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">Sadeem</h1>
              <p className="text-xs text-cyan-300">5-Emotion AI</p>
            </div>
          </div>
          <button onClick={() => setSidebarOpen(false)} className="md:hidden p-1 hover:bg-blue-500/20 rounded ml-auto">
            <X size={20} className="text-cyan-400" />
          </button>
        </div>

        <button onClick={handleNewChat} className="m-4 flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-gradient-to-r from-blue-600 to-magenta-600 text-white hover:shadow-lg hover:shadow-magenta-500/50 transition-all font-semibold shadow-lg group">
          <Plus size={18} className="group-hover:rotate-90 transition-transform" />
          {t('new_chat', language)}
        </button>

        <div className="mx-4 mb-4">
          <LanguageToggle language={language} onLanguageChange={handleLanguageChange} />
        </div>

        <div className="mx-4 p-5 rounded-xl bg-gradient-to-br from-blue-900/50 to-magenta-900/30 border border-cyan-400/30 backdrop-blur-sm shadow-inner">
          <h3 className="text-sm font-bold text-cyan-300 mb-4 flex items-center gap-2">
            <BarChart2 size={16} className="text-magenta-400" />
            Live Emotion Analytics
          </h3>

          <div className="space-y-2 mb-4">
            <div className="flex items-center justify-between text-xs mb-1">
              <span className="text-slate-400">Emotion Distribution</span>
              <span className="text-slate-400">{stats.total} msgs</span>
            </div>

            {/* Emotion Bars */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <div className="w-16 text-xs text-green-300 flex items-center gap-1"><span className="text-xs">😊</span> Happy</div>
                <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
                  <div className="h-full bg-green-400 transition-all duration-500" style={{ width: `${stats.total ? (stats.counts.Happy / stats.total) * 100 : 0}%` }} />
                </div>
                <div className="w-4 text-xs text-right text-slate-400">{stats.counts.Happy}</div>
              </div>

              <div className="flex items-center gap-2">
                <div className="w-16 text-xs text-blue-300 flex items-center gap-1"><span className="text-xs">😐</span> Neutral</div>
                <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
                  <div className="h-full bg-blue-400 transition-all duration-500" style={{ width: `${stats.total ? (stats.counts.Neutral / stats.total) * 100 : 0}%` }} />
                </div>
                <div className="w-4 text-xs text-right text-slate-400">{stats.counts.Neutral}</div>
              </div>

              <div className="flex items-center gap-2">
                <div className="w-16 text-xs text-amber-300 flex items-center gap-1"><span className="text-xs">😕</span> Confused</div>
                <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
                  <div className="h-full bg-amber-400 transition-all duration-500" style={{ width: `${stats.total ? (stats.counts.Confused / stats.total) * 100 : 0}%` }} />
                </div>
                <div className="w-4 text-xs text-right text-slate-400">{stats.counts.Confused}</div>
              </div>

              <div className="flex items-center gap-2">
                <div className="w-16 text-xs text-orange-300 flex items-center gap-1"><span className="text-xs">😠</span> Frustrated</div>
                <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
                  <div className="h-full bg-orange-500 transition-all duration-500" style={{ width: `${stats.total ? (stats.counts.Frustrated / stats.total) * 100 : 0}%` }} />
                </div>
                <div className="w-4 text-xs text-right text-slate-400">{stats.counts.Frustrated}</div>
              </div>

              <div className="flex items-center gap-2">
                <div className="w-16 text-xs text-indigo-300 flex items-center gap-1"><span className="text-xs">😢</span> Sad</div>
                <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
                  <div className="h-full bg-indigo-400 transition-all duration-500" style={{ width: `${stats.total ? (stats.counts.Sad / stats.total) * 100 : 0}%` }} />
                </div>
                <div className="w-4 text-xs text-right text-slate-400">{stats.counts.Sad}</div>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-4 border-t border-white/10 flex items-center justify-between">
            <span className="text-xs text-slate-400">Current Mood</span>
            <EmotionIndicator emotion={getOverallMood()} showLabel={true} />
          </div>
        </div>

        <div className="flex-1" />

        <div className="p-4 border-t border-blue-500/30 bg-gradient-to-t from-slate-900 to-transparent text-xs text-cyan-300/60">
          <p className="font-semibold text-cyan-400 mb-1">System Status</p>
          <div className="flex items-center gap-2 mb-1">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span>RAG Pipeline Active</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse delay-75" />
            <span>Emotion AI Active</span>
          </div>
        </div>
      </div>

      <div className="flex-1 flex flex-col min-w-0 relative">

        <div className="bg-gradient-to-r from-slate-800/80 to-blue-900/80 border-b border-blue-500/30 px-4 md:px-6 py-4 md:py-5 flex items-center justify-between backdrop-blur-md shadow-lg z-10">
          <div className="flex items-center gap-4">
            <button onClick={() => setSidebarOpen(!sidebarOpen)} className="md:hidden p-2 hover:bg-blue-500/20 rounded-lg transition-colors">
              <Menu size={20} className="text-cyan-400" />
            </button>
            <div>
              <h2 className="text-lg md:text-2xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">Sadeem Support</h2>
              <p className="text-xs md:text-sm text-cyan-300/70 flex items-center gap-2">
                {isLoading ? (
                  <span className="flex items-center gap-1"><Loader2 size={12} className="animate-spin" /> Processing...</span>
                ) : error ? (
                  <span className="text-red-400 flex items-center gap-1">❌ Connection Error</span>
                ) : (
                  <span className="flex items-center gap-1">✅ Online</span>
                )}
              </p>
            </div>
          </div>
          <button onClick={handleNewChat} className="hidden sm:flex items-center justify-center w-10 h-10 rounded-lg bg-gradient-to-br from-magenta-600 to-red-600 hover:shadow-lg hover:shadow-magenta-500/50 transition-all text-white group">
            <RotateCcw size={18} className="group-hover:-rotate-180 transition-transform duration-500" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6 scroll-smooth">
          {error && (
            <div className="bg-red-900/30 border border-red-500/50 p-4 text-red-300 text-sm rounded-lg backdrop-blur-sm animate-fadeIn flex items-center gap-2">
              <AlertTriangle size={16} />
              {error}
            </div>
          )}

          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full text-center p-8">
              <div className="max-w-md">
                <div className="text-6xl mb-6 animate-pulse inline-block">⚡</div>
                <h3 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-magenta-400 bg-clip-text text-transparent mb-4">Welcome to Sadeem!</h3>
                <p className="text-cyan-300/70 text-lg mb-8 leading-relaxed">
                  I'm your AI assistant for Sadeem Fuel Cards. I can help with fees, features, applications, and more.
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                  <button onClick={() => setInput("What are the card fees?")} className="p-3 rounded-lg bg-slate-800/50 border border-blue-500/20 hover:bg-blue-600/20 hover:border-blue-500/50 transition-all text-cyan-100">
                    "What are the card fees?"
                  </button>
                  <button onClick={() => setInput("How do I apply?")} className="p-3 rounded-lg bg-slate-800/50 border border-blue-500/20 hover:bg-blue-600/20 hover:border-blue-500/50 transition-all text-cyan-100">
                    "How do I apply?"
                  </button>
                  <button onClick={() => setInput("Can I use BenefitPay?")} className="p-3 rounded-lg bg-slate-800/50 border border-blue-500/20 hover:bg-blue-600/20 hover:border-blue-500/50 transition-all text-cyan-100">
                    "Can I use BenefitPay?"
                  </button>
                  <button onClick={() => setInput("My card is not working")} className="p-3 rounded-lg bg-slate-800/50 border border-blue-500/20 hover:bg-blue-600/20 hover:border-blue-500/50 transition-all text-cyan-100">
                    "My card is not working"
                  </button>
                </div>
              </div>
            </div>
          ) : (
            messages.map((msg) => (
              <div key={msg.id} className={`animate-fadeIn`}>
                <MessageBubble message={msg} sessionId={sessionId} />
              </div>
            ))
          )}

          {isLoading && (
            <div className="flex justify-start animate-fadeIn">
              <LoadingIndicator />
            </div>
          )}
          <div ref={messagesEndRef} className="h-4" />
        </div>

        <div className="border-t border-blue-500/30 bg-gradient-to-t from-slate-900 via-slate-900/95 to-slate-900/80 px-4 md:px-6 py-4 md:py-6 shadow-2xl backdrop-blur-md z-20">
          <form onSubmit={handleSendMessage} className="max-w-4xl mx-auto relative">
            <div className="flex gap-3 items-end">
              <div className="flex-1 relative">
                <input
                  ref={inputRef}
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder={t('type_message', language)}
                  disabled={isLoading || !sessionId}
                  className="w-full px-5 py-4 rounded-xl border border-blue-500/30 bg-slate-800/50 text-white placeholder-cyan-300/30 focus:outline-none focus:ring-2 focus:ring-cyan-400/50 focus:border-cyan-400/50 disabled:opacity-50 disabled:bg-slate-800 text-base backdrop-blur-sm transition-all shadow-inner"
                />
                <div className="absolute right-3 bottom-3 text-[10px] text-cyan-500/40 font-mono hidden sm:block">
                  ENTER to send
                </div>
              </div>
              <button
                type="submit"
                disabled={isLoading || !input.trim() || !sessionId}
                className="px-6 py-4 rounded-xl bg-gradient-to-r from-blue-600 to-magenta-600 text-white hover:shadow-lg hover:shadow-magenta-500/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all font-semibold flex items-center gap-2 shadow-lg disabled:shadow-none transform hover:scale-105 active:scale-95"
              >
                {isLoading ? <Loader2 size={20} className="animate-spin" /> : <Send size={20} />}
                <span className="hidden sm:inline">Send</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

function AlertTriangle({ size, className }: { size?: number, className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={size || 24}
      height={size || 24}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
      <path d="M12 9v4" />
      <path d="M12 17h.01" />
    </svg>
  );
}
