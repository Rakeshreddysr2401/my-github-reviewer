# nodes/git_comment_sender.py
from States.state import ReviewState
from services.git_services.git_review_comment_sender import create_review_comment
from utils.logger import get_logger
import sys

log = get_logger()


def git_comment_sender_node(state: ReviewState) -> ReviewState:
    """Node to send accumulated comments to GitHub PR."""
    comments = state.comments
    pr_details = state.pr_details

    log.info(f"Sending {len(comments)} total comments to GitHub PR")

    if comments:
        try:
            review_id = create_review_comment(pr_details, comments)
            log.info(f"Successfully posted review with ID: {review_id}")
            state.final_response = f"Successfully posted {len(comments)} comments to PR review {review_id}"
        except Exception as e:
            log.error(f"Failed to post comments: {e}")
            state.final_response = f"Failed to post comments: {str(e)}"
            # Don't exit here, let the graph handle the error state
    else:
        log.info("No issues found, no comments to post")
        state.final_response = "No issues found, no comments to post"

    return state