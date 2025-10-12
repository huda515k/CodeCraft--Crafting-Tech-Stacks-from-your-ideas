# backend_generator/erd/utils.py

import base64
import hashlib
import re
from typing import Dict, Any, List, Optional
from PIL import Image
import io
import json
from datetime import datetime

class ImageProcessor:
    """Utility class for image processing operations"""
    
    @staticmethod
    def validate_image_format(image_data: str) -> bool:
        """Validate if image data is in supported format"""
        try:
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Check if format is supported
            supported_formats = ['PNG', 'JPEG', 'JPG', 'GIF', 'BMP']
            return image.format in supported_formats
        except Exception:
            return False
    
    @staticmethod
    def get_image_info(image_data: str) -> Optional[Dict[str, Any]]:
        """Get image information"""
        try:
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            return {
                "format": image.format,
                "size": image.size,
                "mode": image.mode,
                "file_size": len(image_bytes)
            }
        except Exception:
            return None
    
    @staticmethod
    def resize_image(image_data: str, max_size: tuple = (1024, 1024)) -> str:
        """Resize image while maintaining aspect ratio"""
        try:
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Calculate new size maintaining aspect ratio
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convert back to base64
            buffer = io.BytesIO()
            image.save(buffer, format=image.format)
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
        except Exception as e:
            raise ValueError(f"Failed to resize image: {str(e)}")
    
    @staticmethod
    def enhance_image_for_ocr(image_data: str) -> str:
        """Enhance image for better OCR results"""
        try:
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to grayscale
            if image.mode != 'L':
                image = image.convert('L')
            
            # Enhance contrast (simple histogram stretching)
            import numpy as np
            img_array = np.array(image)
            
            # Normalize to 0-255 range
            min_val = np.min(img_array)
            max_val = np.max(img_array)
            
            if max_val > min_val:
                img_array = ((img_array - min_val) / (max_val - min_val) * 255).astype(np.uint8)
            
            enhanced_image = Image.fromarray(img_array)
            
            # Convert back to base64
            buffer = io.BytesIO()
            enhanced_image.save(buffer, format='PNG')
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
            
        except Exception as e:
            # If enhancement fails, return original image
            return image_data

class NameConverter:
    """Utility class for name conversions and formatting"""
    
    @staticmethod
    def to_snake_case(name: str) -> str:
        """Convert string to snake_case"""
        # Replace spaces with underscores
        name = re.sub(r'\s+', '_', name)
        # Insert underscores before uppercase letters
        name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name)
        return name.lower()
    
    @staticmethod
    def to_pascal_case(name: str) -> str:
        """Convert string to PascalCase"""
        # Split by spaces, underscores, or hyphens
        words = re.split(r'[_\s-]+', name)
        return ''.join(word.capitalize() for word in words if word)
    
    @staticmethod
    def to_camel_case(name: str) -> str:
        """Convert string to camelCase"""
        pascal = NameConverter.to_pascal_case(name)
        return pascal[0].lower() + pascal[1:] if pascal else ''
    
    @staticmethod
    def to_kebab_case(name: str) -> str:
        """Convert string to kebab-case"""
        snake = NameConverter.to_snake_case(name)
        return snake.replace('_', '-')
    
    @staticmethod
    def pluralize(word: str) -> str:
        """Simple pluralization of English words"""
        if word.endswith('y'):
            return word[:-1] + 'ies'
        elif word.endswith(('s', 'sh', 'ch', 'x', 'z')):
            return word + 'es'
        elif word.endswith('f'):
            return word[:-1] + 'ves'
        elif word.endswith('fe'):
            return word[:-2] + 'ves'
        else:
            return word + 's'

