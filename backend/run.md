# 1. Install all dependencies
uv pip install -r requirements.txt

# 2. Initialize database
uv run python -c "from app.core.db import engine, Base; from app.models.ad import Ad; Base.metadata.create_all(bind=engine)"

# 3. Start the server
python -m uvicorn app.main:app --reload --port 8080 --host 0.0.0.0


uvicorn app.main:app --reload --host 0.0.0.0 --port 8080 --log-level debug

# Kill process using port 8080
# Windows
netstat -ano | findstr :8080
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8080 | xargs kill -9