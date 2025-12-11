"""
Quick test execution script - run this to test your API
"""
import subprocess
import sys
from pathlib import Path

def main():
    print("🧪 KYC/AML Document Classifier - Quick Test")
    print("=" * 60)
    
    # Check if dependencies are installed
    try:
        import pytest
    except ImportError:
        print("\n❌ Test dependencies not installed!")
        print("\n📦 Installing test dependencies...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements-test.txt"
        ])
    
    # Run tests
    print("\n🚀 Running tests...\n")
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "-x",  # Stop on first failure
    ])
    
    if result.returncode == 0:
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        print("\n📊 For detailed reports, run:")
        print("   python tests/run_tests.py")
    else:
        print("\n" + "=" * 60)
        print("❌ Some tests failed!")
        print("=" * 60)
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
