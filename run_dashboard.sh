#!/bin/bash
# Katsu DCF Engine - Dashboard Launcher

echo "🚀 Starting Katsu DCF Dashboard..."
echo ""

# Navigate to dashboard directory
cd "$(dirname "$0")/src/dashboard"

# Run Streamlit
streamlit run app.py --server.port 8501 --server.address localhost
