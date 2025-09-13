#!/usr/bin/env python3
"""
fix_github_actions.py
Fix deprecated GitHub Actions versions and update workflow.
"""

import os
import re
from pathlib import Path

def fix_workflow_file():
    """Fix deprecated GitHub Actions versions in workflow file."""
    workflow_file = Path('.github/workflows/daily-delivery-automation.yml')
    
    if not workflow_file.exists():
        print("❌ Workflow file not found")
        return False
    
    print("🔧 Fixing deprecated GitHub Actions versions...")
    
    # Read the file
    with open(workflow_file, 'r') as f:
        content = f.read()
    
    # Fix deprecated versions
    fixes = [
        ('actions/upload-artifact@v3', 'actions/upload-artifact@v4'),
        ('actions/setup-python@v4', 'actions/setup-python@v5'),
        ('actions/checkout@v3', 'actions/checkout@v4'),
        ('actions/github-script@v5', 'actions/github-script@v6'),
    ]
    
    original_content = content
    for old_version, new_version in fixes:
        content = content.replace(old_version, new_version)
    
    # Check if any changes were made
    if content != original_content:
        # Write the fixed content
        with open(workflow_file, 'w') as f:
            f.write(content)
        print("✅ Workflow file updated with latest versions")
        return True
    else:
        print("✅ Workflow file already uses latest versions")
        return True

def validate_workflow_syntax():
    """Validate the workflow file syntax."""
    workflow_file = Path('.github/workflows/daily-delivery-automation.yml')
    
    if not workflow_file.exists():
        print("❌ Workflow file not found")
        return False
    
    print("🧪 Validating workflow syntax...")
    
    try:
        import yaml
        with open(workflow_file, 'r') as f:
            yaml.safe_load(f)
        print("✅ Workflow syntax is valid")
        return True
    except ImportError:
        print("⚠️  PyYAML not installed, skipping syntax validation")
        return True
    except yaml.YAMLError as e:
        print(f"❌ Workflow syntax error: {e}")
        return False

def check_action_versions():
    """Check if all actions use latest versions."""
    workflow_file = Path('.github/workflows/daily-delivery-automation.yml')
    
    if not workflow_file.exists():
        print("❌ Workflow file not found")
        return False
    
    print("🔍 Checking action versions...")
    
    with open(workflow_file, 'r') as f:
        content = f.read()
    
    # Find all action references
    action_pattern = r'uses:\s*([^@]+@[^\s]+)'
    actions = re.findall(action_pattern, content)
    
    print("📋 Current action versions:")
    for action in actions:
        print(f"   {action}")
    
    # Check for known deprecated versions
    deprecated_actions = [
        'actions/upload-artifact@v3',
        'actions/setup-python@v4',
        'actions/checkout@v3',
        'actions/github-script@v5'
    ]
    
    found_deprecated = []
    for action in actions:
        if action in deprecated_actions:
            found_deprecated.append(action)
    
    if found_deprecated:
        print(f"⚠️  Found deprecated actions: {', '.join(found_deprecated)}")
        return False
    else:
        print("✅ All actions use latest versions")
        return True

def create_workflow_test():
    """Create a test workflow to verify the setup."""
    test_workflow = """name: Test Daily Delivery Automation

on:
  workflow_dispatch:
    inputs:
      test_mode:
        description: 'Run in test mode'
        required: false
        default: true
        type: boolean

jobs:
  test-automation:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.12'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Test imports
      run: |
        python -c "import requests, pandas, openpyxl, gspread; print('✅ All imports successful')"
        
    - name: Test authentication
      run: |
        cd step_1_authentication
        python token_service.py
        
    - name: Test automation script
      run: |
        python test_github_actions.py
"""
    
    test_file = Path('.github/workflows/test-automation.yml')
    test_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(test_file, 'w') as f:
        f.write(test_workflow)
    
    print(f"✅ Created test workflow: {test_file}")

def main():
    """Main fix function."""
    print("🔧 GitHub Actions Fix Script")
    print("="*50)
    
    # Fix workflow file
    if not fix_workflow_file():
        return 1
    
    # Validate syntax
    if not validate_workflow_syntax():
        return 1
    
    # Check versions
    if not check_action_versions():
        print("⚠️  Some actions may still be deprecated")
    
    # Create test workflow
    create_workflow_test()
    
    print("\n✅ GitHub Actions fix completed!")
    print("\n📋 Next steps:")
    print("1. Commit and push the changes:")
    print("   git add .")
    print("   git commit -m 'Fix deprecated GitHub Actions versions'")
    print("   git push origin main")
    print("\n2. Test the workflow:")
    print("   Go to Actions → Test Daily Delivery Automation → Run workflow")
    print("\n3. Check the main workflow:")
    print("   Go to Actions → Daily Delivery Automation → Run workflow")
    
    return 0

if __name__ == "__main__":
    exit(main())
