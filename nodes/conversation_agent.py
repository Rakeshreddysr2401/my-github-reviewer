# nodes/conversation_agent.py
from States.state import ReviewState
from chains.conversation_agent_chain import conversation_agent_chain
from utils.logger import get_logger

log = get_logger()


def conversation_agent(state: ReviewState) -> ReviewState:
    log.info(f"Running threaded conversation agent for comment {state.pr_details.comment_id}")

    try:
        conversation_history = "\n".join(
            f"**{msg.type.upper()}**: {msg.content}"
            for msg in state.messages
            if hasattr(msg, 'content') and msg.content and msg.content.strip()
        )

        if not conversation_history:
            conversation_history = "No previous conversation history."

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