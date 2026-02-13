#!/bin/bash
# Update dependencies to add web search capability

echo "🔄 Updating dependencies for web search feature..."
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "✅ Found virtual environment"
    source venv/bin/activate
else
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
fi

echo ""
echo "📦 Installing/updating packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Dependencies updated successfully!"
echo ""
echo "🌐 Web search is now enabled with:"
echo "  - DuckDuckGo (default, free, no API key needed)"
echo "  - Google Custom Search (optional, requires API key)"
echo "  - Bing Search (optional, requires API key)"
echo ""
echo "📖 See README.md for configuration details"
echo ""
echo "🚀 Run the app with: streamlit run app.py"
