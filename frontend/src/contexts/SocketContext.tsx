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
      console.log('🔌 Socket connected:', socketInstance.id);
      setConnected(true);

      // Register session if available
      if (sessionId) {
        console.log('📝 Registering session:', sessionId);
        socketInstance.emit('register_session', { session_id: sessionId });
      }
    });

    socketInstance.on('disconnect', () => {
      console.log('🔌 Socket disconnected');
      setConnected(false);
    });

    socketInstance.on('connected', (data) => {
      console.log('✅ Socket connection confirmed:', data);
    });

    socketInstance.on('session_registered', (data) => {
      console.log('📝 Session registered:', data);
    });

    // Queue events
    socketInstance.on('queue_update', (data) => {
      console.log('📊 Queue update:', data);
      setQueuePosition(data.position);
      setQueueTotal(data.total);
    });

    // Processing events
    socketInstance.on('processing_start', (data) => {
      console.log('🚀 Processing started:', data);
      setProcessingStatus(data.message);
      setProcessingProgress(0);
      setQueuePosition(null);
      setQueueTotal(null);
    });

    socketInstance.on('processing_progress', (data) => {
      console.log('⏳ Processing progress:', data);
      setProcessingProgress(data.progress);
      setProcessingStatus(data.message);
    });

    socketInstance.on('processing_complete', (data) => {
      console.log('✅ Processing complete:', data);
      setProcessingStatus(null);
      setProcessingProgress(null);
    });

    socketInstance.on('processing_error', (data) => {
      console.error('❌ Processing error:', data);
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
      console.log('📝 Registering session (on sessionId change):', sessionId);
      socket.emit('register_session', { session_id: sessionId });
    }
  }, [socket, connected, sessionId]);

  return (
    <SocketContext.Provider
      value={{
        socket,
        connected,
        queuePosition,
        queueTotal,
        processingStatus,
        processingProgress,
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

