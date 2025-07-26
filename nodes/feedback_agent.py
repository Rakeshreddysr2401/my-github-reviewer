# nodes/reviewer_agent.py
import os
from chains.feedback_agent_chain import feedback_agent_chain, ReviewFeedback
from States.state import ReviewState
from utils.path_utils import normalize_file_path

MAX_RETRIES = os.getenv("MAX_LOOP", 2)

def feedback_agent(state: ReviewState):
    retry_count = state.retry_count
    satisfied = state.satisfied
    messages = []

    pr_details = state.pr_details
    file = state.files[state.current_file_index]
    chunk = file.chunks[state.current_chunk_index]
    normalized_path = normalize_file_path(file.to_file)


    guidelines_available = chunk.guidelines is not None and chunk.guidelines.strip() != ""
    formatted_chunk = "\n".join(chunk.formatted_chunk)
    last_ai_response =  "\n".join(state.llm_response)

    print(f"Feedback Agent called : {retry_count+1} time")

    # If we've exceeded max retries, accept the current response and END
    if retry_count >= MAX_RETRIES:
        print(f"Max retries exceeded. Accepting final response: {last_ai_response}")
        state.satisfied = True
        return state

    # Build chat history string
    history_str = "\n".join(
        f"{msg.type.upper()}: {msg.content}"
        for msg in messages
        if hasattr(msg, 'content') and msg.content
    )

    try:
        feedback: ReviewFeedback = feedback_agent_chain.invoke({
            "chat_history": history_str,
            "ai_response": last_ai_response if last_ai_response else "",
            "user_query": formatted_chunk or ""
        })
    except Exception as e:
        print(f"Error in review_chain.invoke: {e}")
        # If review fails, accept the response
        state.satisfied=True
        return state

    feedback_dict = feedback.dict()
    satisfied = feedback_dict.get("satisfied", False)

    if satisfied:
        print("Satisfied by reviewer")
        state.satisfied=True
        return state


    return {
        "satisfied": False,
        "final_response": last_ai_response if satisfied else state.final_response,
        "review_feedback": feedback_dict,
        "retry_count": retry_count + 1 if not satisfied else retry_count,
    }
