# services/get_pr_details.py
import os
import json
from services.git_services.github_client import gh
from utils.logger import get_logger

log = get_logger()

class PRDetails:
    def __init__(
        self,
        owner: str,
        repo: str,
        pull_number: int,
        title: str,
        description: str,
        pr_obj=None,
        comment_id: int = None,
        parent_comment_id: int = None,
        reply_body: str = None,
        original_bot_comment: str = None,
    ):
        self.owner = owner
        self.repo = repo
        self.pull_number = pull_number
        self.title = title
        self.description = description
        self.pr_obj = pr_obj
        self.comment_id = comment_id
        self.parent_comment_id = parent_comment_id
        self.reply_body = reply_body
        self.original_bot_comment = original_bot_comment


def get_pr_details() -> PRDetails:
    pull_number = int(os.environ.get("PULL_NUMBER"))
    repo_full_name = os.environ.get("REPOSITORY")
    owner, repo = repo_full_name.split("/")
    repo_obj = gh.get_repo(repo_full_name)
    pr = repo_obj.get_pull(pull_number)

    # Extract comment context from GitHub event file
    with open(os.environ["GITHUB_EVENT_PATH"], "r") as f:
        event = json.load(f)
    print(f"git event {event}")
    comment_id = event["comment"]["id"]
    parent_comment_id = event["comment"].get("in_reply_to_id")
    reply_body = event["comment"]["body"]

    original_bot_comment = None
    if parent_comment_id:
        review_comments = pr.get_review_comments()
        original = next((c for c in review_comments if c.id == parent_comment_id), None)

        if original:
            original_bot_comment = original.body
        else:
            log.warning(f"Parent comment with ID {parent_comment_id} not found.")

    return PRDetails(
        owner=owner,
        repo=repo,
        pull_number=pull_number,
        title=pr.title,
        description=pr.body,
        pr_obj=pr,
        comment_id=comment_id,
        parent_comment_id=parent_comment_id,
        reply_body=reply_body,
        original_bot_comment=original_bot_comment
    )
