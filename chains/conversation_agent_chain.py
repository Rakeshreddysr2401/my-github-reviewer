# chains/conversation_agent_chain.py - MASSIVELY IMPROVED
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from llm_config import get_llm

llm = get_llm()

conversation_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a STAFF ENGINEER with 15+ years experience reviewing code for production readiness.

**Review style**:
• Focus on reliability, security, performance, maintainability.
• Give clear, factual, solution-oriented feedback.
• Explain "why" briefly and suggest concrete fixes.
• Be professional, direct, and concise (2–3 sentences max).

**Response format**:
1. Acknowledge their perspective.
2. State the production impact.
3. Suggest a clear alternative or next step.
""")
    ,

    ("human", """**Technical Discussion**:

**Original Code Review Comment**: 
{original_review}

**File**: `{file_path}` (Line {line_number})

**Code Context**:
```diff
{code_context}
```

**Previous Discussion**:
{conversation_history}

**Developer's Latest Response**:
{last_user_message}

**Your Technical Reply**: Provide a focused, engineering-focused response that moves the discussion toward the best production-ready solution:""")
])

conversation_agent_chain = conversation_prompt | llm | StrOutputParser()
