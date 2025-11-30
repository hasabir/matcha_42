#!/usr/bin/env python3
"""
Environment Variable Audit Script
Verifies that all credentials, API keys, and sensitive values are stored in .env
and not hardcoded in the codebase (as per subject requirements)
"""
import os
import re
import sys
from pathlib import Path

# Patterns that indicate hardcoded secrets/credentials
SUSPICIOUS_PATTERNS = [
    # Generic patterns
    (r'password\s*=\s*["\'](?!.*getenv)([^"\']{3,})["\']', 'Hardcoded password'),
    (r'api[_-]?key\s*=\s*["\'](?!.*getenv)([^"\']{10,})["\']', 'Hardcoded API key'),
    (r'secret[_-]?key\s*=\s*["\'](?!.*getenv)([^"\']{10,})["\']', 'Hardcoded secret key'),
    (r'token\s*=\s*["\'](?!.*getenv)([^"\']{10,})["\']', 'Hardcoded token'),
    
    # Database credentials
    (r'DB_PASSWORD\s*=\s*["\'](?!.*getenv)([^"\']+)["\']', 'Hardcoded DB password'),
    (r'DB_USER\s*=\s*["\'](?!.*getenv)((?!admin|postgres|root)[^"\']{3,})["\']', 'Hardcoded DB user'),
    
    # Email/SMTP
    (r'MAIL_PASSWORD\s*=\s*["\'](?!.*getenv)([^"\']{3,})["\']', 'Hardcoded mail password'),
    (r'MAIL_USERNAME\s*=\s*["\'](?!.*getenv)([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})["\']', 'Hardcoded email address'),
    
    # JWT secrets
    (r'JWT_[A-Z_]*\s*=\s*["\'](?!.*getenv)([^"\']{10,})["\']', 'Hardcoded JWT secret'),
]

# Environment variables that should be in .env
REQUIRED_ENV_VARS = [
    'DB_HOST',
    'DB_PORT', 
    'DB_NAME',
    'DB_USER',
    'DB_PASSWORD',
    'MAIL_SERVER',
    'MAIL_PORT',
    'MAIL_USERNAME',
    'MAIL_PASSWORD',
    'JWT_ACCESS_TOKEN',
    'JWT_REFRESH_TOKEN',
    'SMTP_SECRET_KEY',
    'REDIS_HOST',
    'REDIS_PORT',
    'REDIS_DB',
]

# Files/directories to exclude from scanning
EXCLUDE_PATTERNS = [
    '__pycache__',
    '.git',
    'node_modules',
    '.env',
    '.env.example',
    '.env.backup',
    'verify_env_vars.py',  # Don't scan this file
    'build/',
    'migrations/',
]

def should_exclude(file_path):
    """Check if file should be excluded from scanning"""
    path_str = str(file_path)
    return any(pattern in path_str for pattern in EXCLUDE_PATTERNS)

def scan_file_for_hardcoded_secrets(file_path):
    """Scan a single file for hardcoded secrets"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
            
            for pattern, description in SUSPICIOUS_PATTERNS:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    # Find line number
                    line_num = content[:match.start()].count('\n') + 1
                    line_content = lines[line_num - 1].strip()
                    
                    # Skip if it's a comment or in a docstring
                    if line_content.startswith('#') or line_content.startswith('"""') or line_content.startswith("'''"):
                        continue
                    
                    # Skip if it's using os.getenv or os.environ
                    if 'getenv' in line_content or 'os.environ' in line_content:
                        continue
                    
                    issues.append({
                        'file': str(file_path),
                        'line': line_num,
                        'description': description,
                        'content': line_content[:100]  # First 100 chars
                    })
    
    except Exception as e:
        print(f"⚠️  Error scanning {file_path}: {e}")
    
    return issues

def check_env_file(env_file_path):
    """Check if .env file exists and contains required variables"""
    issues = []
    
    if not os.path.exists(env_file_path):
        return [{'type': 'missing_env', 'message': '.env file not found'}]
    
    try:
        with open(env_file_path, 'r') as f:
            content = f.read()
            
            for var in REQUIRED_ENV_VARS:
                if var not in content:
                    issues.append({
                        'type': 'missing_var',
                        'variable': var,
                        'message': f'Required variable {var} not found in .env'
                    })
    
    except Exception as e:
        issues.append({'type': 'error', 'message': f'Error reading .env: {e}'})
    
    return issues

def scan_codebase(root_dir):
    """Scan entire codebase for hardcoded secrets"""
    print("🔍 Scanning codebase for hardcoded credentials...\n")
    
    all_issues = []
    files_scanned = 0
    
    # Scan all Python files
    for py_file in Path(root_dir).rglob('*.py'):
        if should_exclude(py_file):
            continue
        
        files_scanned += 1
        issues = scan_file_for_hardcoded_secrets(py_file)
        all_issues.extend(issues)
    
    print(f"📊 Scanned {files_scanned} Python files\n")
    
    return all_issues

def main():
    # Get backend directory
    backend_dir = Path(__file__).parent.parent
    env_file = backend_dir / '.env'
    
    print("=" * 80)
    print("🔐 ENVIRONMENT VARIABLE SECURITY AUDIT")
    print("   Verifying all credentials are stored in .env (Subject Requirement)")
    print("=" * 80)
    print()
    
    # Check .env file
    print("1️⃣  Checking .env file...")
    env_issues = check_env_file(env_file)
    
    if env_issues:
        print("❌ Issues with .env file:")
        for issue in env_issues:
            if issue.get('type') == 'missing_var':
                print(f"   ⚠️  {issue['message']}")
            else:
                print(f"   ❌ {issue['message']}")
        print()
    else:
        print("✅ .env file contains all required variables\n")
    
    # Scan codebase
    print("2️⃣  Scanning codebase for hardcoded secrets...")
    code_issues = scan_codebase(backend_dir)
    
    if code_issues:
        print(f"❌ Found {len(code_issues)} potential hardcoded secrets:\n")
        for issue in code_issues:
            print(f"   📁 {issue['file']}")
            print(f"   📍 Line {issue['line']}")
            print(f"   ⚠️  {issue['description']}")
            print(f"   💬 {issue['content']}")
            print()
    else:
        print("✅ No hardcoded secrets found in codebase\n")
    
    # Summary
    print("=" * 80)
    print("📋 AUDIT SUMMARY")
    print("=" * 80)
    total_issues = len(env_issues) + len(code_issues)
    
    if total_issues == 0:
        print("✅ PASSED: All credentials are stored in environment variables")
        print("✅ Subject requirement satisfied: No hardcoded secrets found")
        return 0
    else:
        print(f"⚠️  WARNINGS: {len(env_issues)} .env issues, {len(code_issues)} potential hardcoded secrets")
        print("⚠️  Review the issues above and move credentials to .env file")
        return 1

if __name__ == '__main__':
    sys.exit(main())
