import { useState, useEffect, useRef, FormEvent } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

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

// Typing Indicator Component
const TypingIndicator = () => (
  <div className="typing-indicator">
    <span></span>
    <span></span>
    <span></span>
  </div>
);

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
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

const Chat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [useScrape, setUseScrape] = useState(false);
  const [scrapeUrl, setScrapeUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(getSessionId());
  const [showSuggestions, setShowSuggestions] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const suggestions = [
    "What can you help me with?",
    "Search for the latest AI trends",
    "Explain quantum computing",
    "Write a Python function"
  ];

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Hide suggestions once messages exist
  useEffect(() => {
    if (messages.length > 0) {
      setShowSuggestions(false);
    }
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

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text).then(() => {
      // Optional: Add toast notification here
      console.log('Copied to clipboard!');
    });
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInputMessage(suggestion);
    setShowSuggestions(false);
  };

  const sendMessage = async (e: FormEvent, customMessage?: string) => {
    e.preventDefault();
    
    const messageText = customMessage || inputMessage.trim();
    if (!messageText) return;
    if (useScrape && !scrapeUrl.trim()) {
      alert('Please provide a URL to scrape');
      return;
    }

    // Add user message to UI immediately
    const userMessage: Message = {
      role: 'user',
      content: messageText,
      timestamp: new Date(),
    };
    setMessages((prev: Message[]) => [...prev, userMessage]);
    
    // Clear input
    setInputMessage('');
    setIsLoading(true);

    try {
      const requestBody: ChatRequest = {
        session_id: sessionId,
        message: messageText,
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
        setShowSuggestions(true);
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
        <div className="header-content">
          <h1>✨ InnoviTech AI</h1>
          <p className="subtitle">Powered by LLaMA 3.1 via Ollama</p>
        </div>
        <button 
          onClick={resetSession} 
          className="reset-button"
          title="Start new conversation"
        >
          <span>🔄</span> New Chat
        </button>
      </header>

      <div className="messages-container">
        {showSuggestions && messages.length === 0 && (
          <div className="suggestions-container">
            <h2>👋 Welcome! Try asking:</h2>
            <div className="suggestions-grid">
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  className="suggestion-chip"
                  onClick={() => handleSuggestionClick(suggestion)}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}
        
        {messages.map((msg: Message, index: number) => (
          <div key={index} className={`message ${msg.role}`}>
            <div className="message-avatar">
              {msg.role === 'user' ? '👤' : '🤖'}
            </div>
            <div className="message-bubble">
              <div className="message-header">
                <span className="message-role">
                  {msg.role === 'user' ? 'You' : 'AI Assistant'}
                </span>
                <span className="message-time">{formatTime(msg.timestamp)}</span>
              </div>
              <div className="message-content">
                {msg.role === 'assistant' ? (
                  <ReactMarkdown
                    components={{
                      code({ node, inline, className, children, ...props }) {
                        const match = /language-(\w+)/.exec(className || '');
                        return !inline && match ? (
                          <div className="code-block-wrapper">
                            <div className="code-block-header">
                              <span>{match[1]}</span>
                              <button
                                className="copy-button"
                                onClick={() => copyToClipboard(String(children))}
                              >
                                📋 Copy
                              </button>
                            </div>
                            <SyntaxHighlighter
                              style={vscDarkPlus}
                              language={match[1]}
                              PreTag="div"
                              {...props}
                            >
                              {String(children).replace(/\n$/, '')}
                            </SyntaxHighlighter>
                          </div>
                        ) : (
                          <code className={className} {...props}>
                            {children}
                          </code>
                        );
                      },
                    }}
                  >
                    {msg.content}
                  </ReactMarkdown>
                ) : (
                  <p>{msg.content}</p>
                )}
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="message assistant">
            <div className="message-avatar">🤖</div>
            <div className="message-bubble">
              <div className="message-header">
                <span className="message-role">AI Assistant</span>
              </div>
              <div className="message-content">
                <TypingIndicator />
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={(e) => sendMessage(e)} className="input-container">
        <div className="scrape-options">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={useScrape}
              onChange={(e) => setUseScrape(e.target.checked)}
            />
            <span>🌐 Use Web Scraping</span>
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
            {isLoading ? '⏳' : '🚀'} Send
          </button>
        </div>
      </form>
    </div>
  );
};

export default Chat;
