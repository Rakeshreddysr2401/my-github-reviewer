# nodes/reply_sender.py
from States.state import ReviewState
from services.git_services.github_client import gh

def reply_sender(state: ReviewState) -> ReviewState:
    """
    Posts a reply comment in the same thread using GitHub's API.
    """
    print("State before sending reply:", state)
    # owner = state.pr_details.owner
    # repo = state.pr_details.repo
    # pr_number = state.pr_details.pull_number
    # parent_comment_id = state.pr_details.parent_comment_id
    # reply_body = state.generated_reply
    #
    # repo_obj = gh.get_repo(f"{owner}/{repo}")
    #
    # # Create reply to comment thread
    # repo_obj.create_pull_request_review_comment(
    #     body=reply_body,
    #     pull_number=pr_number,
    #     in_reply_to=parent_comment_id
    # )

    return state
