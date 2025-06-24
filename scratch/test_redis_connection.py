#!/usr/bin/env python3
"""Quick test to verify Redis connection to Upstash."""
import os
import asyncio
from dotenv import load_dotenv
import redis.asyncio as redis

# Load environment variables
load_dotenv()

async def test_connection():
    redis_url = os.getenv("UPSTASH_REDIS_URL")
    print(f"Redis URL from env: {redis_url}")
    
    if not redis_url:
        print("❌ UPSTASH_REDIS_URL not found in environment")
        return
    
    print("Attempting to connect to Upstash Redis...")
    
    try:
        # Create connection
        client = await redis.from_url(redis_url, decode_responses=True)
        
        # Test ping
        result = await client.ping()
        print(f"✅ Connected successfully! Ping result: {result}")
        
        # Test set/get
        await client.set("test_key", "Hello from AI Rails TDD!")
        value = await client.get("test_key")
        print(f"✅ Set/Get test successful: {value}")
        
        # Cleanup
        await client.delete("test_key")
        await client.aclose()
        
        print("\n🎉 Upstash Redis is working correctly!")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"   Error type: {type(e).__name__}")

if __name__ == "__main__":
    asyncio.run(test_connection())