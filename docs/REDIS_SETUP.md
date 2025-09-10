# Redis Setup for MCP-Langchin

Use Redis to persist conversational memory across sessions. This guide covers Docker and native installs, environment configuration, Python dependencies, verification, and troubleshooting.

## Prerequisites
- Python venv active (recommended): `.venv`
- Network access to Redis (local or remote)

## Option A — Docker (recommended)
1) Pull and run Redis:
```bash
sudo docker pull redis:7-alpine
sudo docker rm -f redis 2>/dev/null || true
sudo docker run -d --name redis -p 6379:6379 redis:7-alpine
```

2) Verify container:
```bash
sudo docker exec redis redis-cli ping
# Expect: PONG
```

## Option B — Native install (Ubuntu/Debian)
1) Install and start:
```bash
sudo apt-get update -y
sudo apt-get install -y redis-server
sudo systemctl enable --now redis-server
```

2) Verify service:
```bash
redis-cli ping
# Expect: PONG
```

## Python dependencies (inside venv)
```bash
source .venv/bin/activate
pip install -U langchain-community redis
```

## Configure environment
Create or update `.env` in the project root:
```bash
REDIS_URL=redis://127.0.0.1:6379/0
# With password: redis://:your_password@127.0.0.1:6379/0
```

## How the app uses Redis
- `agent/conversation_agent.py` tries Redis-backed chat history using `REDIS_URL`.
- If Redis or `langchain-community` is unavailable, it automatically falls back to in-process memory (so the app still runs).
- To ensure Redis is used, confirm:
  - Redis is reachable and responds to `PING`
  - `REDIS_URL` is set correctly
  - `langchain-community` is installed in your venv

## Run the system
In terminal 1 (server):
```bash
source .venv/bin/activate
python -m server.data_server
```

In terminal 2 (client):
```bash
source .venv/bin/activate
python client.py
```

## Verification checklist
- Redis running:
  - Docker: `sudo docker ps | grep redis` and `sudo docker exec redis redis-cli ping`
  - Native: `systemctl status redis-server` and `redis-cli ping`
- App uses Redis (optional):
  - Set a unique user_id when creating the agent (server already passes `"ved"` in `conversation_agent("ved")`)
  - Observe persisted context across restarts when using memory mode

## Troubleshooting
- **Connection refused**:
  - Redis not running or wrong host/port → fix service, update `REDIS_URL`
  - Docker permissions → prefix with `sudo` or add user to `docker` group
- **Authentication error**:
  - If Redis requires a password, include it in `REDIS_URL` (`redis://:pass@host:port/db`)
- **Different host/containers**:
  - WSL/Docker: use the correct host IP instead of `127.0.0.1`
- **Deprecation warnings**:
  - LangChain warns about `LLMChain` deprecation; app remains functional
- **Fallback happening (no Redis used)**:
  - Ensure `pip install -U langchain-community redis` in the same venv
  - Confirm `REDIS_URL` resolves and `PING` returns `PONG`

## Security notes
- Don’t expose Redis publicly without auth/TLS
- Prefer Docker with restricted host networking in production
- Rotate credentials if using a password
