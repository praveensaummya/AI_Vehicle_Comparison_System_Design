# 1. Go to your backend folder
cd your-project/backend

# 2. Create the environment (only needs to be done once)
python -m venv venv

# 3. Activate it (do this every time you start working)
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 4. Install packages (do this after creating the venv or when requirements change)
pip install -r requirements.txt

# 5. Run your FastAPI app, etc.
# For example: uvicorn main:app --reload

# 6. Deactivate when you're done
deactivate