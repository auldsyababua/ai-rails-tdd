"""
Redis Manager for AI Rails TDD
Handles caching and state management for the TDD workflow
"""

import json
import logging
import time
from typing import Dict, Any, Optional, List, Union
from contextlib import contextmanager
from datetime import datetime

import redis
from redis.connection import ConnectionPool
from redis.exceptions import ConnectionError, TimeoutError, RedisError


# Configure logging
logger = logging.getLogger(__name__)


class RedisConnectionError(Exception):
    """Raised when Redis connection fails"""
    pass


class RedisDataError(Exception):
    """Raised when data operations fail"""
    pass


class RedisManager:
    """Manages Redis connections and operations for AI Rails TDD"""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        decode_responses: bool = True,
        max_connections: int = 50,
        socket_timeout: Optional[float] = None,
        **kwargs
    ):
        """
        Initialize Redis manager with connection parameters
        
        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            password: Redis password (if required)
            decode_responses: Whether to decode responses to strings
            max_connections: Maximum number of connections in pool
            socket_timeout: Socket timeout in seconds
            **kwargs: Additional Redis client arguments
        """
        self.host = host
        self.port = port
        self.db = db
        self._pool = None
        self._client = None
        
        try:
            # Create connection pool
            self._pool = ConnectionPool(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=decode_responses,
                max_connections=max_connections,
                socket_timeout=socket_timeout,
                **kwargs
            )
            
            # Create Redis client
            self._client = redis.Redis(connection_pool=self._pool)
            
            # Test connection
            self._client.ping()
            logger.info(f"Connected to Redis at {host}:{port}")
            
        except (ConnectionError, TimeoutError) as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise RedisConnectionError(f"Cannot connect to Redis at {host}:{port}: {e}")
    
    def is_connected(self) -> bool:
        """Check if Redis connection is active"""
        try:
            return self._client.ping()
        except (ConnectionError, TimeoutError, AttributeError):
            return False
    
    def reconnect(self) -> bool:
        """Attempt to reconnect to Redis"""
        try:
            self._client.ping()
            return True
        except (ConnectionError, TimeoutError):
            logger.warning("Attempting to reconnect to Redis...")
            try:
                # Reset connection
                if self._pool:
                    self._pool.disconnect()
                self._client = redis.Redis(connection_pool=self._pool)
                self._client.ping()
                logger.info("Reconnected to Redis successfully")
                return True
            except Exception as e:
                logger.error(f"Reconnection failed: {e}")
                return False
    
    def close(self):
        """Close Redis connection"""
        if self._pool:
            self._pool.disconnect()
            logger.info("Closed Redis connection")
    
    def store_planning_doc(self, feature_id: str, document: Dict[str, Any]) -> str:
        """
        Store a planning document
        
        Args:
            feature_id: Unique identifier for the feature
            document: Planning document as dictionary
            
        Returns:
            Redis key where document was stored
        """
        key = f"planning:{feature_id}"
        try:
            serialized = json.dumps(document)
            self._client.set(key, serialized)
            logger.debug(f"Stored planning doc at {key}")
            return key
        except (TypeError, ValueError) as e:
            raise RedisDataError(f"Cannot serialize planning document: {e}")
        except RedisError as e:
            raise RedisDataError(f"Failed to store planning document: {e}")
    
    def get_planning_doc(self, feature_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a planning document
        
        Args:
            feature_id: Unique identifier for the feature
            
        Returns:
            Planning document or None if not found
        """
        key = f"planning:{feature_id}"
        try:
            data = self._client.get(key)
            if data:
                return json.loads(data)
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {key}: {e}")
            return None
        except RedisError as e:
            logger.error(f"Failed to retrieve planning document: {e}")
            return None
    
    def store_test_output(self, feature_id: str, test_code: str) -> str:
        """
        Store test output code
        
        Args:
            feature_id: Unique identifier for the feature
            test_code: Generated test code
            
        Returns:
            Redis key where test was stored
        """
        key = f"tests:{feature_id}"
        try:
            self._client.set(key, test_code)
            logger.debug(f"Stored test output at {key}")
            return key
        except RedisError as e:
            raise RedisDataError(f"Failed to store test output: {e}")
    
    def get_test_output(self, feature_id: str) -> Optional[str]:
        """
        Retrieve test output code
        
        Args:
            feature_id: Unique identifier for the feature
            
        Returns:
            Test code or None if not found
        """
        key = f"tests:{feature_id}"
        try:
            return self._client.get(key)
        except RedisError as e:
            logger.error(f"Failed to retrieve test output: {e}")
            return None
    
    def store_with_ttl(self, key: str, data: Union[str, Dict], ttl: int) -> None:
        """
        Store data with expiration time
        
        Args:
            key: Redis key
            data: Data to store (string or dict)
            ttl: Time to live in seconds
        """
        try:
            if isinstance(data, dict):
                data = json.dumps(data)
            self._client.setex(key, ttl, data)
            logger.debug(f"Stored {key} with TTL={ttl}s")
        except (TypeError, ValueError) as e:
            raise RedisDataError(f"Cannot serialize data: {e}")
        except RedisError as e:
            raise RedisDataError(f"Failed to store with TTL: {e}")
    
    def delete(self, key: str) -> int:
        """
        Delete a key from Redis
        
        Args:
            key: Redis key to delete
            
        Returns:
            Number of keys deleted
        """
        try:
            return self._client.delete(key)
        except RedisError as e:
            logger.error(f"Failed to delete {key}: {e}")
            return 0
    
    def clear_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern
        
        Args:
            pattern: Redis key pattern (e.g., "test:*")
            
        Returns:
            Number of keys deleted
        """
        try:
            keys = self._client.keys(pattern)
            if keys:
                return self._client.delete(*keys)
            return 0
        except RedisError as e:
            logger.error(f"Failed to clear pattern {pattern}: {e}")
            return 0
    
    def clear_all(self) -> None:
        """Clear all data (use with caution)"""
        try:
            self._client.flushdb()
            logger.warning("Cleared all Redis data")
        except RedisError as e:
            logger.error(f"Failed to clear all data: {e}")
    
    @contextmanager
    def pipeline(self):
        """
        Create a pipeline for batch operations
        
        Yields:
            Redis pipeline object
        """
        pipe = self._client.pipeline()
        try:
            yield pipe
        finally:
            pipe.reset()
    
    def mget(self, keys: List[str]) -> List[Optional[str]]:
        """
        Get multiple values at once
        
        Args:
            keys: List of Redis keys
            
        Returns:
            List of values (None for missing keys)
        """
        try:
            return self._client.mget(keys)
        except RedisError as e:
            logger.error(f"Failed to mget: {e}")
            return [None] * len(keys)
    
    def get_connection(self):
        """Get a connection from the pool"""
        return self._pool.get_connection('GET')
    
    # Workflow-specific methods
    
    def store_workflow_state(self, workflow_id: str, stage: str, data: Any) -> None:
        """
        Store workflow state for a specific stage
        
        Args:
            workflow_id: Unique workflow identifier
            stage: Workflow stage (planning, tests, implementation)
            data: Stage data
        """
        key = f"workflow:{workflow_id}:{stage}"
        try:
            if isinstance(data, dict):
                data = json.dumps(data)
            self._client.set(key, data)
            logger.debug(f"Stored workflow state: {key}")
        except Exception as e:
            raise RedisDataError(f"Failed to store workflow state: {e}")
    
    def get_complete_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get all stages of a workflow
        
        Args:
            workflow_id: Unique workflow identifier
            
        Returns:
            Dictionary with all workflow stages
        """
        stages = ["planning", "tests", "implementation"]
        workflow = {}
        
        for stage in stages:
            key = f"workflow:{workflow_id}:{stage}"
            data = self._client.get(key)
            if data:
                try:
                    # Try to parse as JSON first
                    workflow[stage] = json.loads(data)
                except json.JSONDecodeError:
                    # If not JSON, store as string
                    workflow[stage] = data
        
        return workflow
    
    def add_approval_record(self, feature_id: str, record: Dict[str, Any]) -> None:
        """
        Add an approval record to history
        
        Args:
            feature_id: Feature identifier
            record: Approval record with stage, approved, feedback, timestamp
        """
        key = f"approvals:{feature_id}"
        try:
            serialized = json.dumps(record)
            self._client.rpush(key, serialized)
            logger.debug(f"Added approval record for {feature_id}")
        except Exception as e:
            raise RedisDataError(f"Failed to add approval record: {e}")
    
    def get_approval_history(self, feature_id: str) -> List[Dict[str, Any]]:
        """
        Get approval history for a feature
        
        Args:
            feature_id: Feature identifier
            
        Returns:
            List of approval records
        """
        key = f"approvals:{feature_id}"
        try:
            records = self._client.lrange(key, 0, -1)
            return [json.loads(record) for record in records]
        except Exception as e:
            logger.error(f"Failed to get approval history: {e}")
            return []