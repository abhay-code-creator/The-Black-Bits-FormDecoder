
import io
import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image, ImageOps

load_dotenv()

MODEL_ID = "gemma-4-26b-a4b-it"
FALLBACK_MODEL = "gemini-2.5-flash"


def _get_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY was not found in your .env file."
        )

    return genai.Client(api_key=api_key)


def prepare_image(uploaded_file):
    image = Image.open(uploaded_file)
    image = ImageOps.exif_transpose(image)

    image.thumbnail((1024, 1024))

    buffer = io.BytesIO()
    image.convert("RGB").save(
        buffer,
        format="JPEG",
        quality=85
    )

    return buffer.getvalue()


def _get_prompt(language):
    if language == "हिंदी":
        return """
You explain paper forms to ordinary people in simple Hindi.

Analyze visible fields. Explain what the applicant should enter.
Never invent unreadable information. Mark unclear fields as unclear.
Suggest documents cautiously and advise verification with the
relevant institution.

Return ONLY valid JSON:
{
  "form_type": "फॉर्म का प्रकार",
  "fields": [
    {
      "name": "फील्ड का नाम",
      "explanation": "क्या भरना है",
      "example": "उदाहरण"
    }
  ],
  "documents_needed": ["दस्तावेज का नाम"],
  "warnings": ["महत्वपूर्ण सूचना"]
}

All values must be in Hindi using Devanagari script.
Do not return Markdown fences or additional text.
"""

    return """
You explain paper forms to ordinary people in simple English.

Analyze visible fields. Explain what the applicant should enter.
Never invent unreadable information. Mark unclear fields as unclear.
Suggest documents cautiously and advise verification with the
relevant institution.

Return ONLY valid JSON:
{
  "form_type": "Type of form",
  "fields": [
    {
      "name": "Field name",
      "explanation": "What to enter",
      "example": "Example"
    }
  ],
  "documents_needed": ["Document name"],
  "warnings": ["Important warning"]
}

All values must be in English.
Do not return Markdown fences or additional text.
"""


def _parse_response(response_text):
    text = response_text.strip()

    if text.startswith("```"):
        lines = text.splitlines()
        lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

        if text.lower().startswith("json"):
            text = text[4:].strip()

    data = json.loads(text)

    if not isinstance(data, dict):
        raise ValueError("The AI response must be a JSON object.")

    if not isinstance(data.get("fields", []), list):
        raise ValueError("The fields property must be a list.")

    if not isinstance(data.get("documents_needed", []), list):
        raise ValueError("The documents_needed property must be a list.")

    if not isinstance(data.get("warnings", []), list):
        raise ValueError("The warnings property must be a list.")

    return data


def _request_model(client, model_name, image_bytes, language):
    response = client.models.generate_content(
        model=model_name,
        contents=[
            types.Part.from_bytes(
                data=image_bytes,
                mime_type="image/jpeg"
            ),
            (
                "Explain this form field by field. Identify visible "
                "fields, explain what to enter, provide examples, "
                "and list potentially relevant documents and warnings."
            )
        ],
        config=types.GenerateContentConfig(
            system_instruction=_get_prompt(language),
            temperature=0.2
        )
    )

    if not response.text:
        raise ValueError("The AI model returned an empty response.")

    return _parse_response(response.text)


def analyze_form(uploaded_file, language="English"):
    if language not in ("English", "हिंदी"):
        raise ValueError("Unsupported language selected.")

    image_bytes = prepare_image(uploaded_file)
    client = _get_client()

    try:
        return _request_model(
            client,
            MODEL_ID,
            image_bytes,
            language
        )
    except Exception as primary_error:
        try:
            return _request_model(
                client,
                FALLBACK_MODEL,
                image_bytes,
                language
            )
        except Exception as fallback_error:
            raise RuntimeError(
                "Both AI models failed. "
                f"Primary error: {primary_error}. "
                f"Fallback error: {fallback_error}."
            ) from fallback_error
