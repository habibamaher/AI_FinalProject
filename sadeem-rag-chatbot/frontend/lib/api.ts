const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';

export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: string;
  sentiment: string;
  source?: string;
  context_used?: boolean;
}

export interface SessionResponse {
  success: boolean;
  session_id: string;
  message?: string;
  initial_message?: Message;
  error?: string;
}

export interface ChatResponse {
  success: boolean;
  user_message: Message;
  bot_message: Message;
  session_id: string;
  error?: string;
}

export interface HistoryResponse {
  session_id: string;
  messages: Message[];
  error?: string;
}

class ChatbotAPI {
  private sessionId: string | null = null;

  async startSession(): Promise<SessionResponse> {
    try {
      const response = await fetch(`${API_URL}/session/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: SessionResponse = await response.json();
      if (data.success) {
        this.sessionId = data.session_id;
      }
      return data;
    } catch (error) {
      console.error('Error starting session:', error);
      throw error;
    }
  }

  async sendMessage(message: string): Promise<ChatResponse> {
    if (!this.sessionId) {
      throw new Error('No active session. Call startSession first.');
    }

    try {
      const response = await fetch(`${API_URL}/chat/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: this.sessionId,
          message: message,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: ChatResponse = await response.json();
      return data;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  }

  async getHistory(): Promise<HistoryResponse> {
    if (!this.sessionId) {
      throw new Error('No active session. Call startSession first.');
    }

    try {
      const response = await fetch(`${API_URL}/session/${this.sessionId}/history`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: HistoryResponse = await response.json();
      return data;
    } catch (error) {
      console.error('Error getting history:', error);
      throw error;
    }
  }

  async resetSession(): Promise<{ success: boolean; message: string; error?: string }> {
    if (!this.sessionId) {
      throw new Error('No active session. Call startSession first.');
    }

    try {
      const response = await fetch(`${API_URL}/session/${this.sessionId}/reset`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error resetting session:', error);
      throw error;
    }
  }

  getSessionId(): string | null {
    return this.sessionId;
  }

  setSessionId(id: string): void {
    this.sessionId = id;
  }
}

export const chatbotAPI = new ChatbotAPI();