#!/bin/bash
# Install Python dependencies
pip install -r requirements-vercel.txt

# Create necessary directories
mkdir -p hackrx_llm/static
mkdir -p hackrx_llm/templates

# Copy static files
cp -r hackrx_llm/static/* hackrx_llm/static/ 2>/dev/null || :

# Copy templates
cp -r hackrx_llm/templates/* hackrx_llm/templates/ 2>/dev/null || :

echo "Build completed successfully"
