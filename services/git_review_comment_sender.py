# src/github/review_commenter.py
from typing import List, Dict, Any
from github import Github
from utils.logger import get_logger

log = get_logger()

def create_review_comment(owner: str, repo: str, pull_number: int, comments: List[Dict[str, Any]], gh: Github):
    """Creates a pull request review with comments on specific lines."""
    log.info(f"Creating PR review with {len(comments)} comments")

    if not comments:
        log.warning("No comments to post, skipping")
        return

    comments_by_file = _group_comments_by_file(comments)
    _log_comment_distribution(comments_by_file)

    try:
        pr = _get_pr(gh, owner, repo, pull_number)
        formatted_comments = _format_comments(comments)

        if not formatted_comments:
            log.warning("No valid comments to post")
            return

        review = pr.create_review(
            body="Code review by Claude",
            event="COMMENT",
            comments=formatted_comments
        )

        log.info(f"Successfully created PR review with ID: {review.id}")
        return review.id

    except Exception as e:
        log.error(f"Failed to create PR review: {str(e)}")
        return _fallback_post_individual_or_consolidated(pr, comments, comments_by_file)

def _group_comments_by_file(comments: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    grouped = {}
    for comment in comments:
        file_path = comment.get('path', 'Unknown')
        grouped.setdefault(file_path, []).append(comment)
    return grouped

def _log_comment_distribution(comments_by_file: Dict[str, List[Dict[str, Any]]]):
    log.info("Comments distribution by file:")
    for file_path, file_comments in comments_by_file.items():
        log.info(f"  - {file_path}: {len(file_comments)} comments")

def _get_pr(gh: Github, owner: str, repo: str, pull_number: int):
    log.debug(f"Getting repo object for {owner}/{repo}...")
    repo_obj = gh.get_repo(f"{owner}/{repo}")
    log.debug(f"Getting PR #{pull_number}...")
    pr = repo_obj.get_pull(pull_number)
    log.debug(f"Successfully retrieved PR: {pr.title}")
    return pr

def _format_comments(comments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    formatted = []
    for comment in comments:
        path, line, body = comment.get('path'), comment.get('line'), comment.get('body')
        if not path or not line or not body:
            log.debug(f"Skipping comment with missing data: path={path}, line={line}")
            continue
        formatted.append({"path": path, "line": line, "body": body})
        log.debug(f"Adding comment for {path}:{line}")
    return formatted

def _fallback_post_individual_or_consolidated(pr, comments, comments_by_file):
    try:
        log.info("Using fallback: Posting comments individually")
        comment_ids = []

        for comment in comments:
            path, line, body = comment.get('path'), comment.get('line'), comment.get('body')
            if not path or not line or not body:
                continue
            try:
                pr_comment = pr.create_comment(body=body, path=path, line=line)
                comment_ids.append(pr_comment.id)
                log.debug(f"Created individual comment on {path}:{line}")
            except Exception as ce:
                log.warning(f"Failed to create individual comment: {str(ce)}")

        if comment_ids:
            log.info(f"Created {len(comment_ids)} individual comments")
            return comment_ids

        raise Exception("Failed to create any individual comments")

    except Exception as e2:
        log.warning(f"Individual comment fallback failed: {str(e2)}")
        return _post_fallback_issue_comment(pr, comments_by_file)

def _post_fallback_issue_comment(pr, comments_by_file):
    try:
        log.info("Using final fallback: Posting consolidated issue comment")
        comment_body = "# Claude Code Review Results\n\n"
        for file_path, file_comments in comments_by_file.items():
            comment_body += f"## File: {file_path}\n\n"
            file_comments.sort(key=lambda c: c.get('line', 0))
            for comment in file_comments:
                line = comment.get('line', 'N/A')
                comment_body += f"### Line {line}\n\n{comment.get('body', '')}\n\n---\n\n"
        fallback_comment = pr.create_issue_comment(comment_body)
        log.info(f"Created fallback consolidated comment with ID: {fallback_comment.id}")
        return [fallback_comment.id]
    except Exception as e3:
        log.error(f"All fallback methods failed: {str(e3)}")
        raise Exception("Failed to create any type of comments")
