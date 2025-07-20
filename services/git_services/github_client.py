# services/github_client.py
import os
from github import Github

gh = Github(os.getenv("GITHUB_TOKEN"))
