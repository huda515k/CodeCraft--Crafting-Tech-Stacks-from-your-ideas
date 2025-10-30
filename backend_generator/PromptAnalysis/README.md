# Prompt Analysis Module

The Prompt Analysis module provides AI-powered analysis of user prompts to extract role-based access control and business rules for Node.js backend generation.

## Features

- **Role Extraction**: Automatically extract user roles and permissions from natural language prompts
- **Business Rules Parsing**: Identify and parse business rules and constraints
- **Authorization Code Generation**: Generate complete Node.js authorization middleware and models
- **Backend Modification**: Modify existing backends with new roles and rules
- **Security Suggestions**: Get AI-powered security improvement recommendations

## API Endpoints

### Core Analysis

- `POST /prompt-analysis/analyze` - Analyze user prompt for roles and business rules
- `POST /prompt-analysis/quick-analysis` - Quick analysis without full code generation
- `POST /prompt-analysis/analyze-with-erd` - Analyze prompt in context of ERD schema

### Backend Modification

- `POST /prompt-analysis/modify-backend` - Modify existing backend based on prompt
- `POST /prompt-analysis/generate-authorization-code` - Generate complete authorization code

### Validation & Analysis

- `POST /prompt-analysis/validate` - Validate extracted roles and business rules
- `POST /prompt-analysis/generate-hierarchy` - Generate role hierarchy
- `POST /prompt-analysis/generate-permission-matrix` - Generate permission matrix
- `POST /prompt-analysis/security-suggestions` - Get security improvement suggestions

### Health Check

- `GET /prompt-analysis/health` - Service health check

## Usage Examples

### 1. Basic Prompt Analysis

```python
import requests

# Analyze a prompt for roles and business rules
response = requests.post("http://localhost:8000/prompt-analysis/analyze", json={
    "prompt": """
    Create a system where:
    - Admin users can manage all data and users
    - Manager users can read and update employee data
    - Employee users can only read their own data
    - Customers can only view products and place orders
    - Validate that orders must have a valid customer
    - Ensure employees cannot access customer financial data
    """
})

result = response.json()
print(f"Found {result['roles_found']} roles and {result['rules_found']} business rules")
```

### 2. ERD Integration

```python
# Process ERD with role-based access control
response = requests.post("http://localhost:8000/erd/process-with-prompt", 
    files={"file": open("erd_image.png", "rb")},
    data={
        "role_prompt": """
        Admin role: full access to all entities
        Manager role: can read and update employee and department data
        Employee role: can only read their own employee record
        Customer role: can read products and create orders
        Business rules:
        - Orders must have valid customer
        - Employees cannot modify salary data
        - Only managers can approve leave requests
        """
    }
)
```

### 3. Backend Modification

```python
# Modify existing backend with new roles
response = requests.post("http://localhost:8000/prompt-analysis/modify-backend", json={
    "backend_code": "existing_backend_code_here",
    "modification_prompt": """
    Add a new role called 'Supervisor' that can:
    - Read all employee data
    - Update employee schedules
    - Approve time-off requests
    Add business rule: Supervisors cannot modify employee salaries
    """,
    "current_roles": [
        {"name": "Admin", "permissions": ["read", "write", "update", "delete", "admin"]},
        {"name": "Employee", "permissions": ["read"]}
    ]
})
```

## Generated Code Structure

The module generates the following Node.js files:

### 1. Authentication Middleware (`middleware/auth.js`)
- JWT token validation
- Role-based access control
- Permission checking
- User context injection

### 2. Database Models (`models/authorization.js`)
- Role schema with permissions
- User schema with role assignments
- Business rule schema
- Mongoose models for MongoDB

### 3. Authorization Routes (`routes/authorization.js`)
- Role management endpoints
- Business rule management
- Permission checking endpoints

### 4. Business Rule Engine (`services/businessRuleEngine.js`)
- Rule evaluation engine
- Context-based rule execution
- Rule priority handling

### 5. Role Service (`services/roleService.js`)
- Role assignment logic
- Permission checking
- User role management

## Role Types

The module recognizes these permission types:
- `read` - Read access to data
- `write` - Create new records
- `update` - Modify existing records
- `delete` - Remove records
- `admin` - Administrative access
- `manage` - Management permissions

## Business Rule Types

- `validation` - Data validation rules
- `authorization` - Access control rules
- `workflow` - Process workflow rules
- `data_integrity` - Data consistency rules
- `business_logic` - Business logic rules
- `audit` - Audit and logging rules

## Integration with ERD Module

The prompt analysis module integrates seamlessly with the ERD module:

1. **Upload ERD with Prompt**: Use `/erd/process-with-prompt` to upload an ERD image with role-based access control prompts
2. **Automatic Analysis**: The system automatically analyzes the prompt and extracts roles and business rules
3. **Code Generation**: Generates authorization code that works with the ERD entities
4. **Entity-Specific Access**: Maps roles to specific ERD entities with appropriate permissions

## Security Features

- **Role Hierarchy**: Automatic role hierarchy generation
- **Permission Matrix**: Visual permission matrix for all roles
- **Security Suggestions**: AI-powered security recommendations
- **Validation**: Comprehensive validation of roles and rules
- **Audit Logging**: Built-in audit trail for authorization decisions

## Example Prompts

### E-commerce System
```
Admin: full access to all data
Manager: can manage products and orders
Employee: can process orders and update inventory
Customer: can view products and place orders
Business rules:
- Orders must have valid customer
- Inventory cannot go below zero
- Only managers can modify product prices
```

### HR Management System
```
HR Admin: full access to all employee data
Manager: can view and update team member data
Employee: can view own data and submit requests
Business rules:
- Salary data is confidential to HR only
- Managers cannot modify salaries
- Employees cannot view other employees' personal data
```

### Project Management System
```
Project Manager: full access to project data
Team Lead: can manage team tasks and updates
Developer: can update task status and add comments
Client: can view project progress and add feedback
Business rules:
- Only project managers can create new projects
- Developers cannot modify project budgets
- Clients can only view their own project data
```

## Error Handling

The module provides comprehensive error handling:
- Invalid prompt format detection
- Role validation errors
- Business rule syntax errors
- Code generation failures
- Integration errors with ERD module

## Performance Considerations

- **Lazy Loading**: Services are loaded only when needed
- **Caching**: Role and rule definitions are cached for performance
- **Async Processing**: All operations are asynchronous
- **Batch Processing**: Multiple roles and rules are processed in batches

## Dependencies

- FastAPI for API endpoints
- Pydantic for data validation
- Regular expressions for prompt parsing
- JSON for data serialization
- MongoDB/Mongoose for data persistence (generated code)

## Future Enhancements

- **Machine Learning**: Enhanced prompt understanding with ML
- **Visual Role Editor**: GUI for role and rule management
- **Advanced Workflows**: Complex business process automation
- **Integration APIs**: Connect with external identity providers
- **Real-time Updates**: Live role and rule updates without restarts
