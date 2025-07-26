# nodes/feedback_agent.py
import os
from langchain_core.messages import HumanMessage
from chains.feedback_agent_chain import feedback_agent_chain, ReviewFeedback
from States.state import ReviewState
from utils.path_utils import normalize_file_path
from utils.logger import get_logger
log=get_logger()
MAX_RETRIES = os.getenv("MAX_LOOP", 2)


def feedback_agent(state: ReviewState):
    state.next_agent = "reviewer_agent"
    retry_count = state.retry_count
    messages = state.messages
    pr_details = state.pr_details
    file = state.files[state.current_file_index]
    chunk = file.chunks[state.current_chunk_index]
    normalized_path = normalize_file_path(file.to_file)

    guidelines_available = chunk.guidelines is not None and chunk.guidelines.strip() != ""
    formatted_chunk = "\n".join(chunk.formatted_chunk)
    last_ai_response=state.llm_response.model_dump_json(indent=2)
    # last_ai_response = "\n".join([f"lineNumber: {comment.lineNumber}  reviewComment: {comment.reviewComment}" for comment in state.llm_response.reviews])

    log.info(f"Feedback Agent called : {retry_count + 1} time  for file: {normalized_path}, chunk index: {state.current_chunk_index}, retry count: {retry_count}")

    if retry_count==0:
        state.final_response = last_ai_response

    # If we've exceeded max retries, accept the current response and END
    if retry_count >= MAX_RETRIES:
        log.info(f"Max retries exceeded. Accepting final response: {last_ai_response}")
        state.satisfied = True
        return state

    history_str = "\n".join(
        f"{msg.type.upper()}: {msg.content}"
        for msg in state.messages
        if hasattr(msg, 'content') and msg.content
    )

    try:
        feedback: ReviewFeedback = feedback_agent_chain.invoke({
            "guidelines": guidelines_available,
            "history_messages": history_str,
            "ai_response": last_ai_response if last_ai_response else "",
            "user_query": formatted_chunk or ""
        })
    except Exception as e:
        log.error(f"Error in feedback agent chain invoking : {e}")
        # If review fails, accept the response
        state.satisfied = True
        return state

    feedback_dict = feedback.dict()
    satisfied = feedback_dict.get("satisfied", False)

    if satisfied:
        log.info("Feedback Agent Satisfied, no further action needed.")
        state.satisfied = True
        return state
    state.messages.append(HumanMessage(content=f"Feedback Agent Response: {feedback.model_dump_json(indent=2)}"))
    log.info(f"Feedback Agent Response: \n{feedback.model_dump_json(indent=2)}\n")
    return {
        "next_agent": "reviewer_agent",
        "satisfied": False,
        "final_response": last_ai_response if satisfied else state.final_response,
        "review_feedback": feedback_dict,
        "retry_count": retry_count + 1 if not satisfied else retry_count,
    }
