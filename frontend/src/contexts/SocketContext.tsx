import { createContext, useContext, useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import { io, Socket } from 'socket.io-client';

interface SocketContextType {
  socket: Socket | null;
  connected: boolean;
  queuePosition: number | null;
  queueTotal: number | null;
  processingStatus: string | null;
  processingProgress: number | null;
  evaluateCV: (data: {
    session_id: string;
    cv_content: string;
    job_description?: string;
    custom_rules?: string;
    llm_model?: string;
  }) => void;
  sendChat: (data: {
    session_id: string;
    message: string;
    job_description?: string;
    custom_rules?: string;
    cv_evaluations?: any[];
    chat_history?: any[];
    llm_model?: string;
  }) => void;
}

const SocketContext = createContext<SocketContextType | undefined>(undefined);

export function SocketProvider({ children, sessionId }: { children: ReactNode; sessionId: string | null }) {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [connected, setConnected] = useState(false);
  const [queuePosition, setQueuePosition] = useState<number | null>(null);
  const [queueTotal, setQueueTotal] = useState<number | null>(null);
  const [processingStatus, setProcessingStatus] = useState<string | null>(null);
  const [processingProgress, setProcessingProgress] = useState<number | null>(null);

  useEffect(() => {
    // Create socket connection
    const socketInstance = io(import.meta.env.VITE_BACKEND_API_URL || '', {
      path: '/socket.io',
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5,
    });

    setSocket(socketInstance);

    // Connection events
    socketInstance.on('connect', () => {
      setConnected(true);

      // Register session if available
      if (sessionId) {
        socketInstance.emit('register_session', { session_id: sessionId });
      }
    });

    socketInstance.on('disconnect', () => {
      setConnected(false);
    });

    socketInstance.on('session_registered', (data) => {
      console.log('✅ Session registered:', data.session_id);
    });

    // Queue events
    socketInstance.on('queue_update', (data) => {
      setQueuePosition(data.position);
      setQueueTotal(data.total);
    });

    // Processing events
    socketInstance.on('processing_start', (data) => {
      setProcessingStatus(data.message);
      setProcessingProgress(0);
      setQueuePosition(null);
      setQueueTotal(null);
    });

    socketInstance.on('processing_progress', (data) => {
      setProcessingProgress(data.progress);
      setProcessingStatus(data.message);
    });

    socketInstance.on('processing_complete', () => {
      setProcessingStatus(null);
      setProcessingProgress(null);
    });

    socketInstance.on('processing_error', (data) => {
      console.error('❌ Processing error:', data.error);
      setProcessingStatus(null);
      setProcessingProgress(null);
    });

    // Cleanup on unmount
    return () => {
      socketInstance.disconnect();
    };
  }, []);

  // Register session when sessionId changes
  useEffect(() => {
    if (socket && connected && sessionId) {
      socket.emit('register_session', { session_id: sessionId });
    }
  }, [socket, connected, sessionId]);

  // Emit functions
  const evaluateCV = (data: {
    session_id: string;
    cv_content: string;
    job_description?: string;
    custom_rules?: string;
    llm_model?: string;
  }) => {
    if (socket && connected) {
      socket.emit('evaluate_cv', data);
    } else {
      console.error('Socket not connected');
    }
  };

  const sendChat = (data: {
    session_id: string;
    message: string;
    job_description?: string;
    custom_rules?: string;
    cv_evaluations?: any[];
    chat_history?: any[];
    llm_model?: string;
  }) => {
    if (socket && connected) {
      socket.emit('chat', data);
    } else {
      console.error('Socket not connected');
    }
  };

  return (
    <SocketContext.Provider
      value={{
        socket,
        connected,
        queuePosition,
        queueTotal,
        processingStatus,
        processingProgress,
        evaluateCV,
        sendChat,
      }}
    >
      {children}
    </SocketContext.Provider>
  );
}

export function useSocket() {
  const context = useContext(SocketContext);
  if (context === undefined) {
    throw new Error('useSocket must be used within a SocketProvider');
  }
  return context;
}

