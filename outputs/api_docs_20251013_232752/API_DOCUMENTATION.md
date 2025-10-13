# Backend API Documentation

Comprehensive API documentation generated from backend analysis

**Base URL:** http://localhost:3000

## Authentication

**Method:** JSON Web Token (JWT)

**How to authenticate:** Include JWT token in Authorization header

## API Endpoints

### GET /account
- **Method:** GET
- **Path:** /account
- **Description:** GET /account
- **Handler:** Function in file

### POST /account
- **Method:** POST
- **Path:** /account
- **Description:** POST /account
- **Handler:** Function in file

### GET /character
- **Method:** GET
- **Path:** /character
- **Description:** GET /character
- **Handler:** Function in file

### POST /character
- **Method:** POST
- **Path:** /character
- **Description:** POST /character
- **Handler:** Function in file

### GET /region
- **Method:** GET
- **Path:** /region
- **Description:** GET /region
- **Handler:** Function in file

### POST /region
- **Method:** POST
- **Path:** /region
- **Description:** POST /region
- **Handler:** Function in file

### GET /item
- **Method:** GET
- **Path:** /item
- **Description:** GET /item
- **Handler:** Function in file

### POST /item
- **Method:** POST
- **Path:** /item
- **Description:** POST /item
- **Handler:** Function in file

### GET /item_instantiation
- **Method:** GET
- **Path:** /item_instantiation
- **Description:** GET /item_instantiation
- **Handler:** Function in file

### POST /item_instantiation
- **Method:** POST
- **Path:** /item_instantiation
- **Description:** POST /item_instantiation
- **Handler:** Function in file

### GET /creep
- **Method:** GET
- **Path:** /creep
- **Description:** GET /creep
- **Handler:** Function in file

### POST /creep
- **Method:** POST
- **Path:** /creep
- **Description:** POST /creep
- **Handler:** Function in file

### GET /creep_instantiation
- **Method:** GET
- **Path:** /creep_instantiation
- **Description:** GET /creep_instantiation
- **Handler:** Function in file

### POST /creep_instantiation
- **Method:** POST
- **Path:** /creep_instantiation
- **Description:** POST /creep_instantiation
- **Handler:** Function in file

### GET /character_creep_encounter
- **Method:** GET
- **Path:** /character_creep_encounter
- **Description:** GET /character_creep_encounter
- **Handler:** Function in file

### POST /character_creep_encounter
- **Method:** POST
- **Path:** /character_creep_encounter
- **Description:** POST /character_creep_encounter
- **Handler:** Function in file

## Data Models

### Account
- **Type:** Data Model
- **Description:** Data model: Account

### CharacterCreepEncounter
- **Type:** Data Model
- **Description:** Data model: CharacterCreepEncounter

### Item
- **Type:** Data Model
- **Description:** Data model: Item

### ItemInstantiation
- **Type:** Data Model
- **Description:** Data model: ItemInstantiation

### Character
- **Type:** Data Model
- **Description:** Data model: Character

### Creep
- **Type:** Data Model
- **Description:** Data model: Creep

### Region
- **Type:** Data Model
- **Description:** Data model: Region

### index
- **Type:** Data Model
- **Description:** Data model: index

### CreepInstantiation
- **Type:** Data Model
- **Description:** Data model: CreepInstantiation

## Error Handling
- **400:** Bad Request - Invalid input data
- **401:** Unauthorized - Authentication required
- **403:** Forbidden - Insufficient permissions
- **404:** Not Found - Resource not found
- **500:** Internal Server Error - Server error