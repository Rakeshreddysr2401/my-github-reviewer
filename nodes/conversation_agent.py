# nodes/conversation_agent.py
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from States.state import ReviewState
from chains.conversation_agent_chain import conversation_agent_chain  # New chain needed
from utils.logger import get_logger

log = get_logger()


def conversation_agent_node(state: ReviewState) -> ReviewState:
    """Generate AI responses to user replies in conversation threads."""

    if (state.current_thread_index >= len(state.conversation_threads) or
            not state.conversation_threads):
        log.info("No more conversation threads to process")
        state.done = True
        return state

    thread = state.conversation_threads[state.current_thread_index]

    if not thread.needs_ai_response:
        log.info(f"Thread {thread.comment_id} doesn't need AI response")
        state.current_thread_index += 1
        return state

    log.info(f"Processing conversation thread {thread.comment_id}")

    # Build context for the conversation
    conversation_context = []
    for msg in thread.conversation_history:
        role = "AI" if msg['is_ai_comment'] else "User"
        conversation_context.append(f"{role}: {msg['body']}")

    context_str = "\n".join(conversation_context)

    # Get the relevant code chunk for context
    relevant_file = None
    relevant_chunk = None

    for file in state.files:
        if file.to_file and thread.file_path in file.to_file:
            relevant_file = file
            for chunk in file.chunks:
                for change in chunk.changes:
                    if change.line_number == thread.line_number:
                        relevant_chunk = chunk
                        break
                if relevant_chunk:
                    break
            break

    code_context = ""
    if relevant_chunk:
        code_context = "\n".join(relevant_chunk.formatted_chunk or [relevant_chunk.content])

    try:
        # Generate response using conversation chain
        response = conversation_agent_chain.invoke({
            "conversation_history": context_str,
            "last_user_message": thread.last_user_reply,
            "code_context": code_context,
            "file_path": thread.file_path,
            "line_number": thread.line_number,
            "original_review": thread.original_comment
        })

        # Add response to pending replies
        state.pending_replies.append({
            'thread_id': thread.comment_id,
            'response': response,
            'file_path': thread.file_path,
            'line_number': thread.line_number
        })

        # Mark thread as processed
        thread.needs_ai_response = False

        log.info(f"Generated response for thread {thread.comment_id}")

    except Exception as e:
        log.error(f"Error generating conversation response: {e}")

    state.current_thread_index += 1
    return state