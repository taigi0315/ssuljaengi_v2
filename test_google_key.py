import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv('backend/.env')

api_key = os.getenv('GOOGLE_API_KEY')
print(f"Testing API Key: {api_key[:10]}...")

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Hello, can you hear me?")
    print("Success! Response:", response.text)
except Exception as e:
    print("Error:", str(e))
