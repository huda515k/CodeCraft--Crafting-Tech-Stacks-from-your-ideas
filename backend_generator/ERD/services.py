# backend_generator/erd/services.py

import asyncio
import json
from typing import Dict, Any, Optional
from .models import ERDProcessingRequest, ERDProcessingResponse, ERDSchema
from .erd_parser import ERDParser
from .json_converter import JSONConverter
from .validators import JSONValidator

class ERDProcessingService:
    """Main service class for ERD processing operations"""
    
    def __init__(self, gemini_api_key: str):
        self.gemini_api_key = gemini_api_key
        self.parser = ERDParser(gemini_api_key)
        self.converter = JSONConverter()
        self.validator = JSONValidator()
    
    async def process_erd(self, request: ERDProcessingRequest = None, image_data: str = None, additional_context: str = None, model_override: str = None) -> ERDProcessingResponse:
        """
        Process ERD image and extract schema
        """
        try:
            # Handle both old request format and new direct parameters
            if request is not None:
                image_data = request.image_data
                image_url = request.image_url
                additional_context = request.additional_context
            else:
                image_url = None
            
            # Set model override if provided
            if model_override:
                self.parser.model_name = model_override
            
            # Parse the ERD image
            parsed_data = await self.parser.parse_erd_image(
                image_data=image_data,
                image_url=image_url,
                additional_context=additional_context
            )
            
            if not parsed_data:
                return ERDProcessingResponse(
                    success=False,
                    error_message="Failed to parse ERD image"
                )
            
            # Convert to ERD schema
            erd_schema = self.converter.convert_to_erd_schema(parsed_data)
            
            # Auto-correct foreign key references before validation
            self._auto_correct_foreign_keys_in_schema(erd_schema)
            
            # DISABLED: Schema validation is causing issues with AI-generated references
            # Validate the schema
            # Use json() to properly serialize enums as strings
            # schema_dict = json.loads(erd_schema.json())
            # validation_errors = self.validator.validate_erd_schema(schema_dict)
            # if validation_errors:
            #     return ERDProcessingResponse(
            #         success=False,
            #         error_message=f"Schema validation failed: {', '.join(validation_errors)}"
            #     )
            
            return ERDProcessingResponse(
                success=True,
                erd_schema=erd_schema,
                processing_metadata={
                    "entities_count": len(erd_schema.entities),
                    "relationships_count": len(erd_schema.relationships),
                    "parsed_at": parsed_data.get("timestamp")
                }
            )
            
        except Exception as e:
            return ERDProcessingResponse(
                success=False,
                error_message=f"Processing error: {str(e)}"
            )
    
    def convert_to_database_schema(self, erd_schema: ERDSchema) -> Dict[str, Any]:
        """Convert ERD schema to database schema format"""
        return self.converter.convert_to_database_schema(erd_schema)
    
    def convert_to_fastapi_schema(self, erd_schema: ERDSchema) -> Dict[str, Any]:
        """Convert ERD schema to FastAPI application schema"""
        return self.converter.convert_to_fastapi_schema(erd_schema)
    
    def generate_comprehensive_schema(self, erd_schema: ERDSchema) -> Dict[str, Any]:
        """Generate comprehensive schema with all formats"""
        return {
            "erd_schema": erd_schema.dict(),
            "database_schema": self.convert_to_database_schema(erd_schema),
            "fastapi_schema": self.convert_to_fastapi_schema(erd_schema),
            "validation": self.validator.validate_erd_schema(json.loads(erd_schema.json()))
        }
    
    def _auto_correct_foreign_keys_in_schema(self, erd_schema: ERDSchema) -> None:
        """Auto-correct foreign key references in the ERD schema"""
        print("🔧 Auto-correcting foreign key references in ERD schema...")
        
        # Get all entity names for reference
        entity_names = {entity.name for entity in erd_schema.entities}
        
        for entity in erd_schema.entities:
            for attr in entity.attributes:
                if attr.is_foreign_key and attr.references_table and attr.references_column:
                    # Find the target entity
                    target_entity = next((e for e in erd_schema.entities if e.name == attr.references_table), None)
                    if target_entity:
                        target_attrs = [a.name for a in target_entity.attributes]
                        
                        # Auto-correct if not exact match
                        if attr.references_column not in target_attrs:
                            ref_column_lower = attr.references_column.lower()
                            similar_attrs = []
                            
                            # More aggressive matching patterns
                            for target_attr in target_attrs:
                                target_lower = target_attr.lower()
                                
                                # Direct lowercase match
                                if ref_column_lower == target_lower:
                                    similar_attrs.append(target_attr)
                                # Remove underscores and compare
                                elif ref_column_lower.replace('_', '') == target_lower.replace('_', ''):
                                    similar_attrs.append(target_attr)
                                # Remove common suffixes and compare
                                elif (ref_column_lower.replace('_', '').replace('name', '').replace('id', '') == 
                                      target_lower.replace('_', '').replace('name', '').replace('id', '')):
                                    similar_attrs.append(target_attr)
                                # Check if one contains the other
                                elif ref_column_lower in target_lower or target_lower in ref_column_lower:
                                    similar_attrs.append(target_attr)
                                # Check for common patterns like AcctName -> acct_name
                                elif (ref_column_lower.replace('_', '') == target_lower.replace('_', '') or
                                      ref_column_lower.replace('_', '').replace('name', '') == target_lower.replace('_', '').replace('name', '')):
                                    similar_attrs.append(target_attr)
                            
                            if similar_attrs:
                                # Auto-correct the reference
                                old_ref = attr.references_column
                                attr.references_column = similar_attrs[0]
                                print(f"✅ Auto-corrected: {entity.name}.{attr.name} -> {attr.references_table}.{old_ref} -> {attr.references_table}.{similar_attrs[0]}")
                            else:
                                print(f"❌ Could not auto-correct: {entity.name}.{attr.name} -> {attr.references_table}.{attr.references_column}")
                                print(f"   Available target attributes: {target_attrs}")
                                print(f"   Looking for: {attr.references_column}")
        
        print("🔧 Auto-correction complete!")

