import json
from typing import List, Dict
from langchain_core.messages import SystemMessage, HumanMessage
from llm_config import get_llm
from utils.logger import get_logger

log = get_logger()

def code_reviewer_agent(prompt: str) -> List[Dict[str, str]]:
    llm=get_llm()
    messages = [
        SystemMessage(content="You are an expert code reviewer. Provide feedback in the requested JSON format."),
        HumanMessage(content=prompt)
    ]
    response = llm.invoke(messages)
    response_text = response.content.strip()
    return _parse_review_json(response_text)

def _parse_review_json(response_text: str) -> List[Dict[str, str]]:
    """Parses the LLM's raw response string into a validated list of review comments."""
    # Clean Markdown-style JSON block
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
        elif isinstance(data, list):
            return [
                review for review in data
                if "lineNumber" in review and "reviewComment" in review
            ]
        else:
            log.warning("Invalid review structure in response")
            return []
    except json.JSONDecodeError as e:
        log.error(f"Failed to parse JSON: {e}")
        return []
