# nodes/reviewer_agent.py
from langchain_core.messages import AIMessage
from States.state import ReviewState, ReviewResponse
from chains.reviewer_agent_chain import reviewer_agent_chain
from utils.path_utils import normalize_file_path
from utils.logger import get_logger

log = get_logger()

def reviewer_agent(state: ReviewState) -> ReviewState:
    if not state.files or state.current_file_index >= len(state.files):
        log.error("No valid file to process")
        return state

    file = state.files[state.current_file_index]

    if not file.chunks or state.current_chunk_index >= len(file.chunks):
        log.error("No valid chunk to process")
        return state

    chunk = file.chunks[state.current_chunk_index]
    pr_details = state.pr_details

    state.messages.append(AIMessage(
        content=f"Reviewing chunk: {chunk.content} in file: {file.to_file} for PR: {pr_details.title}"
    ))

    normalized_path = normalize_file_path(file.to_file)
    formatted_chunk = "\n".join(chunk.formatted_chunk or [chunk.content])
    critique = state.review_feedback.critique if state.review_feedback else "None provided."
    suggestion_text = "\n".join(state.review_feedback.suggestions) if state.review_feedback else "None."

    log.info(f"Reviewer Agent called {state.retry_count + 1} time for file: {normalized_path}, chunk index: {state.current_chunk_index}")


    history_str = "\n".join(
        f"{msg.type.upper()}: {msg.content}\n"
        for msg in state.messages
        if hasattr(msg, 'content') and msg.content
    )

    try:
        review = reviewer_agent_chain.invoke({
            "pr_title": pr_details.title,
            "pr_description": pr_details.description or "",
            "file_path": normalized_path,
            "code_diff": formatted_chunk,
            "history_messages": history_str,
            "critique": critique,
            "suggestion_text": suggestion_text,
        })
    except Exception as e:
        log.error(f"Error in reviewer_agent_chain.invoke: {e}")
        state.llm_response = ReviewResponse(reviews=[])
        state.next_agent = "feedback_agent"
        return state

    state.messages.append(AIMessage(content=f"Git Reviewer Response: {review.model_dump_json(indent=2)}"))
    state.llm_response = review
    state.next_agent = "feedback_agent"

    log.info(f"Reviewer Agent Response: \n{review.model_dump_json(indent=2)}")
    return state
