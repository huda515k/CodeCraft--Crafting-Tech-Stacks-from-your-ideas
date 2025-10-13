from __future__ import annotations

import os
import json
import shutil
import tempfile
from dataclasses import dataclass
from typing import Dict, Any, List
from pathlib import Path

from ..ERD.models import ERDSchema, Entity, Attribute, DataType


@dataclass
class GeneratedProject:
    output_dir: str


class NodeProjectGenerator:
    def __init__(self) -> None:
        pass

    def generate(self, erd_schema: ERDSchema) -> GeneratedProject:
        project_dir = tempfile.mkdtemp(prefix="codecraft_node_")
        
        # Create basic project structure
        self._create_directory_structure(project_dir)
        self._write_package_json(project_dir)
        self._write_tsconfig(project_dir)
        self._write_env(project_dir)
        self._write_gitignore(project_dir)
        self._write_readme(project_dir, erd_schema)
        
        # Core application files
        self._write_src_index(project_dir)
        self._write_src_app(project_dir)
        self._write_src_db(project_dir)
        
        # Models based on ERD with relationships
        self._write_src_models(project_dir, erd_schema)
        
        # Controllers for each entity
        self._write_src_controllers(project_dir, erd_schema)
        
        # Middleware (auth, validation, error handling)
        self._write_src_middleware(project_dir)
        
        # Routes based on ERD entities (now using controllers)
        self._write_src_routes(project_dir, erd_schema)

        return GeneratedProject(output_dir=project_dir)

    def _create_directory_structure(self, root: str) -> None:
        """Create basic directory structure"""
        dirs = [
            "src",
            "src/models",
            "src/controllers", 
            "src/middleware",
            "src/routes",
            "src/db",
            "src/utils",
        ]
        for dir_path in dirs:
            os.makedirs(os.path.join(root, dir_path), exist_ok=True)

    def _write_package_json(self, root: str) -> None:
        pkg = {
            "name": "codecraft-generated-backend",
            "version": "1.0.0",
            "private": True,
            "scripts": {
                "dev": "nodemon --watch src --exec ts-node src/index.ts",
                "build": "tsc",
                "start": "node dist/index.js",
                "lint": "eslint ."
            },
            "dependencies": {
                "express": "^4.19.2",
                "sequelize": "^6.37.3",
                "pg": "^8.13.1",
                "cors": "^2.8.5",
                "dotenv": "^16.4.5",
                "express-validator": "^7.0.1",
                "jsonwebtoken": "^9.0.2",
                "bcryptjs": "^2.4.3",
                "helmet": "^7.1.0",
                "morgan": "^1.10.0",
                "compression": "^1.7.4"
            },
            "devDependencies": {
                "typescript": "^5.5.4",
                "ts-node": "^10.9.2",
                "nodemon": "^3.1.0",
                "@types/express": "^4.17.21",
                "@types/node": "^20.0.0",
                "@types/jsonwebtoken": "^9.0.5",
                "@types/bcryptjs": "^2.4.6",
                "@types/morgan": "^1.9.9",
                "@types/compression": "^1.7.5",
                "@types/cors": "^2.8.17",
                "eslint": "^8.57.0",
                "@typescript-eslint/eslint-plugin": "^7.0.0",
                "@typescript-eslint/parser": "^7.0.0"
            }
        }
        os.makedirs(root, exist_ok=True)
        with open(os.path.join(root, "package.json"), "w", encoding="utf-8") as f:
            json.dump(pkg, f, indent=2)

    def _write_tsconfig(self, root: str) -> None:
        tsconfig = {
            "compilerOptions": {
                "target": "ES2020",
                "module": "CommonJS",
                "moduleResolution": "Node",
                "outDir": "dist",
                "rootDir": "src",
                "esModuleInterop": True,
                "allowSyntheticDefaultImports": True,
                "forceConsistentCasingInFileNames": True,
                "skipLibCheck": True,
                "strict": False
            },
            "include": ["src/**/*"],
            "ts-node": {
                "esm": False
            }
        }
        with open(os.path.join(root, "tsconfig.json"), "w", encoding="utf-8") as f:
            json.dump(tsconfig, f, indent=2)

    def _write_src_index(self, root: str) -> None:
        src = os.path.join(root, "src")
        os.makedirs(src, exist_ok=True)
        content = (
            "import { createServer } from './app';\n\n"
            "const port = process.env.PORT || 3000;\n"
            "const app = createServer();\n"
            "app.listen(port, () => {\n"
            "  console.log(`Server listening on port ${port}`);\n"
            "});\n"
        )
        with open(os.path.join(src, "index.ts"), "w", encoding="utf-8") as f:
            f.write(content)

    def _write_src_app(self, root: str) -> None:
        src = os.path.join(root, "src")
        content = (
            "import express from 'express';\n"
            "import cors from 'cors';\n"
            "import dotenv from 'dotenv';\n"
            "import helmet from 'helmet';\n"
            "import morgan from 'morgan';\n"
            "import compression from 'compression';\n"
            "import { sequelize } from './db';\n"
            "import routes from './routes';\n"
            "import { errorHandler, notFoundHandler } from './middleware/errorHandler';\n"
            "import { corsHandler } from './middleware/cors';\n\n"
            "export function createServer() {\n"
            "  dotenv.config();\n"
            "  const app = express();\n"
            "  \n"
            "  // Security middleware\n"
            "  app.use(helmet());\n"
            "  \n"
            "  // CORS middleware\n"
            "  app.use(corsHandler);\n"
            "  \n"
            "  // Logging middleware\n"
            "  app.use(morgan('combined'));\n"
            "  \n"
            "  // Compression middleware\n"
            "  app.use(compression());\n"
            "  \n"
            "  // Body parsing middleware\n"
            "  app.use(express.json({ limit: '10mb' }));\n"
            "  app.use(express.urlencoded({ extended: true, limit: '10mb' }));\n"
            "  \n"
            "  // API routes\n"
            "  app.use('/api', routes);\n"
            "  \n"
            "  // Health check endpoint\n"
            "  app.get('/health', (req, res) => {\n"
            "    res.json({ status: 'OK', timestamp: new Date().toISOString() });\n"
            "  });\n"
            "  \n"
            "  // Error handling middleware (must be last)\n"
            "  app.use(notFoundHandler);\n"
            "  app.use(errorHandler);\n"
            "  \n"
            "  // Optional database connection - won't crash if DB is unavailable\n"
            "  sequelize.authenticate()\n"
            "    .then(() => console.log('✅ Database connected successfully'))\n"
            "    .catch((err) => {\n"
            "      console.log('⚠️  Database connection failed (server will still work):', err.message);\n"
            "      console.log('   To connect to database, update .env with your DATABASE_URL');\n"
            "    });\n"
            "  \n"
            "  return app;\n"
            "}\n"
        )
        with open(os.path.join(src, "app.ts"), "w", encoding="utf-8") as f:
            f.write(content)

    def _write_src_db(self, root: str) -> None:
        src = os.path.join(root, "src")
        content = (
            "import { Sequelize } from 'sequelize';\n\n"
            "export const sequelize = new Sequelize(\n"
            "  process.env.DATABASE_URL || 'postgres://user:password@localhost:5432/app',\n"
            "  { dialect: 'postgres', logging: false }\n"
            ");\n"
        )
        with open(os.path.join(src, "db.ts"), "w", encoding="utf-8") as f:
            f.write(content)

    def _map_ts_type(self, dt: DataType) -> str:
        return {
            DataType.STRING: 'string',
            DataType.INTEGER: 'number',
            DataType.FLOAT: 'number',
            DataType.BOOLEAN: 'boolean',
            DataType.DATE: 'Date',
            DataType.DATETIME: 'Date',
            DataType.TEXT: 'string',
            DataType.JSON: 'object',
            DataType.UUID: 'string',
            DataType.DECIMAL: 'number',
            DataType.ENUM: 'string',
            DataType.ARRAY: 'any[]',
            DataType.TIME: 'string',
            DataType.BLOB: 'Buffer',
            DataType.BINARY: 'Buffer',
            DataType.CHAR: 'string',
            DataType.VARCHAR: 'string',
            DataType.LONGTEXT: 'string',
            DataType.TINYINT: 'number',
            DataType.SMALLINT: 'number',
            DataType.BIGINT: 'number',
            DataType.DOUBLE: 'number',
            DataType.REAL: 'number',
            DataType.TIMESTAMP: 'Date',
            DataType.YEAR: 'number',
            DataType.SET: 'string[]',
        }.get(dt, 'string')

    def _sequelize_type(self, dt: DataType) -> str:
        return {
            DataType.STRING: 'DataTypes.STRING',
            DataType.INTEGER: 'DataTypes.INTEGER',
            DataType.FLOAT: 'DataTypes.FLOAT',
            DataType.BOOLEAN: 'DataTypes.BOOLEAN',
            DataType.DATE: 'DataTypes.DATEONLY',
            DataType.DATETIME: 'DataTypes.DATE',
            DataType.TEXT: 'DataTypes.TEXT',
            DataType.JSON: 'DataTypes.JSONB',
            DataType.UUID: 'DataTypes.UUID',
            DataType.DECIMAL: 'DataTypes.DECIMAL',
            DataType.ENUM: 'DataTypes.ENUM',
            DataType.ARRAY: 'DataTypes.ARRAY',
            DataType.TIME: 'DataTypes.TIME',
            DataType.BLOB: 'DataTypes.BLOB',
            DataType.BINARY: 'DataTypes.BLOB',
            DataType.CHAR: 'DataTypes.CHAR',
            DataType.VARCHAR: 'DataTypes.STRING',
            DataType.LONGTEXT: 'DataTypes.TEXT',
            DataType.TINYINT: 'DataTypes.TINYINT',
            DataType.SMALLINT: 'DataTypes.SMALLINT',
            DataType.BIGINT: 'DataTypes.BIGINT',
            DataType.DOUBLE: 'DataTypes.DOUBLE',
            DataType.REAL: 'DataTypes.REAL',
            DataType.TIMESTAMP: 'DataTypes.DATE',
            DataType.YEAR: 'DataTypes.INTEGER',
            DataType.SET: 'DataTypes.ENUM',
        }.get(dt, 'DataTypes.STRING')

    def _write_src_models(self, root: str, erd: ERDSchema) -> None:
        models_dir = os.path.join(root, "src", "models")
        os.makedirs(models_dir, exist_ok=True)
        
        # Generate all models first
        for entity in erd.entities:
            self._write_individual_model(models_dir, entity)
        
        # Generate relationships after all models are created
        self._write_model_relationships(models_dir, erd)
        
        # Generate index file
        index_lines: List[str] = [
            "import { Sequelize, DataTypes } from 'sequelize';",
            "import { sequelize } from '../db';",
        ]
        for entity in erd.entities:
            index_lines.append(f"export * from './{entity.name}';")
        
        with open(os.path.join(models_dir, "index.ts"), "w", encoding="utf-8") as f:
            f.write("\n".join(index_lines) + "\n")

    def _write_individual_model(self, models_dir: str, entity) -> None:
        """Write individual model file with enhanced structure"""
        name = entity.name
        file = os.path.join(models_dir, f"{name}.ts")
        
        # Generate fields with better structure
        fields: List[str] = []
        
        # Always include id field for Sequelize compatibility
        fields.extend([
            "  id: {",
            "    type: DataTypes.INTEGER,",
            "    allowNull: false,",
            "    autoIncrement: true,",
            "    primaryKey: true,",
            "  },"
        ])
        
        for attr in entity.attributes:
            col = [f"  {attr.name}: {{", f"    type: {self._sequelize_type(attr.data_type)},"]
            if not attr.is_nullable:
                col.append("    allowNull: false,")
            if attr.is_unique:
                col.append("    unique: true,")
            if attr.is_primary_key:
                col.append("    primaryKey: true,")
            if attr.max_length and attr.data_type == DataType.STRING:
                col[1] = f"    type: DataTypes.STRING({attr.max_length}),"
            # Note: autoIncrement is typically handled by primary key in Sequelize
            col.append("  },")
            fields.append("\n".join(col))
        
        # Add timestamps
        fields.extend([
            "  createdAt: {",
            "    type: DataTypes.DATE,",
            "    allowNull: false,",
            "    defaultValue: DataTypes.NOW,",
            "  },",
            "  updatedAt: {",
            "    type: DataTypes.DATE,",
            "    allowNull: false,",
            "    defaultValue: DataTypes.NOW,",
            "  },"
        ])
        
        model_ts = (
            "import { DataTypes, Model, Optional } from 'sequelize';\n"
            "import { sequelize } from '../db';\n\n"
            f"// Interface for {name} attributes\n"
            f"interface {name}Attributes {{\n"
            f"  id: number;\n"
            + "\n".join([f"  {attr.name}: {self._get_typescript_type(attr.data_type)};" for attr in entity.attributes]) + "\n"
            f"  createdAt: Date;\n"
            f"  updatedAt: Date;\n"
            f"}}\n\n"
            f"// Interface for {name} creation attributes\n"
            f"interface {name}CreationAttributes extends Optional<{name}Attributes, 'id' | 'createdAt' | 'updatedAt'> {{}}\n\n"
            f"// {name} model class\n"
            f"export class {name} extends Model<{name}Attributes, {name}CreationAttributes> implements {name}Attributes {{\n"
            f"  public id!: number;\n"
            + "\n".join([f"  public {attr.name}!: {self._get_typescript_type(attr.data_type)};" for attr in entity.attributes]) + "\n"
            f"  public readonly createdAt!: Date;\n"
            f"  public readonly updatedAt!: Date;\n"
            f"}}\n\n"
            f"// Initialize the model\n"
            f"{name}.init({{\n"
            + "\n".join(fields) + "\n"
            f"}}, {{\n"
            f"  sequelize,\n"
            f"  tableName: '{entity.table_name or self._to_snake(name)}',\n"
            f"  timestamps: true,\n"
            f"}});\n\n"
            f"export default {name};"
        )
        
        with open(file, "w", encoding="utf-8") as f:
            f.write(model_ts)

    def _write_model_relationships(self, models_dir: str, erd: ERDSchema) -> None:
        """Write model relationships based on ERD"""
        relationships_file = os.path.join(models_dir, "relationships.ts")
        
        relationship_code = [
            "// Model relationships",
            "import { sequelize } from '../db';",
            "import { " + ", ".join([entity.name for entity in erd.entities]) + " } from './index';",
            "",
            "// Define associations between models",
            "// Note: You may need to adjust these based on your specific ERD relationships",
            ""
        ]
        
        # Add basic relationships (this is a simplified version)
        # In a real implementation, you'd parse the ERD relationships
        for i, entity in enumerate(erd.entities):
            for j, other_entity in enumerate(erd.entities):
                if i != j:
                    # Add a basic hasMany relationship (this should be based on actual ERD relationships)
                    relationship_code.append(
                        f"// {entity.name} -> {other_entity.name} relationship\n"
                        f"// {entity.name}.hasMany({other_entity.name});\n"
                        f"// {other_entity.name}.belongsTo({entity.name});\n"
                    )
        
        relationship_code.extend([
            "",
            "// Export all models with relationships",
            "export { " + ", ".join([entity.name for entity in erd.entities]) + " };"
        ])
        
        with open(relationships_file, "w", encoding="utf-8") as f:
            f.write("\n".join(relationship_code))

    def _get_typescript_type(self, data_type) -> str:
        """Convert DataType to TypeScript type"""
        type_mapping = {
            DataType.INTEGER: 'number',
            DataType.STRING: 'string',
            DataType.TEXT: 'string',
            DataType.BOOLEAN: 'boolean',
            DataType.DATE: 'Date',
            DataType.DATETIME: 'Date',
            DataType.TIMESTAMP: 'Date',
            DataType.DECIMAL: 'number',
            DataType.FLOAT: 'number',
            DataType.DOUBLE: 'number',
            DataType.BIGINT: 'number',
            DataType.SMALLINT: 'number',
            DataType.TINYINT: 'number',
        }
        return type_mapping.get(data_type, 'string')

    def _write_src_controllers(self, root: str, erd: ERDSchema) -> None:
        """Generate controllers for each entity"""
        controllers_dir = os.path.join(root, "src", "controllers")
        os.makedirs(controllers_dir, exist_ok=True)
        
        for entity in erd.entities:
            self._write_individual_controller(controllers_dir, entity)
        
        # Generate controller index
        index_lines = [
            "// Controllers index",
            "import { Request, Response } from 'express';",
            ""
        ]
        
        for entity in erd.entities:
            index_lines.append(f"export * from './{entity.name}Controller';")
        
        with open(os.path.join(controllers_dir, "index.ts"), "w", encoding="utf-8") as f:
            f.write("\n".join(index_lines) + "\n")

    def _write_individual_controller(self, controllers_dir: str, entity) -> None:
        """Write individual controller for an entity"""
        name = entity.name
        controller_file = os.path.join(controllers_dir, f"{name}Controller.ts")
        
        controller_code = [
            f"import {{ Request, Response }} from 'express';",
            f"import {{ {name} }} from '../models/{name}';",
            f"import {{ validationResult }} from 'express-validator';",
            f"import {{ {name}Service }} from '../services/{name}Service';",
            "",
            f"export class {name}Controller {{",
            f"  private {name.lower()}Service: {name}Service;",
            "",
            f"  constructor() {{",
            f"    this.{name.lower()}Service = new {name}Service();",
            f"  }}",
            "",
            f"  // Get all {name.lower()}s",
            f"  public getAll = async (req: Request, res: Response): Promise<void> => {{",
            f"    try {{",
            f"      const {{ page = 1, limit = 10, ...filters }} = req.query;",
            f"      const result = await this.{name.lower()}Service.findAll({{",
            f"        page: Number(page),",
            f"        limit: Number(limit),",
            f"        filters",
            f"      }});",
            f"      res.json(result);",
            f"    }} catch (error) {{",
            f"      res.status(500).json({{ error: 'Failed to fetch {name.lower()}s' }});",
            f"    }}",
            f"  }};",
            "",
            f"  // Get {name.lower()} by ID",
            f"  public getById = async (req: Request, res: Response): Promise<void> => {{",
            f"    try {{",
            f"      const {{ id }} = req.params;",
            f"      const {name.lower()} = await this.{name.lower()}Service.findById(Number(id));",
            f"      if (!{name.lower()}) {{",
            f"        res.status(404).json({{ error: '{name} not found' }});",
            f"        return;",
            f"      }}",
            f"      res.json({name.lower()});",
            f"    }} catch (error) {{",
            f"      res.status(500).json({{ error: 'Failed to fetch {name.lower()}' }});",
            f"    }}",
            f"  }};",
            "",
            f"  // Create new {name.lower()}",
            f"  public create = async (req: Request, res: Response): Promise<void> => {{",
            f"    try {{",
            f"      const errors = validationResult(req);",
            f"      if (!errors.isEmpty()) {{",
            f"        res.status(400).json({{ errors: errors.array() }});",
            f"        return;",
            f"      }}",
            f"      const {name.lower()} = await this.{name.lower()}Service.create(req.body);",
            f"      res.status(201).json({name.lower()});",
            f"    }} catch (error) {{",
            f"      res.status(500).json({{ error: 'Failed to create {name.lower()}' }});",
            f"    }}",
            f"  }};",
            "",
            f"  // Update {name.lower()}",
            f"  public update = async (req: Request, res: Response): Promise<void> => {{",
            f"    try {{",
            f"      const {{ id }} = req.params;",
            f"      const errors = validationResult(req);",
            f"      if (!errors.isEmpty()) {{",
            f"        res.status(400).json({{ errors: errors.array() }});",
            f"        return;",
            f"      }}",
            f"      const {name.lower()} = await this.{name.lower()}Service.update(Number(id), req.body);",
            f"      if (!{name.lower()}) {{",
            f"        res.status(404).json({{ error: '{name} not found' }});",
            f"        return;",
            f"      }}",
            f"      res.json({name.lower()});",
            f"    }} catch (error) {{",
            f"      res.status(500).json({{ error: 'Failed to update {name.lower()}' }});",
            f"    }}",
            f"  }};",
            "",
            f"  // Delete {name.lower()}",
            f"  public delete = async (req: Request, res: Response): Promise<void> => {{",
            f"    try {{",
            f"      const {{ id }} = req.params;",
            f"      const deleted = await this.{name.lower()}Service.delete(Number(id));",
            f"      if (!deleted) {{",
            f"        res.status(404).json({{ error: '{name} not found' }});",
            f"        return;",
            f"      }}",
            f"      res.status(204).send();",
            f"    }} catch (error) {{",
            f"      res.status(500).json({{ error: 'Failed to delete {name.lower()}' }});",
            f"    }}",
            f"  }};",
            f"}}",
            "",
            f"export default {name}Controller;"
        ]
        
        with open(controller_file, "w", encoding="utf-8") as f:
            f.write("\n".join(controller_code))

    def _write_src_middleware(self, root: str) -> None:
        """Generate middleware files"""
        middleware_dir = os.path.join(root, "src", "middleware")
        os.makedirs(middleware_dir, exist_ok=True)
        
        # Error handling middleware
        error_middleware = [
            "import { Request, Response, NextFunction } from 'express';",
            "",
            "export const errorHandler = (",
            "  error: Error,",
            "  req: Request,",
            "  res: Response,",
            "  next: NextFunction",
            "): void => {",
            "  console.error('Error:', error);",
            "  res.status(500).json({",
            "    error: 'Internal server error',",
            "    message: process.env.NODE_ENV === 'development' ? error.message : 'Something went wrong'",
            "  });",
            "};",
            "",
            "export const notFoundHandler = (req: Request, res: Response): void => {",
            "  res.status(404).json({ error: 'Route not found' });",
            "};"
        ]
        
        with open(os.path.join(middleware_dir, "errorHandler.ts"), "w", encoding="utf-8") as f:
            f.write("\n".join(error_middleware))
        
            # Authentication middleware
            auth_middleware = [
                "import { Request, Response, NextFunction } from 'express';",
                "import jwt from 'jsonwebtoken';",
                "",
                "// Extend Request interface to include user",
                "declare global {",
                "  namespace Express {",
                "    interface Request {",
                "      user?: any;",
                "    }",
                "  }",
                "}",
                "",
                "export const authenticateToken = (req: Request, res: Response, next: NextFunction): void => {",
                "  const authHeader = req.headers['authorization'];",
                "  const token = authHeader && authHeader.split(' ')[1];",
                "",
                "  if (!token) {",
                "    res.status(401).json({ error: 'Access token required' });",
                "    return;",
                "  }",
                "",
                "  jwt.verify(token, process.env.JWT_SECRET || 'your-secret-key', (err, user) => {",
                "    if (err) {",
                "      res.status(403).json({ error: 'Invalid token' });",
                "      return;",
                "    }",
                "    req.user = user;",
                "    next();",
                "  });",
                "};",
                "",
                "export const optionalAuth = (req: Request, res: Response, next: NextFunction): void => {",
                "  const authHeader = req.headers['authorization'];",
                "  const token = authHeader && authHeader.split(' ')[1];",
                "",
                "  if (token) {",
                "    jwt.verify(token, process.env.JWT_SECRET || 'your-secret-key', (err, user) => {",
                "      if (!err) {",
                "        req.user = user;",
                "      }",
                "    });",
                "  }",
                "  next();",
                "};"
            ]
        
        with open(os.path.join(middleware_dir, "auth.ts"), "w", encoding="utf-8") as f:
            f.write("\n".join(auth_middleware))
        
        # Validation middleware
        validation_middleware = [
            "import { Request, Response, NextFunction } from 'express';",
            "import { validationResult } from 'express-validator';",
            "",
            "export const validateRequest = (req: Request, res: Response, next: NextFunction): void => {",
            "  const errors = validationResult(req);",
            "  if (!errors.isEmpty()) {",
            "    res.status(400).json({",
            "      error: 'Validation failed',",
            "      details: errors.array()",
            "    });",
            "    return;",
            "  }",
            "  next();",
            "};",
            "",
            "export const validateId = (req: Request, res: Response, next: NextFunction): void => {",
            "  const { id } = req.params;",
            "  if (!id || isNaN(Number(id))) {",
            "    res.status(400).json({ error: 'Invalid ID parameter' });",
            "    return;",
            "  }",
            "  next();",
            "};"
        ]
        
        with open(os.path.join(middleware_dir, "validation.ts"), "w", encoding="utf-8") as f:
            f.write("\n".join(validation_middleware))
        
        # CORS middleware
        cors_middleware = [
            "import { Request, Response, NextFunction } from 'express';",
            "",
            "export const corsHandler = (req: Request, res: Response, next: NextFunction): void => {",
            "  res.header('Access-Control-Allow-Origin', '*');",
            "  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');",
            "  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');",
            "",
            "  if (req.method === 'OPTIONS') {",
            "    res.sendStatus(200);",
            "    return;",
            "  }",
            "  next();",
            "};"
        ]
        
        with open(os.path.join(middleware_dir, "cors.ts"), "w", encoding="utf-8") as f:
            f.write("\n".join(cors_middleware))
        
        # Middleware index
        middleware_index = [
            "// Middleware exports",
            "export * from './errorHandler';",
            "export * from './auth';",
            "export * from './validation';",
            "export * from './cors';"
        ]
        
        with open(os.path.join(middleware_dir, "index.ts"), "w", encoding="utf-8") as f:
            f.write("\n".join(middleware_index))

    def _write_src_routes(self, root: str, erd: ERDSchema) -> None:
        """Generate routes using controllers and middleware"""
        routes_dir = os.path.join(root, "src", "routes")
        os.makedirs(routes_dir, exist_ok=True)
        
        # Generate services first
        self._write_src_services(root, erd)
        
        # Generate main routes file
        imports = [
            "import { Router } from 'express';",
            "import { body, param } from 'express-validator';",
            "import { validateRequest, validateId } from '../middleware/validation';",
            "import { authenticateToken, optionalAuth } from '../middleware/auth';",
            "import { corsHandler } from '../middleware/cors';"
        ]
        
        body = [
            "const router = Router();",
            "",
            "// Apply CORS middleware",
            "router.use(corsHandler);",
            ""
        ]
        
        for entity in erd.entities:
            table = entity.table_name or self._to_snake(entity.name)
            name = entity.name
            controller_name = f"{name}Controller"
            
            imports.append(f"import {{ {controller_name} }} from '../controllers/{controller_name}';")
            
            # Create controller instance
            body.extend([
                f"// {name} routes",
                f"const {name.lower()}Controller = new {controller_name}();",
                ""
            ])
            
            # Add routes with validation
            body.extend([
                f"// GET /{table} - Get all {name.lower()}s",
                f"router.get('/{table}',",
                f"  optionalAuth,",
                f"  {name.lower()}Controller.getAll",
                f");",
                "",
                f"// GET /{table}/:id - Get {name.lower()} by ID",
                f"router.get('/{table}/:id',",
                f"  validateId,",
                f"  optionalAuth,",
                f"  {name.lower()}Controller.getById",
                f");",
                "",
                f"// POST /{table} - Create new {name.lower()}",
                f"router.post('/{table}',",
                f"  authenticateToken,",
                f"  [",
                # Add validation rules for each attribute
                *[f"    body('{attr.name}').notEmpty().withMessage('{attr.name} is required')," for attr in entity.attributes if not attr.is_nullable],
                f"  ],",
                f"  validateRequest,",
                f"  {name.lower()}Controller.create",
                f");",
                "",
                f"// PUT /{table}/:id - Update {name.lower()}",
                f"router.put('/{table}/:id',",
                f"  validateId,",
                f"  authenticateToken,",
                f"  [",
                *[f"    body('{attr.name}').optional().notEmpty().withMessage('{attr.name} cannot be empty')," for attr in entity.attributes],
                f"  ],",
                f"  validateRequest,",
                f"  {name.lower()}Controller.update",
                f");",
                "",
                f"// DELETE /{table}/:id - Delete {name.lower()}",
                f"router.delete('/{table}/:id',",
                f"  validateId,",
                f"  authenticateToken,",
                f"  {name.lower()}Controller.delete",
                f");",
                ""
            ])
        
        content = "\n".join(imports) + "\n\n" + "\n".join(body) + "\n\nexport default router;\n"
        with open(os.path.join(routes_dir, "index.ts"), "w", encoding="utf-8") as f:
            f.write(content)

    def _write_src_services(self, root: str, erd: ERDSchema) -> None:
        """Generate service layer for business logic"""
        services_dir = os.path.join(root, "src", "services")
        os.makedirs(services_dir, exist_ok=True)
        
        for entity in erd.entities:
            self._write_individual_service(services_dir, entity)
        
        # Generate services index
        index_lines = [
            "// Services index",
            "import { Request, Response } from 'express';",
            ""
        ]
        
        for entity in erd.entities:
            index_lines.append(f"export * from './{entity.name}Service';")
        
        with open(os.path.join(services_dir, "index.ts"), "w", encoding="utf-8") as f:
            f.write("\n".join(index_lines) + "\n")

    def _write_individual_service(self, services_dir: str, entity) -> None:
        """Write individual service for an entity"""
        name = entity.name
        service_file = os.path.join(services_dir, f"{name}Service.ts")
        
        service_code = [
            f"import {{ {name} }} from '../models/{name}';",
            f"import {{ Op }} from 'sequelize';",
            "",
            f"export class {name}Service {{",
            "",
            f"  // Find all {name.lower()}s with pagination and filtering",
            f"  async findAll(options: {{ page?: number; limit?: number; filters?: any }} = {{}}) {{",
            f"    const {{ page = 1, limit = 10, filters = {{}} }} = options;",
            f"    const offset = (page - 1) * limit;",
            "",
            f"    const whereClause = {{}};",
            f"    // Add filter logic here based on filters object",
            "",
            f"    const {{ count, rows }} = await {name}.findAndCountAll({{",
            f"      where: whereClause,",
            f"      limit: Number(limit),",
            f"      offset: Number(offset),",
            f"      order: [['createdAt', 'DESC']]",
            f"    }});",
            "",
            f"    return {{",
            f"      data: rows,",
            f"      pagination: {{",
            f"        page: Number(page),",
            f"        limit: Number(limit),",
            f"        total: count,",
            f"        pages: Math.ceil(count / limit)",
            f"      }}",
            f"    }};",
            f"  }}",
            "",
            f"  // Find {name.lower()} by ID",
            f"  async findById(id: number) {{",
            f"    return await {name}.findByPk(id);",
            f"  }}",
            "",
            f"  // Create new {name.lower()}",
            f"  async create(data: any) {{",
            f"    return await {name}.create(data);",
            f"  }}",
            "",
            f"  // Update {name.lower()}",
            f"  async update(id: number, data: any) {{",
            f"    const {name.lower()} = await {name}.findByPk(id);",
            f"    if (!{name.lower()}) {{",
            f"      return null;",
            f"    }}",
            f"    await {name.lower()}.update(data);",
            f"    return {name.lower()};",
            f"  }}",
            "",
            f"  // Delete {name.lower()}",
            f"  async delete(id: number) {{",
            f"    const {name.lower()} = await {name}.findByPk(id);",
            f"    if (!{name.lower()}) {{",
            f"      return false;",
            f"    }}",
            f"    await {name.lower()}.destroy();",
            f"    return true;",
            f"  }}",
            "",
            f"  // Search {name.lower()}s",
            f"  async search(query: string) {{",
            f"    return await {name}.findAll({{",
            f"      where: {{",
            f"        [Op.or]: [",
            # Add search fields based on entity attributes
            *[f"          {{ {attr.name}: {{ [Op.iLike]: `%${{query}}%` }} }}," for attr in entity.attributes if attr.data_type.value == 'STRING'],
            f"        ]",
            f"      }}",
            f"    }});",
            f"  }}",
            f"}}",
            "",
            f"export default {name}Service;"
        ]
        
        with open(service_file, "w", encoding="utf-8") as f:
            f.write("\n".join(service_code))

    def _write_env(self, root: str) -> None:
        with open(os.path.join(root, ".env"), "w", encoding="utf-8") as f:
            f.write("DATABASE_URL=postgres://user:password@localhost:5432/app\n")

    def _write_gitignore(self, root: str) -> None:
        gitignore_content = """node_modules/
dist/
.env
*.log
.DS_Store
"""
        with open(os.path.join(root, ".gitignore"), "w", encoding="utf-8") as f:
            f.write(gitignore_content)

    def _write_readme(self, root: str, erd: ERDSchema) -> None:
        with open(os.path.join(root, "README.md"), "w", encoding="utf-8") as f:
            f.write(
                "# 🚀 CodeCraft Generated Backend\n\n"
                "**AI-Powered Node.js Backend with Complete Architecture**\n\n"
                "This backend was automatically generated from your ERD schema and includes:\n\n"
                "## ✨ Features\n\n"
                "### 🏗️ **Complete Architecture**\n"
                "- **Models**: TypeScript interfaces with Sequelize ORM\n"
                "- **Controllers**: Full CRUD operations with error handling\n"
                "- **Services**: Business logic layer with pagination & filtering\n"
                "- **Middleware**: Authentication, validation, CORS, security\n"
                "- **Routes**: RESTful API with proper HTTP methods\n\n"
                "### 🔒 **Security & Middleware**\n"
                "- Helmet for security headers\n"
                "- JWT authentication\n"
                "- Input validation with express-validator\n"
                "- CORS handling\n"
                "- Error handling middleware\n"
                "- Request logging with Morgan\n"
                "- Response compression\n\n"
                "### 📊 **Database Features**\n"
                "- Sequelize ORM with TypeScript\n"
                "- Model relationships and associations\n"
                "- Automatic timestamps (createdAt, updatedAt)\n"
                "- Pagination and filtering\n"
                "- Search functionality\n\n"
                "## 🚀 Getting Started\n\n"
                "### 1. Install Dependencies\n"
                "```bash\nnpm install\n```\n\n"
                "### 2. Environment Setup\n"
                "Create a `.env` file:\n"
                "```env\n"
                "DATABASE_URL=postgres://username:password@localhost:5432/your_database\n"
                "JWT_SECRET=your-super-secret-jwt-key\n"
                "NODE_ENV=development\n"
                "PORT=3000\n"
                "```\n\n"
                "### 3. Database Setup (Optional)\n"
                "The server runs without a database, but for full functionality:\n\n"
                "1. Install PostgreSQL\n"
                "2. Create a database\n"
                "3. Update `.env` with your `DATABASE_URL`\n"
                "4. Restart the server\n\n"
                "### 4. Start Development\n"
                "```bash\n# Development mode\nnpm run dev\n\n# Production build\nnpm run build\nnpm start\n```\n\n"
                "## 📡 API Endpoints\n\n"
                "### Health Check\n"
                "- `GET /health` - Server health status\n\n"
                "### Entity Endpoints\n"
                + "\n".join([f"- `GET /api/{entity.table_name or self._to_snake(entity.name)}` - List all {entity.name.lower()}s\n"
                           f"- `GET /api/{entity.table_name or self._to_snake(entity.name)}/:id` - Get {entity.name.lower()} by ID\n"
                           f"- `POST /api/{entity.table_name or self._to_snake(entity.name)}` - Create new {entity.name.lower()}\n"
                           f"- `PUT /api/{entity.table_name or self._to_snake(entity.name)}/:id` - Update {entity.name.lower()}\n"
                           f"- `DELETE /api/{entity.table_name or self._to_snake(entity.name)}/:id` - Delete {entity.name.lower()}\n" for entity in erd.entities]) +
                "\n### Authentication\n"
                "- All POST, PUT, DELETE operations require JWT authentication\n"
                "- Include `Authorization: Bearer <token>` header\n\n"
                "## 🏗️ Project Structure\n\n"
                "```\n"
                "src/\n"
                "├── controllers/     # Request handlers\n"
                "├── middleware/      # Auth, validation, error handling\n"
                "├── models/          # Database models with relationships\n"
                "├── routes/          # API route definitions\n"
                "├── services/        # Business logic layer\n"
                "├── utils/          # Utility functions\n"
                "├── db.ts           # Database connection\n"
                "├── app.ts          # Express app configuration\n"
                "└── index.ts        # Server entry point\n"
                "```\n\n"
                "## 🔧 Development\n\n"
                "### Available Scripts\n"
                "- `npm run dev` - Start development server with hot reload\n"
                "- `npm run build` - Build for production\n"
                "- `npm start` - Start production server\n"
                "- `npm run lint` - Run ESLint\n\n"
                "### Model Relationships\n"
                "Check `src/models/relationships.ts` for model associations.\n"
                "Update relationships based on your specific ERD requirements.\n\n"
                "## 🛡️ Security Features\n\n"
                "- Input validation on all endpoints\n"
                "- JWT-based authentication\n"
                "- Security headers with Helmet\n"
                "- CORS protection\n"
                "- Request size limits\n"
                "- Error handling without information leakage\n\n"
                "## 📝 Notes\n\n"
                "- Server runs without database (returns helpful error messages)\n"
                "- Full functionality requires database connection\n"
                "- All endpoints include proper error handling\n"
                "- TypeScript for type safety\n"
                "- Production-ready code structure\n"
            )

    def _to_snake(self, s: str) -> str:
        out = []
        for ch in s:
            if ch.isupper():
                if out:
                    out.append('_')
                out.append(ch.lower())
            else:
                out.append(ch)
        return ''.join(out)
