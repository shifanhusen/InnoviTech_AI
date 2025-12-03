import { useState, useEffect, useRef, FormEvent } from 'react';

// Types
interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ChatRequest {
  session_id: string;
  message: string;
  use_scrape: boolean;
  scrape_url?: string;
}

interface ChatResponse {
  reply: string;
  session_expired: boolean;
}

interface HistoryMessage {
  role: 'user' | 'assistant';
  content: string;
}

// Utility to generate/retrieve session ID
const getSessionId = (): string => {
  let sessionId = localStorage.getItem('ai_assistant_session_id');
  if (!sessionId) {
    sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('ai_assistant_session_id', sessionId);
  }
  return sessionId;
};

// API base URL from environment variable
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001';

const Chat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [useScrape, setUseScrape] = useState(false);
  const [scrapeUrl, setScrapeUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(getSessionId());
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Load session history on mount
  useEffect(() => {
    const loadHistory = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/llm/session/${sessionId}`);
        if (response.ok) {
          const data = await response.json();
          if (data.history && data.history.length > 0) {
            const loadedMessages: Message[] = data.history.map((msg: HistoryMessage) => ({
              role: msg.role,
              content: msg.content,
              timestamp: new Date(),
            }));
            setMessages(loadedMessages);
          }
        }
      } catch (error) {
        console.error('Failed to load session history:', error);
      }
    };
    loadHistory();
  }, [sessionId]);

  const sendMessage = async (e: FormEvent) => {
    e.preventDefault();
    
    if (!inputMessage.trim()) return;
    if (useScrape && !scrapeUrl.trim()) {
      alert('Please provide a URL to scrape');
      return;
    }

    // Add user message to UI immediately
    const userMessage: Message = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };
    setMessages((prev: Message[]) => [...prev, userMessage]);
    
    // Clear input
    const messageToSend = inputMessage;
    setInputMessage('');
    setIsLoading(true);

    try {
      const requestBody: ChatRequest = {
        session_id: sessionId,
        message: messageToSend,
        use_scrape: useScrape,
      };

      if (useScrape && scrapeUrl.trim()) {
        requestBody.scrape_url = scrapeUrl.trim();
      }

      const response = await fetch(`${API_BASE_URL}/api/llm/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: ChatResponse = await response.json();

      // Add assistant message
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.reply,
        timestamp: new Date(),
      };
      setMessages((prev: Message[]) => [...prev, assistantMessage]);

      // Show session expiration notice if applicable
      if (data.session_expired) {
        console.log('Session was expired, started new conversation');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Add error message
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      };
      setMessages((prev: Message[]) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const resetSession = async () => {
    if (!confirm('Are you sure you want to reset the conversation?')) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/llm/reset`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ session_id: sessionId }),
      });

      if (response.ok) {
        setMessages([]);
        setInputMessage('');
        setScrapeUrl('');
        console.log('Session reset successfully');
      }
    } catch (error) {
      console.error('Error resetting session:', error);
    }
  };

  const formatTime = (date: Date): string => {
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className="chat-container">
      <header className="chat-header">
        <h1>AI Assistant</h1>
        <p className="subtitle">Powered by LLaMA 3.1 via Ollama</p>
        <button 
          onClick={resetSession} 
          className="reset-button"
          title="Reset conversation"
        >
          Reset
        </button>
      </header>

      <div className="messages-container">
        {messages.length === 0 && (
          <div className="empty-state">
            <h2>👋 Hello!</h2>
            <p>I'm your AI assistant. Ask me anything!</p>
          </div>
        )}
        
        {messages.map((msg: Message, index: number) => (
          <div key={index} className={`message ${msg.role}`}>
            <div className="message-header">
              <span className="message-role">
                {msg.role === 'user' ? '👤 You' : '🤖 Bot'}
              </span>
              <span className="message-time">{formatTime(msg.timestamp)}</span>
            </div>
            <div className="message-content">{msg.content}</div>
          </div>
        ))}
        
        {isLoading && (
          <div className="message assistant loading">
            <div className="message-header">
              <span className="message-role">🤖 Bot</span>
            </div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={sendMessage} className="input-container">
        <div className="scrape-options">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={useScrape}
              onChange={(e) => setUseScrape(e.target.checked)}
            />
            <span>Use Web Scraping</span>
          </label>
          
          {useScrape && (
            <input
              type="url"
              value={scrapeUrl}
              onChange={(e) => setScrapeUrl(e.target.value)}
              placeholder="Enter URL to scrape..."
              className="url-input"
            />
          )}
        </div>

        <div className="message-input-row">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Type your message..."
            disabled={isLoading}
            className="message-input"
          />
          <button 
            type="submit" 
            disabled={isLoading || !inputMessage.trim()}
            className="send-button"
          >
            {isLoading ? '⏳' : '➤'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default Chat;
