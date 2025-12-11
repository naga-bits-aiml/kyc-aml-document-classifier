#!/usr/bin/env python
"""
Test runner with HTML report generation
"""
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def run_tests():
    """Run pytest with HTML report generation"""
    
    # Create reports directory
    reports_dir = PROJECT_ROOT / "test_reports"
    reports_dir.mkdir(exist_ok=True)
    
    # Generate timestamp for report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_report = reports_dir / f"test_report_{timestamp}.html"
    
    # pytest arguments
    pytest_args = [
        "pytest",
        str(PROJECT_ROOT / "tests"),
        "-v",  # Verbose
        "--tb=short",  # Short traceback format
        f"--html={html_report}",  # HTML report
        "--self-contained-html",  # Single file report
        "--cov=api",  # Coverage for api module
        "--cov=inference",  # Coverage for inference module
        "--cov-report=html:test_reports/coverage",  # HTML coverage report
        "--cov-report=term-missing",  # Terminal coverage report
        "--junit-xml=test_reports/junit.xml",  # JUnit XML report
    ]
    
    print("=" * 80)
    print("Running KYC/AML Document Classifier Test Suite")
    print("=" * 80)
    print(f"\nTest reports will be saved to: {reports_dir}")
    print(f"HTML Report: {html_report}")
    print(f"Coverage Report: {reports_dir / 'coverage' / 'index.html'}")
    print("\n" + "=" * 80 + "\n")
    
    # Run pytest
    try:
        result = subprocess.run(pytest_args, cwd=PROJECT_ROOT)
        
        print("\n" + "=" * 80)
        print("Test execution completed!")
        print("=" * 80)
        print(f"\n📊 View HTML report: {html_report}")
        print(f"📈 View coverage report: {reports_dir / 'coverage' / 'index.html'}")
        print(f"📋 JUnit XML: {reports_dir / 'junit.xml'}")
        
        return result.returncode
    
    except FileNotFoundError:
        print("\n❌ Error: pytest not found. Please install test dependencies:")
        print("   pip install pytest pytest-html pytest-cov")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