class DataTypeInference:
    """Utility class for inferring data types from attribute names"""
    
    TYPE_PATTERNS = {
        'integer': [
            r'.*id', r'.*_id', r'count', r'.*count', r'number', r'.*number',
            r'age', r'year', r'quantity', r'amount', r'total', r'sum'
        ],
        'string': [
            r'name', r'.*name', r'title', r'.*title', r'description', r'.*description',
            r'email', r'.*email', r'phone', r'.*phone', r'address', r'.*address',
            r'url', r'.*url', r'code', r'.*code', r'status', r'type'
        ],
        'boolean': [
            r'is_.*', r'has_.*', r'can_.*', r'should_.*', r'.*_flag', r'active',
            r'enabled', r'disabled', r'visible', r'deleted'
        ],
        'date': [
            r'.*_date', r'date_.*', r'birthday', r'born_on'
        ],
        'datetime': [
            r'.*_at', r'.*_time', r'created_at', r'updated_at', r'deleted_at',
            r'timestamp', r'.*timestamp'
        ],
        'float': [
            r'price', r'.*price', r'cost', r'.*cost', r'rate', r'.*rate',
            r'percentage', r'.*percentage', r'weight', r'height', r'width',
            r'length', r'latitude', r'longitude'
        ],
        'text': [
            r'.*text', r'content', r'.*content', r'body', r'.*body',
            r'notes', r'.*notes', r'comments', r'.*comments'
        ],
        'uuid': [
            r'uuid', r'.*uuid', r'guid', r'.*guid'
        ]
    }
    
    @classmethod
    def infer_type(cls, attribute_name: str) -> str:
        """Infer data type from attribute name"""
        name_lower = attribute_name.lower()
        
        for data_type, patterns in cls.TYPE_PATTERNS.items():
            for pattern in patterns:
                if re.match(pattern, name_lower):
                    return data_type
        
        # Default to string if no pattern matches
        return 'string'
    
    @classmethod
    def suggest_constraints(cls, attribute_name: str, data_type: str) -> Dict[str, Any]:
        """Suggest constraints based on attribute name and type"""
        constraints = {}
        name_lower = attribute_name.lower()
        
        if data_type == 'string':
            if 'email' in name_lower:
                constraints['max_length'] = 255
                constraints['pattern'] = r'^[^@]+@[^@]+\.[^@]+$'
            elif 'phone' in name_lower:
                constraints['max_length'] = 20
            elif 'name' in name_lower:
                constraints['max_length'] = 100
            elif 'title' in name_lower:
                constraints['max_length'] = 200
            elif 'code' in name_lower:
                constraints['max_length'] = 50
            else:
                constraints['max_length'] = 255
        
        elif data_type == 'integer':
            if 'age' in name_lower:
                constraints['min_value'] = 0
                constraints['max_value'] = 150
            elif 'year' in name_lower:
                constraints['min_value'] = 1900
                constraints['max_value'] = 2100
        
        elif data_type == 'float':
            if any(x in name_lower for x in ['price', 'cost', 'amount']):
                constraints['min_value'] = 0.0
            elif any(x in name_lower for x in ['percentage', 'rate']):
                constraints['min_value'] = 0.0
                constraints['max_value'] = 100.0
        
        return constraints

