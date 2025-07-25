from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any
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


class ReviewState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    pr_details: PRDetails
    files: List[File]
    current_file_index: int = 0
    current_chunk_index: int = 0
    current_prompt: Optional[str] = None
    llm_response: Optional[List[dict]] = None
    comments: List[dict] = Field(default_factory=list)
    guidelines_store: Optional[Any] = None
    done: bool = False
