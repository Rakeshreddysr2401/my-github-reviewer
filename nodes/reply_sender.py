# nodes/reply_sender.py
from States.state import ReviewState
from services.git_services.github_client import gh
from utils.logger import get_logger

log = get_logger()

def reply_sender(state: ReviewState) -> ReviewState:
    """
    Posts a reply in the same GitHub comment thread using the GitHub API.
    """
    log.info("Preparing to send threaded reply...")

    try:
        owner = state.pr_details.owner
        repo = state.pr_details.repo
        pr_number = state.pr_details.pull_number
        parent_comment_id = state.pr_details.parent_comment_id
        reply_body = state.generated_reply

        log.info(f"Replying to PR #{pr_number} in {owner}/{repo}, comment ID: {parent_comment_id}")

        repo_obj = gh.get_repo(f"{owner}/{repo}")

        # Post reply in thread using GitHub API
        repo_obj.create_pull_request_review_comment(
            body=reply_body,
            pull_number=pr_number,
            in_reply_to=parent_comment_id
        )

        log.info("Threaded reply successfully posted.")

    except Exception as e:
        log.error(f"Failed to send reply comment: {e}")

    return state
