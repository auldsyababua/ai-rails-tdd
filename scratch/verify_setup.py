#!/usr/bin/env python3
"""
Comprehensive verification script for Upstash Redis and Vector setup.
Run this after completing the setup to ensure everything is working.
"""
import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"


async def check_redis():
    """Verify Redis connection and functionality."""
    print(f"\n{BOLD}1. Checking Redis Connection...{RESET}")
    
    from src.redis_state_manager import RedisStateManager, WorkflowState
    
    try:
        # Initialize manager
        manager = RedisStateManager()
        await manager.connect()
        
        # Test connection (ping is internal method)
        storage = await manager._get_storage()
        ping_result = await storage.ping() if hasattr(storage, 'ping') else True
        print(f"   Connection test: {GREEN}✓ Connected{RESET}" if ping_result else f"{RED}✗ Failed{RESET}")
        
        # Test workflow state
        test_state = WorkflowState(
            session_id="verify-test-001",
            current_step="verification",
            agent_outputs={"test": "Verification successful"},
            metadata={"timestamp": datetime.now().isoformat()}
        )
        
        # Save and retrieve
        saved = await manager.save_workflow_state(test_state)
        print(f"   Save state: {GREEN}✓ Success{RESET}" if saved else f"{RED}✗ Failed{RESET}")
        
        retrieved = await manager.get_workflow_state("verify-test-001")
        print(f"   Retrieve state: {GREEN}✓ Success{RESET}" if retrieved else f"{RED}✗ Failed{RESET}")
        
        # Health check
        health = await manager.health_check()
        status = health.get('status', 'unknown')
        backend = health.get('backend', 'unknown')
        print(f"   Health check: {GREEN}✓ {status}{RESET} (backend: {backend})")
        
        # Cleanup
        await manager.close()
        
        return True
        
    except Exception as e:
        print(f"   {RED}✗ Error: {e}{RESET}")
        return False


async def check_vector():
    """Verify Vector connection and functionality."""
    print(f"\n{BOLD}2. Checking Vector Connection...{RESET}")
    
    vector_url = os.getenv("UPSTASH_VECTOR_URL")
    vector_token = os.getenv("UPSTASH_VECTOR_TOKEN")
    
    if not vector_url or not vector_token:
        print(f"   {YELLOW}⚠ Vector credentials not configured{RESET}")
        print(f"   {YELLOW}  Please create a Vector index and add credentials to .env{RESET}")
        return False
    
    from src.vector_manager import VectorManager, EmbeddingManager
    
    try:
        # Initialize managers
        vector_mgr = VectorManager()
        embedding_mgr = EmbeddingManager()
        
        if vector_mgr.index:
            print(f"   Connection: {GREEN}✓ Connected to Upstash Vector{RESET}")
        else:
            print(f"   Connection: {YELLOW}⚠ Using memory fallback{RESET}")
        
        # Test vector operations
        test_text = "AI Rails TDD verification test"
        test_embedding = await embedding_mgr.create_embedding(test_text)
        
        # Upsert
        success = await vector_mgr.upsert(
            id="verify-vector-001",
            vector=test_embedding,
            metadata={"type": "test", "timestamp": datetime.now().isoformat()}
        )
        print(f"   Upsert test: {GREEN}✓ Success{RESET}" if success else f"{RED}✗ Failed{RESET}")
        
        # Query
        results = await vector_mgr.query(test_embedding, top_k=1)
        print(f"   Query test: {GREEN}✓ Found {len(results)} results{RESET}" if results else f"{RED}✗ No results{RESET}")
        
        # Cleanup
        await vector_mgr.delete(["verify-vector-001"])
        
        return True
        
    except Exception as e:
        print(f"   {RED}✗ Error: {e}{RESET}")
        return False


async def check_environment():
    """Verify all required environment variables."""
    print(f"\n{BOLD}3. Checking Environment Variables...{RESET}")
    
    required_vars = {
        "UPSTASH_REDIS_URL": "Redis connection string",
        "REDIS_MAX_POOL_SIZE": "Connection pool size",
        "WORKFLOW_STATE_TTL": "Workflow state TTL",
        "ENABLE_REDIS_FALLBACK": "Redis fallback flag"
    }
    
    optional_vars = {
        "UPSTASH_VECTOR_URL": "Vector endpoint URL",
        "UPSTASH_VECTOR_TOKEN": "Vector authentication token",
        "ENABLE_VECTOR_SEARCH": "Vector search flag"
    }
    
    all_good = True
    
    print("   Required:")
    for var, desc in required_vars.items():
        value = os.getenv(var)
        if value:
            display_value = value[:20] + "..." if len(value) > 20 else value
            print(f"     {var}: {GREEN}✓ {display_value}{RESET}")
        else:
            print(f"     {var}: {RED}✗ Missing{RESET} ({desc})")
            all_good = False
    
    print("\n   Optional:")
    for var, desc in optional_vars.items():
        value = os.getenv(var)
        if value:
            display_value = value[:20] + "..." if len(value) > 20 else value
            print(f"     {var}: {GREEN}✓ {display_value}{RESET}")
        else:
            print(f"     {var}: {YELLOW}⚠ Not configured{RESET} ({desc})")
    
    return all_good


async def main():
    """Run all verification checks."""
    print(f"{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}AI Rails TDD - Upstash Setup Verification{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")
    
    # Check environment
    env_ok = await check_environment()
    
    # Check Redis
    redis_ok = await check_redis()
    
    # Check Vector
    vector_ok = await check_vector()
    
    # Summary
    print(f"\n{BOLD}Summary:{RESET}")
    print(f"  Environment: {GREEN}✓ Configured{RESET}" if env_ok else f"{RED}✗ Missing variables{RESET}")
    print(f"  Redis: {GREEN}✓ Working{RESET}" if redis_ok else f"{RED}✗ Not working{RESET}")
    print(f"  Vector: {GREEN}✓ Working{RESET}" if vector_ok else f"{YELLOW}⚠ Not configured{RESET}")
    
    if redis_ok and env_ok:
        print(f"\n{GREEN}{BOLD}✅ Setup verified! Redis is working correctly.{RESET}")
        if not vector_ok:
            print(f"{YELLOW}   Note: Vector is optional but recommended for semantic search.{RESET}")
    else:
        print(f"\n{RED}{BOLD}❌ Setup incomplete. Please check the errors above.{RESET}")
    
    print(f"\n{BOLD}Next Steps:{RESET}")
    if not vector_ok:
        print("1. Create a Vector index at https://console.upstash.com")
        print("   - Choose 'sentence-transformers/all-MiniLM-L6-v2' as embedding model")
        print("   - Add UPSTASH_VECTOR_URL and UPSTASH_VECTOR_TOKEN to .env")
    print("2. Run your AI Rails TDD workflows!")


if __name__ == "__main__":
    asyncio.run(main())