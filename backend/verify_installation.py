#!/usr/bin/env python3
"""
Installation Verification Script for AI Vehicle Comparison System
This script verifies that all required dependencies are properly installed.
"""

import sys
import importlib
from typing import List, Tuple

def test_import(module_name: str, from_module: str = None) -> Tuple[bool, str]:
    """Test if a module can be imported successfully."""
    try:
        if from_module:
            module = importlib.import_module(from_module)
            getattr(module, module_name)
            return True, f"✅ {from_module}.{module_name}"
        else:
            importlib.import_module(module_name)
            return True, f"✅ {module_name}"
    except ImportError as e:
        return False, f"❌ {module_name}: {str(e)}"
    except AttributeError as e:
        return False, f"❌ {module_name}: {str(e)}"

def main():
    """Main verification function."""
    print("🔍 AI Vehicle Comparison System - Dependency Verification")
    print("=" * 60)
    
    # Core Framework Dependencies
    print("\n📦 Core Framework:")
    tests = [
        ("fastapi", None),
        ("FastAPI", "fastapi"),
        ("HTTPException", "fastapi"),
        ("uvicorn", None),
        ("pydantic", None),
        ("BaseModel", "pydantic"),
    ]
    
    # AI Agent Framework
    print("\n🤖 AI Agent Framework:")
    tests.extend([
        ("crewai", None),
        ("Crew", "crewai"),
        ("Agent", "crewai"),
        ("Task", "crewai"),
        ("Process", "crewai"),
        ("BaseTool", "crewai.tools"),
        ("litellm", None),
    ])
    
    # LLM Providers
    print("\n🧠 LLM Providers:")
    tests.extend([
        ("openai", None),
        ("langchain_openai", None),
        ("ChatOpenAI", "langchain_openai"),
        ("langchain_google_genai", None),
        ("ChatGoogleGenerativeAI", "langchain_google_genai"),
        ("google.generativeai", None),
        ("langchain_core", None),
        ("langchain_community", None),
    ])
    
    # Web Scraping & Automation
    print("\n🌐 Web Scraping & Automation:")
    tests.extend([
        ("playwright", None),
        ("sync_playwright", "playwright.sync_api"),
        ("requests", None),
        ("bs4", None),
    ])
    
    # Database
    print("\n🗄️ Database:")
    tests.extend([
        ("sqlalchemy", None),
        ("create_engine", "sqlalchemy"),
        ("Column", "sqlalchemy"),
        ("sessionmaker", "sqlalchemy.orm"),
        ("declarative_base", "sqlalchemy.orm"),
        ("alembic", None),
    ])
    
    # Configuration & Environment
    print("\n⚙️ Configuration & Environment:")
    tests.extend([
        ("dotenv", None),
        ("load_dotenv", "dotenv"),
    ])
    
    # Logging & Monitoring
    print("\n📊 Logging & Monitoring:")
    tests.extend([
        ("structlog", None),
        ("coloredlogs", None),
    ])
    
    # Utilities
    print("\n🛠️ Utilities:")
    tests.extend([
        ("click", None),
        ("multipart", None),
        ("typing_extensions", None),
        ("markdown", None),
    ])
    
    # Built-in Modules
    print("\n🐍 Built-in Python Modules:")
    tests.extend([
        ("json", None),
        ("re", None),
        ("time", None),
        ("os", None),
        ("asyncio", None),
        ("subprocess", None),
    ])
    
    # Run all tests
    passed = 0
    failed = 0
    failed_imports = []
    
    for module_name, from_module in tests:
        success, message = test_import(module_name, from_module)
        print(f"  {message}")
        if success:
            passed += 1
        else:
            failed += 1
            failed_imports.append(message)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY:")
    print(f"  ✅ Passed: {passed}")
    print(f"  ❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 SUCCESS: All dependencies are correctly installed!")
        print("\n📝 Next steps:")
        print("  1. Run: playwright install")
        print("  2. Set up your .env file with API keys")
        print("  3. Initialize the database: python -c \"from app.core.db import engine, Base; from app.models.ad import Ad; Base.metadata.create_all(bind=engine)\"")
        print("  4. Start the server: uv run uvicorn app.main:app --reload")
        return True
    else:
        print(f"\n❌ FAILED: {failed} dependencies are missing!")
        print("\nFailed imports:")
        for failure in failed_imports:
            print(f"  {failure}")
        print("\n💡 To fix missing dependencies:")
        print("  uv pip install -r requirements.txt")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
