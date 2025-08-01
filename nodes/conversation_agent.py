from States.state import ReviewState
from chains.conversation_agent_chain import conversation_agent_chain
from utils.logger import get_logger

log = get_logger()


def conversation_agent(state: ReviewState) -> ReviewState:
    log.info(f"Running threaded conversation agent for comment {state.pr_details.comment_id}")


    conversation_history = "\n".join(
        f"{msg.type.upper()}: {msg.content}\n"
        for msg in state.messages
        if hasattr(msg, 'content') and msg.content
    )

    response = conversation_agent_chain.invoke({
        "original_review": state.original_review,
        "conversation_history": state.conversation_history,
        "file_path": state.file_path,
        "line_number": state.line_number,
        "code_context": state.current_diff_hunk ,
        "last_user_message": state.last_user_message
    })

    state.generated_reply = response.strip()
    log.info(f"Generated reply: {state.generated_reply}")
    return state
