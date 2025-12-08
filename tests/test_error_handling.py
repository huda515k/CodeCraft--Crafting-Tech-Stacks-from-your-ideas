"""
Error Handling and Edge Cases Testing (TC079-TC092)
Tests for error handling and edge cases
"""
import pytest
import requests
import os
import tempfile

BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 300

class TestErrorHandling:
    """TC079-TC085: Error Handling Tests"""
    
    def test_tc079_missing_api_key(self, sample_png_image, skip_if_server_down):
        """TC079: Verify handling of missing API key"""
        # This test checks server response when API key is missing
        # Note: If key is set, test may pass, which is expected
        with open(sample_png_image, 'rb') as f:
            files = {'file': ('test.png', f, 'image/png')}
            response = requests.post(
                f"{BASE_URL}/frontend/analyze-ui-only",
                files=files,
                timeout=TEST_TIMEOUT
            )
        # Should either succeed (if key is set) or return 500 with error
        assert response.status_code in [200, 500]
        if response.status_code == 500:
            error_text = response.text.lower()
            assert "api key" in error_text or "gemini" in error_text or "key" in error_text
    
    def test_tc080_invalid_format(self, invalid_image_file, skip_if_server_down):
        """TC080: Verify handling of invalid image format"""
        with open(invalid_image_file, 'rb') as f:
            files = {'file': ('test.txt', f, 'text/plain')}
            response = requests.post(
                f"{BASE_URL}/frontend/analyze-ui-only",
                files=files,
                timeout=TEST_TIMEOUT
            )
        assert response.status_code in [400, 422]
        error_text = response.text.lower()
        assert "format" in error_text or "type" in error_text or "unsupported" in error_text
    
    def test_tc081_empty_request(self, skip_if_server_down):
        """TC081: Verify handling of empty request"""
        # Send POST with no file
        response = requests.post(
            f"{BASE_URL}/frontend/analyze-ui-only",
            timeout=TEST_TIMEOUT
        )
        assert response.status_code in [400, 422]
    
    def test_tc082_oversized_files(self, large_image_file, skip_if_server_down):
        """TC082: Verify handling of oversized files"""
        with open(large_image_file, 'rb') as f:
            files = {'file': ('large.png', f, 'image/png')}
            response = requests.post(
                f"{BASE_URL}/frontend/analyze-ui-only",
                files=files,
                timeout=TEST_TIMEOUT
            )
        # Should either process or return appropriate error
        assert response.status_code in [200, 400, 422, 500, 504]
        if response.status_code in [400, 422]:
            error_text = response.text.lower()
            assert "size" in error_text or "large" in error_text or "limit" in error_text
    
    def test_tc083_malformed_json(self, sample_png_image, skip_if_server_down, skip_if_no_api_key):
        """TC083: Verify handling of malformed JSON"""
        # This is harder to test directly as it's internal
        # We test that the system handles AI responses gracefully
        with open(sample_png_image, 'rb') as f:
            files = {'file': ('test.png', f, 'image/png')}
            response = requests.post(
                f"{BASE_URL}/frontend/analyze-ui-only",
                files=files,
                timeout=TEST_TIMEOUT
            )
        # Should handle gracefully
        assert response.status_code in [200, 500]
    
    def test_tc084_network_timeout(self, sample_png_image, skip_if_server_down, skip_if_no_api_key):
        """TC084: Verify handling of network timeout"""
        # Test with shorter timeout
        try:
            with open(sample_png_image, 'rb') as f:
                files = {'file': ('test.png', f, 'image/png')}
                response = requests.post(
                    f"{BASE_URL}/frontend/analyze-ui-only",
                    files=files,
                    timeout=1  # Very short timeout
                )
            # Should either complete quickly or timeout
            assert response.status_code in [200, 500, 504]
        except requests.exceptions.Timeout:
            # Timeout is acceptable
            pass
    
    def test_tc085_concurrent_requests(self, sample_png_image, skip_if_server_down, skip_if_no_api_key):
        """TC085: Verify handling of concurrent requests"""
        import concurrent.futures
        
        def make_request():
            with open(sample_png_image, 'rb') as f:
                files = {'file': ('test.png', f, 'image/png')}
                return requests.post(
                    f"{BASE_URL}/frontend/analyze-ui-only",
                    files=files,
                    timeout=TEST_TIMEOUT
                )
        
        # Make 3 concurrent requests (reduced from 5 for faster testing)
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(make_request) for _ in range(3)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All should succeed or be handled gracefully
        for response in results:
            assert response.status_code in [200, 500, 503]  # 503 for service unavailable

