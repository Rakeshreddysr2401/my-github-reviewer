# nodes/get_history.py
from States.state import ReviewState
from utils.logger import get_logger
log=get_logger()
def get_history(state: ReviewState) -> ReviewState:
    print(f"history before sending {state}")
    """
    Extracts conversation context from the original bot comment and user's reply.
    """
    state.history_id = state.pr_details.parent_comment_id
    state.current_id = state.pr_details.comment_id
    state.current_body = state.pr_details.reply_body
    state.current_diff_hunk = state.pr_details.diff_hunk


    log.info(f"History ID: {state.history_id}, Current ID: {state.current_id}, Current Body: {state.current_body}, Current Diff Hunk: {state.current_diff_hunk}")

#     bot_comment = state.pr_details.original_bot_comment or "No original bot comment found."
#     user_reply = state.pr_details.reply_body or "No user reply found."
#
#     # Dummy prompt context for LLM
#     prompt = f"""
# A GitHub user replied to the following comment made by the bot:
#
# --- Bot's Original Comment ---
# {bot_comment}
#
# --- User's Reply ---
# {user_reply}
#
# Please generate a helpful, concise, and professional response to the user.
# """
#     state.context_prompt = prompt
    return state
