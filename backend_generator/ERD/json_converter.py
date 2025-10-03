# backend_generator/erd/json_converter.py

import json
from typing import Dict, Any, List
from .models import ERDSchema, Entity, Attribute, Relationship, DataType, RelationshipType
from .utils import NameConverter

class JSONConverter:
    """Convert between different schema formats"""
    
    def __init__(self):
        self.name_converter = NameConverter()
    
    def convert_to_erd_schema(self, parsed_data: Dict[str, Any]) -> ERDSchema:
        """Convert parsed data to ERD schema"""
        entities = []
        relationships = []
        
        # Convert entities
        for entity_data in parsed_data.get('entities', []):
            attributes = []
            
            for attr_data in entity_data.get('attributes', []):
                attribute = Attribute(
                    name=attr_data.get('name', ''),
                    data_type=DataType(attr_data.get('data_type', 'string')),
                    is_primary_key=attr_data.get('is_primary_key', False),
                    is_foreign_key=attr_data.get('is_foreign_key', False),
                    is_nullable=attr_data.get('is_nullable', True),
                    is_unique=attr_data.get('is_unique', False),
                    max_length=attr_data.get('max_length'),
                    default_value=attr_data.get('default_value'),
                    references_table=attr_data.get('references_table'),
                    references_column=attr_data.get('references_column')
                )
                attributes.append(attribute)
            
            entity = Entity(
                name=entity_data.get('name', ''),
                attributes=attributes,
                table_name=entity_data.get('table_name')
            )
            entities.append(entity)
        
        # Convert relationships
        for rel_data in parsed_data.get('relationships', []):
            relationship = Relationship(
                name=rel_data.get('name'),
                source_entity=rel_data.get('source_entity', ''),
                target_entity=rel_data.get('target_entity', ''),
                relationship_type=RelationshipType(rel_data.get('relationship_type', '1:N')),
                source_cardinality=rel_data.get('source_cardinality'),
                target_cardinality=rel_data.get('target_cardinality')
            )
            relationships.append(relationship)
        
        return ERDSchema(
            project_name=parsed_data.get('project_name'),
            entities=entities,
            relationships=relationships,
            metadata=parsed_data.get('metadata', {})
        )
    
    def convert_to_database_schema(self, erd_schema: ERDSchema) -> Dict[str, Any]:
        """Convert ERD schema to database schema format"""
        tables = {}
        
        for entity in erd_schema.entities:
            table_name = entity.table_name or self.name_converter.to_snake_case(entity.name)
            columns = []
            
            for attr in entity.attributes:
                column = {
                    "name": attr.name,
                    "type": self._map_to_sql_type(attr.data_type),
                    "nullable": attr.is_nullable,
                    "unique": attr.is_unique,
                    "primary_key": attr.is_primary_key,
                    "foreign_key": attr.is_foreign_key
                }
                
                if attr.max_length:
                    column["max_length"] = attr.max_length
                
                if attr.default_value is not None:
                    column["default"] = attr.default_value
                
                if attr.is_foreign_key and attr.references_table:
                    column["references"] = {
                        "table": attr.references_table,
                        "column": attr.references_column or "id"
                    }
                
                columns.append(column)
            
            tables[table_name] = {
                "columns": columns,
                "indexes": self._generate_indexes(entity),
                "constraints": self._generate_constraints(entity)
            }
        
        return {
            "database_type": "postgresql",  # Default, can be configured
            "tables": tables,
            "relationships": self._convert_relationships_to_db(erd_schema.relationships),
            "metadata": {
                "generated_from": "ERD Schema",
                "project_name": erd_schema.project_name
            }
        }
    
    def convert_to_fastapi_schema(self, erd_schema: ERDSchema) -> Dict[str, Any]:
        """Convert ERD schema to FastAPI application schema"""
        models = {}
        routes = {}
        
        for entity in erd_schema.entities:
            model_name = entity.name
            fields = {}
            
            for attr in entity.attributes:
                field_def = self._map_to_pydantic_field(attr)
                fields[attr.name] = field_def
            
            models[model_name] = {
                "type": "PydanticModel",
                "fields": fields,
                "table_name": entity.table_name or self.name_converter.to_snake_case(entity.name)
            }
            
            # Generate CRUD routes
            table_name = entity.table_name or self.name_converter.to_snake_case(entity.name)
            routes[f"/{table_name}"] = {
                "GET": f"get_{table_name}_list",
                "POST": f"create_{table_name}",
                "PUT": f"update_{table_name}",
                "DELETE": f"delete_{table_name}"
            }
        
        return {
            "models": models,
            "routes": routes,
            "dependencies": self._generate_dependencies(erd_schema),
            "metadata": {
                "generated_from": "ERD Schema",
                "project_name": erd_schema.project_name,
                "api_version": "1.0"
            }
        }
    
    def _map_to_sql_type(self, data_type: DataType) -> str:
        """Map ERD data type to SQL type"""
        mapping = {
            DataType.STRING: "VARCHAR",
            DataType.INTEGER: "INTEGER",
            DataType.FLOAT: "FLOAT",
            DataType.BOOLEAN: "BOOLEAN",
            DataType.DATE: "DATE",
            DataType.DATETIME: "TIMESTAMP",
            DataType.TEXT: "TEXT",
            DataType.JSON: "JSONB",
            DataType.UUID: "UUID"
        }
        return mapping.get(data_type, "VARCHAR")
    
    def _map_to_pydantic_field(self, attr: Attribute) -> Dict[str, Any]:
        """Map attribute to Pydantic field definition"""
        field_type = self._get_python_type(attr.data_type)
        
        field_def = {
            "type": field_type,
            "description": f"{attr.name} field"
        }
        
        if not attr.is_nullable:
            field_def["required"] = True
        
        if attr.max_length and attr.data_type == DataType.STRING:
            field_def["max_length"] = attr.max_length
        
        if attr.default_value is not None:
            field_def["default"] = attr.default_value
        
        return field_def
    
    def _get_python_type(self, data_type: DataType) -> str:
        """Get Python type for Pydantic"""
        mapping = {
            DataType.STRING: "str",
            DataType.INTEGER: "int",
            DataType.FLOAT: "float",
            DataType.BOOLEAN: "bool",
            DataType.DATE: "date",
            DataType.DATETIME: "datetime",
            DataType.TEXT: "str",
            DataType.JSON: "dict",
            DataType.UUID: "UUID"
        }
        return mapping.get(data_type, "str")
    
    def _generate_indexes(self, entity: Entity) -> List[Dict[str, Any]]:
        """Generate database indexes for entity"""
        indexes = []
        
        # Primary key index
        pk_attrs = [attr.name for attr in entity.attributes if attr.is_primary_key]
        if pk_attrs:
            indexes.append({
                "name": f"pk_{entity.name.lower()}",
                "columns": pk_attrs,
                "unique": True,
                "primary": True
            })
        
        # Unique indexes
        unique_attrs = [attr.name for attr in entity.attributes if attr.is_unique and not attr.is_primary_key]
        for attr in unique_attrs:
            indexes.append({
                "name": f"uk_{entity.name.lower()}_{attr}",
                "columns": [attr],
                "unique": True
            })
        
        # Foreign key indexes
        fk_attrs = [attr.name for attr in entity.attributes if attr.is_foreign_key]
        for attr in fk_attrs:
            indexes.append({
                "name": f"fk_{entity.name.lower()}_{attr}",
                "columns": [attr],
                "unique": False
            })
        
        return indexes
    
    def _generate_constraints(self, entity: Entity) -> List[Dict[str, Any]]:
        """Generate database constraints for entity"""
        constraints = []
        
        # Check constraints for data validation
        for attr in entity.attributes:
            if attr.data_type == DataType.INTEGER and attr.name in ['age', 'year']:
                if 'age' in attr.name:
                    constraints.append({
                        "name": f"chk_{entity.name.lower()}_{attr.name}_range",
                        "type": "CHECK",
                        "expression": f"{attr.name} >= 0 AND {attr.name} <= 150"
                    })
                elif 'year' in attr.name:
                    constraints.append({
                        "name": f"chk_{entity.name.lower()}_{attr.name}_range",
                        "type": "CHECK",
                        "expression": f"{attr.name} >= 1900 AND {attr.name} <= 2100"
                    })
        
        return constraints
    
    def _convert_relationships_to_db(self, relationships: List[Relationship]) -> List[Dict[str, Any]]:
        """Convert ERD relationships to database relationships"""
        db_relationships = []
        
        for rel in relationships:
            db_rel = {
                "name": rel.name or f"{rel.source_entity}_{rel.target_entity}",
                "source_table": self.name_converter.to_snake_case(rel.source_entity),
                "target_table": self.name_converter.to_snake_case(rel.target_entity),
                "type": rel.relationship_type.value
            }
            
            if rel.source_cardinality:
                db_rel["source_cardinality"] = rel.source_cardinality
            if rel.target_cardinality:
                db_rel["target_cardinality"] = rel.target_cardinality
            
            db_relationships.append(db_rel)
        
        return db_relationships
    
    def _generate_dependencies(self, erd_schema: ERDSchema) -> Dict[str, Any]:
        """Generate FastAPI dependencies"""
        dependencies = {
            "database": {
                "type": "PostgreSQL",
                "connection_string": "postgresql://user:password@localhost/dbname"
            },
            "authentication": {
                "type": "JWT",
                "required": True
            },
            "validation": {
                "enabled": True,
                "strict_mode": True
            }
        }
        
        return dependencies

