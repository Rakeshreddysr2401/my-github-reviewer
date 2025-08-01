# nodes/reply_sender.py
from States.state import ReviewState
from services.git_services.github_client import gh
from utils.logger import get_logger

log = get_logger()

def reply_sender(state: ReviewState) -> ReviewState:
    """
    Posts a threaded reply to an existing GitHub review comment.
    """
    log.info("Preparing to send threaded reply...")
    log.info("Reply body: %s", state.generated_reply)

    try:
        owner = state.pr_details.owner
        repo = state.pr_details.repo
        parent_comment_id = state.pr_details.parent_comment_id
        reply_body = state.generated_reply

        # Get repo object
        repo_obj = gh.get_repo(f"{owner}/{repo}")

        # Fetch the parent comment object by ID
        comment = repo_obj.get_pull_request_review_comment(parent_comment_id)

        # Reply to the parent comment
        comment.reply(reply_body)

        log.info(f"Reply posted to comment ID {parent_comment_id}")

    except Exception as e:
        log.error(f"Failed to send reply comment: {e}")

    return state
