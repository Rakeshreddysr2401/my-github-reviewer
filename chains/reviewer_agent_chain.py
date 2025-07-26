# chains/reviewer_agent_chain.py

from dotenv import load_dotenv

load_dotenv()

from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List
from llm_config import get_llm

llm = get_llm()


class ReviewComment(BaseModel):
    lineNumber: int = Field(..., description="Line number of the code to comment on")
    reviewComment: str = Field(..., description="Actual review comment")


class ReviewResponse(BaseModel):
    reviews: List[ReviewComment] = Field(default=[], description="List of review comments on the code diff")


parser = PydanticOutputParser(pydantic_object=ReviewResponse)
format_instructions = parser.get_format_instructions()

reviewer_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert **code reviewer**. Provide feedback in the requested JSON format.

{format_instructions}

Instructions:
- Only reference added lines (those starting with '+') in the diff
- Only add a comment if improvement is needed (bugs, performance, security, style)
- Use GitHub Markdown formatting
- Do NOT suggest adding comments in the code
- Look at Previous Response Suggestions and critique
"""),
    ("human", """Review the following code diff in file: "{file_path}"
Pull request title: {pr_title}
Pull request description: {pr_description}

{guidelines_section}

The previous response had issues:
{critique}

Suggestions for improvement:
{suggestion_text}

Git diff to review:
```diff
{code_diff}
```""")
])
reviewer_prompt = reviewer_prompt.partial(format_instructions=format_instructions)
reviewer_agent_chain = reviewer_prompt | llm | parser
