@echo off
REM Update dependencies to add web search capability

echo 🔄 Updating dependencies for web search feature...
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo ✅ Found virtual environment
    call venv\Scripts\activate.bat
) else (
    echo ⚠️ Virtual environment not found. Creating one...
    python -m venv venv
    call venv\Scripts\activate.bat
)

echo.
echo 📦 Installing/updating packages...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ✅ Dependencies updated successfully!
echo.
echo 🌐 Web search is now enabled with:
echo   - DuckDuckGo (default, free, no API key needed)
echo   - Google Custom Search (optional, requires API key)
echo   - Bing Search (optional, requires API key)
echo.
echo 📖 See README.md for configuration details
echo.
echo 🚀 Run the app with: streamlit run app.py
echo.
pause