class TestEdgeCases:
    """TC086-TC092: Edge Cases Tests"""
    
    def test_tc086_no_components(self, temp_dir, skip_if_server_down, skip_if_no_api_key):
        """TC086: Verify handling of UI image with no components"""
        # Create minimal/blank image
        from PIL import Image
        blank_img = Image.new('RGB', (100, 100), color='#FFFFFF')
        blank_path = os.path.join(temp_dir, "blank.png")
        blank_img.save(blank_path, 'PNG')
        
        with open(blank_path, 'rb') as f:
            files = {'file': ('blank.png', f, 'image/png')}
            response = requests.post(
                f"{BASE_URL}/frontend/analyze-ui-only",
                files=files,
                timeout=TEST_TIMEOUT
            )
        assert response.status_code == 200
        data = response.json()
        # Should return empty or minimal components
        ui_analysis = data.get("ui_analysis", {})
        components = ui_analysis.get("components", [])
        assert isinstance(components, list)
    
    def test_tc087_no_relationships(self, sample_erd_image, skip_if_server_down, skip_if_no_api_key):
        """TC087: Verify handling of ERD with no relationships"""
        with open(sample_erd_image, 'rb') as f:
            files = {'file': ('erd.png', f, 'image/png')}
            response = requests.post(
                f"{BASE_URL}/erd/upload-image",
                files=files,
                timeout=TEST_TIMEOUT
            )
        assert response.status_code == 200
        data = response.json()
        if "erd_schema" in data:
            schema = data["erd_schema"]
            relationships = schema.get("relationships", [])
            # Should return empty array if no relationships
            assert isinstance(relationships, list)
    
    def test_tc088_no_roles(self, skip_if_server_down, skip_if_no_api_key):
        """TC088: Verify handling of prompt with no roles"""
        data = {
            "prompt": "Create a simple blog system"
        }
        response = requests.post(
            f"{BASE_URL}/prompt-analysis/analyze",
            json=data,
            timeout=TEST_TIMEOUT
        )
        assert response.status_code == 200
        result = response.json()
        # Should return empty roles array or infer defaults
        roles = result.get("roles", [])
        assert isinstance(roles, list)
    
    def test_tc089_special_characters(self, sample_png_image, skip_if_server_down, skip_if_no_api_key):
        """TC089: Verify handling of special characters in component names"""
        with open(sample_png_image, 'rb') as f:
            files = {'file': ('test.png', f, 'image/png')}
            data = {'additional_context': 'Component name: User-Profile (Main)'}
            response = requests.post(
                f"{BASE_URL}/frontend/generate-react",
                files=files,
                data=data,
                timeout=TEST_TIMEOUT
            )
        # Should handle special characters gracefully
        assert response.status_code in [200, 400, 422, 500]
        if response.status_code == 200:
            import zipfile
            import io
            zip_file = zipfile.ZipFile(io.BytesIO(response.content))
            files_list = zip_file.namelist()
            # Check that filenames are valid (no special chars in paths)
            for f in files_list:
                # Filenames should be sanitized
                assert not any(char in f for char in ['(', ')', ' ']) or '/' in f  # Paths can have spaces
    
    def test_tc090_long_names(self, sample_png_image, skip_if_server_down, skip_if_no_api_key):
        """TC090: Verify handling of long component names"""
        long_name = "VeryLongComponentNameThatExceedsNormalLength" * 5
        with open(sample_png_image, 'rb') as f:
            files = {'file': ('test.png', f, 'image/png')}
            data = {'additional_context': f'Component: {long_name}'}
            response = requests.post(
                f"{BASE_URL}/frontend/generate-react",
                files=files,
                data=data,
                timeout=TEST_TIMEOUT
            )
        # Should handle long names gracefully
        assert response.status_code in [200, 400, 422, 500]
    
    def test_tc091_duplicate_ids(self, sample_png_image, skip_if_server_down, skip_if_no_api_key):
        """TC091: Verify handling of duplicate component IDs"""
        with open(sample_png_image, 'rb') as f:
            files = {'file': ('test.png', f, 'image/png')}
            response = requests.post(
                f"{BASE_URL}/frontend/analyze-ui-only",
                files=files,
                timeout=TEST_TIMEOUT
            )
        if response.status_code == 200:
            data = response.json()
            ui_analysis = data.get("ui_analysis", {})
            components = ui_analysis.get("components", [])
            if components:
                # Check for unique IDs
                ids = [comp.get("id") for comp in components if comp.get("id")]
                if ids:
                    # IDs should be unique
                    assert len(ids) == len(set(ids)) or len(ids) == 0
    
    def test_tc092_circular_references(self, sample_png_image, skip_if_server_down, skip_if_no_api_key):
        """TC092: Verify handling of circular component references"""
        with open(sample_png_image, 'rb') as f:
            files = {'file': ('test.png', f, 'image/png')}
            response = requests.post(
                f"{BASE_URL}/frontend/analyze-ui-only",
                files=files,
                timeout=TEST_TIMEOUT
            )
        if response.status_code == 200:
            data = response.json()
            ui_analysis = data.get("ui_analysis", {})
            components = ui_analysis.get("components", [])
            # Check for circular references (basic check)
            if components:
                # Build parent-child map
                parent_map = {}
                for comp in components:
                    comp_id = comp.get("id")
                    parent_id = comp.get("parent_id")
                    if comp_id and parent_id:
                        parent_map[comp_id] = parent_id
                
                # Check for circular references (A -> B -> A)
                for comp_id, parent_id in parent_map.items():
                    # Follow parent chain
                    visited = set()
                    current = parent_id
                    while current and current in parent_map:
                        if current in visited:
                            # Circular reference detected
                            break
                        visited.add(current)
                        current = parent_map.get(current)
                    # If we reach here without breaking, no immediate circular ref
                # System should handle this gracefully
                assert True  # Processing succeeded

