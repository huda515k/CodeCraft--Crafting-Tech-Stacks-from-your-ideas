# 🤖 CodeCraft - AI-Powered Backend Generator

**Crafting Tech Stacks from your Ideas**

CodeCraft is an intelligent AI agent that:
converts Entity-Relationship Diagrams (ERDs) into complete, production-ready Node.js backends using LangGraph and Gemini Flash AI.
analyses prompts and generates backend.
generates backend from an already developed frontend.

## ✨ Features

- **🧠 AI-Powered ERD Analysis**: Uses Gemini Flash Latest for intelligent ERD processing with robust error handling
- **🔄 LangGraph Workflow**: Multi-step reasoning with state management
- **⚡ Seamless Generation**: Upload ERD → Get complete backend automatically
- **📦 Intelligent Naming**: Automatically names backends based on domain (e.g., "sales_management_system")
- **🏗️ Production Ready**: Generates complete Express.js backends with:
  - **Controllers**: Full CRUD operations for each entity
  - **Middleware**: Authentication, validation, error handling, CORS, security
  - **Services**: Business logic layer with pagination and filtering
  - **Models**: Enhanced TypeScript models with proper relationships
  - **Routes**: RESTful API endpoints with proper HTTP methods
- **🔧 Enhanced ERD Processing**: Fixed foreign key reference issues and improved JSON parsing
- **🎯 Domain Detection**: Recognizes 15+ business domains (HR, E-commerce, Healthcare, etc.)

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- Node.js 18+ (for generated backends)
- Gemini API Key

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/huda515k/CodeCraft--Crafting-Tech-Stacks-from-your-ideas.git
cd CodeCraft--Crafting-Tech-Stacks-from-your-ideas
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment**
```bash
# Create .env file
echo "GEMINI_API_KEY=your_gemini_api_key_here" > .env
```

5. **Run the server**
```bash
uvicorn main:app --host 127.0.0.1 --port 8000
```

## 🎯 Usage

### Web Interface
The web-facing index and documentation are intentionally simplified to surface only the ERD processing and core generator flows. Visit `http://localhost:8000/docs` for the full API docs (internal), or use the endpoints below for the main UI flows.

### Exposed Endpoints (UI-focused)

#### ERD Processing
- `POST /erd/upload-image` - Upload ERD Image
- `POST /erd/validate-schema` - Validate ERD Schema
- `POST /erd/convert-to-database-schema` - Convert To Database Schema
- `POST /erd/convert-to-fastapi-schema` - Convert To FastAPI Schema
- `POST /erd/generate-comprehensive-schema` - Generate Comprehensive Schema
- `GET /erd/health` - Health Check

#### NodeJS Generator
- `POST /nodegen/advanced-upload-erd` - 🚀 AI-Powered Advanced Generator: Upload ERD Image

#### LangGraph AI Agent
- `POST /agent/upload-erd` - 🤖 Upload ERD and Generate Complete Backend
- `POST /agent/process-schema` - 🤖 Process ERD Schema and Generate Backend
- `GET /agent/capabilities` - 🤖 Get AI Agent Capabilities
- `GET /agent/status` - 🤖 Get AI Agent Status

#### Default
- `GET /` - Root
- `GET /health` - Health Check
- `POST /claude-documentation` - Claude Documentation

## 🏗️ Generated Backend Features

Each generated backend includes a complete, production-ready structure:

### 🎯 **Core Architecture**
- **Express.js** server with TypeScript
- **Sequelize** ORM with PostgreSQL support
- **RESTful API** routes for all entities
- **Database models** with proper relationships

### 🛡️ **Security & Middleware**
- **JWT Authentication** with secure token handling
- **Input Validation** using express-validator
- **CORS** and security headers (Helmet)
- **Error Handling** middleware with proper logging
- **Request Logging** (Morgan) and compression

### 🏢 **Business Logic**
- **Controllers** with full CRUD operations for each entity
- **Services** with pagination, filtering, and search
- **TypeScript Interfaces** for type safety
- **Model Relationships** properly defined

### 🚀 **Production Features**
- **Development scripts** (npm run dev, build, start)
- **TypeScript configuration** with strict settings
- **Package.json** with all dependencies
- **Health check endpoints**
- **Comprehensive documentation**

## 🧠 AI Agent Capabilities

