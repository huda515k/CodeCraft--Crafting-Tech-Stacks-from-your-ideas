

backend_prompt_template = """
You are a **senior backend engineer**.

Generate a **{architectureType} architecture** backend using:
- Node.js
- Express.js
- MongoDB (Mongoose)
- TypeScript

Follow these exact output instructions:

- Always output each file inside properly formatted Markdown code blocks like this:

```js filename:path/to/file.ts
// file content here
DO NOT include explanations or text outside of code blocks.

Each file must include full, runnable code (no placeholders).

Use clean, maintainable folder structure with:

routes/

controllers/

models/

middlewares/

utils/

config/

Include .env setup and MongoDB connection file.

Implement:

JWT Authentication (login/signup)

Role-Based Access Control (RBAC)

CRUD endpoints for main entities

Proper error handling middleware

Validation (basic)

Use ES modules (import/export) and TypeScript best practices.

Include all necessary types and interfaces.

The following specification describes the system requirements:
{specs}

Output all files fully with correct paths.
"""

frontend_to_backend_template = """
You are a full-stack engineer.

Analyze this frontend and generate a {architectureType} backend using Node.js, Express, MongoDB, and TypeScript.

Frontend Code:
{frontend_code}

Steps:
Detect forms, API calls, and state management from the frontend.

Derive models, controllers, and routes accordingly.

Include JWT auth if login/register is found.

Ensure CORS, DB connection, and role-based access.

Output valid code blocks in format:

js
Copy code
// code
Complete every module (models, controllers, routes, middleware, server).
"""




microservices_planner_prompt = """
You are a **senior Node.js microservices architect**.

Task: Plan a full backend architecture based on this description:

"{specs}"

Return **only one JSON object** — no Markdown, no commentary, no code blocks.
Surround nothing with backticks.

Schema:
{{
  "services": [
    {{
      "name": "ServiceName",
      "description": "Purpose of this service",
      "routes": ["/api/v1/..."],
      "database": "PostgreSQL (...tables...)",
      "depends_on": []
    }}
  ],
  "shared": [
    "shared utilities",
    "common types",
    "event bus"
  ]
}}

Rules:
- Always begin with {{ and end with }}.
- Do NOT include triple backticks.
- Keep valid JSON parsable by Python json.loads.
"""



microservices_infra_prompt = """
You are a **senior backend DevOps engineer**.

Generate the **infrastructure layer** for a **Node.js + TypeScript microservices** project using the following system description:

"{specs}"

----------------------------------------
 REQUIRED COMPONENTS:

1. **API Gateway (TypeScript + Express)**
   - Acts as a reverse proxy to route requests to internal services.
   - Implements JWT validation middleware.
   - Includes centralized error handling, logging, and rate limiting.
   - Each route should forward to the correct microservice based on its path prefix.

2. **Shared Package (packages/shared/)**
   - Include:
     - Common constants (status codes, messages)
     - Utility functions (errorHandler, logger)
     - Validation schemas (Zod or Joi)
     - TypeScript interfaces for entities (User, Lead, Notification, etc.)
   - Must be importable by every service (e.g., via `@shared/utils`).

3. **Docker Compose Setup**
   - Define all microservices listed in the plan.
   - Include RabbitMQ broker and PostgreSQL container.
   - Add environment variables for ports, service names, and credentials.
   - Attach all services to a single Docker network.
   - Include health checks and dependency ordering.

4. **Root-Level Files**
   - `.env.example` with default values.
   - `README.md` with complete setup and startup instructions.

----------------------------------------
 OUTPUT FORMAT (MANDATORY):

Return multiple code blocks, each specifying the correct file path.

Example:

```ts filename:api-gateway/src/server.ts
// code here
# docker setup here
Do not include explanations or text outside of code blocks.

 GUIDELINES:

Use TypeScript ES modules (import/export).

Each file must contain complete, runnable code — no placeholders.

Keep folder structure clean and production-ready.

Include comments where helpful (especially in Docker Compose and gateway routing).

For logging, use Winston or Pino.

For environment variables, use dotenv + validation via zod.

Ensure the gateway can proxy all routes (Auth, CRM, Notification, etc.) via http-proxy-middleware.

Each service should have a distinct container name and exposed port.

Make the README step-by-step (install → env → docker-compose up → access URLs).

Output fully formatted, runnable code with the exact file paths for each generated file.
"""




