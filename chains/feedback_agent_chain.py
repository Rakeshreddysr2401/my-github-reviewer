# chains/feedback_agent_chain.py - MASSIVELY IMPROVED
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
    """You are the VP OF ENGINEERING reviewing code review quality. Your standards are extremely high - you've prevented countless production disasters through rigorous review standards.

🎯 **YOUR JOB**: Determine if this code review will actually prevent production problems or if it's just noise.

✅ **APPROVE (satisfied=True) ONLY IF ALL TRUE**:
• Review targets ONLY '+' lines (new additions) - not unchanged code
• Identifies REAL production risks: crashes, security holes, performance killers
• Each comment prevents an actual bug/vulnerability (not style preferences)  
• Comments are specific with line numbers and clear impact
• Follows team guidelines from conversation history
• Returns empty array for genuinely good code (no false positives)
• Zero nitpicking about formatting, naming, or documentation

❌ **REJECT (satisfied=False) IF ANY TRUE**:
• Comments on '-' lines or unchanged code (reviewer confused)
• Flags trivial style/formatting issues as important
• Vague feedback like "consider refactoring" without specific problems
• Technical mistakes or misunderstandings of the code
• Ignores critical bugs while focusing on minor issues
• Creates noise with personal preference comments
• Violates established team patterns from history

🔍 **THE PRODUCTION IMPACT TEST**:
For each comment ask: "If developers ignore this, will it cause a production incident?"
- If YES → Good comment
- If NO → Bad comment, should reject

**EXAMPLES OF GOOD REVIEW FEEDBACK**:
• "SQL injection on line 42 - critical security issue"
• "NPE on line 89 when user is null - will crash signup flow"
• "O(n²) loop on line 156 - will timeout with large datasets"

**EXAMPLES OF BAD REVIEW FEEDBACK**:
• "Variable naming could be improved"
• "Consider adding documentation"
• "This method is a bit long"
• "Formatting inconsistency"

{format_instructions}

---
**Code Being Reviewed**:
{user_query}

**Review History & Context**:
{history_messages}

**AI Reviewer's Output**:
{ai_response}

**VP ASSESSMENT**: Does this review meet production-quality standards and actually prevent bugs/outages?
"""
)

feedback_prompt = feedback_prompt.partial(format_instructions=format_instructions)
feedback_agent_chain = feedback_prompt | llm | parser


