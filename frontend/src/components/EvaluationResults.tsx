import { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';

interface EvaluationResultsProps {
  evaluations: Array<{ filename: string; evaluation: string }>;
}

export default function EvaluationResults({ evaluations }: EvaluationResultsProps) {
  const [expandedIndex, setExpandedIndex] = useState<number>(0);

  const toggleExpand = (index: number) => {
    setExpandedIndex(expandedIndex === index ? -1 : index);
  };

  return (
    <div className="evaluation-results">
      <h2>📊 Evaluation Results</h2>
      
      {evaluations.length === 0 ? (
        <div className="info-message">
          No evaluations yet. Upload and evaluate CVs to see results here.
        </div>
      ) : (
        <div className="results-list">
          {evaluations.map((cv, index) => (
            <div key={index} className="result-item">
              <div
                className="result-header"
                onClick={() => toggleExpand(index)}
              >
                <span className="filename">📄 {cv.filename}</span>
                {expandedIndex === index ? (
                  <ChevronUp size={20} />
                ) : (
                  <ChevronDown size={20} />
                )}
              </div>
              {expandedIndex === index && (
                <div className="result-content">
                  <div
                    className="markdown-content"
                    dangerouslySetInnerHTML={{
                      __html: formatMarkdown(cv.evaluation),
                    }}
                  />
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function formatMarkdown(text: string): string {
  let html = text;

  // Code blocks (must be before inline code)
  html = html.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');

  // Inline code
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

  // Headers (order matters: h3 before h2 before h1)
  html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
  html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
  html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');

  // Bold
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

  // Italic
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');

  // Links
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');

  // Lists
  html = html.replace(/^- (.*$)/gim, '<li>$1</li>');
  html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');

  // Line breaks
  html = html.replace(/\n/g, '<br>');

  return html;
}

