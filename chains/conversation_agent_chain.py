# chains/conversation_agent_chain.py - SHORT & CLEAR VERSION
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from llm_config import get_llm

llm = get_llm()

conversation_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a STAFF ENGINEER reviewing code for production readiness.

**Review style**:
• Focus on reliability, security, performance, maintainability.
• Keep responses short: 2–3 sentences max.
• Be factual, professional, and solution-oriented.
• Briefly explain the "why" and suggest a concrete fix.
• Avoid unnecessary detail or repetition.

**Response format**:
1. Acknowledge their perspective.
2. State the production impact.
3. Suggest the fix or next step.
"""),

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
