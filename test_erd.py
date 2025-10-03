# test_erd.py
import asyncio
import base64
from backend_generator.erd.services import ERDProcessingService
from backend_generator.erd.models import ERDProcessingRequest

async def test_erd_processing():
    service = ERDProcessingService("your_gemini_api_key")
    
    # Test with sample image
    with open("sample_erd.png", "rb") as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    request = ERDProcessingRequest(image_data=image_data)
    result = await service.process_erd(request)
    
    print(f"Success: {result.success}")
    if result.success:
        print(f"Entities: {len(result.erd_schema.entities)}")

# Run test
if __name__ == "__main__":
    asyncio.run(test_erd_processing())

