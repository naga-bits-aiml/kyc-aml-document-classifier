"""
Pytest configuration and fixtures for API tests
"""
import pytest
import sys
from pathlib import Path
from io import BytesIO
from PIL import Image

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient
from api.main import app


@pytest.fixture(scope="module")
def client():
    """Create a test client for the FastAPI app"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_image_bytes():
    """Generate a sample image in memory"""
    img = Image.new('RGB', (224, 224), color='white')
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return img_byte_arr


@pytest.fixture
def sample_image_file(tmp_path):
    """Create a temporary image file"""
    img = Image.new('RGB', (224, 224), color='blue')
    img_path = tmp_path / "test_image.jpg"
    img.save(img_path)
    return img_path


@pytest.fixture
def sample_png_file(tmp_path):
    """Create a temporary PNG image file"""
    img = Image.new('RGB', (300, 300), color='green')
    img_path = tmp_path / "test_image.png"
    img.save(img_path)
    return img_path


@pytest.fixture
def large_image_file(tmp_path):
    """Create a large image file"""
    img = Image.new('RGB', (4000, 4000), color='red')
    img_path = tmp_path / "large_image.jpg"
    img.save(img_path)
    return img_path


@pytest.fixture
def invalid_file(tmp_path):
    """Create an invalid (non-image) file"""
    file_path = tmp_path / "invalid.txt"
    file_path.write_text("This is not an image")
    return file_path
