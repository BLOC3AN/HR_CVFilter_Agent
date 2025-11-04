import { useState, useRef, useEffect, useCallback } from 'react';
import { Send, GripHorizontal } from 'lucide-react';
import { apiClient } from '../services/apiClient';

interface ChatProps {
  jobDescription: string;
  customRules: string;
  cvEvaluations: Array<{ filename: string; evaluation: string }>;
  llmModel: string;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function Chat({
  jobDescription,
  customRules,
  cvEvaluations,
  llmModel,
}: ChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [chatHeight, setChatHeight] = useState(500);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const resizeRef = useRef<HTMLDivElement>(null);
  const isDraggingRef = useRef(false);
  const startYRef = useRef(0);
  const startHeightRef = useRef(0);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const formatMarkdown = (text: string) => {
    let formatted = text;

    // Headers
    formatted = formatted.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    formatted = formatted.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    formatted = formatted.replace(/^# (.*$)/gim, '<h1>$1</h1>');

    // Bold
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Italic
    formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Code blocks
    formatted = formatted.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');

    // Inline code
    formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Links
    formatted = formatted.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');

    // Line breaks
    formatted = formatted.replace(/\n/g, '<br>');

    // Lists
    formatted = formatted.replace(/^- (.*$)/gim, '<li>$1</li>');
    formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');

    return formatted;
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    isDraggingRef.current = true;
    startYRef.current = e.clientY;
    startHeightRef.current = chatHeight;
    document.body.style.cursor = 'ns-resize';
    document.body.style.userSelect = 'none';
  }, [chatHeight]);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDraggingRef.current) return;

      // Kéo xuống = giảm height, kéo lên = tăng height
      const deltaY = e.clientY - startYRef.current;
      const newHeight = Math.min(Math.max(startHeightRef.current - deltaY, 300), 800);
      setChatHeight(newHeight);
    };

    const handleMouseUp = () => {
      if (isDraggingRef.current) {
        isDraggingRef.current = false;
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
      }
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, []);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const result = await apiClient.chat({
        message: input,
        job_description: jobDescription,
        custom_rules: customRules,
        cv_evaluations: cvEvaluations,
        chat_history: messages,
        llm_model: llmModel,
      });

      if (result.success && result.response) {
        const assistantMessage: Message = {
          role: 'assistant',
          content: result.response,
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } else {
        const errorMessage: Message = {
          role: 'assistant',
          content: `Error: ${result.error || 'Unknown error'}`,
        };
        setMessages((prev) => [...prev, errorMessage]);
      }
    } catch (error) {
      const errorMessage: Message = {
        role: 'assistant',
        content: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-container" style={{ height: `${chatHeight}px` }}>
      <div
        ref={resizeRef}
        className="chat-resize-handle"
        onMouseDown={handleMouseDown}
      >
        <GripHorizontal size={20} />
      </div>

      <h2>💬 Chat with Agent</h2>

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="info-message">
            Ask questions about the evaluated CVs...
          </div>
        ) : (
          messages.map((message, index) => (
            <div key={index} className={`chat-message ${message.role}`}>
              <div className="message-role">
                {message.role === 'user' ? '👤 You' : '🤖 Assistant'}
              </div>
              <div
                className="message-content markdown-content"
                dangerouslySetInnerHTML={{ __html: formatMarkdown(message.content) }}
              />
            </div>
          ))
        )}
        {isLoading && (
          <div className="chat-message assistant">
            <div className="message-role">🤖 Assistant</div>
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

      <div className="chat-input-container">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask questions about the evaluated CVs..."
          disabled={isLoading}
          className="chat-input"
        />
        <button
          onClick={handleSend}
          disabled={isLoading || !input.trim()}
          className="btn-send"
        >
          <Send size={20} />
        </button>
      </div>
    </div>
  );
}

