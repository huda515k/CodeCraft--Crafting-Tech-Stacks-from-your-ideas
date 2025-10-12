"""
Test script for the Documentation Agent
"""
import requests
import os
from pathlib import Path
import zipfile
import json


def create_sample_backend():
    """Create a sample Express backend for testing"""
    sample_backend = Path("sample_backend")
    sample_backend.mkdir(exist_ok=True)
    
    # Create sample app.js
    app_js = """
const express = require('express');
const app = express();
const userRoutes = require('./routes/userRoutes');
const authMiddleware = require('./middlewares/auth');

app.use(express.json());
app.use('/api/users', authMiddleware, userRoutes);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});

module.exports = app;
    """
    
    with open(sample_backend / "app.js", "w") as f:
        f.write(app_js)
    
    # Create routes directory
    routes_dir = sample_backend / "routes"
    routes_dir.mkdir(exist_ok=True)
    
    user_routes = """
const express = require('express');
const router = express.Router();
const userController = require('../controllers/userController');

// Get all users
router.get('/', userController.getAllUsers);

// Get user by ID
router.get('/:id', userController.getUserById);

// Create new user
router.post('/', userController.createUser);

// Update user
router.put('/:id', userController.updateUser);

// Delete user
router.delete('/:id', userController.deleteUser);

module.exports = router;
    """
    
    with open(routes_dir / "userRoutes.js", "w") as f:
        f.write(user_routes)
    
    # Create controllers directory
    controllers_dir = sample_backend / "controllers"
    controllers_dir.mkdir(exist_ok=True)
    
    user_controller = """
const User = require('../models/User');

exports.getAllUsers = async (req, res) => {
    try {
        const { page = 1, limit = 10 } = req.query;
        const users = await User.find()
            .limit(limit * 1)
            .skip((page - 1) * limit);
        
        const count = await User.countDocuments();
        
        res.json({
            users,
            totalPages: Math.ceil(count / limit),
            currentPage: page
        });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

exports.getUserById = async (req, res) => {
    try {
        const user = await User.findById(req.params.id);
        if (!user) return res.status(404).json({ message: 'User not found' });
        res.json(user);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

exports.createUser = async (req, res) => {
    try {
        const { email, name, password } = req.body;
        const user = new User({ email, name, password });
        await user.save();
        res.status(201).json(user);
    } catch (error) {
        res.status(400).json({ message: error.message });
    }
};

exports.updateUser = async (req, res) => {
    try {
        const user = await User.findByIdAndUpdate(req.params.id, req.body, { new: true });
        if (!user) return res.status(404).json({ message: 'User not found' });
        res.json(user);
    } catch (error) {
        res.status(400).json({ message: error.message });
    }
};

exports.deleteUser = async (req, res) => {
    try {
        const user = await User.findByIdAndDelete(req.params.id);
        if (!user) return res.status(404).json({ message: 'User not found' });
        res.json({ message: 'User deleted successfully' });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};
    """
    
    with open(controllers_dir / "userController.js", "w") as f:
        f.write(user_controller)
    
    # Create models directory
    models_dir = sample_backend / "models"
    models_dir.mkdir(exist_ok=True)
    
    user_model = """
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

const userSchema = new mongoose.Schema({
    email: {
        type: String,
        required: true,
        unique: true,
        lowercase: true,
        trim: true
    },
    name: {
        type: String,
        required: true,
        trim: true
    },
    password: {
        type: String,
        required: true,
        minlength: 6
    },
    role: {
        type: String,
        enum: ['user', 'admin'],
        default: 'user'
    },
    createdAt: {
        type: Date,
        default: Date.now
    }
});

// Hash password before saving
userSchema.pre('save', async function(next) {
    if (!this.isModified('password')) return next();
    this.password = await bcrypt.hash(this.password, 10);
    next();
});

module.exports = mongoose.model('User', userSchema);
    """
    
    with open(models_dir / "User.js", "w") as f:
        f.write(user_model)
    
    # Create middlewares directory
    middlewares_dir = sample_backend / "middlewares"
    middlewares_dir.mkdir(exist_ok=True)
    
    auth_middleware = """
const jwt = require('jsonwebtoken');

module.exports = (req, res, next) => {
    try {
        const token = req.header('Authorization').replace('Bearer ', '');
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        req.user = decoded;
        next();
    } catch (error) {
        res.status(401).json({ message: 'Authentication required' });
    }
};
    """
    
    with open(middlewares_dir / "auth.js", "w") as f:
        f.write(auth_middleware)
    
    # Create package.json
    package_json = {
        "name": "sample-backend",
        "version": "1.0.0",
        "main": "app.js",
        "dependencies": {
            "express": "^4.18.0",
            "mongoose": "^7.0.0",
            "bcryptjs": "^2.4.3",
            "jsonwebtoken": "^9.0.0"
        }
    }
    
    with open(sample_backend / "package.json", "w") as f:
        json.dump(package_json, f, indent=2)
    
    # Create ZIP file
    zip_path = "sample_backend.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in sample_backend.rglob('*'):
            if file_path.is_file():
                zipf.write(file_path, file_path.relative_to(sample_backend.parent))
    
    print(f"✅ Sample backend created: {zip_path}")
    return zip_path


