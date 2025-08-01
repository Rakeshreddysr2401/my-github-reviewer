from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from llm_config import get_llm

llm = get_llm()

conversation_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an AI code reviewer having a conversation with a developer about code quality.

You previously made a review comment, and the developer has replied. Your job is to:
1. Acknowledge their response
2. Clarify if needed
3. Suggest improvements if relevant
4. Be collaborative and concise
5. Maintain a constructive, helpful tone

You are part of a GitHub PR review thread, so keep your message specific and actionable.
"""),

    ("human", """Here's the full context:

- **Original Review Comment**: {original_review}
- **File**: {file_path}
- **Line**: {line_number}

- **Code Context**:
{code_context}

- **Conversation History**:
{conversation_history}

- **Latest User Message**:
{last_user_message}

Write a thoughtful reply to continue the conversation:""")
])

conversation_agent_chain = conversation_prompt | llm | StrOutputParser()
