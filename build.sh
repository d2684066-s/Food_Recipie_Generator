#!/bin/bash

# Create public directory
mkdir -p public

# Copy main HTML file
cp RecipieGenerator/Template/Home.html public/index.html

# Copy static assets
if [ -d "RecipieGenerator/assests" ]; then
  mkdir -p public/assets
  cp -r RecipieGenerator/assests/* public/ 2>/dev/null || true
fi

# Copy static folder
if [ -d "RecipieGenerator/static" ]; then
  cp -r RecipieGenerator/static/* public/ 2>/dev/null || true
fi

# Create a simple robots.txt
echo "User-agent: *
Allow: /" > public/robots.txt

echo "Build complete!"
