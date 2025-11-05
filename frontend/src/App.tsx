import { useState, useEffect } from 'react';
import './App.css';
import Sidebar from './components/Sidebar';
import CVUpload from './components/CVUpload';
import EvaluationResults from './components/EvaluationResults';
import Chat from './components/Chat';
import { apiClient } from './services/apiClient';

function App() {
  const [jobDescription, setJobDescription] = useState('');
  const [customRules, setCustomRules] = useState('');
  const [llmModel, setLlmModel] = useState('gemini-2.0-flash');
  const [cvEvaluations, setCvEvaluations] = useState<Array<{ filename: string; evaluation: string }>>([]);
  const [backendStatus, setBackendStatus] = useState<'checking' | 'healthy' | 'unhealthy'>('checking');
  const [backendError, setBackendError] = useState('');

  useEffect(() => {
    checkBackendHealth();
  }, []);

  const checkBackendHealth = async () => {
    const health = await apiClient.healthCheck();
    if (health.status === 'healthy') {
      setBackendStatus('healthy');
    } else {
      setBackendStatus('unhealthy');
      setBackendError(health.error || 'Unknown error');
    }
  };

  if (backendStatus === 'checking') {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Checking backend connection...</p>
      </div>
    );
  }

  if (backendStatus === 'unhealthy') {
    return (
      <div className="error-container">
        <h2>⚠️ Backend API is not available</h2>
        <p>{backendError}</p>
        <p>Please make sure the backend service is running</p>
        <button onClick={checkBackendHealth} className="btn-retry">
          Retry Connection
        </button>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>📄 HR CV Filter Agent</h1>
      </header>

      <div className="app-container">
        <aside className="app-sidebar">
          <Sidebar
            jobDescription={jobDescription}
            onJobDescriptionChange={setJobDescription}
            customRules={customRules}
            onCustomRulesChange={setCustomRules}
            llmModel={llmModel}
            onLlmModelChange={setLlmModel}
          />
        </aside>

        <main className="app-main">
          <div className="main-grid">
            <div className="grid-item">
              <CVUpload
                jobDescription={jobDescription}
                customRules={customRules}
                llmModel={llmModel}
                onEvaluationsChange={setCvEvaluations}
              />
            </div>
            <div className="grid-item">
              <EvaluationResults evaluations={cvEvaluations} />
            </div>
          </div>

          <div className="chat-section">
            <Chat
              jobDescription={jobDescription}
              customRules={customRules}
              cvEvaluations={cvEvaluations}
              llmModel={llmModel}
            />
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
