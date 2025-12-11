# 🧪 Quick Test Guide

## Run Tests in 3 Easy Steps

### 1. Install Dependencies
```bash
pip install -r requirements-test.txt
```

### 2. Run Tests
```bash
# Quick test (stops on first failure)
python test_quick.py

# Full test suite with reports
python tests/run_tests.py
```

### 3. View Reports
```bash
# Open custom report
start test_reports/custom_report_TIMESTAMP.html

# Open coverage report
start test_reports/coverage/index.html
```

## Test Results

### ✅ Latest Run: December 11, 2025
- **Total Tests:** 37
- **Passed:** 37 (100%)
- **Failed:** 0
- **Coverage:** 70%
- **Duration:** 3.53s

## What's Tested?

### ✅ All API Endpoints
- Root (/) - API information
- Health (/health) - Service status
- Info (/info) - Model details
- Classes (/classes) - Document types
- Predict (/predict) - Image classification

### ✅ Test Categories
- Functional tests (endpoints work correctly)
- Integration tests (workflows work end-to-end)
- Error handling (invalid inputs handled gracefully)
- Performance tests (responses under 1 second)
- CORS tests (cross-origin requests allowed)

### ✅ Test Data
- Valid JPEG images
- Valid PNG images
- Large images (4000x4000)
- Invalid files (text files)
- Empty filenames

## Reports Generated

📊 **Pytest HTML Report**
- Detailed test results
- Execution times
- Captured logs

📈 **Custom Visualization Report**
- Beautiful UI with statistics
- Progress bar
- Color-coded results
- Tests grouped by class

📋 **Coverage Report**
- Line-by-line coverage
- Missing lines highlighted
- 70% overall coverage

📄 **JUnit XML Report**
- CI/CD integration ready
- Standard format

## Quick Commands

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_endpoints.py -v

# Run specific test class
pytest tests/test_endpoints.py::TestPredictEndpoint -v

# Run with coverage
pytest tests/ --cov=api --cov=inference

# Generate HTML coverage report
pytest tests/ --cov=api --cov-report=html

# Run and stop on first failure
pytest tests/ -x

# Show print statements
pytest tests/ -s
```

## Test Files

```
tests/
├── __init__.py               # Test package
├── conftest.py               # Fixtures and configuration
├── test_endpoints.py         # Endpoint tests (32 tests)
├── test_integration.py       # Integration tests (3 tests)
├── run_tests.py              # Test runner with reports
├── generate_report.py        # Custom report generator
└── README.md                 # Full documentation
```

## Need Help?

- See `tests/README.md` for full documentation
- See `TEST_SUITE_SUMMARY.md` for detailed results
- Check pytest docs: https://docs.pytest.org/
