"""
Request Queue Service for handling API requests sequentially
Prevents backend crashes from concurrent heavy LLM requests
"""

import asyncio
from typing import Callable, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import uuid


class RequestStatus(Enum):
    """Request status enum"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class QueuedRequest:
    """Queued request data structure"""
    request_id: str
    session_id: str
    request_type: str  # 'evaluate_cv' or 'chat'
    handler: Callable
    args: tuple
    kwargs: dict
    status: RequestStatus = RequestStatus.PENDING
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class RequestQueue:
    """
    Async request queue to handle LLM requests sequentially
    Prevents backend overload and crashes
    """
    
    def __init__(self, max_concurrent: int = 1, max_queue_size: int = 100):
        """
        Initialize request queue
        
        Args:
            max_concurrent: Maximum number of concurrent requests (default: 1 for sequential)
            max_queue_size: Maximum queue size before rejecting new requests
        """
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        self.max_concurrent = max_concurrent
        self.active_requests: dict[str, QueuedRequest] = {}
        self.completed_requests: dict[str, QueuedRequest] = {}
        self.workers: list[asyncio.Task] = []
        self.is_running = False
        self.lock = asyncio.Lock()
    
    async def start(self):
        """Start queue workers"""
        if self.is_running:
            return
        
        self.is_running = True
        # Create worker tasks
        for i in range(self.max_concurrent):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self.workers.append(worker)
    
    async def stop(self):
        """Stop queue workers"""
        self.is_running = False
        
        # Cancel all workers
        for worker in self.workers:
            worker.cancel()
        
        # Wait for workers to finish
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()
    
    async def _worker(self, worker_name: str):
        """Worker coroutine to process requests from queue"""
        while self.is_running:
            try:
                # Get request from queue with timeout
                try:
                    request = await asyncio.wait_for(
                        self.queue.get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Process request
                await self._process_request(request, worker_name)
                
                # Mark task as done
                self.queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Worker {worker_name} error: {str(e)}")
    
    async def _process_request(self, request: QueuedRequest, worker_name: str):
        """Process a single request"""
        try:
            # Update status
            async with self.lock:
                request.status = RequestStatus.PROCESSING
                request.started_at = datetime.now()
                self.active_requests[request.request_id] = request
            
            # Execute handler
            if asyncio.iscoroutinefunction(request.handler):
                result = await request.handler(*request.args, **request.kwargs)
            else:
                result = request.handler(*request.args, **request.kwargs)
            
            # Update with result
            async with self.lock:
                request.status = RequestStatus.COMPLETED
                request.completed_at = datetime.now()
                request.result = result
                
                # Move to completed
                if request.request_id in self.active_requests:
                    del self.active_requests[request.request_id]
                self.completed_requests[request.request_id] = request
                
        except Exception as e:
            # Update with error
            async with self.lock:
                request.status = RequestStatus.FAILED
                request.completed_at = datetime.now()
                request.error = str(e)
                
                # Move to completed
                if request.request_id in self.active_requests:
                    del self.active_requests[request.request_id]
                self.completed_requests[request.request_id] = request
    
    async def enqueue(
        self,
        session_id: str,
        request_type: str,
        handler: Callable,
        *args,
        **kwargs
    ) -> str:
        """
        Add request to queue

        Returns:
            request_id: Unique ID for tracking the request

        Raises:
            asyncio.QueueFull: If queue is full
        """
        request_id = str(uuid.uuid4())

        request = QueuedRequest(
            request_id=request_id,
            session_id=session_id,
            request_type=request_type,
            handler=handler,
            args=args,
            kwargs=kwargs
        )

        # Add to active requests immediately so wait_for_request can find it
        async with self.lock:
            self.active_requests[request_id] = request

        # Add to queue (will raise QueueFull if full)
        await self.queue.put(request)

        return request_id
    
    async def get_request_status(self, request_id: str) -> Optional[QueuedRequest]:
        """Get request status by ID"""
        async with self.lock:
            # Check active requests
            if request_id in self.active_requests:
                return self.active_requests[request_id]
            
            # Check completed requests
            if request_id in self.completed_requests:
                return self.completed_requests[request_id]
        
        return None
    
    async def wait_for_request(
        self,
        request_id: str,
        timeout: Optional[float] = None
    ) -> QueuedRequest:
        """
        Wait for request to complete
        
        Args:
            request_id: Request ID to wait for
            timeout: Maximum time to wait in seconds (None = wait forever)
        
        Returns:
            Completed request
        
        Raises:
            asyncio.TimeoutError: If timeout exceeded
            ValueError: If request not found
        """
        start_time = datetime.now()
        
        while True:
            request = await self.get_request_status(request_id)
            
            if request is None:
                raise ValueError(f"Request {request_id} not found")
            
            if request.status in [RequestStatus.COMPLETED, RequestStatus.FAILED, RequestStatus.CANCELLED]:
                return request
            
            # Check timeout
            if timeout is not None:
                elapsed = (datetime.now() - start_time).total_seconds()
                if elapsed >= timeout:
                    raise asyncio.TimeoutError(f"Request {request_id} timed out after {timeout}s")
            
            # Wait a bit before checking again
            await asyncio.sleep(0.1)
    
    def get_queue_size(self) -> int:
        """Get current queue size"""
        return self.queue.qsize()
    
    def get_active_count(self) -> int:
        """Get number of active requests"""
        return len(self.active_requests)
    
    async def cleanup_old_requests(self, max_age_hours: int = 24):
        """Remove old completed requests from memory"""
        async with self.lock:
            cutoff = datetime.now() - timedelta(hours=max_age_hours)
            to_remove = []
            
            for request_id, request in self.completed_requests.items():
                if request.completed_at and request.completed_at < cutoff:
                    to_remove.append(request_id)
            
            for request_id in to_remove:
                del self.completed_requests[request_id]
            
            return len(to_remove)

