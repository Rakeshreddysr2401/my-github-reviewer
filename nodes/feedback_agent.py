# nodes/feedback_agent.py
import os
from langchain_core.messages import HumanMessage
from chains.feedback_agent_chain import feedback_agent_chain, ReviewFeedback
from States.state import ReviewState
from utils.path_utils import normalize_file_path
from utils.logger import get_logger

log = get_logger()
MAX_RETRIES = int(os.getenv("MAX_LOOP", "2"))

def feedback_agent(state: ReviewState) -> ReviewState:
    state.next_agent = "reviewer_agent"

    if not state.files or state.current_file_index >= len(state.files):
        log.error("No valid file to process")
        state.satisfied = True
        return state

    file = state.files[state.current_file_index]

    if not file.chunks or state.current_chunk_index >= len(file.chunks):
        log.error("No valid chunk to process")
        state.satisfied = True
        return state

    chunk = file.chunks[state.current_chunk_index]
    normalized_path = normalize_file_path(file.to_file)

    if not state.llm_response:
        log.error("No LLM response to evaluate")
        state.satisfied = True
        return state

    last_ai_response = state.llm_response.model_dump_json(indent=2)

    if state.retry_count == 0:
        state.final_response = last_ai_response

    if state.retry_count >= MAX_RETRIES:
        log.info("Max retries exceeded. Accepting final response")
        state.satisfied = True
        return state

    history_str = "\n".join(
        f"{msg.type.upper()}: {msg.content}"
        for msg in state.messages
        if hasattr(msg, 'content') and msg.content
    )

    formatted_chunk = "\n".join(chunk.formatted_chunk or [chunk.content])

    try:
        feedback: ReviewFeedback = feedback_agent_chain.invoke({
            "history_messages": history_str,
            "ai_response": last_ai_response,
            "user_query": formatted_chunk
        })
    except Exception as e:
        log.error(f"Error in feedback agent chain: {e}")
        state.satisfied = True
        return state

    if feedback.satisfied:
        log.info("Feedback Agent satisfied, no further action needed.")
        state.satisfied = True
    else:
        state.messages.append(HumanMessage(content=f"Feedback Agent Response: {feedback.model_dump_json(indent=2)}"))
        state.review_feedback = feedback
        state.retry_count += 1
        state.satisfied = False
        state.final_response = last_ai_response
        log.info(f"Feedback Agent Response: \n{feedback.model_dump_json(indent=2)}")

    return state
