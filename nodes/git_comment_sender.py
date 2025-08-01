# nodes/git_comment_sender.py
from States.state import ReviewState
from services.git_services.get_pr_details import PRDetails
from utils.logger import get_logger
from typing import List, Dict, Any
import json

log = get_logger()

def git_comment_sender(state: ReviewState) -> ReviewState:
    comments = state.comments
    pr = state.pr_details.pr_obj
    commit_sha = pr.head.sha  # latest commit SHA for the PR

    if comments:
        comment = comments[0]
        try:
            comment_obj = pr.create_review_comment(
                body=comment["body"],
                commit=commit_sha,  # ✅ FIXED
                path=comment["path"],
                line=comment["line"],
                side="RIGHT"
            )

            comment_id = comment_obj.id

            log.info(f"Posted single comment to {comment['path']}:{comment['line']}")
            log.info(f"Comment ID: {comment_id}")

            # Optionally save memory
            # state.memory[str(comment_id)] = {
            #     "body": comment["body"],
            #     "path": comment["path"],
            #     "line": comment["line"]
            # }

            state.final_response = f"Posted comment to {comment['path']}:{comment['line']}"
        except Exception as e:
            log.error(f"Failed to post single comment: {e}")
            state.final_response = f"Failed to post comment: {str(e)}"
    else:
        log.debug("No comment to post for this chunk")

    # Clear the comments list and move to next chunk
    state.comments = []
    state.current_chunk_index += 1
    return state
