# nodes/reply_sender.py
from States.state import ReviewState
from services.git_services.comment_monitor import CommentMonitor
from utils.logger import get_logger

log = get_logger()


def reply_sender_node(state: ReviewState) -> ReviewState:
    """Send AI replies to user comments."""

    if not state.pending_replies:
        log.info("No pending replies to send")
        return state

    monitor = CommentMonitor(state.pr_details)

    for reply_data in state.pending_replies:
        try:
            # Post reply to the conversation thread
            pr = state.pr_details.pr_obj

            # Find the original comment to reply to
            review_comments = pr.get_review_comments()
            original_comment = None

            for comment in review_comments:
                if comment.id == reply_data['thread_id']:
                    original_comment = comment
                    break

            if original_comment:
                # Create reply comment
                reply_comment = pr.create_review_comment_reply(
                    comment=original_comment,
                    body=reply_data['response']
                )

                # Register the new AI comment for monitoring
                monitor.register_ai_comment(
                    reply_comment.id,
                    reply_data['file_path'],
                    reply_data['line_number'],
                    reply_data['response']
                )

                log.info(f"Posted reply to thread {reply_data['thread_id']}")

        except Exception as e:
            log.error(f"Error posting reply: {e}")

    # Clear pending replies
    state.pending_replies = []

    return state