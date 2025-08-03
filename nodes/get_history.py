# nodes/get_history.py
from States.state import ReviewState, RedisStorageState
from utils.logger import get_logger
from configs.redis_memory_manager import redis_map
log = get_logger()


def get_history(state: ReviewState) -> ReviewState:
    print(f"history before sending {state}")
    state.history_id = state.pr_details.parent_comment_id
    state.current_id = state.pr_details.comment_id
    state.last_user_message = state.pr_details.reply_body
    state.current_diff_hunk = state.pr_details.diff_hunk

    log.info(
        f"History ID: {state.history_id}, Current ID: {state.current_id}, Last User Message: {state.last_user_message}, Current Diff Hunk: {state.current_diff_hunk}"
    )

    history = redis_map.get(str(state.pr_details.parent_comment_id))  # Convert to str as Redis keys are usually strings

    if history is None:
        log.warning(f"No Redis history found for parent_comment_id={state.pr_details.parent_comment_id}")
        state.error_message = "❌ Redis: No stored history found for this comment ID"
        return state  # Or raise a controlled exception / trigger retry if you want

    state.original_review = history.last_comment
    state.messages = history.messages
    state.file_path = history.file_path
    state.line_number = history.line_number

    log.info(f"✅ Loaded history for ID {state.history_id}")
    return state

