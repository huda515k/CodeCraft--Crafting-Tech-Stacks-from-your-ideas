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
    
    async def process_erd(self, request: ERDProcessingRequest) -> ERDProcessingResponse:
        """
        Process ERD image and extract schema
        """
        try:
            # Parse the ERD image
            parsed_data = await self.parser.parse_erd_image(
                image_data=request.image_data,
                image_url=request.image_url,
                additional_context=request.additional_context
            )
            
            if not parsed_data:
                return ERDProcessingResponse(
                    success=False,
                    error_message="Failed to parse ERD image"
                )
            
            # Convert to ERD schema
            erd_schema = self.converter.convert_to_erd_schema(parsed_data)
            
            # Validate the schema
            # Use json() to properly serialize enums as strings
            schema_dict = json.loads(erd_schema.json())
            validation_errors = self.validator.validate_erd_schema(schema_dict)
            if validation_errors:
                return ERDProcessingResponse(
                    success=False,
                    error_message=f"Schema validation failed: {', '.join(validation_errors)}"
                )
            
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

