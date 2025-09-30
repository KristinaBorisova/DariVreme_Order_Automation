#!/usr/bin/env python3
"""
security_check.py
Security checker to identify sensitive data before making repository public.
"""

import os
import re
import sys
from pathlib import Path

def check_for_sensitive_data():
    """Check for sensitive data that should not be in public repository."""
    print("🔍 Security Check for Public Repository")
    print("="*50)
    
    issues_found = []
    
    # Patterns to check for - only real security threats
    sensitive_patterns = [
            {
                "name": "Real API Keys",
                "pattern": r'API_KEY\s*=\s*["\'][0-9]{10,}["\']',
                "description": "Real API keys found (not placeholders)"
            },
            {
                "name": "Real API Secrets", 
                "pattern": r'API_SECRET\s*=\s*["\'][a-f0-9]{20,}["\']',
                "description": "Real API secrets found (not placeholders)"
            },
            {
                "name": "Real Google Sheets URLs",
                "pattern": r'docs\.google\.com/spreadsheets/d/[a-zA-Z0-9-_]{20,}',
                "description": "Real Google Sheets URLs found (not placeholders)"
            },
            {
                "name": "Real Email Addresses",
                "pattern": r'[a-zA-Z0-9._%+-]+@(gmail|yahoo|outlook|hotmail)\.com',
                "description": "Real email addresses found"
            },
            {
                "name": "Real Phone Numbers",
                "pattern": r'(\+359|886|0888)[0-9]{7,}',
                "description": "Real phone numbers found (Bulgarian numbers)"
            },
            {
                "name": "Real Client Names",
                "pattern": r'[А-Яа-я]+[A-Za-z]+',
                "description": "Real client names found (Cyrillic + Latin)"
            }
        ]
    
    # Files to check
    file_extensions = ['.py', '.md', '.txt', '.json', '.yml', '.yaml']
    exclude_dirs = ['.git', '__pycache__', 'node_modules', '.venv', 'venv']
    
    # Walk through all files
    for root, dirs, files in os.walk('.'):
        # Remove excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if any(file.endswith(ext) for ext in file_extensions):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        line_num = 0
                        
                        for line in content.split('\n'):
                            line_num += 1
                            
                            for check in sensitive_patterns:
                                if re.search(check['pattern'], line, re.IGNORECASE):
                                    # Skip if it's an example or placeholder
                                    if any(placeholder in line.lower() for placeholder in [
                                        'example', 'placeholder', 'your_', 'sample', 'test'
                                    ]):
                                        continue
                                    
                                    issues_found.append({
                                        'file': file_path,
                                        'line': line_num,
                                        'type': check['name'],
                                        'description': check['description'],
                                        'content': line.strip()
                                    })
                                    
                except Exception as e:
                    print(f"⚠️  Could not read {file_path}: {e}")
    
    # Report results
    if issues_found:
        print(f"❌ Found {len(issues_found)} potential security issues:")
        print()
        
        for issue in issues_found:
            print(f"🔴 {issue['type']} in {issue['file']}:{issue['line']}")
            print(f"   {issue['description']}")
            print(f"   Content: {issue['content']}")
            print()
        
        print("🚨 RECOMMENDATIONS:")
        print("1. Replace hardcoded values with environment variables")
        print("2. Use placeholder values for examples")
        print("3. Add sensitive files to .gitignore")
        print("4. Create .env.example with placeholder values")
        print()
        print("📝 Example fixes:")
        print("   OLD: API_KEY = 'your_real_key'")
        print("   NEW: API_KEY = os.getenv('API_KEY', 'your_api_key_here')")
        
        return False
    else:
        print("✅ No sensitive data found!")
        print("🎉 Repository appears safe for public release.")
        return True

def create_gitignore_additions():
    """Create .gitignore additions for security."""
    gitignore_additions = """
# Security - Environment files
.env
*.env
.env.local
.env.production

# Security - Credentials
google_sheets_credentials.json
*credentials*.json
*secret*.json

# Security - Logs and results
logs/
daily_results/
*.log

# Security - Cache and temporary files
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
"""
    
    print("\n📝 Add these to your .gitignore file:")
    print(gitignore_additions)

def create_env_example():
    """Create .env.example template."""
    env_example = """# Glovo API Configuration
TOKEN_URL=https://stageapi.glovoapp.com/oauth/token
API_KEY=your_api_key_here
API_SECRET=your_api_secret_here

# Google Sheets Configuration  
GOOGLE_SHEETS_URL=https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit"""
    
    print("\n📝 Create .env.example file with this content:")
    print(env_example)

def main():
    """Main security check function."""
    print("🛡️  Pre-Public Security Check")
    print("="*50)
    
    # Check if we're in a git repository
    if not os.path.exists('.git'):
        print("⚠️  Not in a git repository. Run this from your project root.")
        return 1
    
    # Run security check
    is_safe = check_for_sensitive_data()
    
    if not is_safe:
        create_gitignore_additions()
        create_env_example()
        print("\n🚨 Please fix the issues above before making your repository public!")
        return 1
    else:
        print("\n✅ Repository is ready for public release!")
        return 0

if __name__ == "__main__":
    exit(main())
