# graph.py
from langgraph.graph import StateGraph, END
from States.state import ReviewState
from nodes.format_comments import format_comments_node
from nodes.get_next_chunk import get_next_chunk
from nodes.retrieve_guidelines import retrieve_guidelines
from nodes.feedback_agent import feedback_agent, MAX_RETRIES
from nodes.reviewer_agent import reviewer_agent
from utils.logger import get_logger
import os

log = get_logger()
MAX_RETRIES = int(os.getenv("MAX_LOOP", "2"))


def create_reviewer_graph():
    """Create and configure the LangGraph state machine for code review."""

    def get_next_chunk_branch(state: ReviewState) -> str:
        if state.done:
            log.info("All chunks processed, ending review.")
            return END
        elif state.guidelines_store is not None:
            return "retrieve_guidelines"
        else:
            return "reviewer_agent"

    def guidelines_transition(state: ReviewState) -> str:
        """Determine next step after guidelines retrieval."""
        next_agent = state.next_agent
        if next_agent in ["reviewer_agent", "feedback_agent"]:
            return next_agent
        log.error("No valid next agent specified after guidelines retrieval.")
        return END

    def feedback_agent_transition(state: ReviewState) -> str:
        """Determine next step after feedback agent."""
        retry_count = state.retry_count
        satisfied = state.satisfied

        if retry_count == 1 and state.guidelines_store is not None:
            return "retrieve_guidelines"
        elif satisfied or retry_count > MAX_RETRIES:
            return "format_comments"
        elif not satisfied and retry_count <= MAX_RETRIES:
            return "reviewer_agent"
        return END

    def reviewer_agent_transition(state: ReviewState) -> str:
        """Determine next step after reviewer agent."""
        retry_count = state.retry_count
        if retry_count == 0 and state.guidelines_store is not None:
            return "retrieve_guidelines"
        return "feedback_agent"

    builder = StateGraph(ReviewState)

    # Add nodes
    builder.add_node("get_next_chunk", get_next_chunk)
    builder.add_node("retrieve_guidelines", retrieve_guidelines)
    builder.add_node("reviewer_agent", reviewer_agent)
    builder.add_node("feedback_agent", feedback_agent)
    builder.add_node("format_comments", format_comments_node)

    builder.set_entry_point("get_next_chunk")

    # Add conditional edges
    builder.add_conditional_edges(
        "get_next_chunk",
        get_next_chunk_branch,
        {
            END: END,
            "retrieve_guidelines": "retrieve_guidelines",
            "reviewer_agent": "reviewer_agent",
        },
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

    return builder.compile()


graph = create_reviewer_graph()

if __name__ == "__main__":
    print("Graph created successfully!")
    print(graph)