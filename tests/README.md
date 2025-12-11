# KYC/AML Document Classifier - Test Suite

Comprehensive test suite for the FastAPI-based document classification API.

## 📋 Test Coverage

### Endpoints Tested
- **GET /** - Root endpoint with API information
- **GET /health** - Health check endpoint
- **GET /info** - Model information endpoint
- **GET /classes** - Document classes endpoint
- **POST /predict** - Image classification endpoint

### Test Categories

1. **Functional Tests** (`test_endpoints.py`)
   - Root endpoint tests
   - Health check tests
   - Info endpoint tests
   - Classes endpoint tests
   - Prediction endpoint tests
   - Error handling tests
   - CORS middleware tests
   - Performance tests

2. **Integration Tests** (`test_integration.py`)
   - Complete prediction workflow
   - Multiple predictions consistency
   - API info consistency

## 🚀 Quick Start

### Install Test Dependencies

```bash
pip install pytest pytest-html pytest-cov
```

### Run Tests

#### Option 1: Using the test runner (Recommended)
```bash
python tests/run_tests.py
```

This will:
- Run all tests with verbose output
- Generate HTML test report
- Generate code coverage report
- Create JUnit XML report

#### Option 2: Using pytest directly
```bash
pytest tests/ -v
```

#### Option 3: With coverage
```bash
pytest tests/ --cov=api --cov=inference --cov-report=html
```

### Generate Custom Report

After running tests, generate a custom visualization report:

```bash
python tests/generate_report.py
```

## 📊 Test Reports

Test reports are saved in the `test_reports/` directory:

- `test_report_YYYYMMDD_HHMMSS.html` - Pytest HTML report
- `custom_report_YYYYMMDD_HHMMSS.html` - Custom visualization report
- `junit.xml` - JUnit XML format (for CI/CD integration)
- `coverage/index.html` - Code coverage report

## 📈 Example Test Execution

```bash
$ python tests/run_tests.py

================================================================================
Running KYC/AML Document Classifier Test Suite
================================================================================

Test reports will be saved to: test_reports/
HTML Report: test_reports/test_report_20251211_091800.html
Coverage Report: test_reports/coverage/index.html

================================================================================

tests/test_endpoints.py::TestRootEndpoint::test_root_returns_200 PASSED
tests/test_endpoints.py::TestRootEndpoint::test_root_returns_json PASSED
tests/test_endpoints.py::TestHealthEndpoint::test_health_returns_200 PASSED
...

================================================================================
Test execution completed!
================================================================================

📊 View HTML report: test_reports/test_report_20251211_091800.html
📈 View coverage report: test_reports/coverage/index.html
📋 JUnit XML: test_reports/junit.xml
```

## 🧪 Writing New Tests

### Test Structure

```python
import pytest
from fastapi import status

class TestYourFeature:
    """Tests for your feature"""
    
    def test_something(self, client):
        """Test description"""
        response = client.get("/endpoint")
        assert response.status_code == status.HTTP_200_OK
        assert "key" in response.json()
```

### Available Fixtures

- `client` - TestClient for making API requests
- `sample_image_bytes` - In-memory image bytes
- `sample_image_file` - Temporary JPEG image file
- `sample_png_file` - Temporary PNG image file
- `large_image_file` - Large 4000x4000 image
- `invalid_file` - Non-image text file

### Example Test

```python
def test_predict_with_image(client, sample_image_file):
    """Test prediction with valid image"""
    with open(sample_image_file, "rb") as f:
        response = client.post(
            "/predict",
            files={"file": ("test.jpg", f, "image/jpeg")}
        )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "predicted_class" in data
    assert "confidence" in data
```

## 🔧 Test Configuration

### pytest.ini

Create a `pytest.ini` file in the project root:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --tb=short
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
```

## 📝 Test Best Practices

1. **Test Naming**: Use descriptive names that explain what is being tested
   - `test_health_returns_200` ✅
   - `test_1` ❌

2. **Arrange-Act-Assert**: Structure tests clearly
   ```python
   def test_something(client):
       # Arrange
       data = {"key": "value"}
       
       # Act
       response = client.post("/endpoint", json=data)
       
       # Assert
       assert response.status_code == 200
   ```

3. **Test Independence**: Each test should be independent
   - Don't rely on test execution order
   - Use fixtures for setup/teardown

4. **Mock External Dependencies**: Use mocks for external services
   ```python
   @pytest.fixture
   def mock_model(monkeypatch):
       monkeypatch.setattr("module.function", lambda: "mock_result")
   ```

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-html pytest-cov
      
      - name: Run tests
        run: python tests/run_tests.py
      
      - name: Upload test results
        uses: actions/upload-artifact@v2
        with:
          name: test-results
          path: test_reports/
```

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Test Coverage Best Practices](https://coverage.readthedocs.io/)

## 🤝 Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain test coverage above 80%
4. Update this README with new test categories

## 📧 Support

For issues or questions about the test suite, please contact the development team.
