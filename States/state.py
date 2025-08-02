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
    """Structured review comment with validation."""
    lineNumber: int = Field(..., description="Line number of the code to comment on", gt=0)
    reviewComment: str = Field(..., description="Actual review comment", min_length=10, max_length=500)


class ReviewResponse(BaseModel):
    """Collection of review comments with validation."""
    reviews: List[ReviewComment] = Field(
        default_factory=list,
        description="List of review comments on the code diff",
        max_items=5  # Limit to prevent spam
    )


class ReviewFeedback(BaseModel):
    """Feedback on review quality with detailed critique."""
    satisfied: bool = Field(..., description="False if the answer needs to be retried.")
    critique: Optional[str] = Field(
        default=None,
        description="Brief critique of the response, if any.",
        max_length=200
    )
    suggestions: Optional[List[str]] = Field(
        default_factory=list,
        description="List of specific suggestions for improvement.",
        max_items=3
    )


class ReviewState(BaseModel):
    """Enhanced state management for code review workflow."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Core workflow state
    messages: List[BaseMessage] = Field(default_factory=list)
    pr_details: Optional[PRDetails] = None
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

    # Reply workflow state
    context_prompt: str = ""
    generated_reply: str = ""
    history_id: Optional[int] = None
    current_id: Optional[int] = None
    line_number: int = 0
    file_path: Optional[str] = None
    original_review: Optional[str] = None
    last_user_message: Optional[str] = None
    current_diff_hunk: Optional[str] = None

    # Error handling
    error_message: Optional[str] = None
    error_count: int = 0
    max_errors: int = 3

class RedisStorageState (BaseModel):
    comment_id: str = Field(..., description="Unique identifier for the review state")
    messages: List[BaseMessage] = Field(default_factory=list)
    last_comment: Optional[str] = None
    line_number: Optional[int] = None
    file_path: Optional[str] = None
    timestamp: Optional[str] = None

