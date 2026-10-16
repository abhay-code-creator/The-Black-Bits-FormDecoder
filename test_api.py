# test_api.py
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

with open("test.jpg", "rb") as f:
    img_bytes = f.read()

resp = client.models.generate_content(
    model="gemma-4-26b-a4b-it",
    contents=[
        types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"),
        "What text is in this image?"
    ]
)
print(resp.text)