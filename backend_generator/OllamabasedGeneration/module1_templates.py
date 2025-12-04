backend_prompt_template = """
You are a senior backend engineer.

Your task: Generate a **{architectureType} architecture** backend using Node.js, Express, and MongoDB.
The following specification describes the database structure and business logic:

---
{specs}
---

### Requirements:
1. Generate a clean folder structure.
   - If **Monolith**, create single app.js with modular routes/controllers.
   - If **Microservices**, split features into independent service folders (auth-service, user-service, etc.), each with its own routes and server file.
2. Include .env config, database connection, and README.md.
3. Ensure RESTful API endpoints, using async/await.
4. Write clean, commented, production-ready code.
5. Include:
   - Mongoose models/controllers/routes
   - JWT auth (register/login/me)
   - Role-Based Access Control (Admin, Manager, User)
   - Business rules if mentioned
   - package.json with scripts (start/dev)
   - api_map.json summarizing endpoints
6. For each file, wrap code as:
   ```js filename: path/to/file.js
   // code here

7. At the end, ensure all related files are generated completely.

Output only valid code blocks as described above.
"""

frontend_to_backend_template = """
You are a full-stack engineer.
Analyze the following frontend code (React/HTML/JS) and generate a {architectureType} architecture
backend using Node.js + Express + MongoDB.

Frontend Code:
{frontend_code}
Requirements:

Detect forms, API calls, and data states.

Create corresponding Mongoose models, controllers, and routes.

Include JWT auth if login/register is found.

Configure CORS, DB connection, and package.json.

Generate business rules if provided.

Structure depends on architecture:

Monolith -> single Express app
Microservices -> split by domain (auth-service, product-service, etc.)

Output only valid code blocks using:

// code
"""