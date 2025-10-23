#!/bin/bash

# Cortex Guard Demo - Quick Start Script

echo "🛡️  Cortex Guard Demo - Quick Start"
echo "===================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "✓ Python 3 found"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

echo "✓ pip3 found"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt -q

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "🚀 Choose a demo mode:"
echo ""
echo "  1) Web Interface (Recommended)"
echo "  2) Command Line Demo"
echo "  3) API Server + Tests"
echo "  4) Exit"
echo ""
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "Starting web interface..."
        echo "Open your browser to: http://localhost:5000"
        echo ""
        python3 app.py
        ;;
    2)
        echo ""
        echo "Starting CLI demo..."
        echo ""
        python3 cli_demo.py
        ;;
    3)
        echo ""
        echo "Starting API server..."
        echo "The test script will run in 3 seconds..."
        echo ""
        python3 api_server.py &
        API_PID=$!
        sleep 3
        python3 test_api.py
        echo ""
        echo "Press Enter to stop the API server..."
        read
        kill $API_PID
        ;;
    4)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

