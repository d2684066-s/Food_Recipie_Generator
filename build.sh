#!/bin/bash

set -e  # Exit on any error

echo "🔨 Building Food Recipe Generator frontend..."

# Create public directory
mkdir -p public

# Process HTML file - convert Django template tags to direct paths
python3 process_html.py RecipieGenerator/Template/Home.html public/index.html

# Copy static assets
if [ -d "RecipieGenerator/assests" ]; then
  echo "📁 Copying assets..."
  cp -r RecipieGenerator/assests/* public/ 2>/dev/null || true
fi

# Copy static folder
if [ -d "RecipieGenerator/static" ]; then
  echo "📁 Copying static files..."
  cp -r RecipieGenerator/static/* public/ 2>/dev/null || true
fi

# Create robots.txt
echo "User-agent: *
Allow: /" > public/robots.txt

echo "✅ Build complete! Files ready in public/"
