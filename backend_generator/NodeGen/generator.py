from __future__ import annotations

import os
import json
import shutil
import tempfile
from dataclasses import dataclass
from typing import Dict, Any, List

from ..ERD.models import ERDSchema, Entity, Attribute, DataType


@dataclass
class GeneratedProject:
    output_dir: str


class NodeProjectGenerator:
    def __init__(self) -> None:
        pass

    def generate(self, erd_schema: ERDSchema) -> GeneratedProject:
        project_dir = tempfile.mkdtemp(prefix="codecraft_node_")

        self._write_package_json(project_dir)
        self._write_tsconfig(project_dir)
        self._write_src_index(project_dir)
        self._write_src_app(project_dir)
        self._write_src_db(project_dir)
        self._write_src_models(project_dir, erd_schema)
        self._write_src_routes(project_dir, erd_schema)
        self._write_env(project_dir)
        self._write_readme(project_dir, erd_schema)

        return GeneratedProject(output_dir=project_dir)

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
                "dotenv": "^16.4.5"
            },
            "devDependencies": {
                "typescript": "^5.5.4",
                "ts-node": "^10.9.2",
                "nodemon": "^3.1.0",
                "@types/express": "^4.17.21",
                "@types/node": "^20.0.0"
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
            "import { sequelize } from './db';\n"
            "import routes from './routes';\n\n"
            "export function createServer() {\n"
            "  dotenv.config();\n"
            "  const app = express();\n"
            "  app.use(cors());\n"
            "  app.use(express.json());\n"
            "  app.use('/api', routes);\n"
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
        }.get(dt, 'DataTypes.STRING')

    def _write_src_models(self, root: str, erd: ERDSchema) -> None:
        models_dir = os.path.join(root, "src", "models")
        os.makedirs(models_dir, exist_ok=True)
        index_lines: List[str] = [
            "import { Sequelize, DataTypes } from 'sequelize';",
            "import { sequelize } from '../db';",
        ]
        for entity in erd.entities:
            name = entity.name
            file = os.path.join(models_dir, f"{name}.ts")
            fields: List[str] = []
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
                col.append("  },")
                fields.append("\n".join(col))
            model_ts = (
                "import { DataTypes } from 'sequelize';\n"
                "import { sequelize } from '../db';\n\n"
                f"export const {name} = sequelize.define('{name}', {{\n"
                + "\n".join(fields) + "\n"
                + "});\n"
            )
            with open(file, "w", encoding="utf-8") as f:
                f.write(model_ts)
            index_lines.append(f"export * from './{name}';")

        with open(os.path.join(models_dir, "index.ts"), "w", encoding="utf-8") as f:
            f.write("\n".join(index_lines) + "\n")

    def _write_src_routes(self, root: str, erd: ERDSchema) -> None:
        routes_dir = os.path.join(root, "src", "routes")
        os.makedirs(routes_dir, exist_ok=True)
        imports: List[str] = ["import { Router } from 'express';"]
        body: List[str] = ["const router = Router();"]

        for entity in erd.entities:
            table = entity.table_name or self._to_snake(entity.name)
            name = entity.name
            imports.append(f"import {{ {name} }} from '../models/{name}';")
            body.extend([
                f"// {name} CRUD",
                f"router.get('/{table}', async (req, res) => {{",
                f"  try {{",
                f"    const items = await {name}.findAll();",
                f"    res.json(items);",
                f"  }} catch (error) {{",
                f"    res.status(500).json({{ error: 'Database not connected. Please check your DATABASE_URL in .env' }});",
                f"  }}",
                f"}});",
                f"router.post('/{table}', async (req, res) => {{",
                f"  try {{",
                f"    const item = await {name}.create(req.body);",
                f"    res.status(201).json(item);",
                f"  }} catch (error) {{",
                f"    res.status(500).json({{ error: 'Database not connected. Please check your DATABASE_URL in .env' }});",
                f"  }}",
                f"}});",
            ])
        content = (
            "\n".join(imports) + "\n\n" + "\n".join(body) + "\n\nexport default router;\n"
        )
        with open(os.path.join(routes_dir, "index.ts"), "w", encoding="utf-8") as f:
            f.write(content)

    def _write_env(self, root: str) -> None:
        with open(os.path.join(root, ".env"), "w", encoding="utf-8") as f:
            f.write("DATABASE_URL=postgres://user:password@localhost:5432/app\n")

    def _write_readme(self, root: str, erd: ERDSchema) -> None:
        with open(os.path.join(root, "README.md"), "w", encoding="utf-8") as f:
            f.write(
                "# CodeCraft Generated Backend\n\n"
                "Generated from ERD schema.\n\n"
                "## Getting Started\n\n"
                "1. npm install\n"
                "2. npm run dev\n\n"
                "## Database Setup (Optional)\n\n"
                "The server will run without a database, but to use the API endpoints:\n\n"
                "1. Install PostgreSQL\n"
                "2. Create a database\n"
                "3. Update .env with your DATABASE_URL:\n"
                "   ```\n"
                "   DATABASE_URL=postgres://username:password@localhost:5432/your_database\n"
                "   ```\n"
                "4. Restart the server\n\n"
                "## API Endpoints\n\n"
                "Without database: Returns helpful error messages\n"
                "With database: Full CRUD operations\n\n"
                f"Available endpoints:\n"
                + "\n".join([f"- GET/POST /api/{entity.table_name or self._to_snake(entity.name)}" for entity in erd.entities])
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


