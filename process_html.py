#!/usr/bin/env python3
import os
import re
import sys

def process_html(input_file, output_file):
    """Convert Django template tags to direct file paths"""
    
    try:
        with open(input_file, 'r') as f:
            content = f.read()
        
        # Remove {% load static %} tag
        content = re.sub(r'{%\s*load\s+static\s*%}', '', content)
        
        # Replace {% static 'path' %} with just 'path' (remove leading slash if present)
        # Pattern: {% static 'anything' %} or {% static "anything" %}
        def replace_static(match):
            path = match.group(1) or match.group(2)
            # Remove leading slash for relative paths
            path = path.lstrip('/')
            return path
        
        content = re.sub(r'{%\s*static\s+[\'"]([^\'"]*)[\'"]s*%}', replace_static, content)
        
        # Write output
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(content)
        
        print(f"✅ Processed: {input_file} → {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error processing {input_file}: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: process_html.py <input> <output>")
        sys.exit(1)
    
    success = process_html(sys.argv[1], sys.argv[2])
    sys.exit(0 if success else 1)
