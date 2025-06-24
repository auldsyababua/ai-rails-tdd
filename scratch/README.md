# Scratch Directory

This directory contains temporary scripts and test files for the Redis State Management and Vector Search implementation.

## Files

### Setup
- `setup_upstash_env.py` - Interactive script to configure Upstash credentials

### Redis State Management
- `test_redis_state_manager.py` - Basic test script that verifies the Redis state manager works with memory fallback
- `example_usage.py` - Production-style example showing how to use the Redis state manager with Upstash Redis

### Vector Search
- `test_vector_manager.py` - Test script for Upstash Vector integration with semantic search examples

## Quick Start

1. **Set up Upstash credentials:**
   ```bash
   python scratch/setup_upstash_env.py
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Test Redis functionality:**
   ```bash
   python scratch/test_redis_state_manager.py
   ```

4. **Test Vector search:**
   ```bash
   python scratch/test_vector_manager.py
   ```

## Notes

- All scripts support memory fallback if Upstash services are not configured
- The setup script creates a `.env` file with your credentials
- Never commit the `.env` file to version control