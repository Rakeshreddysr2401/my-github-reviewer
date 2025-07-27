# chains/feedback_agent_chain.py
from dotenv import load_dotenv
from States.state import ReviewFeedback

load_dotenv()
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from llm_config import get_llm

llm = get_llm()
parser = PydanticOutputParser(pydantic_object=ReviewFeedback)
format_instructions = parser.get_format_instructions()

feedback_prompt = PromptTemplate.from_template(
    """
You are a **feedback evaluator**. Your job is to verify whether the code review provided by the AI is helpful, accurate, and aligned with team expectations.

You will be given:
- A Git code diff
- A history of the review conversation
- The final AI review output

✅ Mark `satisfied=True` if:
- The review refers only to ADDED lines (`+`)
- It points out REAL problems: bugs, security risks, performance, major readability issues
- Each review comment is under 120 words, actionable, and technically sound
- Comments follow the coding guidelines from history (if present)
- The AI returns an empty `reviews` array for clean code

❌ Mark `satisfied=False` if:
- Comments are vague or unrelated to the actual code diff
- It flags minor or trivial issues as major ones
- It gives incorrect or misleading feedback
- Comments violate or ignore shared guidelines

Always use this JSON output format:
{format_instructions}

---
Git Code Diff:
{user_query}

Conversation History:
{history_messages}

Final AI Reviewer Response:
{ai_response}
"""
)

feedback_agent_chain = feedback_prompt | llm | parser
