#!/usr/bin/env python3
"""
deploy_to_github.py
Deployment script to help set up GitHub Actions for daily delivery automation.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_git_repo():
    """Check if we're in a git repository."""
    try:
        result = subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def check_github_remote():
    """Check if GitHub remote is configured."""
    try:
        result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                              capture_output=True, text=True)
        return 'github.com' in result.stdout
    except:
        return False

def create_github_workflow():
    """Create the GitHub Actions workflow file."""
    workflow_dir = Path('.github/workflows')
    workflow_dir.mkdir(parents=True, exist_ok=True)
    
    workflow_file = workflow_dir / 'daily-delivery-automation.yml'
    
    if workflow_file.exists():
        print(f"✅ Workflow file already exists: {workflow_file}")
        return True
    
    print(f"📝 Creating workflow file: {workflow_file}")
    return True

def check_requirements():
    """Check if requirements.txt exists and has necessary packages."""
    requirements_file = Path('requirements.txt')
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    print("✅ requirements.txt found")
    
    # Check for key packages
    with open(requirements_file, 'r') as f:
        content = f.read()
    
    required_packages = ['requests', 'pandas', 'openpyxl', 'gspread']
    missing_packages = []
    
    for package in required_packages:
        if package not in content:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"⚠️  Missing packages in requirements.txt: {', '.join(missing_packages)}")
        return False
    
    print("✅ All required packages found in requirements.txt")
    return True

def create_env_example():
    """Create .env.example file with required environment variables."""
    env_example = """# GitHub Secrets Configuration
# Copy this file to .env and fill in your values
# Then add these as GitHub Secrets in your repository settings

# Glovo API Configuration
TOKEN_URL=https://stageapi.glovoapp.com/v2/laas/oauth/token
API_KEY=your_glovo_api_key_here
API_SECRET=your_glovo_api_secret_here

# Google Sheets Configuration
GOOGLE_SHEETS_URL=https://docs.google.com/spreadsheets/d/your_sheet_id/edit#gid=your_gid

# Optional: Email notifications
EMAIL_USERNAME=your_email@example.com
EMAIL_PASSWORD=your_app_password

# Optional: Slack notifications
SLACK_WEBHOOK=https://hooks.slack.com/services/your/webhook/url
"""
    
    env_file = Path('.env.example')
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write(env_example)
        print(f"✅ Created .env.example file")
    else:
        print(f"✅ .env.example already exists")

def print_github_setup_instructions():
    """Print instructions for setting up GitHub Actions."""
    print("\n" + "="*60)
    print("🚀 GITHUB ACTIONS SETUP INSTRUCTIONS")
    print("="*60)
    
    print("\n1. 📁 Push your code to GitHub:")
    print("   git add .")
    print("   git commit -m 'Add daily delivery automation'")
    print("   git push origin main")
    
    print("\n2. 🔐 Configure GitHub Secrets:")
    print("   Go to: Repository → Settings → Secrets and variables → Actions")
    print("   Add these secrets:")
    print("   - TOKEN_URL: https://stageapi.glovoapp.com/v2/laas/oauth/token")
    print("   - API_KEY: your_glovo_api_key")
    print("   - API_SECRET: your_glovo_api_secret")
    print("   - GOOGLE_SHEETS_URL: your_google_sheets_url")
    
    print("\n3. 🧪 Test the workflow:")
    print("   Go to: Repository → Actions → Daily Delivery Automation")
    print("   Click 'Run workflow' → Select 'Run in test mode' → Run workflow")
    
    print("\n4. 📅 Schedule is already configured:")
    print("   - Runs every weekday at 9:00 AM UTC")
    print("   - Monday-Friday only")
    print("   - Automatic execution")
    
    print("\n5. 📊 Monitor results:")
    print("   - Check Actions tab for run status")
    print("   - Download logs and results from each run")
    print("   - Set up notifications if needed")

def main():
    """Main deployment function."""
    print("🚀 GitHub Actions Deployment Setup")
    print("="*60)
    
    # Check prerequisites
    checks = [
        ("Git Repository", check_git_repo()),
        ("GitHub Remote", check_github_remote()),
        ("Requirements File", check_requirements()),
    ]
    
    print("\n📋 Prerequisites Check:")
    all_passed = True
    
    for check_name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {check_name}: {status}")
        if not passed:
            all_passed = False
    
    if not all_passed:
        print("\n⚠️  Some prerequisites failed. Please fix them before proceeding.")
        return 1
    
    # Create necessary files
    print("\n📝 Creating necessary files:")
    create_github_workflow()
    create_env_example()
    
    # Print instructions
    print_github_setup_instructions()
    
    print("\n✅ Setup completed! Follow the instructions above to deploy to GitHub.")
    return 0

if __name__ == "__main__":
    exit(main())
