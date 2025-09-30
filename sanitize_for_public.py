#!/usr/bin/env python3
"""
sanitize_for_public.py
Sanitize the repository for public release by replacing sensitive data with placeholders.
"""

import os
import re
import shutil
from pathlib import Path

def sanitize_file(file_path):
    """Sanitize a single file by replacing sensitive data with placeholders."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace API keys
        content = re.sub(r'API_KEY\s*=\s*["\']175482686405285["\']', 'API_KEY = os.getenv("API_KEY", "your_api_key_here")', content)
        content = re.sub(r'api_key\s*=\s*os\.getenv\(["\']API_KEY["\'],\s*["\']175482686405285["\']', 'api_key = os.getenv("API_KEY", "your_api_key_here")', content)
        
        # Replace API secrets
        content = re.sub(r'API_SECRET\s*=\s*["\'][^"\']+["\']', 'API_SECRET = os.getenv("API_SECRET", "your_api_secret_here")', content)
        content = re.sub(r'api_secret\s*=\s*os\.getenv\(["\']API_SECRET["\'],\s*["\'][^"\']+["\']', 'api_secret = os.getenv("API_SECRET", "your_api_secret_here")', content)
        
        # Replace Google Sheets URLs
        content = re.sub(
            r'https://docs\.google\.com/spreadsheets/d/[a-zA-Z0-9-_]+/[^"\']*',
            'https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit',
            content
        )
        
        # Replace real email addresses with examples
        content = re.sub(r'[a-zA-Z0-9._%+-]+@gmail\.com', 'client@example.com', content)
        content = re.sub(r'[a-zA-Z0-9._%+-]+@darivreme\.com', 'client@example.com', content)
        
        # Replace real phone numbers with examples
        content = re.sub(r'886611111[0-9]', '+1234567890', content)
        content = re.sub(r'\+1234567890', '+1234567890', content)
        
        # Replace real client names with examples
        content = re.sub(r'Sample Client', 'Sample Client', content)
        content = re.sub(r'pancho@gmail\.com', 'client@example.com', content)
        content = re.sub(r'robert@gmail\.com', 'client@example.com', content)
        
        # Replace real UUIDs with examples
        content = re.sub(r'12345678-1234-1234-1234-123456789012', '12345678-1234-1234-1234-123456789012', content)
        content = re.sub(r'12345678-1234-1234-1234-123456789012', '12345678-1234-1234-1234-123456789012', content)
        content = re.sub(r'12345678-1234-1234-1234-123456789012', '12345678-1234-1234-1234-123456789012', content)
        
        # Replace real order IDs with examples
        content = re.sub(r'100010000000', '100010000000', content)
        content = re.sub(r'100010000001', '100010000001', content)
        content = re.sub(r'100010000002', '100010000002', content)
        
        # Replace real partner IDs with examples
        content = re.sub(r'12345678', '12345678', content)
        
        # Replace real tracking numbers with examples
        content = re.sub(r'ORD1234567890', 'ORD1234567890', content)
        content = re.sub(r'ORD1234567891', 'ORD1234567891', content)
        content = re.sub(r'ORD1234567892', 'ORD1234567892', content)
        content = re.sub(r'ORD1234567893', 'ORD1234567893', content)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Sanitized: {file_path}")
            return True
        else:
            print(f"⏭️  No changes needed: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error sanitizing {file_path}: {e}")
        return False

def main():
    """Main sanitization function."""
    print("🧹 Sanitizing Repository for Public Release")
    print("="*50)
    
    # Files to sanitize
    file_extensions = ['.py', '.md', '.yml', '.yaml', '.json']
    exclude_dirs = ['.git', '__pycache__', 'node_modules', '.venv', 'venv', 'Test Scripts']
    
    sanitized_count = 0
    total_files = 0
    
    # Walk through all files
    for root, dirs, files in os.walk('.'):
        # Remove excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if any(file.endswith(ext) for ext in file_extensions):
                file_path = os.path.join(root, file)
                total_files += 1
                
                if sanitize_file(file_path):
                    sanitized_count += 1
    
    print(f"\n📊 Sanitization Summary:")
    print(f"   Total files processed: {total_files}")
    print(f"   Files sanitized: {sanitized_count}")
    print(f"   Files unchanged: {total_files - sanitized_count}")
    
    # Create .env.example
    env_example = """# Glovo API Configuration
TOKEN_URL=https://stageapi.glovoapp.com/oauth/token
API_KEY=your_api_key_here
API_SECRET=your_api_secret_here

# Google Sheets Configuration
GOOGLE_SHEETS_URL=https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit

# Optional: Production API (if different)
# PRODUCTION_TOKEN_URL=https://api.glovoapp.com/oauth/token
"""
    
    with open('.env.example', 'w') as f:
        f.write(env_example)
    print("✅ Created .env.example file")
    
    print("\n🎉 Sanitization complete!")
    print("📝 Next steps:")
    print("   1. Review the changes")
    print("   2. Test the sanitized code")
    print("   3. Run 'python security_check.py' to verify")
    print("   4. Commit and push to public repository")

if __name__ == "__main__":
    main()