microservice_code_prompt = """
You are a **senior backend engineer**.

Generate the complete backend code for the following **microservice** described below:

{service}

----------------------------------------
 STACK & REQUIREMENTS:

Use:
- Node.js
- Express.js
- TypeScript
- Prisma ORM (PostgreSQL)
- JWT authentication where required
- Docker-ready environment

Follow this **clean folder structure**:
src/
controllers/
routes/
services/
models/
middlewares/
utils/
config/
prisma/schema.prisma
server.ts
.env.example
README.md

----------------------------------------
 IMPLEMENT THE FOLLOWING:

- **Controllers** → Implement CRUD operations for the described entities.  
- **Routes** → RESTful routes using Express Router, versioned as `/api/v1/{entity}`.  
- **Services** → Business logic layer using async/await.  
- **Models (Prisma)** → Define complete database schema for PostgreSQL.  
- **Middlewares** → Include JWT auth check, errorHandler, request logger.  
- **Utils** → Helper functions (logger, API response wrapper).  
- **Config** → `db.ts` for Prisma connection and `env.ts` for environment variables (validated with Zod).  
- **Server** → Entry point (`server.ts`) with Express setup, middlewares, and routes registration.  
- **.env.example** → Provide realistic defaults for DB, PORT, JWT_SECRET, etc.  
- **README.md** → Setup, run, and environment instructions.

----------------------------------------
 OUTPUT FORMAT (MANDATORY):

Return multiple code blocks, one per file, using the format:

```ts filename:services/<service-name>/src/server.ts
// code here
File extensions must match (.ts, .prisma, .env, .md, etc.).

Each file must include full runnable code (no “...” or placeholders).

Do not include explanations or text outside of code blocks.

 CODING GUIDELINES:

Use modern ES modules (import / export).

Apply TypeScript types and interfaces everywhere.

Use async/await and proper error handling with try/catch.

If this is the Auth service:

Implement /register, /login, /refresh-token.

Generate JWTs with expiry and hashed passwords using bcrypt.

If this is the Notification service:

Include email sending (nodemailer) and WebSocket event example.

If this is the File service:

Integrate AWS S3 for upload/download via pre-signed URLs.

Include proper comments where logic is non-trivial.

Code must be ready to run via:
npm install && npm run dev
Return only complete code blocks with accurate file paths.
"""


frontend_prompt_template = """
You are a **senior frontend engineer**.

Generate a **modern React + TypeScript + Tailwind CSS frontend** based on the following specification:

{specs}

---

### 🔧 Requirements

- Use **Vite + React + TypeScript**
- Include **all setup files**:
  - index.html
  - vite.config.ts
  - tsconfig.json
  - tailwind.config.js
  - postcss.config.js
  - package.json
  - tsconfig.node.json

- Folder structure:

index.html
vite.config.ts
tsconfig.json
tailwind.config.js
postcss.config.js
package.json
src/
main.tsx
App.tsx
components/
pages/
hooks/
styles/
utils/

yaml
Copy code

- Include:
  - Responsive UI
  - Clean, maintainable layout
  - At least one complete functional page (form/table/dashboard)
  - Reusable UI components (buttons, inputs, modals, cards)
  - Tailwind for styling (no inline styles except micro cases)

---

### ⚙️ Output Rules (MANDATORY)

1. **Each file must be inside a properly formatted Markdown code block** like this:

```tsx filename:src/App.tsx
// full file content here
If the file is not TypeScript (like HTML, CSS, JSON, or JS), use the correct language tag, for example:

html
Copy code
<!DOCTYPE html>
<html>...</html>
json
Copy code
{{ ... }}
Do NOT include any explanations, commentary, or summaries outside of code blocks.

Every file must contain complete runnable code — no placeholders like ..., TODO, or omitted sections.

Ensure imports and file paths are valid and consistent.

Never wrap all files in a single large block — each file must be a separate fenced block.

Optional: Prefix additional folders with ### folder_name if needed for clarity.

🧩 Example Output Format
php-template
Copy code
### index.html
```html filename:index.html
<!DOCTYPE html>
<html lang="en">
  <head>...</head>
</html>
ts
Copy code
// full code here
End of template.
"""


frontend_to_backend_template = """
You are a full-stack engineer.

Analyze this frontend and generate a {architectureType} backend using Node.js, Express, MongoDB, and TypeScript.

Frontend Code:
{frontend_code}

Steps:

Detect forms, API calls, and state management from the frontend.

Derive models, controllers, and routes accordingly.

Include JWT auth if login/register is found.

Ensure CORS, DB connection, and role-based access.

Output valid code blocks in format:

// code


Complete every module (models, controllers, routes, middleware, server).
"""

backend_to_frontend_template = """
You are a **senior frontend engineer**.

Analyze this backend code and generate a **modern React + TypeScript + Tailwind CSS frontend** that matches the backend API structure.

Backend Code:
{backend_code}

---

### 🔧 Requirements

- Use **Vite + React + TypeScript**
- Include **all setup files**:
  - index.html
  - vite.config.ts
  - tsconfig.json
  - tailwind.config.js
  - postcss.config.js
  - package.json
  - tsconfig.node.json

- Folder structure:

index.html
vite.config.ts
tsconfig.json
tailwind.config.js
postcss.config.js
package.json
src/
main.tsx
App.tsx
components/
pages/
hooks/
styles/
utils/

- Include:
  - Responsive UI
  - Clean, maintainable layout
  - Complete functional pages matching backend routes
  - API integration using fetch/axios
  - Reusable UI components (buttons, inputs, modals, cards)
  - Tailwind for styling (no inline styles except micro cases)
  - Forms for all POST/PUT endpoints
  - Lists/tables for all GET endpoints

---

### ⚙️ Output Rules (MANDATORY)

1. **Each file must be inside a properly formatted Markdown code block** like this:

```tsx filename:src/App.tsx
// full file content here
```

If the file is not TypeScript (like HTML, CSS, JSON, or JS), use the correct language tag.

Do NOT include any explanations, commentary, or summaries outside of code blocks.

Every file must contain complete runnable code — no placeholders like ..., TODO, or omitted sections.

Ensure imports and file paths are valid and consistent.

Never wrap all files in a single large block — each file must be a separate fenced block.
"""