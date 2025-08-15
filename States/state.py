# States/state.py (updated)
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Literal, Dict
from services.git_services.get_pr_details import PRDetails


class Change(BaseModel):
    """Represents a single change line in a diff."""
    content: str = ""
    line_number: Optional[int] = None
    diff_position: Optional[int] = None
    suggested_code: Optional[str] = None
    suggested_comment: Optional[str] = None
    formatted_comment: Optional[Dict[str, Any]] = None


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
    suggestions: Optional[List[str]] = Field(default_factory=list,
                                             description="List of specific suggestions for improvement.")


# New models for conversation handling
class ConversationThread(BaseModel):
    """Represents a conversation thread for a specific comment."""
    comment_id: int = Field(..., description="GitHub comment ID")
    file_path: str = Field(..., description="File path of the comment")
    line_number: int = Field(..., description="Line number of the comment")
    original_comment: str = Field(..., description="Original AI review comment")
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list, description="Thread conversation history")
    last_user_reply: Optional[str] = Field(default=None, description="Last user reply in the thread")
    needs_ai_response: bool = Field(default=False, description="Whether AI needs to respond")


class ReviewState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    messages: List[BaseMessage] = Field(default_factory=list)
    pr_details: PRDetails
    files: List[File] = Field(default_factory=list)
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

    # New fields for conversation handling
    mode: Literal["initial_review", "reply_mode"] = "initial_review"
    conversation_threads: List[ConversationThread] = Field(default_factory=list)
    current_thread_index: int = 0
    pending_replies: List[Dict[str, Any]] = Field(default_factory=list)