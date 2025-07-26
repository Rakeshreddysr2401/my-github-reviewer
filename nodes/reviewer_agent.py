# nodes/reviewer_agent.py
import os
from States.state import ReviewState
from chains import reviewer_agent_chain
from chains.reviewer_agent_chain import ReviewResponse
from utils.path_utils import normalize_file_path

def reviewer_agent(state: ReviewState):
    pr_details = state.pr_details
    file = state.files[state.current_file_index]
    chunk = file.chunks[state.current_chunk_index]

    normalized_path = normalize_file_path(file.to_file)
    guidelines_available = chunk.guidelines is not None and chunk.guidelines.strip() != ""
    formatted_chunk = "\n".join(chunk.formatted_chunk)

    critique = state.review_feedback.get("critique") if state.review_feedback else "None provided."
    suggestion_text = "\n".join(state.review_feedback.get("suggestions", [])) if state.review_feedback else "None."



    try:
        review : ReviewResponse = reviewer_agent_chain.invoke({
            "pr_title": pr_details.title,
            "pr_description": pr_details.description or "",
            "file_path": normalized_path,
            "code_diff": formatted_chunk,
            "guidelines_section": chunk.guidelines if guidelines_available else None,
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
    return {
        "llm_response": review.reviews if review.reviews else [],
    }





