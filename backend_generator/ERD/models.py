# backend_generator/erd/models.py

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class DataType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    TEXT = "text"
    JSON = "json"
    UUID = "uuid"
    DECIMAL = "decimal"
    ENUM = "enum"
    ARRAY = "array"
    TIME = "time"
    BLOB = "blob"
    BINARY = "binary"
    CHAR = "char"
    VARCHAR = "varchar"
    LONGTEXT = "longtext"
    TINYINT = "tinyint"
    SMALLINT = "smallint"
    BIGINT = "bigint"
    DOUBLE = "double"
    REAL = "real"
    TIMESTAMP = "timestamp"
    YEAR = "year"
    SET = "set"

class RelationshipType(str, Enum):
    ONE_TO_ONE = "1:1"
    ONE_TO_MANY = "1:N"
    MANY_TO_ONE = "N:1"
    MANY_TO_MANY = "M:N"
    # Common variations that AI might return
    ONE_TO_MANY_IDENTIFYING = "1:N (Identifying)"
    ONE_TO_MANY_NON_IDENTIFYING = "1:N (Non-Identifying)"
    MANY_TO_ONE_IDENTIFYING = "N:1 (Identifying)"
    MANY_TO_ONE_NON_IDENTIFYING = "N:1 (Non-Identifying)"
    ONE_TO_ONE_IDENTIFYING = "1:1 (Identifying)"
    ONE_TO_ONE_NON_IDENTIFYING = "1:1 (Non-Identifying)"
    MANY_TO_MANY_IDENTIFYING = "M:N (Identifying)"
    MANY_TO_MANY_NON_IDENTIFYING = "M:N (Non-Identifying)"
    # Additional common patterns
    ONE_TO_MANY_OPTIONAL = "1:N (Optional)"
    # AI might return N:N instead of M:N
    MANY_TO_MANY_ALT = "N:N"
    # AI might return M:1 instead of N:1
    MANY_TO_ONE_ALT = "M:1"
    # AI might return 1:M instead of 1:N
    ONE_TO_MANY_ALT = "1:M"
    # AI might return M:M instead of M:N
    MANY_TO_MANY_ALT2 = "M:M"
    ONE_TO_MANY_REQUIRED = "1:N (Required)"
    MANY_TO_ONE_OPTIONAL = "N:1 (Optional)"
    MANY_TO_ONE_REQUIRED = "N:1 (Required)"

class Attribute(BaseModel):
    name: str = Field(..., description="Attribute name")
    data_type: DataType = Field(..., description="Data type of the attribute")
    is_primary_key: bool = Field(default=False, description="Whether this is a primary key")
    is_foreign_key: bool = Field(default=False, description="Whether this is a foreign key")
    is_nullable: bool = Field(default=True, description="Whether the field can be null")
    is_unique: bool = Field(default=False, description="Whether the field must be unique")
    max_length: Optional[int] = Field(default=None, description="Maximum length for string types")
    default_value: Optional[Any] = Field(default=None, description="Default value")
    references_table: Optional[str] = Field(default=None, description="Referenced table for FK")
    references_column: Optional[str] = Field(default=None, description="Referenced column for FK")

class Entity(BaseModel):
    name: str = Field(..., description="Entity name")
    attributes: List[Attribute] = Field(..., description="List of entity attributes")
    table_name: Optional[str] = Field(default=None, description="Database table name")

class Relationship(BaseModel):
    name: Optional[str] = Field(default=None, description="Relationship name")
    source_entity: str = Field(..., description="Source entity name")
    target_entity: str = Field(..., description="Target entity name")
    relationship_type: RelationshipType = Field(..., description="Type of relationship")
    source_cardinality: Optional[str] = Field(default=None, description="Source cardinality")
    target_cardinality: Optional[str] = Field(default=None, description="Target cardinality")

class ERDSchema(BaseModel):
    project_name: Optional[str] = Field(default=None, description="Project name")
    entities: List[Entity] = Field(..., description="List of entities in the ERD")
    relationships: List[Relationship] = Field(..., description="List of relationships")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

class ERDProcessingRequest(BaseModel):
    image_data: Optional[str] = Field(default=None, description="Base64 encoded image data")
    image_url: Optional[str] = Field(default=None, description="URL to the ERD image")
    additional_context: Optional[str] = Field(default=None, description="Additional context or instructions")

class ERDProcessingResponse(BaseModel):
    success: bool = Field(..., description="Whether processing was successful")
    erd_schema: Optional[ERDSchema] = Field(default=None, description="Extracted ERD schema")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    processing_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Processing metadata")