class JSONSchemaGenerator:
    """Generate JSON Schema definitions for validation"""
    
    @staticmethod
    def generate_erd_json_schema() -> Dict[str, Any]:
        """Generate JSON Schema for ERD structure validation"""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "ERD Schema",
            "type": "object",
            "properties": {
                "project_name": {
                    "type": ["string", "null"],
                    "description": "Name of the project"
                },
                "entities": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "$ref": "#/definitions/entity"
                    }
                },
                "relationships": {
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/relationship"
                    }
                },
                "metadata": {
                    "type": "object",
                    "description": "Additional metadata"
                }
            },
            "required": ["entities"],
            "definitions": {
                "entity": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "minLength": 1,
                            "description": "Entity name (any valid format)"
                        },
                        "attributes": {
                            "type": "array",
                            "minItems": 1,
                            "items": {
                                "$ref": "#/definitions/attribute"
                            }
                        },
                        "table_name": {
                            "type": ["string", "null"],
                            "description": "Database table name"
                        }
                    },
                    "required": ["name", "attributes"]
                },
                "attribute": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "minLength": 1,
                            "description": "Attribute name (any valid format)"
                        },
                        "data_type": {
                            "enum": [
                                "string", "integer", "float", "boolean", "date", "datetime", "text", "json", "uuid",
                                "decimal", "enum", "array", "time", "blob", "binary", "char", "varchar", "longtext",
                                "tinyint", "smallint", "bigint", "double", "real", "timestamp", "year", "set"
                            ],
                            "description": "Data type of the attribute"
                        },
                        "is_primary_key": {
                            "type": "boolean",
                            "default": False
                        },
                        "is_foreign_key": {
                            "type": "boolean",
                            "default": False
                        },
                        "is_nullable": {
                            "type": "boolean",
                            "default": True
                        },
                        "is_unique": {
                            "type": "boolean",
                            "default": False
                        },
                        "max_length": {
                            "type": ["integer", "null"],
                            "minimum": 1
                        },
                        "default_value": {
                            "description": "Default value for the attribute"
                        },
                        "references_table": {
                            "type": ["string", "null"],
                            "description": "Referenced table for foreign keys"
                        },
                        "references_column": {
                            "type": ["string", "null"],
                            "description": "Referenced column for foreign keys"
                        }
                    },
                    "required": ["name", "data_type"]
                },
                "relationship": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": ["string", "null"],
                            "description": "Relationship name"
                        },
                        "source_entity": {
                            "type": "string",
                            "description": "Source entity name"
                        },
                        "target_entity": {
                            "type": "string",
                            "description": "Target entity name"
                        },
                        "relationship_type": {
                            "enum": ["1:1", "1:N", "N:1", "M:N", "N:N", "M:1", "1:M", "M:M"],
                            "description": "Type of relationship"
                        }
                    },
                    "required": ["source_entity", "target_entity", "relationship_type"]
                }
            }
        }

class HashGenerator:
    """Generate hashes for caching and deduplication"""
    
    @staticmethod
    def generate_schema_hash(erd_schema: Dict[str, Any]) -> str:
        """Generate hash for ERD schema for caching purposes"""
        # Sort the schema to ensure consistent hashing
        schema_str = json.dumps(erd_schema, sort_keys=True)
        return hashlib.sha256(schema_str.encode()).hexdigest()
    
    @staticmethod
    def generate_image_hash(image_data: str) -> str:
        """Generate hash for image data"""
        return hashlib.md5(image_data.encode()).hexdigest()

class ConfigManager:
    """Configuration management utilities"""
    
    DEFAULT_CONFIG = {
        "max_image_size": 10 * 1024 * 1024,  # 10MB
        "supported_formats": ["PNG", "JPEG", "JPG", "GIF", "BMP"],
        "default_data_type": "string",
        "auto_add_id": True,
        "auto_add_timestamps": True,
        "naming_convention": {
            "entities": "PascalCase",
            "attributes": "snake_case",
            "tables": "snake_case"
        },
        "gemini_model": "gemini-1.5-pro",
        "enable_ocr_fallback": True,
        "cache_enabled": True
    }
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Get current configuration"""
        # In a real implementation, this would load from environment variables
        # or configuration files
        return cls.DEFAULT_CONFIG.copy()
    
    @classmethod
    def validate_config(cls, config: Dict[str, Any]) -> List[str]:
        """Validate configuration parameters"""
        errors = []
        
        if "max_image_size" in config:
            if not isinstance(config["max_image_size"], int) or config["max_image_size"] <= 0:
                errors.append("max_image_size must be a positive integer")
        
        if "supported_formats" in config:
            if not isinstance(config["supported_formats"], list):
                errors.append("supported_formats must be a list")
        
        return errors

