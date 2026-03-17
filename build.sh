#!/bin/bash

# Create public directory
mkdir -p public

# Copy main HTML file and convert Django template tags to direct paths
cp RecipieGenerator/Template/Home.html public/index.html

# Remove Django load tag and convert {% static 'xxx' %} to direct paths
sed -i '' 's/{%[[:space:]]*load[[:space:]]*static[[:space:]]*%}//g' public/index.html
sed -i '' "s/{%[[:space:]]*static[[:space:]]*['\"]\/\?\([^'\"]*\)['\"][[:space:]]*%}/\1/g" public/index.html

# Copy static assets
if [ -d "RecipieGenerator/assests" ]; then
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
