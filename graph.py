from langgraph.graph import StateGraph ,END
from States.state import ReviewState
from nodes.format_comments import format_comments_node
from nodes.get_next_chunk import get_next_chunk
from nodes.retrieve_guidelines import retrieve_guidelines
from nodes.feedback_agent import feedback_agent, MAX_RETRIES
from nodes.reviewer_agent import reviewer_agent
from configs.memory_config import get_memory
from utils.logger import get_logger
log= get_logger()
import os

MAX_RETRIES = int(os.getenv("MAX_LOOP", 2))  # Default to 2 if not set

def create_reviewer_graph():

    memory = get_memory()

    def get_next_chunk_branch(state: ReviewState) -> str:
        if state.done:
            print("All chunks processed, ending review.")
            return END
        elif state.guidelines_store is not None:
            return "retrieve_guidelines"
        else:
            return "code_reviewer"


    def guidelines_transition(state:ReviewState):
        """Determine next step after guidelines."""
        next = state.next_agent
        if next:
            return next
        log.error("No next agent specified after guidelines retrieval.. terminating.")
        return END


    def feedback_agent_transition(state:ReviewState):
        """Determine next step after feedback_agent."""
        retry_count = state.retry_count
        satisfied = state.satisfied
        if retry_count==0:
            return "retrieve_guidelines"
        elif satisfied or retry_count > MAX_RETRIES:
            return "format_comments"
        elif not satisfied and retry_count <= MAX_RETRIES:
            return "reviewer_agent"
        return END

    builder = StateGraph(ReviewState)

    builder.add_node("get_next_chunk", get_next_chunk)
    builder.add_node("retrieve_guidelines",retrieve_guidelines)
    builder.add_node("reviewer_agent", reviewer_agent)
    builder.add_node("feedback_agent", feedback_agent)
    builder.add_node("format_comments", format_comments_node)

    builder.set_entry_point("get_next_chunk")


    builder.add_conditional_edges(
        "get_next_chunk",
        get_next_chunk_branch,
        {
             END: END,

            "retrieve_guidelines": "retrieve_guidelines",
            "reviewer_agent": "reviewer_agent",
        },
    )

    builder.add_conditional_edges("retrieve_guidelines", guidelines_transition,{"reviewer_agent": "reviewer_agent", "feedback_agent": "feedback_agent"})

    builder.add_edge("reviewer_agent", "feedback_agent")

    builder.add_conditional_edges(
        "feedback_agent",
        feedback_agent_transition,
        {
            "retrieve_guidelines": "retrieve_guidelines",
            "reviewer_agent": "reviewer_agent",
            "format_comments": "format_comments",
        }
    )
    builder.add_edge("format_comments", "get_next_chunk")

    return builder.compile()

graph = create_reviewer_graph()

if __name__ == "__main__":
    # This is just for testing the graph creation
    print("Graph created successfully!")
    print(graph)