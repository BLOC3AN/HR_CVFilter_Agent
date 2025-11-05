import { useState } from 'react';
import { Upload, Send } from 'lucide-react';
import { apiClient } from '../services/apiClient';
import { CVExtractor } from '../utils/cvExtractor';
import { useSession } from '../contexts/SessionContext';

interface CVUploadWithChatProps {
  jobDescription: string;
  customRules: string;
  llmModel: string;
  onEvaluationsChange: (evaluations: Array<{ filename: string; evaluation: string }>) => void;
  cvEvaluations: Array<{ filename: string; evaluation: string }>;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function CVUploadWithChat({
  jobDescription,
  customRules,
  llmModel,
  onEvaluationsChange,
  cvEvaluations,
}: CVUploadWithChatProps) {
  const { sessionId } = useSession();
  const [files, setFiles] = useState<FileList | null>(null);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [currentFile, setCurrentFile] = useState<string>('');
  const [messages, setMessages] = useState<Array<{ type: 'success' | 'error'; text: string }>>([]);
  
  // Chat state
  const [chatMessages, setChatMessages] = useState<Message[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [isChatLoading, setIsChatLoading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFiles(e.target.files);
    setMessages([]);
  };

  const handleEvaluate = async () => {
    if (!files || files.length === 0) {
      return;
    }

    if (!jobDescription) {
      setMessages([{ type: 'error', text: '⚠️ Please enter a job description first' }]);
      return;
    }

    setIsEvaluating(true);
    setMessages([]);

    // Clear previous evaluations - only show new results
    onEvaluationsChange([]);

    const evaluations: Array<{ filename: string; evaluation: string }> = [];

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      setCurrentFile(file.name);

      try {
        const cvContent = await CVExtractor.extractText(file);

        const result = await apiClient.evaluateCV({
          session_id: sessionId || undefined,
          cv_content: cvContent,
          job_description: jobDescription,
          custom_rules: customRules,
          llm_model: llmModel,
        });

        if (result.success && result.evaluation) {
          evaluations.push({
            filename: file.name,
            evaluation: result.evaluation,
          });
          setMessages((prev) => [
            ...prev,
            { type: 'success', text: `✅ Evaluated ${file.name}` },
          ]);
        } else {
          setMessages((prev) => [
            ...prev,
            { type: 'error', text: `❌ Failed to evaluate ${file.name}: ${result.error}` },
          ]);
        }
      } catch (error) {
        setMessages((prev) => [
          ...prev,
          {
            type: 'error',
            text: `❌ Error processing ${file.name}: ${error instanceof Error ? error.message : 'Unknown error'}`,
          },
        ]);
      }
    }

    // Set only the new evaluations (no history accumulation)
    onEvaluationsChange(evaluations);
    setIsEvaluating(false);
    setCurrentFile('');
  };

  const handleSendMessage = async () => {
    if (!chatInput.trim() || isChatLoading) return;

    const userMessage = chatInput.trim();
    setChatInput('');

    // Add user message
    const newMessages: Message[] = [...chatMessages, { role: 'user', content: userMessage }];
    setChatMessages(newMessages);
    setIsChatLoading(true);

    try {
      const response = await apiClient.chat({
        session_id: sessionId || undefined,
        message: userMessage,
        job_description: jobDescription,
        custom_rules: customRules,
        cv_evaluations: cvEvaluations,
        chat_history: chatMessages,
        llm_model: llmModel,
      });

      if (response.success && response.response) {
        setChatMessages([...newMessages, { role: 'assistant', content: response.response }]);
      } else {
        setChatMessages([
          ...newMessages,
          { role: 'assistant', content: `Error: ${response.error || 'Unknown error'}` },
        ]);
      }
    } catch (error) {
      setChatMessages([
        ...newMessages,
        {
          role: 'assistant',
          content: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        },
      ]);
    } finally {
      setIsChatLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="cv-upload-with-chat">
      {/* CV Upload Section */}
      <div className="cv-upload-section">
        <h2>📤 Upload CVs</h2>

        <div className="upload-area">
          <label htmlFor="file-upload" className="file-upload-label">
            <Upload size={48} />
            <p>Upload CV files (PDF, DOCX, TXT, MD)</p>
            <p className="file-info">
              {files && files.length > 0
                ? `${files.length} file(s) selected`
                : 'Click to select files or drag and drop'}
            </p>
          </label>
          <input
            id="file-upload"
            type="file"
            multiple
            accept=".pdf,.docx,.txt,.md"
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />
        </div>

        {files && files.length > 0 && (
          <div className="file-list">
            <h4>Selected files:</h4>
            <ul>
              {Array.from(files).map((file, index) => (
                <li key={index}>{file.name}</li>
              ))}
            </ul>
          </div>
        )}

        {files && files.length > 0 && (
          <button
            onClick={handleEvaluate}
            disabled={isEvaluating}
            className="btn-primary btn-evaluate"
          >
            {isEvaluating ? `🔍 Evaluating ${currentFile}...` : '🔍 Evaluate CVs'}
          </button>
        )}

        {messages.length > 0 && (
          <div className="messages">
            {messages.map((msg, index) => (
              <div key={index} className={`message ${msg.type}`}>
                {msg.text}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Chat Section */}
      <div className="chat-section-inline">
        <h3>💬 Chat with AI Assistant</h3>
        
        <div className="chat-messages-compact">
          {chatMessages.length === 0 ? (
            <div className="chat-empty">
              <p>Ask questions about the CVs or get help with evaluation...</p>
            </div>
          ) : (
            chatMessages.map((msg, index) => (
              <div key={index} className={`chat-message ${msg.role}`}>
                <div className="message-content" dangerouslySetInnerHTML={{ __html: msg.content }} />
              </div>
            ))
          )}
          {isChatLoading && (
            <div className="chat-message assistant">
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="chat-input-area">
          <input
            type="text"
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            disabled={isChatLoading}
            className="chat-input-compact"
          />
          <button
            onClick={handleSendMessage}
            disabled={!chatInput.trim() || isChatLoading}
            className="btn-send-compact"
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}

