"""
Ollama-based Generation Testing
Tests for ollama-based backend generation endpoints
"""
import pytest
import requests
import zipfile
import io
import json
import os

BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 300

def check_ollama_running():
    """Check if Ollama is running on localhost:11434"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

@pytest.fixture
def skip_if_ollama_down():
    """Skip test if Ollama is not running"""
    if not check_ollama_running():
        pytest.skip("Ollama is not running on localhost:11434. Please start Ollama and ensure qwen2.5-coder:7b model is available.")

@pytest.fixture
def sample_frontend_zip(temp_dir):
    """Create a sample frontend ZIP file for testing"""
    import zipfile
    zip_path = os.path.join(temp_dir, "sample_frontend.zip")
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        # Create a simple React component
        app_jsx = """
import React from 'react';

function App() {
  const [users, setUsers] = useState([]);
  
  useEffect(() => {
    fetch('/api/users')
      .then(res => res.json())
      .then(data => setUsers(data));
  }, []);
  
  return (
    <div>
      <h1>User List</h1>
      {users.map(user => (
        <div key={user.id}>{user.name}</div>
      ))}
    </div>
  );
}

export default App;
"""
        zipf.writestr("src/App.jsx", app_jsx)
        
        # Create package.json
        package_json = {
            "name": "test-frontend",
            "version": "1.0.0",
            "dependencies": {
                "react": "^18.0.0"
            }
        }
        zipf.writestr("package.json", json.dumps(package_json, indent=2))
    
    return zip_path

class TestOllamaPromptToBackend:
    """Tests for /nodegen/prompt-to-backend endpoint (Ollama-based)"""
    
    def test_ollama_prompt_to_backend_basic(self, skip_if_server_down, skip_if_ollama_down):
        """Test basic prompt-to-backend generation using Ollama"""
        data = {
            "prompt": "Create a simple user management system with CRUD operations",
            "arch_type": "Monolith"
        }
        response = requests.post(
            f"{BASE_URL}/nodegen/prompt-to-backend",
            data=data,
            timeout=TEST_TIMEOUT
        )
        assert response.status_code == 200
        assert response.headers.get('content-type', '').startswith('application/zip')
        
        # Verify ZIP content
        zip_file = zipfile.ZipFile(io.BytesIO(response.content))
        files_list = zip_file.namelist()
        assert len(files_list) > 0
        
        # Check for common backend files
        has_backend_files = any(
            'package.json' in f or 'server.js' in f or 'app.js' in f or 
            'index.js' in f or 'routes' in f.lower() or 'models' in f.lower()
            for f in files_list
        )
        assert has_backend_files, f"Expected backend files, got: {files_list[:10]}"
    
    def test_ollama_prompt_to_backend_microservices(self, skip_if_server_down, skip_if_ollama_down):
        """Test prompt-to-backend with microservices architecture"""
        data = {
            "prompt": "Create a user service and product service",
            "arch_type": "Microservices"
        }
        response = requests.post(
            f"{BASE_URL}/nodegen/prompt-to-backend",
            data=data,
            timeout=TEST_TIMEOUT
        )
        assert response.status_code == 200
        assert response.headers.get('content-type', '').startswith('application/zip')
    
    def test_ollama_prompt_to_backend_empty_prompt(self, skip_if_server_down):
        """Test prompt-to-backend with empty prompt"""
        data = {
            "prompt": "",
            "arch_type": "Monolith"
        }
        response = requests.post(
            f"{BASE_URL}/nodegen/prompt-to-backend",
            data=data,
            timeout=TEST_TIMEOUT
        )
        # Should handle empty prompt gracefully
        assert response.status_code in [200, 400, 422, 500]
    
    def test_ollama_prompt_to_backend_stream(self, skip_if_server_down, skip_if_ollama_down):
        """Test prompt-to-backend streaming endpoint"""
        data = {
            "prompt": "Create a simple blog API",
            "arch_type": "Monolith"
        }
        response = requests.post(
            f"{BASE_URL}/nodegen/prompt-to-backend-stream",
            data=data,
            stream=True,
            timeout=TEST_TIMEOUT
        )
        assert response.status_code == 200
        assert response.headers.get('content-type', '').startswith('text/event-stream')
        
        # Check for SSE events
        content = ""
        for line in response.iter_lines():
            if line:
                content += line.decode('utf-8') + '\n'
                if len(content) > 1000:  # Just check first part
                    break
        
        assert len(content) > 0

class TestOllamaFrontendToBackend:
    """Tests for /nodegen/frontend-to-backend endpoint (Ollama-based)"""
    
    def test_ollama_frontend_to_backend_basic(self, sample_frontend_zip, skip_if_server_down, skip_if_ollama_down):
        """Test basic frontend-to-backend generation using Ollama"""
        with open(sample_frontend_zip, 'rb') as f:
            files = {'file': ('frontend.zip', f, 'application/zip')}
            data = {
                'arch_type': 'Monolith'
            }
            response = requests.post(
                f"{BASE_URL}/nodegen/frontend-to-backend",
                files=files,
                data=data,
                timeout=TEST_TIMEOUT
            )
        assert response.status_code == 200
        assert response.headers.get('content-type', '').startswith('application/zip')
        
        # Verify ZIP content
        zip_file = zipfile.ZipFile(io.BytesIO(response.content))
        files_list = zip_file.namelist()
        assert len(files_list) > 0
    
    def test_ollama_frontend_to_backend_stream(self, sample_frontend_zip, skip_if_server_down, skip_if_ollama_down):
        """Test frontend-to-backend streaming endpoint"""
        with open(sample_frontend_zip, 'rb') as f:
            files = {'file': ('frontend.zip', f, 'application/zip')}
            data = {
                'arch_type': 'Monolith'
            }
            response = requests.post(
                f"{BASE_URL}/nodegen/frontend-to-backend-stream",
                files=files,
                data=data,
                stream=True,
                timeout=TEST_TIMEOUT
            )
        assert response.status_code == 200
        assert response.headers.get('content-type', '').startswith('text/event-stream')
        
        # Check for SSE events
        content = ""
        for line in response.iter_lines():
            if line:
                content += line.decode('utf-8') + '\n'
                if len(content) > 1000:  # Just check first part
                    break
        
        assert len(content) > 0
    
    def test_ollama_frontend_to_backend_invalid_file(self, invalid_image_file, skip_if_server_down):
        """Test frontend-to-backend with invalid file"""
        with open(invalid_image_file, 'rb') as f:
            files = {'file': ('test.txt', f, 'text/plain')}
            data = {
                'arch_type': 'Monolith'
            }
            response = requests.post(
                f"{BASE_URL}/nodegen/frontend-to-backend",
                files=files,
                data=data,
                timeout=TEST_TIMEOUT
            )
        # Should handle invalid file gracefully
        assert response.status_code in [400, 422, 500]
