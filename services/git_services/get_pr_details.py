# services/git_services/get_pr_details.py
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
    try:
        pull_number = int(os.environ.get("PULL_NUMBER"))
        repo_full_name = os.environ.get("REPOSITORY")
        mode = os.environ.get("MODE", "").lower()

        if not repo_full_name or "/" not in repo_full_name:
            raise ValueError("Invalid REPOSITORY format. Expected 'owner/repo'")

        owner, repo = repo_full_name.split("/", 1)
        repo_obj = gh.get_repo(repo_full_name)
        pr = repo_obj.get_pull(pull_number)

        comment_id = None
        parent_comment_id = None
        reply_body = None
        original_bot_comment = None
        diff_hunk = None

        if mode == "reply":
            event_path = os.environ.get("GITHUB_EVENT_PATH")
            if not event_path or not os.path.exists(event_path):
                raise FileNotFoundError("GITHUB_EVENT_PATH not found or invalid")

            with open(event_path, "r") as f:
                event = json.load(f)

            log.info("Full GitHub Event Payload:\n" + json.dumps(event, indent=2))

            comment_data = event.get("comment", {})
            comment_id = comment_data.get("id")
            parent_comment_id = comment_data.get("in_reply_to_id")
            reply_body = comment_data.get("body")
            diff_hunk = comment_data.get("diff_hunk")

            if parent_comment_id:
                log.info(f"Parent comment ID: {parent_comment_id}")
                # Try to find parent comment in review comments
                review_comments = list(pr.get_review_comments())
                original = next((c for c in review_comments if c.id == parent_comment_id), None)

                if not original:
                    issue_comments = list(pr.get_issue_comments())
                    original = next((c for c in issue_comments if c.id == parent_comment_id), None)
                    if original:
                        log.info(f"Found original comment in issue comments :" + json.dumps(original, indent=2))
                    else:
                        log.error(f"Not Found original comments ")

                if original:
                    log.info(f"Found original comment in review comments :"+json.dumps(original, indent=2))
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

    except Exception as e:
        log.error(f"Error getting PR details: {e}")
        raise