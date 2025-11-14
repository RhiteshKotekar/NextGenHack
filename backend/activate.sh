#!/bin/bash
# Activate virtual environment for Insight-o-pedia backend

if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Creating it now..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
    echo ""
    echo "Installing dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
    echo "✅ Virtual environment activated"
fi

echo ""
echo "You can now run:"
echo "  python app.py          # Start Flask server"
echo "  python train.py        # Train models"
echo "  python test_api.py     # Test API"
echo "  deactivate            # Exit virtual environment"
