# nodes/reviewer_agent.py (Better error handling)
from langchain_core.messages import AIMessage
from States.state import ReviewState, ReviewResponse
from chains.reviewer_agent_chain import reviewer_agent_chain
from utils.path_utils import normalize_file_path
from utils.logger import get_logger

log = get_logger()


def reviewer_agent(state: ReviewState) -> ReviewState:
    if not state.files or state.current_file_index >= len(state.files):
        log.error("No valid file to process")
        state.llm_response = ReviewResponse(reviews=[])
        state.next_agent = "feedback_agent"
        return state

    file = state.files[state.current_file_index]

    if not file.chunks or state.current_chunk_index >= len(file.chunks):
        log.error("No valid chunk to process")
        state.llm_response = ReviewResponse(reviews=[])
        state.next_agent = "feedback_agent"
        return state

    chunk = file.chunks[state.current_chunk_index]
    pr_details = state.pr_details

    state.messages.append(AIMessage(
        content=f"Reviewing chunk: {chunk.content[:100]}... in file: {file.to_file} for PR: {pr_details.title}"
    ))

    normalized_path = normalize_file_path(file.to_file)
    formatted_chunk = "\n".join(chunk.formatted_chunk or [chunk.content])

    # Handle feedback gracefully
    critique = "None provided."
    suggestion_text = "None."

    if state.review_feedback:
        critique = state.review_feedback.critique or critique
        if state.review_feedback.suggestions:
            suggestion_text = "\n".join(state.review_feedback.suggestions)

    log.info(
        f"Reviewer Agent called {state.retry_count + 1} time(s) for file: {normalized_path}, chunk index: {state.current_chunk_index}")

    try:
        review = reviewer_agent_chain.invoke({
            "pr_title": pr_details.title or "No title provided",
            "pr_description": pr_details.description or "No description provided",
            "file_path": normalized_path,
            "code_diff": formatted_chunk,
            "guidelines": chunk.guidelines or "No specific guidelines provided. Follow general best practices.",
            "critique": critique,
            "suggestion_text": suggestion_text,
        })

        state.messages.append(AIMessage(content=f"Git Reviewer Response: {review.model_dump_json(indent=2)}"))
        state.llm_response = review
        state.next_agent = "feedback_agent"

        log.info(f"Reviewer Agent Response: \n{review.model_dump_json(indent=2)}")

    except Exception as e:
        log.error(f"Error in reviewer_agent_chain.invoke: {e}")
        state.llm_response = ReviewResponse(reviews=[])
        state.next_agent = "feedback_agent"

    return state