### Domain Detection
The AI agent automatically detects business domains:

- **E-commerce**: product, order, customer, cart, payment
- **HR**: employee, department, salary, manager
- **Education**: student, course, teacher, class
- **Healthcare**: patient, doctor, appointment, medical
- **Banking**: account, transaction, loan, card
- **Real Estate**: property, house, rent, lease
- **Library**: book, member, borrow, author
- **Restaurant**: menu, order, table, reservation
- **Hotel**: room, guest, booking, service
- **Transport**: vehicle, route, ticket, passenger
- **Sales**: sales, lead, opportunity, deal
- **Inventory**: product, stock, warehouse, supplier
- **Social**: user, post, comment, friend
- **CRM**: contact, lead, opportunity, client

### Intelligent Naming
- **Sales ERD** → `sales_management_system_backend.zip`
- **HR ERD** → `hr_management_system_backend.zip`
- **E-commerce ERD** → `ecommerce_management_system_backend.zip`

## 🔧 API Endpoints (UI-focused)

### ERD Processing
- `POST /erd/upload-image` - Upload and process ERD image
- `POST /erd/validate-schema` - Validate ERD schema
- `POST /erd/convert-to-database-schema` - Convert to database schema
- `POST /erd/convert-to-fastapi-schema` - Convert to FastAPI schema
- `POST /erd/generate-comprehensive-schema` - Generate all schema outputs

### Node.js Generation
- `POST /nodegen/advanced-upload-erd` - Advanced ERD upload for AI-powered Node.js generator

### AI Agent
- `POST /agent/upload-erd` - ERD to backend generation
- `POST /agent/process-schema` - Process schema and generate backend
- `GET /agent/status` - Check agent status
- `GET /agent/capabilities` - View agent capabilities

## 🛠️ Technology Stack

### Backend Generator
- **FastAPI** - Modern Python web framework
- **LangGraph** - Multi-step AI workflows
- **LangChain** - AI application framework
- **Gemini Flash** - Google's latest AI model
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

### Generated Backends
- **Node.js** - JavaScript runtime
- **Express.js** - Web framework
- **TypeScript** - Type-safe JavaScript
- **Sequelize** - SQL ORM
- **PostgreSQL** - Database
- **CORS** - Cross-origin resource sharing

## 📁 Project Structure

```
CodeCraft/
├── backend_generator/
│   ├── ERD/                 # ERD processing module
│   │   ├── routes.py        # ERD API endpoints
│   │   ├── services.py      # ERD processing service
│   │   ├── erd_parser.py    # Gemini AI integration
│   │   ├── json_converter.py # Schema conversion
│   │   └── models.py        # Pydantic models
│   ├── NodeGen/             # Node.js generation module
│   │   ├── routes.py        # NodeGen API endpoints
│   │   └── generator.py     # Backend generation logic
│   └── Agent/               # AI Agent module
│       ├── routes.py        # Agent API endpoints
│       ├── langgraph_agent.py # LangGraph AI agent
│       └── tools.py         # Agent tools
├── main.py                  # FastAPI application
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🔧 Recent Improvements

### Enhanced Backend Generation
- ✅ **Complete Controller Layer**: Full CRUD operations for each entity
- ✅ **Comprehensive Middleware**: Authentication, validation, error handling, CORS, security
- ✅ **Service Layer**: Business logic with pagination, filtering, and search
- ✅ **Enhanced Models**: TypeScript interfaces with proper relationships
- ✅ **Production Security**: JWT authentication, input validation, security headers

### Fixed ERD Processing
- ✅ **Robust JSON Parsing**: Handles malformed AI responses gracefully
- ✅ **Correct Foreign Keys**: Fixed `composite_pk` reference issues
- ✅ **Better Error Handling**: Clear error messages and debugging information
- ✅ **Improved AI Prompts**: More specific instructions for accurate ERD interpretation

## 🚀 Deployment

### Local Development
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🙏 Acknowledgments

- **Google Gemini** for AI capabilities
- **LangGraph** for workflow management
- **FastAPI** for the web framework
- **Express.js** for generated backends

**Made by:**
Huda Nyazee
Rimsha Nisar
Hamza Tufail
=======
# CodeCraft--Crafting-Tech-Stacks-from-your-ideas
Final Year Project 

