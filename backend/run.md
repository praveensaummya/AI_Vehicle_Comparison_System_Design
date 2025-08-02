# 1. Install all dependencies
uv pip install -r requirements.txt

# 2. Install Playwright browser binaries
playwright install

# 3. Verify installation
uv run python verify_installation.py

# 4. Initialize database
uv run python -c "from app.core.db import engine, Base; from app.models.ad import Ad; Base.metadata.create_all(bind=engine)"

# 5. Start the server
uv run uvicorn app.main:app --reload
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000