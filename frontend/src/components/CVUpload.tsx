import { useState } from 'react';
import { Upload } from 'lucide-react';
import { apiClient } from '../services/apiClient';
import { CVExtractor } from '../utils/cvExtractor';

interface CVUploadProps {
  jobDescription: string;
  customRules: string;
  llmModel: string;
  onEvaluationsChange: (evaluations: Array<{ filename: string; evaluation: string }>) => void;
}

export default function CVUpload({
  jobDescription,
  customRules,
  llmModel,
  onEvaluationsChange,
}: CVUploadProps) {
  const [files, setFiles] = useState<FileList | null>(null);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [currentFile, setCurrentFile] = useState<string>('');
  const [messages, setMessages] = useState<Array<{ type: 'success' | 'error'; text: string }>>([]);

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

  return (
    <div className="cv-upload">
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
  );
}

