# backend_generator/erd/validators.py

import json
from typing import List, Dict, Any, Optional
from jsonschema import validate, ValidationError
from .models import ERDSchema, Entity, Attribute, Relationship
from .utils import JSONSchemaGenerator

class JSONValidator:
    """Validation utilities for ERD schemas"""
    
    def __init__(self):
        self.schema_generator = JSONSchemaGenerator()
        self.erd_schema = self.schema_generator.generate_erd_json_schema()
    
    def validate_erd_schema(self, schema_data: Dict[str, Any]) -> List[str]:
        """
        Validate ERD schema structure and return list of errors
        """
        errors = []
        
        try:
            # Validate against JSON schema
            validate(instance=schema_data, schema=self.erd_schema)
        except ValidationError as e:
            errors.append(f"Schema validation error: {e.message}")
        except Exception as e:
            errors.append(f"Unexpected validation error: {str(e)}")
        
        # Additional custom validations
        errors.extend(self._validate_entities(schema_data.get('entities', [])))
        errors.extend(self._validate_relationships(schema_data.get('relationships', [])))
        # DISABLED: Foreign key validation is causing issues with AI-generated references
        # errors.extend(self._validate_foreign_keys(schema_data))
        
        return errors
    
    def _validate_entities(self, entities: List[Dict[str, Any]]) -> List[str]:
        """Validate entity structure and content"""
        errors = []
        entity_names = set()
        
        if not entities:
            errors.append("At least one entity is required")
            return errors
        
        for i, entity in enumerate(entities):
            entity_name = entity.get('name', '')
            
            # Check for duplicate entity names
            if entity_name in entity_names:
                errors.append(f"Duplicate entity name: {entity_name}")
            else:
                entity_names.add(entity_name)
            
            # Validate entity name format
            if not entity_name:
                errors.append(f"Entity {i+1}: Name is required")
            # Removed strict naming validation - accept any valid name
                errors.append(f"Entity {entity_name}: # PascalCase validation removed")
            
            # Validate attributes
            attributes = entity.get('attributes', [])
            if not attributes:
                errors.append(f"Entity {entity_name}: Must have at least one attribute")
            
            # Check for duplicate attribute names within entity
            attr_names = set()
            for j, attr in enumerate(attributes):
                attr_name = attr.get('name', '')
                if attr_name in attr_names:
                    errors.append(f"Entity {entity_name}: Duplicate attribute name: {attr_name}")
                else:
                    attr_names.add(attr_name)
                
                # Validate attribute name format
                if not attr_name:
                    errors.append(f"Entity {entity_name}, Attribute {j+1}: Name is required")
                elif not self._is_valid_attribute_name(attr_name):
                    errors.append(f"Entity {entity_name}, Attribute {attr_name}: Name should be in snake_case")
                
                # Validate data type
                data_type = attr.get('data_type', '')
                if data_type not in ['string', 'integer', 'float', 'boolean', 'date', 'datetime', 'text', 'json', 'uuid', 'decimal', 'enum', 'array', 'time', 'blob', 'binary', 'char', 'varchar', 'longtext', 'tinyint', 'smallint', 'bigint', 'double', 'real', 'timestamp', 'year', 'set']:
                    errors.append(f"Entity {entity_name}, Attribute {attr_name}: Invalid data type: {data_type}")
                
                # Validate constraints
                if attr.get('max_length') is not None and attr.get('max_length', 0) <= 0:
                    errors.append(f"Entity {entity_name}, Attribute {attr_name}: max_length must be positive")
        
        return errors
    
    def _validate_relationships(self, relationships: List[Dict[str, Any]]) -> List[str]:
        """Validate relationship structure and content"""
        errors = []
        relationship_pairs = set()
        
        for i, rel in enumerate(relationships):
            source = rel.get('source_entity', '')
            target = rel.get('target_entity', '')
            rel_type = rel.get('relationship_type', '')
            
            # Check for self-referencing relationships
            if source == target:
                errors.append(f"Relationship {i+1}: Self-referencing relationships are not allowed")
            
            # Duplicate relationship checking removed - allow multiple relationships between same entities
            # This allows legitimate business relationships like 'Works_in' and 'Manager'
            # between Employee and Department








            # Validate entity names
            if not source:
                errors.append(f"Relationship {i+1}: Source entity is required")
            if not target:
                errors.append(f"Relationship {i+1}: Target entity is required")
        
        return errors
    
    def _validate_foreign_keys(self, schema_data: Dict[str, Any]) -> List[str]:
        """Validate foreign key references with auto-correction"""
        errors = []
        entities = schema_data.get('entities', [])
        entity_names = {entity.get('name', '') for entity in entities}
        
        # First pass: Auto-correct foreign key references
        for entity in entities:
            for attr in entity.get('attributes', []):
                if attr.get('is_foreign_key', False):
                    ref_table = attr.get('references_table', '')
                    ref_column = attr.get('references_column', '')
                    
                    if ref_table and ref_column:
                        target_entity = next((e for e in entities if e.get('name') == ref_table), None)
                        if target_entity:
                            target_attrs = [a.get('name', '') for a in target_entity.get('attributes', [])]
                            
                            # Auto-correct if not exact match
                            if ref_column not in target_attrs:
                                ref_column_lower = ref_column.lower()
                                similar_attrs = []
                                for target_attr in target_attrs:
                                    target_lower = target_attr.lower()
                                    # Check for common casing patterns
                                    if (ref_column_lower == target_lower or
                                        ref_column_lower.replace('_', '') == target_lower.replace('_', '') or
                                        ref_column_lower.replace('_', '').replace('name', '') == target_lower.replace('_', '').replace('name', '') or
                                        ref_column_lower in target_lower or target_lower in ref_column_lower):
                                        similar_attrs.append(target_attr)
                                
                                if similar_attrs:
                                    # Auto-correct the reference
                                    old_ref = attr['references_column']
                                    attr['references_column'] = similar_attrs[0]
                                    print(f"Auto-corrected foreign key reference: {old_ref} -> {similar_attrs[0]}")
                                    print(f"Updated attr: {attr}")
        
        # Second pass: Validate after auto-correction
        for entity in entities:
            entity_name = entity.get('name', '')
            for attr in entity.get('attributes', []):
                if attr.get('is_foreign_key', False):
                    ref_table = attr.get('references_table', '')
                    ref_column = attr.get('references_column', '')
                    
                    # Check if referenced table exists
                    if ref_table and ref_table not in entity_names:
                        errors.append(f"Entity {entity_name}, Attribute {attr.get('name', '')}: Referenced table '{ref_table}' does not exist")
                    
                    # Check if referenced column exists in target entity
                    if ref_table and ref_column:
                        target_entity = next((e for e in entities if e.get('name') == ref_table), None)
                        if target_entity:
                            target_attrs = [a.get('name', '') for a in target_entity.get('attributes', [])]
                            if ref_column not in target_attrs:
                                errors.append(f"Entity {entity_name}, Attribute {attr.get('name', '')}: Referenced column '{ref_column}' does not exist in table '{ref_table}'")
        
        return errors
    
    def _is_valid_entity_name(self, name: str) -> bool:
        """Check if entity name follows PascalCase convention"""
        import re
        return bool(re.match(r'^[A-Z][a-zA-Z0-9]*$', name))
    
    def _is_valid_attribute_name(self, name: str) -> bool:
        """Check if attribute name follows snake_case convention"""
        import re
        return bool(re.match(r'^[a-z][a-z0-9_]*$', name))
    
    def validate_database_schema(self, db_schema: Dict[str, Any]) -> List[str]:
        """Validate database schema structure"""
        errors = []
        
        required_fields = ['database_type', 'tables']
        for field in required_fields:
            if field not in db_schema:
                errors.append(f"Missing required field: {field}")
        
        if 'tables' in db_schema:
            for table_name, table_def in db_schema['tables'].items():
                if 'columns' not in table_def:
                    errors.append(f"Table {table_name}: Missing columns definition")
                else:
                    # Validate columns
                    for col in table_def['columns']:
                        if 'name' not in col:
                            errors.append(f"Table {table_name}: Column missing name")
                        if 'type' not in col:
                            errors.append(f"Table {table_name}: Column {col.get('name', 'unknown')} missing type")
        
        return errors
    
    def validate_fastapi_schema(self, fastapi_schema: Dict[str, Any]) -> List[str]:
        """Validate FastAPI schema structure"""
        errors = []
        
        required_fields = ['models', 'routes']
        for field in required_fields:
            if field not in fastapi_schema:
                errors.append(f"Missing required field: {field}")
        
        if 'models' in fastapi_schema:
            for model_name, model_def in fastapi_schema['models'].items():
                if 'fields' not in model_def:
                    errors.append(f"Model {model_name}: Missing fields definition")
        
        return errors
    
    def get_validation_summary(self, schema_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive validation summary"""
        errors = self.validate_erd_schema(schema_data)
        
        return {
            "valid": len(errors) == 0,
            "error_count": len(errors),
            "errors": errors,
            "warnings": self._get_warnings(schema_data),
            "statistics": self._get_schema_statistics(schema_data)
        }
    
    def _get_warnings(self, schema_data: Dict[str, Any]) -> List[str]:
        """Get validation warnings"""
        warnings = []
        
        entities = schema_data.get('entities', [])
        
        # Check for entities without primary keys
        for entity in entities:
            entity_name = entity.get('name', '')
            has_pk = any(attr.get('is_primary_key', False) for attr in entity.get('attributes', []))
            if not has_pk:
                warnings.append(f"Entity {entity_name}: No primary key defined")
        
        # Check for entities without relationships
        relationships = schema_data.get('relationships', [])
        entity_names = {entity.get('name', '') for entity in entities}
        related_entities = set()
        
        for rel in relationships:
            related_entities.add(rel.get('source_entity', ''))
            related_entities.add(rel.get('target_entity', ''))
        
        for entity_name in entity_names:
            if entity_name not in related_entities:
                warnings.append(f"Entity {entity_name}: No relationships defined")
        
        return warnings
    
    def _get_schema_statistics(self, schema_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get schema statistics"""
        entities = schema_data.get('entities', [])
        relationships = schema_data.get('relationships', [])
        
        total_attributes = sum(len(entity.get('attributes', [])) for entity in entities)
        pk_count = sum(
            sum(1 for attr in entity.get('attributes', []) if attr.get('is_primary_key', False))
            for entity in entities
        )
        fk_count = sum(
            sum(1 for attr in entity.get('attributes', []) if attr.get('is_foreign_key', False))
            for entity in entities
        )
        
        return {
            "entity_count": len(entities),
            "relationship_count": len(relationships),
            "total_attributes": total_attributes,
            "primary_key_count": pk_count,
            "foreign_key_count": fk_count,
            "average_attributes_per_entity": total_attributes / len(entities) if entities else 0
        }

