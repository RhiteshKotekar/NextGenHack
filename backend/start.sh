#!/bin/bash
# Start script for Insight-o-pedia Flask Backend

echo "🚀 Starting Insight-o-pedia Flask Backend..."
echo ""

# Check if venv exists, create if not
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Check if models directory exists
if [ ! -d "models" ]; then
    echo "⚠️  Warning: models/ directory not found!"
    echo "   Please run training first: python train.py orders"
    exit 1
fi

# Check if models exist
if [ ! -f "models/model_orders.pkl" ]; then
    echo "⚠️  Warning: model_orders.pkl not found!"
    echo "   Training models now..."
    python train.py orders 5000
    python train.py seasonal 5000
    python train.py warehouse 5000
    python train.py transport 5000
    python train.py reviews 5000
fi

# Install requirements if needed
echo "📦 Checking dependencies..."
pip install -q -r requirements.txt

echo ""
echo "✅ All checks passed!"
echo "🌐 Starting Flask server on http://localhost:5000"
echo ""

# Start Flask app
python app.py
