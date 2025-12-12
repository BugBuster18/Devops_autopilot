import os
import dotenv
from google import genai
from google.genai import types
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / '.env'
print(f"Loading .env from: {env_path}")
dotenv.load_dotenv(env_path)

print(f"CODERABBIT_API_KEY: {os.getenv('CODERABBIT_API_KEY')}")
print(f"GOOGLE_API_KEY: {os.getenv('GOOGLE_API_KEY')}")

try:
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    print("Client created.")
    print("Searching for 'video' in client.models attributes:")
    attrs = dir(client.models)
    video_methods = [m for m in attrs if 'video' in m.lower()]
    print(f"Video methods: {video_methods}")
    
    if hasattr(types, "GenerateVideosConfig"):
        print("types.GenerateVideosConfig exists.")
    else:
        print("types.GenerateVideosConfig DOES NOT exist.")

    print("All attributes:")
    print(attrs)
except Exception as e:
    print(f"Error: {e}")
