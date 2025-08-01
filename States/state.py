# States/state.py
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Literal
from services.git_services.get_pr_details import PRDetails


class Change(BaseModel):
    """Represents a single change line in a diff."""
    content: str = ""
    line_number: Optional[int] = None
    diff_position: Optional[int] = None
    suggested_code: Optional[str] = None
    suggested_comment: Optional[str] = None


class Chunk(BaseModel):
    """Represents a chunk/hunk in a diff."""
    content: str = ""
    changes: List[Change] = Field(default_factory=list)
    guidelines: str = ""
    source_start: int = 0
    source_length: int = 0
    target_start: int = 0
    target_length: int = 0
    formatted_chunk: Optional[List[str]] = Field(default_factory=list)
    generated_code_snippet: Optional[str] = None
    generated_review_comment: Optional[str] = None


class File(BaseModel):
    """Represents a file in a diff."""
    from_file: Optional[str] = None
    to_file: Optional[str] = None
    chunks: List[Chunk] = Field(default_factory=list)

class ReviewComment(BaseModel):
    lineNumber: int = Field(..., description="Line number of the code to comment on")
    reviewComment: str = Field(..., description="Actual review comment")


class ReviewResponse(BaseModel):
    reviews: List[ReviewComment] = Field(default_factory=list, description="List of review comments on the code diff")

class ReviewFeedback(BaseModel):
    satisfied: bool = Field(..., description="False if the answer needs to be retried.")
    critique: Optional[str] = Field(default=None, description="Brief critique of the response, if any.")
    suggestions: Optional[List[str]] = Field(default_factory=list, description="List of specific suggestions for improvement.")


class ReviewState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    messages: List[BaseMessage] = Field(default_factory=list)
    pr_details: PRDetails
    files: Optional[List[File]] = []
    current_file_index: int = 0
    current_chunk_index: int = 0
    current_prompt: Optional[str] = None
    llm_response: Optional[ReviewResponse] = None
    comments: List[dict] = Field(default_factory=list)
    guidelines_store: Optional[Any] = None
    done: bool = False
    retry_count: int = 0
    satisfied: bool = False
    final_response: Optional[str] = None
    review_feedback: Optional[ReviewFeedback] = None
    next_agent: Optional[str] = None

    context_prompt: str = ""
    generated_reply: str = ""

    history_id: int = None
    current_id: int= None
    current_message: Optional[str] = None
    current_diff_hunk: Optional[str] = None
