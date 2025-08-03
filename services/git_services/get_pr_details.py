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
        diff_hunk: str = None,
        super_parent_id: int = None,
        thread: list = None,
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
        self.super_parent_id = super_parent_id
        self.thread = thread or []


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
        super_parent_id = None
        thread = []

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

            # Map all review comments by ID
            review_comments = list(pr.get_review_comments())
            comment_map = {c.id: c for c in review_comments}

            # Try to find the original bot comment
            if parent_comment_id:
                original = comment_map.get(parent_comment_id)
                if not original:
                    issue_comments = list(pr.get_issue_comments())
                    original = next((c for c in issue_comments if c.id == parent_comment_id), None)
                    if original:
                        log.info(f"Found original comment in issue comments: ID={original.id}, User={original.user.login}")
                    else:
                        log.error("Original parent comment not found.")

                if original:
                    original_bot_comment = original.body
                    log.info(f"Original bot comment found: {original_bot_comment}")

            # Step 1: Trace back to super parent
            current_id = parent_comment_id or comment_id
            super_parent_id = current_id

            while current_id:
                current_comment = comment_map.get(current_id)
                if current_comment is None:
                    break
                if current_comment.in_reply_to_id is None:
                    super_parent_id = current_comment.id
                    break
                current_id = current_comment.in_reply_to_id

            log.info(f"Super parent ID: {super_parent_id}")

            # Step 2: Collect full thread
            def collect_thread(start_id):
                sequence = []
                visited = set()
                queue = [start_id]

                while queue:
                    cid = queue.pop(0)
                    if cid in visited:
                        continue
                    comment = comment_map.get(cid)
                    if comment:
                        sequence.append({
                            "id": comment.id,
                            "author": comment.user.login,
                            "body": comment.body,
                            "in_reply_to_id": comment.in_reply_to_id,
                        })
                        visited.add(cid)
                        children = [c.id for c in comment_map.values() if c.in_reply_to_id == cid]
                        queue.extend(children)
                return sequence

            thread = collect_thread(super_parent_id)
            log.info("Full conversation thread:\n" + json.dumps(thread, indent=2))

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
            super_parent_id=super_parent_id,
            thread=thread,
        )

    except Exception as e:
        log.error(f"Error getting PR details: {e}")
        raise
