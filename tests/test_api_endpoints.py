"""
API Endpoint Testing (TC001-TC005)
Tests for health check and root endpoints
"""
import pytest
import requests

BASE_URL = "http://localhost:8000"

class TestHealthCheckEndpoint:
    """TC001-TC003: Health Check Endpoint Tests"""
    
    def test_tc001_health_check_returns_200(self, skip_if_server_down):
        """TC001: Verify health check endpoint returns status 200"""
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
    
    def test_tc002_health_check_response_structure(self, skip_if_server_down):
        """TC002: Verify health check response structure"""
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "service" in data
    
    def test_tc003_health_check_invalid_endpoint(self, skip_if_server_down):
        """TC003: Verify health check with invalid endpoint"""
        response = requests.get(f"{BASE_URL}/health/invalid", timeout=10)
        assert response.status_code == 404

class TestRootEndpoint:
    """TC004-TC005: Root Endpoint Tests"""
    
    def test_tc004_root_endpoint_returns_api_info(self, skip_if_server_down):
        """TC004: Verify root endpoint returns API info"""
        response = requests.get(f"{BASE_URL}/", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "description" in data
        assert "endpoints" in data
    
    def test_tc005_root_includes_all_endpoints(self, skip_if_server_down):
        """TC005: Verify root endpoint includes all available endpoints"""
        response = requests.get(f"{BASE_URL}/", timeout=10)
        assert response.status_code == 200
        data = response.json()
        endpoints = data.get("endpoints", {})
        # Check for key endpoints
        assert "documentation" in endpoints or "health" in endpoints
        assert "erd" in endpoints or "nodegen" in endpoints or "agent" in endpoints or "prompt_analysis" in endpoints

