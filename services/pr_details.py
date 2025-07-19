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

    pull_number = int(os.environ.get("PULL_NUMBER"))
    repo_full_name = os.environ.get("REPOSITORY")

    owner, repo = repo_full_name.split("/")
    repo_obj = gh.get_repo(repo_full_name)
    pr = repo_obj.get_pull(pull_number)
    return PRDetails(owner, repo, pull_number, pr.title, pr.body)


