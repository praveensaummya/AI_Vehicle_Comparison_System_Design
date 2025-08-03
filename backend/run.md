# 1. Install all dependencies
uv pip install -r requirements.txt

# 2. Initialize database
uv run python -c "from app.core.db import engine, Base; from app.models.ad import Ad; Base.metadata.create_all(bind=engine)"

# 3. Start the server
python -m uvicorn app.main:app --reload --port 8080 --host 0.0.0.0