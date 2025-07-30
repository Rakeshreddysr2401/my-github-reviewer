# nodes/reply_handler.py
from States.state import ReviewState, ConversationThread
from services.git_services.comment_monitor import CommentMonitor
from utils.logger import get_logger

log = get_logger()


def reply_handler_node(state: ReviewState) -> ReviewState:
    """Handle user replies to AI review comments."""

    if state.mode != "reply_mode":
        log.info("Not in reply mode, skipping reply handler")
        return state

    monitor = CommentMonitor(state.pr_details)

    # Check for new replies
    replies = monitor.check_for_replies()

    if not replies:
        log.info("No new replies found")
        state.done = True
        return state

    log.info(f"Found {len(replies)} new replies to process")

    # Process each reply
    for reply in replies:
        # Find or create conversation thread
        thread = None
        for existing_thread in state.conversation_threads:
            if existing_thread.comment_id == reply['in_reply_to_id']:
                thread = existing_thread
                break

        if not thread:
            # Create new thread
            history = monitor.get_conversation_history(reply['in_reply_to_id'])
            original_comment = next((h['body'] for h in history if h['is_ai_comment']), "")

            thread = ConversationThread(
                comment_id=reply['in_reply_to_id'],
                file_path=reply['file_path'],
                line_number=reply['line_number'],
                original_comment=original_comment,
                conversation_history=history
            )
            state.conversation_threads.append(thread)

        # Update thread with new reply
        thread.last_user_reply = reply['body']
        thread.needs_ai_response = True
        thread.conversation_history.append({
            'id': reply['reply_id'],
            'user': reply['user'],
            'body': reply['body'],
            'created_at': reply['created_at'],
            'is_ai_comment': False
        })

    # Set up for processing replies
    state.current_thread_index = 0
    state.done = False

    return state