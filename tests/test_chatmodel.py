import os
import pytest
from dotenv import load_dotenv
from services.chatmodel import get_ai_response

# Load .env file to get OPENAI_API_KEY and OPENAI_MODEL
load_dotenv()

@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set in environment")
def test_get_ai_response_returns_valid_reviews():
    prompt = """
    Please review this Python code and return JSON with 'reviews' key containing lineNumber and reviewComment:
    ```python
    def add(x, y):
        return x + y

    print(add(2, 3))
    ```
    """

    reviews = get_ai_response(prompt)

    assert isinstance(reviews, list), "Expected a list of reviews"
    assert all("lineNumber" in r and "reviewComment" in r for r in reviews), "Each review should contain 'lineNumber' and 'reviewComment'"
    assert len(reviews) > 0, "At least one review should be returned"

    # Optional: Log to console for verification
    for r in reviews:
        print(f"Line {r['lineNumber']}: {r['reviewComment']}")
