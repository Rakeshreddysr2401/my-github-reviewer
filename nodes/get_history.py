# nodes/get_history.py
from States.state import ReviewState, RedisStorageState
from utils.logger import get_logger
from configs.redis_memory_manager import redis_map
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
        f"History ID: {state.history_id}, Current ID: {state.current_id}, Last User Message: {state.last_user_message}, Current Diff Hunk: {state.current_diff_hunk}")


    history = redis_map.get(state.pr_details.comment_id)
    conversation_data = state.model_dump()
    log.info(f"Previous Comment History: {conversation_data} " )

    #todo will add this in messages list
    state.original_review = history.last_comment #if not original comment not found
    state.conversation_history = history.messages
    state.file_path = history.file_path
    state.line_number = history.line_number

    log.info(f"Loaded history for ID {state.history_id}")
    return state

