"""
Test suite for all API endpoints
"""
import pytest
from fastapi import status


class TestRootEndpoint:
    """Tests for GET / endpoint"""
    
    def test_root_returns_200(self, client):
        """Test that root endpoint returns 200 OK"""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
    
    def test_root_returns_json(self, client):
        """Test that root endpoint returns JSON"""
        response = client.get("/")
        assert response.headers["content-type"] == "application/json"
    
    def test_root_contains_app_info(self, client):
        """Test that root endpoint contains application info"""
        response = client.get("/")
        data = response.json()
        assert "app" in data
        assert "version" in data
        assert "status" in data
        assert "endpoints" in data
        assert isinstance(data["endpoints"], dict)
    
    def test_root_app_name(self, client):
        """Test application name"""
        response = client.get("/")
        data = response.json()
        assert data["app"] == "KYC/AML Document Classifier"
    
    def test_root_has_endpoints(self, client):
        """Test that endpoints are documented"""
        response = client.get("/")
        data = response.json()
        endpoints = data["endpoints"]
        assert "health" in endpoints
        assert "info" in endpoints
        assert "predict" in endpoints


class TestHealthEndpoint:
    """Tests for GET /health endpoint"""
    
    def test_health_returns_200(self, client):
        """Test that health endpoint returns 200 OK"""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
    
    def test_health_returns_json(self, client):
        """Test that health endpoint returns JSON"""
        response = client.get("/health")
        assert response.headers["content-type"] == "application/json"
    
    def test_health_contains_status(self, client):
        """Test that health response contains status"""
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_health_contains_model_loaded(self, client):
        """Test that health response contains model_loaded flag"""
        response = client.get("/health")
        data = response.json()
        assert "model_loaded" in data
        assert isinstance(data["model_loaded"], bool)


class TestInfoEndpoint:
    """Tests for GET /info endpoint"""
    
    def test_info_returns_200(self, client):
        """Test that info endpoint returns 200 OK"""
        response = client.get("/info")
        assert response.status_code == status.HTTP_200_OK
    
    def test_info_returns_json(self, client):
        """Test that info endpoint returns JSON"""
        response = client.get("/info")
        assert response.headers["content-type"] == "application/json"
    
    def test_info_contains_model_details(self, client):
        """Test that info contains model details"""
        response = client.get("/info")
        data = response.json()
        
        if data.get("model_loaded"):
            assert "model_info" in data
            model_info = data["model_info"]
            assert "classes" in model_info
            assert "num_classes" in model_info
            assert "device" in model_info
            assert "card_detection_enabled" in model_info
    
    def test_info_classes_count(self, client):
        """Test that info returns correct number of classes"""
        response = client.get("/info")
        data = response.json()
        
        if data.get("model_loaded"):
            assert data["model_info"]["num_classes"] == 5
    
    def test_info_classes_list(self, client):
        """Test that info returns expected classes"""
        response = client.get("/info")
        data = response.json()
        
        if data.get("model_loaded"):
            classes = data["model_info"]["classes"]
            expected_classes = ["aadhar", "driving", "pan", "passport", "voter"]
            assert set(classes) == set(expected_classes)


class TestClassesEndpoint:
    """Tests for GET /classes endpoint"""
    
    def test_classes_returns_200(self, client):
        """Test that classes endpoint returns 200 OK"""
        response = client.get("/classes")
        assert response.status_code == status.HTTP_200_OK
    
    def test_classes_returns_json(self, client):
        """Test that classes endpoint returns JSON"""
        response = client.get("/classes")
        assert response.headers["content-type"] == "application/json"
    
    def test_classes_structure(self, client):
        """Test classes response structure"""
        response = client.get("/classes")
        data = response.json()
        
        if data.get("model_loaded"):
            assert "classes" in data
            assert "num_classes" in data
            assert isinstance(data["classes"], list)
            assert isinstance(data["num_classes"], int)
    
    def test_classes_count_matches(self, client):
        """Test that num_classes matches classes list length"""
        response = client.get("/classes")
        data = response.json()
        
        if data.get("model_loaded"):
            assert len(data["classes"]) == data["num_classes"]
    
    def test_classes_contains_expected_values(self, client):
        """Test that classes contain expected document types"""
        response = client.get("/classes")
        data = response.json()
        
        if data.get("model_loaded"):
            expected = ["aadhar", "driving", "pan", "passport", "voter"]
            assert sorted(data["classes"]) == sorted(expected)


