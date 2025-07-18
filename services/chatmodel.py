import os
import json
from typing import List, Dict
from openai import OpenAI
from utils.logger import get_logger

log = get_logger()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_ai_response(prompt: str) -> List[Dict[str, str]]:
    """Sends the prompt to OpenAI API and retrieves the response."""
    model = os.getenv("OPENAI_MODEL", "gpt-4o")
    log.info(f"Using OpenAI model: {model}")

    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0.7,
            max_tokens=4000,
            messages=[
                {"role": "system", "content": "You are an expert code reviewer. Provide feedback in the requested JSON format."},
                {"role": "user", "content": prompt}
            ]
        )
        response_text = response.choices[0].message.content.strip()

        # Clean code block if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        try:
            data = json.loads(response_text)

            if isinstance(data, dict) and "reviews" in data and isinstance(data["reviews"], list):
                return [
                    review for review in data["reviews"]
                    if "lineNumber" in review and "reviewComment" in review
                ]
            else:
                log.warning("Response missing valid 'reviews' list")
                return []
        except json.JSONDecodeError as e:
            log.error(f"JSON decode failed: {e}")
            return []
    except Exception as e:
        log.exception("OpenAI API call failed")
        raise
