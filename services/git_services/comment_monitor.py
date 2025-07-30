# services/git_services/comment_monitor.py
import os
import time
from typing import List, Dict, Any
from services.git_services.github_client import gh
from services.git_services.get_pr_details import PRDetails
from utils.logger import get_logger

log = get_logger()


class CommentMonitor:
    """Monitors PR comments for user replies to AI review comments."""

    def __init__(self, pr_details: PRDetails):
        self.pr_details = pr_details
        self.repo = gh.get_repo(f"{pr_details.owner}/{pr_details.repo}")
        self.pr = self.repo.get_pull(pr_details.pull_number)
        self.ai_comment_ids = set()  # Track AI-generated comment IDs

    def register_ai_comment(self, comment_id: int, file_path: str, line_number: int, original_comment: str):
        """Register an AI-generated comment for monitoring."""
        self.ai_comment_ids.add(comment_id)
        log.info(f"Registered AI comment {comment_id} for monitoring")

    def check_for_replies(self) -> List[Dict[str, Any]]:
        """Check for user replies to AI comments."""
        replies = []

        try:
            # Get all review comments
            review_comments = self.pr.get_review_comments()

            for comment in review_comments:
                # Check if this is a reply to an AI comment
                if (hasattr(comment, 'in_reply_to_id') and
                        comment.in_reply_to_id and
                        comment.in_reply_to_id in self.ai_comment_ids):
                    # This is a user reply to an AI comment
                    replies.append({
                        'reply_id': comment.id,
                        'in_reply_to_id': comment.in_reply_to_id,
                        'user': comment.user.login,
                        'body': comment.body,
                        'file_path': comment.path,
                        'line_number': comment.line if hasattr(comment, 'line') else comment.original_line,
                        'created_at': comment.created_at.isoformat(),
                        'updated_at': comment.updated_at.isoformat()
                    })

        except Exception as e:
            log.error(f"Error checking for replies: {e}")

        return replies

    def get_conversation_history(self, comment_id: int) -> List[Dict[str, Any]]:
        """Get the full conversation history for a comment thread."""
        history = []

        try:
            review_comments = self.pr.get_review_comments()

            # Find the original comment and all replies
            for comment in review_comments:
                if comment.id == comment_id or (hasattr(comment, 'in_reply_to_id') and
                                                comment.in_reply_to_id == comment_id):
                    history.append({
                        'id': comment.id,
                        'user': comment.user.login,
                        'body': comment.body,
                        'created_at': comment.created_at.isoformat(),
                        'is_ai_comment': comment.id in self.ai_comment_ids
                    })

            # Sort by creation time
            history.sort(key=lambda x: x['created_at'])

        except Exception as e:
            log.error(f"Error getting conversation history: {e}")

        return history