"""
Pytest configuration and shared fixtures for all tests
"""
import pytest
import os
import sys
import tempfile
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import zipfile
import io

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 300  # 5 minutes for AI operations

@pytest.fixture(scope="session")
def base_url():
    """Base URL for API testing"""
    return BASE_URL

@pytest.fixture(scope="session")
def test_timeout():
    """Timeout for test operations"""
    return TEST_TIMEOUT

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    temp_path = tempfile.mkdtemp(prefix="codecraft_test_")
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)

@pytest.fixture
def sample_png_image(temp_dir):
    """Create a sample PNG image for testing"""
    img_path = os.path.join(temp_dir, "test_image.png")
    img = Image.new('RGB', (400, 600), color='#00CED1')  # Teal background
    draw = ImageDraw.Draw(img)
    
    # Draw some UI elements
    # Header
    draw.rectangle([0, 0, 400, 100], fill='#00CED1')
    draw.rectangle([0, 100, 400, 200], fill='#FFFFFF')
    
    # Button
    draw.rectangle([50, 250, 350, 300], fill='#FFD700', outline='#000000', width=2)
    
    # Input field
    draw.rectangle([50, 350, 350, 400], fill='#FFFFFF', outline='#000000', width=2)
    
    # Card
    draw.rectangle([50, 450, 350, 550], fill='#FFFFFF', outline='#00CED1', width=2)
    
    img.save(img_path, 'PNG')
    return img_path

@pytest.fixture
def sample_erd_image(temp_dir):
    """Create a sample ERD image for testing"""
    img_path = os.path.join(temp_dir, "test_erd.png")
    img = Image.new('RGB', (800, 600), color='#FFFFFF')
    draw = ImageDraw.Draw(img)
    
    # Draw entities
    # User entity
    draw.rectangle([50, 50, 250, 200], outline='#000000', width=2)
    draw.text((150, 70), "User", fill='#000000', anchor='mm')
    draw.line([50, 100, 250, 100], fill='#000000', width=1)
    draw.text((60, 120), "id: INTEGER (PK)", fill='#000000')
    draw.text((60, 140), "name: STRING", fill='#000000')
    draw.text((60, 160), "email: STRING", fill='#000000')
    
    # Product entity
    draw.rectangle([400, 50, 600, 200], outline='#000000', width=2)
    draw.text((500, 70), "Product", fill='#000000', anchor='mm')
    draw.line([400, 100, 600, 100], fill='#000000', width=1)
    draw.text((410, 120), "id: INTEGER (PK)", fill='#000000')
    draw.text((410, 140), "name: STRING", fill='#000000')
    draw.text((410, 160), "price: FLOAT", fill='#000000')
    
    # Order entity
    draw.rectangle([225, 300, 425, 450], outline='#000000', width=2)
    draw.text((325, 320), "Order", fill='#000000', anchor='mm')
    draw.line([225, 350, 425, 350], fill='#000000', width=1)
    draw.text((235, 370), "id: INTEGER (PK)", fill='#000000')
    draw.text((235, 390), "user_id: INTEGER (FK)", fill='#000000')
    draw.text((235, 410), "product_id: INTEGER (FK)", fill='#000000')
    
    # Relationships
    draw.line([150, 200, 325, 300], fill='#000000', width=2)  # User to Order
    draw.line([500, 200, 325, 300], fill='#000000', width=2)  # Product to Order
    
    img.save(img_path, 'PNG')
    return img_path

@pytest.fixture
def invalid_image_file(temp_dir):
    """Create an invalid image file (text file)"""
    file_path = os.path.join(temp_dir, "test.txt")
    with open(file_path, 'w') as f:
        f.write("This is not an image file")
    return file_path

@pytest.fixture
def corrupted_image_file(temp_dir):
    """Create a corrupted image file"""
    file_path = os.path.join(temp_dir, "corrupted.png")
    with open(file_path, 'wb') as f:
        f.write(b"PNG\x00\x00\x00\x00INVALID_DATA")
    return file_path

@pytest.fixture
def large_image_file(temp_dir):
    """Create a large image file (>10MB)"""
    img_path = os.path.join(temp_dir, "large_image.png")
    # Create a large image (2000x2000)
    img = Image.new('RGB', (2000, 2000), color='#FFFFFF')
    img.save(img_path, 'PNG')
    return img_path

@pytest.fixture
def sample_backend_zip(temp_dir):
    """Create a sample backend ZIP file for testing"""
    zip_path = os.path.join(temp_dir, "sample_backend.zip")
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        # Create package.json
        package_json = {
            "name": "test-backend",
            "version": "1.0.0",
            "dependencies": {
                "express": "^4.18.0",
                "sequelize": "^6.0.0"
            }
        }
        import json
        zipf.writestr("package.json", json.dumps(package_json, indent=2))
        
        # Create a simple server.js
        server_js = """
const express = require('express');
const app = express();
app.get('/api/users', (req, res) => res.json([]));
app.listen(3000);
"""
        zipf.writestr("server.js", server_js)
    
    return zip_path

@pytest.fixture
def check_server_running():
    """Check if server is running"""
    import requests
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

@pytest.fixture
def check_gemini_cli():
    """Check if Gemini CLI is installed and available"""
    import subprocess
    try:
        # Try both 'gemini' and 'gemini-cli' commands
        for cmd in ["gemini", "gemini-cli"]:
            try:
                result = subprocess.run(
                    [cmd, "--version"],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return True
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
        return False
    except Exception:
        return False

@pytest.fixture
def skip_if_no_api_key(check_gemini_cli):
    """Skip test if Gemini CLI is not available (backward compatibility)"""
    if not check_gemini_cli:
        pytest.skip("Gemini CLI not available. Install with: npm install -g @google/generative-ai-cli && gemini-cli auth login")

@pytest.fixture
def skip_if_no_gemini_cli(check_gemini_cli):
    """Skip test if Gemini CLI is not available"""
    if not check_gemini_cli:
        pytest.skip("Gemini CLI not available. Install with: npm install -g @google/generative-ai-cli && gemini-cli auth login")

@pytest.fixture
def skip_if_server_down(check_server_running):
    """Skip test if server is not running"""
    if not check_server_running:
        pytest.skip("Server is not running on localhost:8000")

