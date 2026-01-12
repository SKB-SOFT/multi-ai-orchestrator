# MAKE_IT_WORKING_NOW.md — Quick 5-step guide

## Goal
Fix `ERR_CONNECTION_REFUSED` by ensuring the backend is running on the same host/port your frontend calls.

---

## Step 1: Delete old database (CRITICAL after schema changes)
If you're using SQLite and changed schema (like adding `user_id` to `cache`), delete the old DB so tables re-create cleanly.

**Windows (PowerShell):**
```powershell
Remove-Item .\server\app.db -Force -ErrorAction SilentlyContinue
```

**Mac/Linux:**
```bash
rm -f ./server/app.db
```

---

## Step 2: Check API keys
Open `server/.env` and ensure at least one provider key exists, e.g.

```env
GROQ_API_KEY=...
GEMINI_API_KEY=...
```

Tip: If no keys are set, providers will show as “not initialized”.

---

## Step 3: Start backend
Choose ONE port and stick to it.

### Option A (recommended): Start on 8001 (matches frontend default)
**Windows (from repo root):**
```powershell
.\server\run_dev.ps1 -Reload
```

This runs `python -m uvicorn server.main:app --host 127.0.0.1 --port 8001`.

### Option B: Start on 8000
```bash
python -m uvicorn server.main:app --reload --host 127.0.0.1 --port 8000
```
Then update the frontend base URL to `http://127.0.0.1:8000`.

---

## Step 4: Test health endpoint
If backend is on 8001:
```bash
curl http://127.0.0.1:8001/api/health
```

If backend is on 8000:
```bash
curl http://127.0.0.1:8000/api/health
```

Expected: JSON like `{"status":"healthy", ...}`

---

## Step 5: Done
- Backend responds to `/api/health`
- Frontend calls the same host+port
- No more `ERR_CONNECTION_REFUSED`
