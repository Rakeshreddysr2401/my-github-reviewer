# graph.py (updated for conversation mode)
from langgraph.graph import StateGraph, END
from States.state import ReviewState
from nodes.format_comments import format_comments_node
from nodes.get_next_chunk import get_next_chunk
from nodes.retrieve_guidelines import retrieve_guidelines
from nodes.feedback_agent import feedback_agent
from nodes.reviewer_agent import reviewer_agent
from nodes.git_comment_sender import git_comment_sender_node
from nodes.reply_handler import reply_handler_node
from nodes.conversation_agent import conversation_agent_node
from nodes.reply_sender import reply_sender_node
from utils.logger import get_logger
import os

log = get_logger()
MAX_RETRIES = int(os.getenv("MAX_LOOP", "2"))


def create_reviewer_graph():
    """Create and configure the LangGraph state machine for code review with conversation support."""

    def mode_router(state: ReviewState) -> str:
        """Route based on current mode."""
        if state.mode == "initial_review":
            return "get_next_chunk"
        elif state.mode == "reply_mode":
            return "reply_handler"
        return END

    def get_next_chunk_branch(state: ReviewState) -> str:
        if state.done:
            if state.current_file_index >= len(state.files):
                log.info("All files processed, sending comments to GitHub.")
                return "git_comment_sender"
            else:
                log.info("Current file processed, continuing to next.")
                return "reviewer_agent"
        else:
            return "reviewer_agent"

    def reply_handler_branch(state: ReviewState) -> str:
        """Branch after reply handler."""
        if state.done:
            return END
        else:
            return "conversation_agent"

    def conversation_agent_branch(state: ReviewState) -> str:
        """Branch after conversation agent."""
        if state.current_thread_index >= len(state.conversation_threads):
            return "reply_sender"
        else:
            return "conversation_agent"  # Process next thread

    def guidelines_transition(state: ReviewState) -> str:
        next_agent = state.next_agent
        if next_agent in ["reviewer_agent", "feedback_agent"]:
            return next_agent
        return END

    def feedback_agent_transition(state: ReviewState) -> str:
        retry_count = state.retry_count
        satisfied = state.satisfied

        if satisfied or retry_count > MAX_RETRIES:
            return "format_comments"
        elif not satisfied and retry_count <= MAX_RETRIES:
            return "reviewer_agent"
        return END

    def reviewer_agent_transition(state: ReviewState) -> str:
        retry_count = state.retry_count
        if retry_count == 0 and state.guidelines_store is not None:
            return "retrieve_guidelines"
        return "feedback_agent"

    builder = StateGraph(ReviewState)

    # Add all nodes
    builder.add_node("mode_router", lambda state: state)  # Dummy node for routing
    builder.add_node("get_next_chunk", get_next_chunk)
    builder.add_node("retrieve_guidelines", retrieve_guidelines)
    builder.add_node("reviewer_agent", reviewer_agent)
    builder.add_node("feedback_agent", feedback_agent)
    builder.add_node("format_comments", format_comments_node)
    builder.add_node("git_comment_sender", git_comment_sender_node)
    builder.add_node("reply_handler", reply_handler_node)
    builder.add_node("conversation_agent", conversation_agent_node)
    builder.add_node("reply_sender", reply_sender_node)

    # Set entry point
    builder.set_entry_point("mode_router")

    # Add conditional edges
    builder.add_conditional_edges(
        "mode_router",
        mode_router,
        {
            "get_next_chunk": "get_next_chunk",
            "reply_handler": "reply_handler",
            END: END
        }
    )

    # Original review flow
    builder.add_conditional_edges(
        "get_next_chunk",
        get_next_chunk_branch,
        {
            "git_comment_sender": "git_comment_sender",
            "reviewer_agent": "reviewer_agent",
        }
    )

    builder.add_conditional_edges(
        "retrieve_guidelines",
        guidelines_transition,
        {
            "reviewer_agent": "reviewer_agent",
            "feedback_agent": "feedback_agent",
            END: END
        }
    )

    builder.add_conditional_edges(
        "reviewer_agent",
        reviewer_agent_transition,
        {
            "feedback_agent": "feedback_agent",
            "retrieve_guidelines": "retrieve_guidelines"
        }
    )

    builder.add_conditional_edges(
        "feedback_agent",
        feedback_agent_transition,
        {
            "retrieve_guidelines": "retrieve_guidelines",
            "reviewer_agent": "reviewer_agent",
            "format_comments": "format_comments",
            END: END
        }
    )

    builder.add_edge("format_comments", "get_next_chunk")
    builder.add_edge("git_comment_sender", END)

    # Conversation flow
    builder.add_conditional_edges(
        "reply_handler",
        reply_handler_branch,
        {
            "conversation_agent": "conversation_agent",
            END: END
        }
    )

    builder.add_conditional_edges(
        "conversation_agent",
        conversation_agent_branch,
        {
            "conversation_agent": "conversation_agent",
            "reply_sender": "reply_sender"
        }
    )

    builder.add_edge("reply_sender", END)

    return builder.compile()


graph = create_reviewer_graph()