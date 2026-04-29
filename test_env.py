import os
from dotenv import load_dotenv

load_dotenv()

my_secret_key = os.getenv("API_KEY")

if my_secret_key:
    print("✅ SUCCESS! Python found your secret API Key without exposing it in the code!")
    print(f"The first 5 characters of your key are: {my_secret_key[:5]}...")
else:
    print("❌ ERROR: Could not find the API Key. Check your .env file.")