"""
Socket.IO Manager for real-time communication
"""
import socketio
from typing import Dict, Any, Optional
from src.utils.logger import Logger

logger = Logger(__name__)

class SocketManager:
    """Manages Socket.IO connections and events"""
    
    def __init__(self):
        # Create Socket.IO server with ASGI support
        self.sio = socketio.AsyncServer(
            async_mode='asgi',
            cors_allowed_origins='*',
            logger=False,
            engineio_logger=False
        )

        # Track session to socket ID mapping
        self.session_sockets: Dict[str, str] = {}

        # Setup event handlers
        self._setup_handlers()

        # Create ASGI app once
        self.asgi_app = socketio.ASGIApp(self.sio)

        logger.info("✅ SocketManager initialized")
    
    def _setup_handlers(self):
        """Setup Socket.IO event handlers"""

        @self.sio.event
        async def connect(sid, environ):
            """Handle client connection"""
            logger.info(f"🔌 Client connected: {sid}")
            await self.sio.emit('connected', {'sid': sid}, room=sid)
        
        @self.sio.event
        async def disconnect(sid):
            """Handle client disconnection"""
            logger.info(f"🔌 Client disconnected: {sid}")
            # Remove from session mapping
            session_id = None
            for sess_id, socket_id in list(self.session_sockets.items()):
                if socket_id == sid:
                    session_id = sess_id
                    break
            if session_id:
                del self.session_sockets[session_id]
        
        @self.sio.event
        async def register_session(sid, data):
            """Register session ID with socket ID"""
            session_id = data.get('session_id')
            if session_id:
                self.session_sockets[session_id] = sid
                logger.info(f"✅ Registered session {session_id} with socket {sid}")
                await self.sio.emit('session_registered', {'session_id': session_id}, room=sid)
            else:
                logger.warning(f"⚠️ No session_id in register_session data: {data}")

        @self.sio.event
        async def evaluate_cv(sid, data):
            """Handle CV evaluation request via Socket.IO"""
            logger.info(f"📥 Received evaluate_cv from {sid}: {data.get('session_id')}")
            # Import here to avoid circular dependency
            from backend.main import handle_evaluate_cv_socketio
            await handle_evaluate_cv_socketio(sid, data)

        @self.sio.event
        async def chat(sid, data):
            """Handle chat request via Socket.IO"""
            logger.info(f"📥 Received chat from {sid}: {data.get('session_id')}")
            # Import here to avoid circular dependency
            from backend.main import handle_chat_socketio
            await handle_chat_socketio(sid, data)
    
    async def emit_to_session(self, session_id: str, event: str, data: Dict[str, Any]):
        """Emit event to specific session"""
        socket_id = self.session_sockets.get(session_id)
        if socket_id:
            await self.sio.emit(event, data, room=socket_id)
            logger.debug(f"📤 Emitted {event} to session {session_id}")
        else:
            logger.warning(f"⚠️ No socket found for session {session_id}")
    
    async def emit_queue_update(self, session_id: str, position: int, total: int):
        """Emit queue position update"""
        await self.emit_to_session(session_id, 'queue_update', {
            'position': position,
            'total': total,
            'message': f'Position in queue: {position}/{total}'
        })
    
    async def emit_processing_start(self, session_id: str, request_type: str):
        """Emit processing started event"""
        await self.emit_to_session(session_id, 'processing_start', {
            'request_type': request_type,
            'message': f'Processing {request_type}...'
        })
    
    async def emit_processing_progress(self, session_id: str, progress: int, message: str):
        """Emit processing progress update"""
        await self.emit_to_session(session_id, 'processing_progress', {
            'progress': progress,
            'message': message
        })
    
    async def emit_processing_complete(self, session_id: str, request_type: str, result: Any):
        """Emit processing completed event"""
        await self.emit_to_session(session_id, 'processing_complete', {
            'request_type': request_type,
            'result': result,
            'message': f'{request_type} completed'
        })
    
    async def emit_processing_error(self, session_id: str, error: str):
        """Emit processing error event"""
        await self.emit_to_session(session_id, 'processing_error', {
            'error': error,
            'message': f'Error: {error}'
        })
    
    async def emit_chat_response_chunk(self, session_id: str, chunk: str):
        """Emit chat response chunk for streaming"""
        await self.emit_to_session(session_id, 'chat_chunk', {
            'chunk': chunk
        })
    
    def get_asgi_app(self):
        """Get ASGI app for mounting"""
        return self.asgi_app

