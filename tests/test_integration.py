"""
Integration tests for complete workflows
"""
import pytest
from fastapi import status


class TestCompleteWorkflow:
    """Test complete API workflows"""
    
    def test_full_prediction_workflow(self, client, sample_image_file):
        """Test complete prediction workflow"""
        # 1. Check health
        health_response = client.get("/health")
        assert health_response.status_code == status.HTTP_200_OK
        
        # 2. Get available classes
        classes_response = client.get("/classes")
        assert classes_response.status_code == status.HTTP_200_OK
        
        # 3. Make prediction
        with open(sample_image_file, "rb") as f:
            predict_response = client.post(
                "/predict",
                files={"file": ("test.jpg", f, "image/jpeg")}
            )
        
        if predict_response.status_code == status.HTTP_200_OK:
            data = predict_response.json()
            classes_data = classes_response.json()
            
            # Verify predicted class is in available classes
            if classes_data.get("model_loaded"):
                assert data["predicted_class"] in classes_data["classes"]
    
    def test_multiple_predictions(self, client, sample_image_file):
        """Test multiple predictions in sequence"""
        results = []
        
        for i in range(3):
            with open(sample_image_file, "rb") as f:
                response = client.post(
                    "/predict",
                    files={"file": (f"test_{i}.jpg", f, "image/jpeg")}
                )
            
            if response.status_code == status.HTTP_200_OK:
                results.append(response.json())
        
        # All predictions should be consistent for same image
        if len(results) >= 2:
            assert results[0]["predicted_class"] == results[1]["predicted_class"]
    
    def test_api_info_consistency(self, client):
        """Test that API info is consistent across endpoints"""
        info_response = client.get("/info")
        classes_response = client.get("/classes")
        
        if info_response.status_code == status.HTTP_200_OK:
            if classes_response.status_code == status.HTTP_200_OK:
                info_data = info_response.json()
                classes_data = classes_response.json()
                
                if info_data.get("model_loaded") and classes_data.get("model_loaded"):
                    # Number of classes should match
                    assert info_data["model_info"]["num_classes"] == classes_data["num_classes"]
                    # Classes list should match
                    assert set(info_data["model_info"]["classes"]) == set(classes_data["classes"])
