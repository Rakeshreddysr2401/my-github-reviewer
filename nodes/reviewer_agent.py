# nodes/reviewer_agent.py
from langchain_core.messages import AIMessage
from States.state import ReviewState, ReviewResponse
from chains.reviewer_agent_chain import reviewer_agent_chain
from utils.path_utils import normalize_file_path


def reviewer_agent(state: ReviewState):
    pr_details = state.pr_details
    file = state.files[state.current_file_index]
    chunk = file.chunks[state.current_chunk_index]

    state.messages.append(AIMessage(content=f" Reviewing chunk: {chunk.content} in file: {file.to_file} for PR: {pr_details.title}"))
    normalized_path = normalize_file_path(file.to_file)
    guidelines_available = chunk.guidelines is not None and chunk.guidelines.strip() != ""
    formatted_chunk = "\n".join(chunk.formatted_chunk)

    critique = state.review_feedback.get("critique") if state.review_feedback else "None provided."
    suggestion_text = "\n".join(state.review_feedback.get("suggestions", [])) if state.review_feedback else "None."

    try:
        review: ReviewResponse = reviewer_agent_chain.invoke({
            "pr_title": pr_details.title,
            "pr_description": pr_details.description or "",
            "file_path": normalized_path,
            "code_diff": formatted_chunk,
            "history_messages": state.messages,
            "critique": critique,
            "suggestion_text": suggestion_text,
        })
    except Exception as e:
        print(f"Error in reviewer_agent_chain.invoke: {e}")
        # If review fails, return empty response
        return {
            "llm_response": [],
            "error": str(e)
        }
    state.messages.append(AIMessage(content=f" Reviewing chunk: {chunk.content} in file: {file.to_file} for PR: {pr_details.title}"))
    state.messages.append(AIMessage(content=f"Git Reviewer Response: {review.model_dump_json(indent=2)}"))
    state.next_agent = "feedback_agent"
    return {
        "llm_response": review
    }
