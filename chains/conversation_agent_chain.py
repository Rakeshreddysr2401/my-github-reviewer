# chains/conversation_agent_chain.py (new file needed)
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from llm_config import get_llm

llm = get_llm()

conversation_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an AI code reviewer having a conversation with a developer about code quality. 
    You previously made a review comment, and the developer has replied. Your job is to:

    1. Acknowledge their response thoughtfully
    2. Provide additional clarification if needed
    3. Suggest improvements or alternatives if appropriate
    4. Be helpful and constructive in your tone
    5. Keep responses concise but informative

    Remember: You're having a conversation, not just reviewing code. Be collaborative."""),

    ("human", """Here's the conversation context:

Original Review Comment: {original_review}

File: {file_path}
Line: {line_number}

Code Context:
{code_context}

Conversation History:
{conversation_history}

Latest User Message: {last_user_message}

Please provide a thoughtful response to continue this conversation:""")
])

conversation_agent_chain = conversation_prompt | llm | StrOutputParser()