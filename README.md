# 🤖 CodeCraft - AI-Powered Backend Generator

**Crafting Tech Stacks from your Ideas**

CodeCraft is an intelligent AI agent that:
converts Entity-Relationship Diagrams (ERDs) into complete, production-ready Node.js backends using LangGraph and Gemini Flash AI.
analyses prompts and generates backend.
generates backend from an already developed frontend.

## ✨ Features

- **🧠 AI-Powered ERD Analysis**: Uses Gemini Flash Latest for intelligent ERD processing
- **🔄 LangGraph Workflow**: Multi-step reasoning with state management
- **⚡ Seamless Generation**: Upload ERD → Get complete backend automatically
- **📦 Intelligent Naming**: Automatically names backends based on domain (e.g., "sales_management_system")
- **🏗️ Production Ready**: Generates Express.js, Sequelize, TypeScript backends
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
Visit `http://localhost:8000/docs` to access the interactive API documentation.

### AI Agent Endpoints

#### 🤖 Upload ERD and Generate Backend
```bash
POST /agent/upload-erd
```
- Upload an ERD image
- Get complete Node.js backend automatically
- Download as intelligently named ZIP file

#### 📋 Process Schema
```bash
POST /agent/process-schema
```
- Process existing ERD schema
- Generate backend from JSON schema

#### 🔍 Agent Status
```bash
GET /agent/status
GET /agent/capabilities
```

## 🏗️ Generated Backend Features

Each generated backend includes:

- **Express.js** server with TypeScript
- **Sequelize** ORM with PostgreSQL support
- **RESTful API** routes for all entities
- **Database models** with relationships
- **Error handling** and validation
- **CORS** and security middleware
- **Development scripts** (npm run dev, build, start)
- **TypeScript configuration**
- **Package.json** with all dependencies

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

## 🔧 API Endpoints

### ERD Processing
- `POST /erd/upload-image` - Upload and process ERD image
- `POST /erd/process-base64` - Process base64 encoded image
- `POST /erd/convert-to-database-schema` - Convert to database schema
- `POST /erd/convert-to-fastapi-schema` - Convert to FastAPI schema

### Node.js Generation
- `POST /nodegen/generate` - Generate Node.js backend from schema
- `POST /nodegen/agent-generate` - AI agent backend generation

### AI Agent
- `POST /agent/upload-erd` - Seamless ERD to backend generation
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

