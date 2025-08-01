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
        pr_number = state.pr_details.pull_number
        parent_comment_id = state.pr_details.parent_comment_id
        reply_body = state.generated_reply

        # Get PullRequest object
        repo_obj = gh.get_repo(f"{owner}/{repo}")
        pr = repo_obj.get_pull(pr_number)

        # Fetch the parent review comment
        review_comments = pr.get_review_comments()
        parent_comment = next(
            (c for c in review_comments if c.id == parent_comment_id), None
        )

        if parent_comment is None:
            raise ValueError(f"Parent comment with ID {parent_comment_id} not found.")

        # Post a reply
        reply_comment = parent_comment.reply(reply_body)
        log.info(f"Reply posted to comment ID {parent_comment_id} (Reply ID: {reply_comment.id})")

    except Exception as e:
        log.error(f"Failed to send reply comment: {e}")

    return state
