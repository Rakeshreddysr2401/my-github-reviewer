# services/get_diff.py
import os
import requests
from services.git_services.get_pr_details import PRDetails
from utils.logger import get_logger

log = get_logger()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")



def get_diff(pr_details:PRDetails) -> str:
    """
    Fetches the raw .diff of a pull request from GitHub.
    """
    print("=============STARTED GETTING DIFF================")
    full_repo_name = f"{pr_details.owner}/{pr_details.repo}"
    log.info(f"Attempting to fetch diff for PR #{pr_details.pull_number} from {full_repo_name}")
    try:
        api_url = f"https://api.github.com/repos/{full_repo_name}/pulls/{pr_details.pull_number}.diff"
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
