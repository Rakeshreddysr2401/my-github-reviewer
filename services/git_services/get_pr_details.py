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
        diff_hunk: str = None
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
        self.diff_hunk = diff_hunk


def get_pr_details() -> PRDetails:
    pull_number = int(os.environ.get("PULL_NUMBER"))
    repo_full_name = os.environ.get("REPOSITORY")
    mode = os.environ.get("MODE", "").lower()

    owner, repo = repo_full_name.split("/")
    repo_obj = gh.get_repo(repo_full_name)
    pr = repo_obj.get_pull(pull_number)

    comment_id = None
    parent_comment_id = None
    reply_body = None
    original_bot_comment = None
    diff_hunk = None

    if mode == "reply":
        # Load GitHub event payload
        with open(os.environ["GITHUB_EVENT_PATH"], "r") as f:
            event = json.load(f)
        log.info("Full GitHub Event Payload:\n" + json.dumps(event, indent=2))
        comment_id = event["comment"]["id"]
        parent_comment_id = event["comment"].get("in_reply_to_id")
        reply_body = event["comment"]["body"]
        diff_hunk = event.get("comment", {}).get("diff_hunk")

        if parent_comment_id:
            # Try to find parent comment in review comments
            review_comments = list(pr.get_review_comments())
            original = next((c for c in review_comments if c.id == parent_comment_id), None)

            if not original:
                issue_comments = list(pr.get_issue_comments())
                original = next((c for c in issue_comments if c.id == parent_comment_id), None)

            if original:
                original_bot_comment = original.body
            else:
                log.warning(f"Parent comment with ID {parent_comment_id} not found in review or issue comments.")

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
        original_bot_comment=original_bot_comment,
        diff_hunk=diff_hunk,
    )
