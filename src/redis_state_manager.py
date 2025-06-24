"""
Redis-backed state management system for AI Rails TDD workflow.

This module provides persistent storage for workflow states, approval requests,
and test results using Redis with automatic expiration and graceful fallback.
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Literal, Optional, Union
from urllib.parse import urlparse

import redis.asyncio as redis
from pydantic import BaseModel, Field, field_validator
from redis.asyncio import ConnectionPool
from redis.exceptions import ConnectionError, RedisError, ResponseError

# Configure logging
logger = logging.getLogger(__name__)


class WorkflowState(BaseModel):
    """Model representing the state of a workflow."""
    
    workflow_id: str
    status: Literal['pending', 'in_progress', 'completed', 'failed']
    feature_description: str
    current_stage: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    last_updated: datetime
    ttl_hours: int = Field(default=24, ge=1, le=720)  # 1 hour to 30 days
    
    @field_validator('created_at', 'last_updated', mode='before')
    def parse_datetime(cls, v: Union[str, datetime]) -> datetime:
        """Parse datetime from string or return as-is if already datetime."""
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v
    
    @field_validator('last_updated')
    def validate_last_updated(cls, v: datetime, info) -> datetime:
        """Ensure last_updated is not before created_at."""
        if 'created_at' in info.data and v < info.data['created_at']:
            raise ValueError('last_updated cannot be before created_at')
        return v


class ApprovalRequest(BaseModel):
    """Model representing an approval request."""
    
    approval_id: str
    workflow_id: str
    request_type: Literal['test', 'code', 'deploy']
    content: str
    requester: str
    created_at: datetime
    expires_at: datetime
    status: Literal['pending', 'approved', 'rejected', 'expired'] = 'pending'
    
    @field_validator('created_at', 'expires_at', mode='before')
    def parse_datetime(cls, v: Union[str, datetime]) -> datetime:
        """Parse datetime from string or return as-is if already datetime."""
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v
    
    @field_validator('expires_at')
    def validate_expires_at(cls, v: datetime, info) -> datetime:
        """Ensure expires_at is after created_at."""
        if 'created_at' in info.data and v <= info.data['created_at']:
            raise ValueError('expires_at must be after created_at')
        return v


class TestResults(BaseModel):
    """Model representing test execution results."""
    
    test_id: str
    workflow_id: str
    test_suite: str
    passed: int = Field(ge=0)
    failed: int = Field(ge=0)
    skipped: int = Field(ge=0)
    duration_seconds: float = Field(ge=0)
    failure_details: Optional[List[Dict[str, Any]]] = None
    coverage_percent: Optional[float] = Field(default=None, ge=0, le=100)
    executed_at: datetime
    
    @field_validator('executed_at', mode='before')
    def parse_datetime(cls, v: Union[str, datetime]) -> datetime:
        """Parse datetime from string or return as-is if already datetime."""
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v


class InMemoryStorage:
    """In-memory storage fallback when Redis is unavailable."""
    
    def __init__(self):
        self._data: Dict[str, Dict[str, Any]] = {}
        self._expiry: Dict[str, datetime] = {}
        self._lock = asyncio.Lock()
    
    async def set(self, key: str, value: str, ttl_seconds: Optional[int] = None) -> bool:
        """Store a key-value pair with optional TTL."""
        async with self._lock:
            self._data[key] = value
            if ttl_seconds:
                self._expiry[key] = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
            return True
    
    async def get(self, key: str) -> Optional[str]:
        """Retrieve a value by key."""
        async with self._lock:
            # Check if key has expired
            if key in self._expiry:
                if datetime.now(timezone.utc) > self._expiry[key]:
                    del self._data[key]
                    del self._expiry[key]
                    return None
            
            return self._data.get(key)
    
    async def delete(self, key: str) -> bool:
        """Delete a key."""
        async with self._lock:
            if key in self._data:
                del self._data[key]
                if key in self._expiry:
                    del self._expiry[key]
                return True
            return False
    
    async def ping(self) -> bool:
        """Check if storage is available."""
        return True
    
    async def info(self) -> Dict[str, Any]:
        """Get storage info."""
        async with self._lock:
            return {
                'type': 'memory',
                'keys': len(self._data),
                'expired_keys': sum(1 for k, exp in self._expiry.items() 
                                  if datetime.now(timezone.utc) > exp)
            }


class RedisStateManager:
    """
    Redis-backed state management with automatic expiration and memory fallback.
    
    Supports TLS connections for Upstash Redis and gracefully falls back to
    in-memory storage when Redis is unavailable.
    """
    
    def __init__(
        self,
        redis_url: Optional[str] = None,
        fallback_memory: Optional[bool] = None,
        pool_size: Optional[int] = None,
        socket_connect_timeout: float = 5.0,
        socket_timeout: float = 5.0
    ):
        """
        Initialize the Redis state manager.
        
        Args:
            redis_url: Redis connection URL (defaults to UPSTASH_REDIS_URL env var)
            fallback_memory: Enable in-memory fallback on connection failure (defaults to ENABLE_REDIS_FALLBACK)
            pool_size: Maximum number of connections in the pool (defaults to REDIS_MAX_POOL_SIZE)
            socket_connect_timeout: Timeout for establishing connection
            socket_timeout: Timeout for socket operations
        """
        # Load from environment if not provided
        self.redis_url = redis_url or os.getenv('UPSTASH_REDIS_URL', 'redis://localhost:6379')
        self.fallback_memory = fallback_memory if fallback_memory is not None else os.getenv('ENABLE_REDIS_FALLBACK', 'true').lower() == 'true'
        self.pool_size = pool_size or int(os.getenv('REDIS_MAX_POOL_SIZE', '50'))
        self.socket_connect_timeout = socket_connect_timeout
        self.socket_timeout = socket_timeout
        
        self._redis: Optional[redis.Redis] = None
        self._pool: Optional[ConnectionPool] = None
        self._memory_storage: Optional[InMemoryStorage] = None
        self._is_connected = False
        self._using_memory = False
    
    async def connect(self) -> None:
        """
        Initialize Redis connection with TLS support.
        
        Falls back to memory storage if connection fails and fallback is enabled.
        """
        try:
            # Parse URL to determine if TLS is needed
            parsed_url = urlparse(self.redis_url)
            use_ssl = parsed_url.scheme == 'rediss'
            
            # Create connection pool with proper SSL configuration
            pool_kwargs = {
                'max_connections': self.pool_size,
                'socket_connect_timeout': self.socket_connect_timeout,
                'socket_timeout': self.socket_timeout,
                'decode_responses': True,  # Return strings instead of bytes
            }
            
            # Source: Context7 - redis-py v5.0.1 - SSL connection examples
            if use_ssl:
                pool_kwargs.update({
                    'connection_class': redis.SSLConnection,
                    'ssl_cert_reqs': 'required',  # Upstash requires cert validation
                })
            
            # Create connection pool from URL
            self._pool = ConnectionPool.from_url(self.redis_url, **pool_kwargs)
            self._redis = redis.Redis(connection_pool=self._pool)
            
            # Test connection
            await self._redis.ping()
            self._is_connected = True
            self._using_memory = False
            logger.info("Successfully connected to Redis")
            
        except (ConnectionError, RedisError, OSError) as e:
            logger.error(f"Failed to connect to Redis: {e}")
            
            if self.fallback_memory:
                logger.info("Falling back to in-memory storage")
                self._memory_storage = InMemoryStorage()
                self._using_memory = True
                self._is_connected = True
            else:
                self._is_connected = False
                raise
    
    async def _get_storage(self) -> Union[redis.Redis, InMemoryStorage]:
        """Get the active storage backend."""
        if self._using_memory:
            return self._memory_storage
        return self._redis
    
    async def save_workflow_state(self, state: WorkflowState) -> bool:
        """
        Persist workflow state with TTL based on state.ttl_hours.
        
        Args:
            state: WorkflowState object to save
            
        Returns:
            Success boolean
        """
        if not self._is_connected:
            return False
        
        try:
            key = f"workflow:{state.workflow_id}"
            # Ensure timestamps are timezone-aware
            if state.created_at.tzinfo is None:
                state.created_at = state.created_at.replace(tzinfo=timezone.utc)
            if state.last_updated.tzinfo is None:
                state.last_updated = state.last_updated.replace(tzinfo=timezone.utc)
            
            # Serialize to JSON with ISO format timestamps
            data = state.model_dump(mode='json')
            json_data = json.dumps(data)
            
            # Calculate TTL in seconds
            ttl_seconds = state.ttl_hours * 3600
            
            storage = await self._get_storage()
            if self._using_memory:
                return await storage.set(key, json_data, ttl_seconds)
            else:
                # Source: Context7 - redis-py async examples
                result = await storage.set(key, json_data, ex=ttl_seconds)
                return bool(result)
            
        except Exception as e:
            logger.error(f"Failed to save workflow state: {e}")
            return False
    
    async def get_workflow_state(self, workflow_id: str) -> Optional[WorkflowState]:
        """
        Retrieve workflow state by ID.
        
        Args:
            workflow_id: Unique workflow identifier
            
        Returns:
            WorkflowState object or None if not found
        """
        if not self._is_connected:
            return None
        
        try:
            key = f"workflow:{workflow_id}"
            storage = await self._get_storage()
            
            data = await storage.get(key)
            if data is None:
                return None
            
            # Parse JSON and create WorkflowState object
            state_dict = json.loads(data)
            return WorkflowState(**state_dict)
            
        except Exception as e:
            logger.error(f"Failed to get workflow state: {e}")
            return None
    
    async def update_workflow_state(self, workflow_id: str, updates: Dict[str, Any]) -> bool:
        """
        Partial update of existing workflow state.
        
        Preserves non-updated fields and updates last_updated timestamp.
        
        Args:
            workflow_id: Unique workflow identifier
            updates: Dictionary of fields to update
            
        Returns:
            Success boolean
        """
        if not self._is_connected:
            return False
        
        try:
            # Get existing state
            existing_state = await self.get_workflow_state(workflow_id)
            if existing_state is None:
                logger.warning(f"Workflow {workflow_id} not found for update")
                return False
            
            # Update fields
            state_dict = existing_state.model_dump()
            state_dict.update(updates)
            state_dict['last_updated'] = datetime.now(timezone.utc)
            
            # Create updated state object
            updated_state = WorkflowState(**state_dict)
            
            # Save updated state
            return await self.save_workflow_state(updated_state)
            
        except Exception as e:
            logger.error(f"Failed to update workflow state: {e}")
            return False
    
    async def save_approval_request(self, request: ApprovalRequest) -> bool:
        """
        Store approval request with expiration.
        
        TTL is calculated based on expires_at field.
        
        Args:
            request: ApprovalRequest object to save
            
        Returns:
            Success boolean
        """
        if not self._is_connected:
            return False
        
        try:
            key = f"approval:{request.approval_id}"
            
            # Ensure timestamps are timezone-aware
            if request.created_at.tzinfo is None:
                request.created_at = request.created_at.replace(tzinfo=timezone.utc)
            if request.expires_at.tzinfo is None:
                request.expires_at = request.expires_at.replace(tzinfo=timezone.utc)
            
            # Calculate TTL from expires_at
            now = datetime.now(timezone.utc)
            ttl_seconds = int((request.expires_at - now).total_seconds())
            
            if ttl_seconds <= 0:
                logger.warning(f"Approval request {request.approval_id} already expired")
                return False
            
            # Serialize to JSON
            data = request.model_dump(mode='json')
            json_data = json.dumps(data)
            
            storage = await self._get_storage()
            if self._using_memory:
                return await storage.set(key, json_data, ttl_seconds)
            else:
                result = await storage.set(key, json_data, ex=ttl_seconds)
                return bool(result)
            
        except Exception as e:
            logger.error(f"Failed to save approval request: {e}")
            return False
    
    async def get_approval_request(self, approval_id: str) -> Optional[ApprovalRequest]:
        """
        Retrieve approval request.
        
        Args:
            approval_id: Unique approval identifier
            
        Returns:
            ApprovalRequest object or None if not found
        """
        if not self._is_connected:
            return None
        
        try:
            key = f"approval:{approval_id}"
            storage = await self._get_storage()
            
            data = await storage.get(key)
            if data is None:
                return None
            
            # Parse JSON and create ApprovalRequest object
            request_dict = json.loads(data)
            return ApprovalRequest(**request_dict)
            
        except Exception as e:
            logger.error(f"Failed to get approval request: {e}")
            return None
    
    async def save_test_results(self, results: TestResults) -> bool:
        """
        Store test execution results.
        
        Args:
            results: TestResults object to save
            
        Returns:
            Success boolean
        """
        if not self._is_connected:
            return False
        
        try:
            key = f"test_results:{results.workflow_id}:{results.test_id}"
            
            # Ensure timestamp is timezone-aware
            if results.executed_at.tzinfo is None:
                results.executed_at = results.executed_at.replace(tzinfo=timezone.utc)
            
            # Serialize to JSON
            data = results.model_dump(mode='json')
            json_data = json.dumps(data)
            
            # Default TTL of 30 days for test results
            ttl_seconds = 30 * 24 * 3600
            
            storage = await self._get_storage()
            if self._using_memory:
                return await storage.set(key, json_data, ttl_seconds)
            else:
                result = await storage.set(key, json_data, ex=ttl_seconds)
                return bool(result)
            
        except Exception as e:
            logger.error(f"Failed to save test results: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Report Redis connection health and stats.
        
        Returns:
            Dict with connection status, memory usage, etc.
        """
        health_info = {
            'connected': self._is_connected,
            'using_memory_fallback': self._using_memory,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        if not self._is_connected:
            health_info['status'] = 'disconnected'
            return health_info
        
        try:
            storage = await self._get_storage()
            
            if self._using_memory:
                info = await storage.info()
                health_info.update({
                    'status': 'healthy',
                    'backend': 'memory',
                    'keys': info['keys'],
                    'expired_keys': info['expired_keys']
                })
            else:
                # Test connection with ping
                await storage.ping()
                
                # Get Redis server info
                info = await storage.info()
                health_info.update({
                    'status': 'healthy',
                    'backend': 'redis',
                    'redis_version': info.get('redis_version', 'unknown'),
                    'connected_clients': info.get('connected_clients', 0),
                    'used_memory_human': info.get('used_memory_human', 'unknown'),
                    'uptime_in_seconds': info.get('uptime_in_seconds', 0)
                })
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            health_info['status'] = 'unhealthy'
            health_info['error'] = str(e)
        
        return health_info
    
    async def close(self) -> None:
        """Close Redis connection and clean up resources."""
        if self._redis:
            await self._redis.aclose()
        if self._pool:
            await self._pool.aclose()
        self._is_connected = False
        logger.info("Redis connection closed")