# services/get_diff.py
import os
import requests
from services.github_client import gh
from utils.logger import get_logger

log = get_logger()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")



def get_diff(owner: str, repo_name: str, pull_number: int) -> str:
    """
    Fetches the raw .diff of a pull request from GitHub.
    """
    full_repo_name = f"{owner}/{repo_name}"
    log.debug(f"Attempting to fetch diff for PR #{pull_number} from {full_repo_name}")

    try:
        repo = gh.get_repo(full_repo_name)
        pr = repo.get_pull(pull_number)
        log.debug(f"Successfully retrieved PR: {pr.title}")

        api_url = f"https://api.github.com/repos/{full_repo_name}/pulls/{pull_number}.diff"
        headers = {
            'Authorization': f'Bearer {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3.diff'
        }

        log.debug(f"Making API request to: {api_url}")
        response = requests.get(api_url, headers=headers)
        log.debug(f"GitHub API response status code: {response.status_code}")

        if response.status_code == 200:
            diff = response.text
            log.debug(f"Retrieved diff of length: {len(diff)} characters")
            return diff
        else:
            log.error(f"Failed to get diff. Status code: {response.status_code}")
            log.error(f"Response content: {response.text}")
            raise Exception(f"GitHub API returned {response.status_code}: {response.text}")
    except Exception as e:
        log.exception(f"Exception occurred while getting diff: {str(e)}")
        raise
