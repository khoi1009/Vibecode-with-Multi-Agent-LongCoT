
import google.generativeai as genai
import os

API_KEY = "AIzaSyAiWFWfavyEuWWSi0ySW_7N5GFGK4K-SK0"

genai.configure(api_key=API_KEY)

print("Listing available models...")
try:
    with open("models_log.txt", "w") as f:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
                f.write(f"{m.name}\n")
            
except Exception as e:
    with open("models_log.txt", "w") as f:
        f.write(f"Error: {e}")
