# backend_generator/test_erd_module.py

import asyncio
import base64
from .erd.services import ERDProcessingService
from .erd.models import ERDProcessingRequest

async def test_erd_processing():
    """Test ERD processing functionality"""
    service = ERDProcessingService("AIzaSyDouU_AFueIGyjEE2btH6-qsNEHfVtt8tc")
    
    # Test with sample image
    try:
        with open("sample_erd.png", "rb") as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        request = ERDProcessingRequest(image_data=image_data)
        result = await service.process_erd(request)
        
        print(f"Success: {result.success}")
        if result.success:
            print(f"Entities: {len(result.erd_schema.entities)}")
            print(f"Relationships: {len(result.erd_schema.relationships)}")
        else:
            print(f"Error: {result.error_message}")
            
    except FileNotFoundError:
        print("Sample ERD image not found. Please provide a sample_erd.png file.")
    except Exception as e:
        print(f"Test failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_erd_processing())

