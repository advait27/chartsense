#!/bin/bash

echo "🚀 Starting ChartSense Frontend..."
echo ""
echo "📊 The app will open in your browser at http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd "$(dirname "$0")/.."
streamlit run frontend/app.py
