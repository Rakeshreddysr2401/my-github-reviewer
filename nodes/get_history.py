# nodes/get_history.py
from States.state import ReviewState
from utils.logger import get_logger

log = get_logger()


def get_history(state: ReviewState) -> ReviewState:
    print(f"history before sending {state}")
    """
    Extracts conversation context from the original bot comment and user's reply.
    """
    state.history_id = state.pr_details.parent_comment_id
    state.current_id = state.pr_details.comment_id
    state.last_user_message = state.pr_details.reply_body
    state.current_diff_hunk = state.pr_details.diff_hunk

    log.info(
        f"History ID: {state.history_id}, Current ID: {state.current_id}, Current Message: {state.current_message}, Current Diff Hunk: {state.current_diff_hunk}")

    # Assuming Redis-like dictionary for now
    redis_memory = state.memory_store  # Assume this is a dict for now

    conversation_data = redis_memory.get(str(state.history_id), {})

    #todo will add this in messages list
    state.original_review = conversation_data.get("comments", "Original comment not found.")
    # state.conversation_history = conversation_data.get("messages", "No conversation history yet.")
    state.file_path = conversation_data.get("file_path", "unknown.py")
    state.line_number = conversation_data.get("line_number", 0)

    log.info(f"Loaded history for ID {state.history_id}")
    return state

