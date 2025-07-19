# services/pr_details.py
import os
import json
from services.github_client import gh
from utils.logger import get_logger

log = get_logger()

class PRDetails:
    def __init__(self, owner: str, repo: str, pull_number: int, title: str, description: str):
        self.owner = owner
        self.repo = repo
        self.pull_number = pull_number
        self.title = title
        self.description = description


def get_pr_details() -> PRDetails:
    event_path = os.environ.get("GITHUB_EVENT_PATH", ".github/test-data/pull_request_event.json")

    log.debug(f"Using event path: {event_path}")

    try:
        with open(event_path, "r") as f:
            event_data = json.load(f)

        log.debug(f"Event data loaded. {event_data}")


        if "issue" in event_data and "pull_request" in event_data["issue"]:
            pull_number = event_data["issue"]["number"]
            repo_full_name = event_data["repository"]["full_name"]
        else:
            raise ValueError("Unsupported event type")

        owner, repo = repo_full_name.split("/")

        repo_obj = gh.get_repo(repo_full_name)
        pr = repo_obj.get_pull(pull_number)

        return PRDetails(owner, repo, pull_number, pr.title, pr.body)

    except Exception as e:
        log.debug(f"Error in get_pr_details: {e}")
        raise