class TestPredictEndpoint:
    """Tests for POST /predict endpoint"""
    
    def test_predict_without_file_returns_422(self, client):
        """Test that predict without file returns 422 Unprocessable Entity"""
        response = client.post("/predict")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_predict_with_valid_image(self, client, sample_image_file):
        """Test prediction with valid image file"""
        with open(sample_image_file, "rb") as f:
            response = client.post(
                "/predict",
                files={"file": ("test.jpg", f, "image/jpeg")}
            )
        
        # Should return 200 or 503 (if model not loaded)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE]
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "success" in data
            assert "predicted_class" in data
            assert "confidence" in data
            assert "all_probabilities" in data
    
    def test_predict_with_png_image(self, client, sample_png_file):
        """Test prediction with PNG image"""
        with open(sample_png_file, "rb") as f:
            response = client.post(
                "/predict",
                files={"file": ("test.png", f, "image/png")}
            )
        
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE]
    
    def test_predict_with_invalid_file(self, client, invalid_file):
        """Test prediction with non-image file returns 400"""
        with open(invalid_file, "rb") as f:
            response = client.post(
                "/predict",
                files={"file": ("test.txt", f, "text/plain")}
            )
        
        # Should return 400 Bad Request for unsupported file type
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_predict_response_structure(self, client, sample_image_file):
        """Test prediction response structure"""
        with open(sample_image_file, "rb") as f:
            response = client.post(
                "/predict",
                files={"file": ("test.jpg", f, "image/jpeg")}
            )
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert isinstance(data["success"], bool)
            assert isinstance(data["predicted_class"], str)
            assert isinstance(data["confidence"], float)
            assert isinstance(data["all_probabilities"], dict)
            assert 0.0 <= data["confidence"] <= 1.0
    
    def test_predict_probabilities_sum_to_one(self, client, sample_image_file):
        """Test that all probabilities sum to approximately 1.0"""
        with open(sample_image_file, "rb") as f:
            response = client.post(
                "/predict",
                files={"file": ("test.jpg", f, "image/jpeg")}
            )
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            probs = data["all_probabilities"]
            total = sum(probs.values())
            assert 0.99 <= total <= 1.01  # Allow small floating point error
    
    def test_predict_class_in_probabilities(self, client, sample_image_file):
        """Test that predicted class exists in all_probabilities"""
        with open(sample_image_file, "rb") as f:
            response = client.post(
                "/predict",
                files={"file": ("test.jpg", f, "image/jpeg")}
            )
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert data["predicted_class"] in data["all_probabilities"]
    
    def test_predict_confidence_matches_probability(self, client, sample_image_file):
        """Test that confidence matches the probability of predicted class"""
        with open(sample_image_file, "rb") as f:
            response = client.post(
                "/predict",
                files={"file": ("test.jpg", f, "image/jpeg")}
            )
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            predicted_class = data["predicted_class"]
            confidence = data["confidence"]
            prob = data["all_probabilities"][predicted_class]
            assert abs(confidence - prob) < 0.001  # Should be essentially equal


class TestErrorHandling:
    """Tests for error handling and edge cases"""
    
    def test_invalid_endpoint_returns_404(self, client):
        """Test that invalid endpoint returns 404"""
        response = client.get("/invalid-endpoint")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_predict_with_wrong_method(self, client):
        """Test that GET request to /predict returns 405"""
        response = client.get("/predict")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    
    def test_predict_empty_filename(self, client, sample_image_file):
        """Test prediction with empty filename"""
        with open(sample_image_file, "rb") as f:
            response = client.post(
                "/predict",
                files={"file": ("", f, "image/jpeg")}
            )
        
        # Should handle gracefully - may return 422 for invalid input
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_503_SERVICE_UNAVAILABLE
        ]


class TestCORS:
    """Tests for CORS middleware"""
    
    def test_cors_headers_present(self, client):
        """Test that CORS headers are present in response"""
        response = client.get("/", headers={"Origin": "http://localhost:3000"})
        assert "access-control-allow-origin" in response.headers
    
    def test_cors_allows_all_origins(self, client):
        """Test that CORS allows all origins"""
        response = client.get("/", headers={"Origin": "http://example.com"})
        assert response.headers.get("access-control-allow-origin") == "*"


class TestPerformance:
    """Basic performance tests"""
    
    def test_health_response_time(self, client):
        """Test that health endpoint responds quickly"""
        import time
        start = time.time()
        response = client.get("/health")
        duration = time.time() - start
        
        assert response.status_code == status.HTTP_200_OK
        assert duration < 1.0  # Should respond in less than 1 second
    
    def test_classes_response_time(self, client):
        """Test that classes endpoint responds quickly"""
        import time
        start = time.time()
        response = client.get("/classes")
        duration = time.time() - start
        
        assert response.status_code == status.HTTP_200_OK
        assert duration < 1.0
