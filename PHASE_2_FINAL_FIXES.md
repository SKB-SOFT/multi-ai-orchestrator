# PHASE_2_FINAL_FIXES.md — Detailed testing guide

## What Phase 2 is
User-scoped cache isolation:
- Cache key/hash must include `user_id`
- Cache DB rows must include `user_id`
- Cache uniqueness must be per `(user_id, query_hash, agent_id)`

This prevents cross-user cache pollution in a SaaS/multi-tenant setup.

---

## Complete verification checklist
- [ ] Backend starts successfully (no import errors).
- [ ] `/api/health` returns 200.
- [ ] DB tables exist after startup.
- [ ] Create two users (RAM, SHYAM).
- [ ] Send same prompt from both users using same provider(s).
- [ ] Verify cache entries are separated by `user_id`.

---

## Command-by-command test sequence

### 1) Start backend
Pick a port and run it (example uses 8001):
```bash
python -m uvicorn server.main:app --reload --host 127.0.0.1 --port 8001
```

### 2) Health check
```bash
curl http://127.0.0.1:8001/api/health
```

### 3) Register two users
```bash
curl -X POST http://127.0.0.1:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"ram@test.com","password":"test123","full_name":"RAM"}'

curl -X POST http://127.0.0.1:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"shyam@test.com","password":"test456","full_name":"Shyam"}'
```

### 4) Login and capture tokens
If you have `jq` installed:
```bash
TOKEN_RAM=$(curl -s -X POST http://127.0.0.1:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"ram@test.com","password":"test123"}' | jq -r '.access_token')

TOKEN_SHYAM=$(curl -s -X POST http://127.0.0.1:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"shyam@test.com","password":"test456"}' | jq -r '.access_token')
```

### 5) Run the same query as both users
Use ONE provider first (example: groq) to keep it simple:
```bash
curl -X POST http://127.0.0.1:8001/api/query \
  -H "Authorization: Bearer $TOKEN_RAM" \
  -H "Content-Type: application/json" \
  -d '{"query_text":"what is ai","selected_agents":["groq"]}'

curl -X POST http://127.0.0.1:8001/api/query \
  -H "Authorization: Bearer $TOKEN_SHYAM" \
  -H "Content-Type: application/json" \
  -d '{"query_text":"what is ai","selected_agents":["groq"]}'
```

### 6) Database validation (SQLite)
If your DB is `server/app.db`:
```bash
sqlite3 server/app.db "SELECT user_id, agent_id, substr(query_hash,1,10) AS hash10, created_timestamp FROM cache ORDER BY created_timestamp DESC;"
```

Expected outcome:
- You see separate rows with different `user_id`.
- Hash should differ (because Phase 2 includes `user_id` in the hash).

---

## Common issues & solutions

### ERR_CONNECTION_REFUSED
Cause: backend not running, wrong port, or crashed.
Fix: start backend and verify `/api/health`.

### 401 Not authenticated
Cause: missing/invalid Bearer token.
Fix: login again and pass `Authorization: Bearer <token>`.

### Provider not initialized
Cause: missing API key in `server/.env`.
Fix: add provider key and restart backend.

### SQLite schema mismatch after updates
Cause: old `app.db` still exists.
Fix: delete DB and restart backend.

### Port already in use
Fix: change port:
```bash
python -m uvicorn server.main:app --reload --host 127.0.0.1 --port 8010
```
Then update frontend to 8010.
