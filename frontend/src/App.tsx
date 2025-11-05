import { useState, useEffect } from 'react';
import './App.css';
import Sidebar from './components/Sidebar';
import CVUploadWithChat from './components/CVUploadWithChat';
import EvaluationResults from './components/EvaluationResults';
import { apiClient } from './services/apiClient';
import { SessionProvider, useSession } from './contexts/SessionContext';
import { SocketProvider } from './contexts/SocketContext';

function AppContent() {
  const { sessionId } = useSession();
  const [jobDescription, setJobDescription] = useState('');
  const [customRules, setCustomRules] = useState('');
  const [llmModel, setLlmModel] = useState('gemini-2.0-flash');
  const [cvEvaluations, setCvEvaluations] = useState<Array<{ filename: string; evaluation: string }>>([]);
  const [backendStatus, setBackendStatus] = useState<'checking' | 'healthy' | 'unhealthy'>('checking');
  const [backendError, setBackendError] = useState('');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

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
    <SocketProvider sessionId={sessionId}>
      <div className="app">
        <header className="app-header">
          <h1>📄 HR CV Filter Agent</h1>
        </header>

        <div className="app-container">
          <aside className={`app-sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
            <Sidebar
              jobDescription={jobDescription}
              onJobDescriptionChange={setJobDescription}
              customRules={customRules}
              onCustomRulesChange={setCustomRules}
              llmModel={llmModel}
              onLlmModelChange={setLlmModel}
              collapsed={sidebarCollapsed}
              onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
            />
          </aside>

          <main className={`app-main ${sidebarCollapsed ? 'expanded' : ''}`}>
            <div className="main-content">
              <div className="left-panel">
                <CVUploadWithChat
                  jobDescription={jobDescription}
                  customRules={customRules}
                  llmModel={llmModel}
                  onEvaluationsChange={setCvEvaluations}
                  cvEvaluations={cvEvaluations}
                />
              </div>
              <div className="right-panel">
                <EvaluationResults evaluations={cvEvaluations} />
              </div>
            </div>
          </main>
        </div>
      </div>
    </SocketProvider>
  );
}

function App() {
  return (
    <SessionProvider>
      <AppContent />
    </SessionProvider>
  );
}

export default App;
