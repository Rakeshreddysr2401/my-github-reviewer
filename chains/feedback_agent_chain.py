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
You are a **feedback assistant**. Your role is to evaluate whether the AI code reviewer assistant gave a high-quality, useful review comment on a code diff.

You have access to:
- The original code diff the AI was reviewing.
- The full conversation history between user and the reviewer.
- The AI reviewer’s final response.

Please assess:
1. Does the reviewer correctly reference the diff content (only added lines)?
2. Are the suggestions actionable and technically sound?
3. Are the comments clearly written and under 120 words each?
4. Are the comments aligned with any coding guidelines (if present in the history)?
5. Would the review help improve code quality (e.g., bugs, performance, clarity, style)?

If any issues exist, return `satisfied=False` with critique and suggestions.
If the response is good enough, return `satisfied=True`.

Respond in the following JSON format:
{format_instructions}

Git Diff:
{user_query}

Provided Guidelines if applicable:
{guidelines}

AI Reviewer Final Response:
{ai_response}
""",
    partial_variables={
        "format_instructions": format_instructions
    }
)

# Final chain: Prompt → LLM → Pydantic parser
feedback_agent_chain = feedback_prompt | llm | parser