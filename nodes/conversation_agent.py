# nodes/conversation_agent.py
from States.state import ReviewState
from chains.conversation_agent_chain import conversation_agent_chain
from utils.logger import get_logger

log = get_logger()




def map_author_to_type(author: str) -> str:
    """Map author login to type."""
    if "bot" in author.lower():
        return "assistant"
    else:
        return "user"


def format_threaded_conversation(thread):
    """Format the threaded conversation as chat history."""
    # Ensure it's sorted by ID or your known timestamp order (optional)
    sorted_thread = sorted(thread, key=lambda x: x.get("id", 0))

    formatted = []
    for msg in sorted_thread:
        msg_type = map_author_to_type(msg.get("author", "user"))
        content = msg.get("body", "").strip()
        if content:
            formatted.append(f"**{msg_type.upper()}**: {content}")
    return "\n".join(formatted)


def conversation_agent(state: ReviewState) -> ReviewState:
    log.info(f"Running threaded conversation agent for comment {state.pr_details.comment_id}")

    try:
        #todo as of not not using memory history I feeling not that required, we just using conversation chat instead
        # conversation_history = "\n".join(
        #     f"**{msg.type.upper()}**: {msg.content}"
        #     for msg in state.messages
        #     if hasattr(msg, 'content') and msg.content and msg.content.strip()
        # )




        # Format threaded conversation history
        conversation_history = format_threaded_conversation(state.pr_details.thread)

        if not conversation_history:
            conversation_history = "No previous conversation history."

        log.info(f"Conversation History:\n {conversation_history} ")

        response = conversation_agent_chain.invoke({
            "original_review": state.original_review or "No original review found.",
            "conversation_history": conversation_history,
            "file_path": state.file_path or "unknown.py",
            "line_number": state.line_number or 0,
            "code_context": state.current_diff_hunk or "No code context available.",
            "last_user_message": state.last_user_message or "No user message found."
        })

        state.generated_reply = response.strip()
        log.info(f"Generated reply: {state.generated_reply}")

    except Exception as e:
        log.error(f"Error in conversation agent: {e}")
        state.generated_reply = "Sorry, I encountered an error generating a response. Please try again."

    return state