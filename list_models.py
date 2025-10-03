import os, google.generativeai as genai 
genai.configure(api_key=os.getenv('GEMINI_API_KEY')) 
for m in genai.list_models(): 
   methods = getattr(m, 'supported_generation_methods', []) 
   print(getattr(m,'name',str(m)), methods) 