def test_documentation_agent(api_url="http://127.0.0.1:8000"):
    """Test the documentation agent"""
    print("\n" + "="*60)
    print("Testing CodeCraft Documentation Agent")
    print("="*60 + "\n")
    
    # Test 1: Health check
    print("Test 1: Health Check")
    try:
        response = requests.get(f"{api_url}/health")
        if response.status_code == 200:
            print("✅ API is healthy")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Could not connect to API: {e}")
        print(f"   Make sure the API is running at {api_url}")
        return
    
    print("\n" + "-"*60 + "\n")
    
    # Test 2: Create sample backend
    print("Test 2: Creating Sample Backend")
    zip_path = create_sample_backend()
    
    print("\n" + "-"*60 + "\n")
    
    # Test 3: Analyze backend using claude-documentation endpoint
    print("Test 3: Analyzing Backend (claude-documentation endpoint)")
    try:
        with open(zip_path, 'rb') as f:
            files = {'file': (zip_path, f, 'application/zip')}
            response = requests.post(f"{api_url}/claude-documentation", files=files)
        
        if response.status_code == 200:
            print("✅ Analysis successful")
            docs = response.json()
            
            print(f"\n📊 Documentation Summary:")
            if 'metadata' in docs:
                meta = docs['metadata']
                print(f"   • Total Routes: {meta.get('total_routes', 0)}")
                print(f"   • Total Models: {meta.get('total_models', 0)}")
                print(f"   • Total Controllers: {meta.get('total_controllers', 0)}")
                print(f"   • Total Middlewares: {meta.get('total_middlewares', 0)}")
            
            if 'routes' in docs and docs['routes']:
                print(f"\n📝 Detected Routes:")
                for route in docs['routes'][:3]:  # Show first 3
                    method = route.get('method', 'GET')
                    path = route.get('path', '/')
                    print(f"   • {method} {path}")
            
            # Save JSON documentation
            with open("api_documentation.json", "w") as f:
                json.dump(docs, f, indent=2)
            print(f"\n💾 Saved: api_documentation.json")
            
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
    
    print("\n" + "-"*60 + "\n")
    
    # Test 4: Analyze backend (Download ZIP)
    print("Test 4: Analyzing Backend (Download ZIP)")
    try:
        with open(zip_path, 'rb') as f:
            files = {'file': (zip_path, f, 'application/zip')}
            response = requests.post(f"{api_url}/analyze-backend", files=files)
        
        if response.status_code == 200:
            print("✅ Analysis successful")
            
            # Save the ZIP file
            output_zip = "api_documentation.zip"
            with open(output_zip, 'wb') as f:
                f.write(response.content)
            print(f"💾 Saved: {output_zip}")
            
            # Extract and show contents
            with zipfile.ZipFile(output_zip, 'r') as zip_ref:
                print(f"\n📦 Documentation Package Contents:")
                for file_info in zip_ref.filelist:
                    print(f"   • {file_info.filename} ({file_info.file_size} bytes)")
                
                # Extract files
                zip_ref.extractall("documentation_output")
                print(f"\n📂 Extracted to: documentation_output/")
            
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
    
    print("\n" + "="*60)
    print("Testing Complete!")
    print("="*60 + "\n")
    
    print("Generated Files:")
    print("  • sample_backend.zip - Sample backend for testing")
    print("  • api_documentation.zip - Complete documentation package")
    print("  • documentation_output/ - Extracted documentation files")
    print("\nYou can now:")
    print("  1. Review the generated documentation")
    print("  2. Import openapi.yaml into Swagger UI")
    print("  3. Use api_documentation.json in your frontend agent")
    print("\nAPI Documentation available at:")
    print(f"  • Swagger UI: {api_url}/docs")
    print(f"  • ReDoc: {api_url}/redoc")


if __name__ == "__main__":
    import sys
    
    # Get API URL from command line or use default
    api_url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
    
    test_documentation_agent(api_url)