# nodes/git_comment_sender.py
from States.state import ReviewState
from services.git_services.get_pr_details import PRDetails
from utils.logger import get_logger
from typing import List, Dict, Any
import json


log = get_logger()

def git_comment_sender(state: ReviewState) -> ReviewState:
    """Node to send accumulated comments to GitHub PR."""
    comments = state.comments
    pr_details: PRDetails = state.pr_details

    log.info(f"Sending {len(comments)} total comments to GitHub PR")

    if comments:
        try:
            # Begin inlined create_review_comment logic
            formatted_comments: List[Dict[str, Any]] = []
            for comment in comments:
                path = comment.get('path')
                line = comment.get('line')
                body = comment.get('body')
                if not path or not line or not body:
                    log.debug(f"Skipping comment with missing data: path={path}, line={line}")
                    continue
                formatted_comment = {
                    'path': path,
                    'line': line,
                    'body': body
                }
                log.info(f"Adding comment for {path}:{line}")
                formatted_comments.append(formatted_comment)

            if not formatted_comments:
                log.warning("WARNING: No valid comments to post")
                state.final_response = "No valid comments to post"
                return state

            log.debug(f"The review comments are : {formatted_comments}")

            pr = pr_details.pr_obj
            review = pr.create_review(
                body="Code review by OpenAI",
                event="COMMENT",
                comments=formatted_comments
            )
            review_id = review.id
            log.info(f"Successfully created PR review with ID: {review_id}")
            log.info("Full Review details :\n" + json.dumps(review.raw_data, indent=2))

            # End inlined logic

            state.final_response = f"Successfully posted {len(comments)} comments to PR review {review_id}"
        except Exception as e:
            log.error(f"Failed to post comments: {e}")
            state.final_response = f"Failed to post comments: {str(e)}"
    else:
        log.info("No issues found, no comments to post")
        state.final_response = "No issues found, no comments to post"

    return state
