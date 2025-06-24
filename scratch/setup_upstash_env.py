#!/usr/bin/env python3
"""
Interactive setup script for Upstash Redis and Vector configuration.
Run this to create your .env file with the correct credentials.
"""
import os
import sys
from pathlib import Path


def main():
    """Interactive setup for Upstash credentials."""
    print("🚀 AI Rails TDD - Upstash Setup")
    print("=" * 50)
    print()
    
    # Check if .env already exists
    env_path = Path(".env")
    if env_path.exists():
        overwrite = input("⚠️  .env file already exists. Overwrite? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Setup cancelled.")
            return
    
    print("📋 Let's set up your Upstash credentials.")
    print("   You can find these in your Upstash console: https://console.upstash.com")
    print()
    
    # Redis Configuration
    print("1️⃣  REDIS CONFIGURATION")
    print("   From your Redis database page, copy:")
    print()
    
    redis_endpoint = input("   Redis Endpoint (e.g., knowing-dolphin-52030.upstash.io): ").strip()
    redis_password = input("   Redis Password: ").strip()
    
    # Build Redis URL
    redis_url = f"rediss://:{redis_password}@{redis_endpoint}:6379"
    
    # Vector Configuration
    print()
    print("2️⃣  VECTOR CONFIGURATION")
    print("   From your Vector index page, copy:")
    print()
    
    vector_url = input("   Vector URL (e.g., https://example-vector.upstash.io): ").strip()
    vector_token = input("   Vector Token: ").strip()
    
    # Create .env content
    env_content = f"""# Upstash Redis Configuration
UPSTASH_REDIS_URL={redis_url}
REDIS_MAX_POOL_SIZE=50
REDIS_CONNECTION_TIMEOUT=5
REDIS_RETRY_ATTEMPTS=3

# Upstash Vector Configuration
UPSTASH_VECTOR_URL={vector_url}
UPSTASH_VECTOR_TOKEN={vector_token}

# State Management Settings
WORKFLOW_STATE_TTL=86400  # 24 hours
APPROVAL_REQUEST_TTL=3600  # 1 hour
TEST_RESULTS_TTL=604800    # 7 days

# Feature Flags
ENABLE_REDIS_FALLBACK=true
ENABLE_VECTOR_SEARCH=true

# Optional: OpenAI for embeddings (add your key if using)
# OPENAI_API_KEY=your_openai_api_key_here
"""
    
    # Write .env file
    with open(".env", "w") as f:
        f.write(env_content)
    
    print()
    print("✅ Configuration saved to .env")
    print()
    
    # Test connection
    test = input("Would you like to test the connections? (Y/n): ").strip().lower()
    if test != 'n':
        print()
        print("🧪 Testing connections...")
        
        # Test Redis
        print("   Testing Redis...", end=" ")
        sys.stdout.flush()
        try:
            import asyncio
            from src.redis_state_manager import RedisStateManager
            
            async def test_redis():
                manager = RedisStateManager()
                return await manager.ping()
            
            connected = asyncio.run(test_redis())
            print("✅ Connected" if connected else "❌ Failed")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Test Vector
        print("   Testing Vector...", end=" ")
        sys.stdout.flush()
        try:
            from src.vector_manager import VectorManager
            
            async def test_vector():
                manager = VectorManager()
                return manager.index is not None
            
            connected = asyncio.run(test_vector())
            print("✅ Connected" if connected else "❌ Failed (check credentials)")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print()
    print("🎉 Setup complete!")
    print()
    print("Next steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run tests: python scratch/test_redis_state_manager.py")
    print("3. Run vector tests: python scratch/test_vector_manager.py")


if __name__ == "__main__":
    main()