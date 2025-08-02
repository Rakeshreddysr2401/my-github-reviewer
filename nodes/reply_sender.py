from States.state import ReviewState
from utils.logger import get_logger

log = get_logger()


def reply_sender(state: ReviewState) -> ReviewState:
    """Send reply to GitHub comment thread with proper error handling."""
    log.info("🔄 Reply Sender Node called")
    log.info(f"Reply content: {state.generated_reply}")
    log.info("Replying to comment ID: %s", state.pr_details.comment_id)  # in reply id

    if not state.generated_reply:
        log.warning("No reply generated to send")
        state.final_response = "No reply to send"
        return state

    try:
        pr = state.pr_details.pr_obj
        comment_id = state.pr_details.comment_id

        if not comment_id:
            log.error("No comment ID available for reply")
            state.final_response = "No comment ID for reply"
            return state

        # Find the original comment to reply to
        review_comments = list(pr.get_review_comments())
        original_comment = next((c for c in review_comments if c.id == comment_id), None)

        if not original_comment:
            log.error(f"Original comment with ID {comment_id} not found")
            state.final_response = "Original comment not found"
            return state

        log.info(f"Original comment info - id: {original_comment.id}, path: {original_comment.path}, "
                 f"line: {original_comment.line}, body: {original_comment.body[:100]}...")

        # Create reply comment
        reply_comment = pr.create_review_comment(
            body=state.generated_reply,
            commit=pr.head.sha,
            path=original_comment.path,
            line=original_comment.line,
            side="RIGHT",
            in_reply_to=comment_id
        )

        log.info(f"✅ Posted reply ID {reply_comment.id} to comment {comment_id}")
        state.final_response = f"Successfully posted reply to comment {comment_id}"

    except Exception as e:
        log.error(f"❌ Failed to post reply: {e}")
        state.final_response = f"Failed to post reply: {str(e)}"

    return state