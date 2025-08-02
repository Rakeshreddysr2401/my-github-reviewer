# nodes/git_comment_sender.py
from States.state import ReviewState
from services.git_services.get_pr_details import PRDetails
from utils.logger import get_logger
from typing import List, Dict, Any
import json

log = get_logger()


def git_comment_sender(state: ReviewState) -> ReviewState:
    """Send comments to GitHub PR with proper error handling and memory storage."""
    comments = state.comments
    pr = state.pr_details.pr_obj

    if not comments:
        log.debug("No comment to post for this chunk")
        state.comments = []
        state.current_chunk_index += 1
        return state

    try:
        commit_sha = pr.head.sha  # Get the latest commit SHA
        comment = comments[0]  # Process first comment

        # Validate comment structure
        required_fields = ["body", "path", "line"]
        if not all(field in comment for field in required_fields):
            log.error(f"Invalid comment structure: {comment}")
            state.final_response = "Invalid comment structure"
            state.comments = []
            state.current_chunk_index += 1
            return state

        # Create the review comment
        comment_obj = pr.create_review_comment(
            body=comment["body"],
            commit=commit_sha,
            path=comment["path"],
            line=comment["line"],
            side="RIGHT"  # Comment on the new version
        )

        comment_id = comment_obj.id
        log.info(f"✅ Posted comment ID {comment_id} to {comment['path']}:{comment['line']}")

        # Store in memory for future reference (if needed)
        memory_data = {
            "comments": comment["body"],
            "file_path": comment["path"],
            "line_number": comment["line"],
            "timestamp": comment_obj.created_at.isoformat() if hasattr(comment_obj, 'created_at') else None
        }

        # TODO: Implement proper memory storage
        # redis_memory[str(comment_id)] = memory_data

        state.final_response = f"Successfully posted comment to {comment['path']}:{comment['line']}"

    except Exception as e:
        log.error(f"❌ Failed to post comment: {e}")
        log.error(f"Comment data: {comment}")
        state.final_response = f"Failed to post comment: {str(e)}"

    # Clear comments and move to next chunk
    state.comments = []
    state.current_chunk_index += 1
    return state