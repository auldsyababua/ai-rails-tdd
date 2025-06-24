"""
Redis Manager for AI Rails TDD Workflow State
Handles persistent storage of workflow states, approvals, and test results
"""

import os
import json
import redis
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RedisManager:
    """Manage workflow state in Redis for persistence across sessions"""
    
    def __init__(self):
        """Initialize Redis connection if enabled"""
        self.enabled = os.environ.get("REDIS_ENABLED", "false").lower() == "true"
        self.client = None
        
        if self.enabled:
            try:
                redis_url = os.environ.get("REDIS_URL")
                if not redis_url:
                    logger.warning("REDIS_ENABLED is true but REDIS_URL not set")
                    self.enabled = False
                    return
                
                # Parse Redis URL and handle TLS
                if redis_url.startswith("rediss://"):
                    # Already has TLS in URL
                    self.client = redis.from_url(redis_url, decode_responses=True)
                elif os.environ.get("REDIS_TLS", "false").lower() == "true":
                    # Add TLS to URL
                    redis_url = redis_url.replace("redis://", "rediss://")
                    self.client = redis.from_url(redis_url, decode_responses=True)
                else:
                    self.client = redis.from_url(redis_url, decode_responses=True)
                
                # Test connection
                self.client.ping()
                logger.info("Redis connected successfully")
                
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                self.enabled = False
                self.client = None
        
        # Key prefixes
        self.key_prefix = os.environ.get("REDIS_KEY_PREFIX", "ai_rails_")
        self.workflow_prefix = os.environ.get("REDIS_WORKFLOW_PREFIX", "workflow_")
        self.approval_prefix = os.environ.get("REDIS_APPROVAL_PREFIX", "approval_")
        self.test_prefix = os.environ.get("REDIS_TEST_PREFIX", "test_")
    
    def _make_key(self, prefix: str, identifier: str) -> str:
        """Create a properly namespaced Redis key"""
        return f"{self.key_prefix}{prefix}{identifier}"
    
    # Workflow State Management
    
    def save_workflow_state(self, workflow_id: str, state: Dict[str, Any], ttl_hours: int = 24) -> bool:
        """Save workflow state with optional TTL"""
        if not self.enabled:
            return False
        
        try:
            key = self._make_key(self.workflow_prefix, workflow_id)
            state["last_updated"] = datetime.utcnow().isoformat()
            
            self.client.setex(
                key,
                timedelta(hours=ttl_hours),
                json.dumps(state)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to save workflow state: {e}")
            return False
    
    def get_workflow_state(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve workflow state"""
        if not self.enabled:
            return None
        
        try:
            key = self._make_key(self.workflow_prefix, workflow_id)
            data = self.client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Failed to get workflow state: {e}")
            return None
    
    def list_active_workflows(self) -> List[str]:
        """List all active workflow IDs"""
        if not self.enabled:
            return []
        
        try:
            pattern = self._make_key(self.workflow_prefix, "*")
            keys = self.client.keys(pattern)
            # Extract workflow IDs from keys
            prefix_len = len(self.key_prefix + self.workflow_prefix)
            return [key[prefix_len:] for key in keys]
        except Exception as e:
            logger.error(f"Failed to list workflows: {e}")
            return []
    
    # Approval Management
    
    def create_approval_request(self, approval_id: str, data: Dict[str, Any], ttl_hours: int = 1) -> bool:
        """Create an approval request with TTL"""
        if not self.enabled:
            return False
        
        try:
            key = self._make_key(self.approval_prefix, approval_id)
            data["created_at"] = datetime.utcnow().isoformat()
            data["status"] = "pending"
            
            self.client.setex(
                key,
                timedelta(hours=ttl_hours),
                json.dumps(data)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to create approval request: {e}")
            return False
    
    def get_approval_request(self, approval_id: str) -> Optional[Dict[str, Any]]:
        """Get approval request data"""
        if not self.enabled:
            return None
        
        try:
            key = self._make_key(self.approval_prefix, approval_id)
            data = self.client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Failed to get approval request: {e}")
            return None
    
    def update_approval_status(self, approval_id: str, approved: bool, notes: str = "") -> bool:
        """Update approval status"""
        if not self.enabled:
            return False
        
        try:
            key = self._make_key(self.approval_prefix, approval_id)
            data = self.client.get(key)
            if not data:
                return False
            
            approval_data = json.loads(data)
            approval_data["status"] = "approved" if approved else "rejected"
            approval_data["decided_at"] = datetime.utcnow().isoformat()
            approval_data["notes"] = notes
            
            # Keep for 24 hours after decision
            self.client.setex(
                key,
                timedelta(hours=24),
                json.dumps(approval_data)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to update approval status: {e}")
            return False
    
    # Test Results Management
    
    def save_test_results(self, test_id: str, results: Dict[str, Any], ttl_days: int = 7) -> bool:
        """Save test execution results"""
        if not self.enabled:
            return False
        
        try:
            key = self._make_key(self.test_prefix, test_id)
            results["saved_at"] = datetime.utcnow().isoformat()
            
            self.client.setex(
                key,
                timedelta(days=ttl_days),
                json.dumps(results)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to save test results: {e}")
            return False
    
    def get_test_results(self, test_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve test results"""
        if not self.enabled:
            return None
        
        try:
            key = self._make_key(self.test_prefix, test_id)
            data = self.client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Failed to get test results: {e}")
            return None
    
    # Utility Methods
    
    def clear_expired(self) -> int:
        """Clear expired keys (Redis handles this automatically with TTL)"""
        # This is a placeholder - Redis automatically removes expired keys
        # But we could use this to clean up based on custom logic
        return 0
    
    def get_stats(self) -> Dict[str, int]:
        """Get usage statistics"""
        if not self.enabled:
            return {"enabled": False}
        
        try:
            return {
                "enabled": True,
                "active_workflows": len(self.list_active_workflows()),
                "pending_approvals": len(self.client.keys(self._make_key(self.approval_prefix, "*"))),
                "stored_test_results": len(self.client.keys(self._make_key(self.test_prefix, "*"))),
                "total_keys": self.client.dbsize()
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"enabled": True, "error": str(e)}


# Singleton instance
redis_manager = RedisManager()