from langgraph.graph import StateGraph ,END
from States.state import ReviewState
from nodes.code_reviewer import code_reviewer
from nodes.format_comments import format_comments_node
from nodes.get_next_chunk import get_next_chunk
from nodes.retrieve_guidelines import retrieve_guidelines
from configs.memory_config import get_memory



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

    builder = StateGraph(ReviewState)

    builder.add_node("get_next_chunk", get_next_chunk)
    builder.add_node("retrieve_guidelines",retrieve_guidelines)
    builder.add_node("code_reviewer", code_reviewer)
    builder.add_node("format_comments", format_comments_node)

    builder.set_entry_point("get_next_chunk")


    builder.add_conditional_edges(
        "get_next_chunk",
        get_next_chunk_branch,
        {
             END: END,
            "retrieve_guidelines": "retrieve_guidelines",
            "code_reviewer": "code_reviewer",
        },
    )

    builder.add_edge("retrieve_guidelines", "code_reviewer")
    builder.add_edge("code_reviewer", "format_comments")
    builder.add_edge("format_comments", "get_next_chunk")

    return builder.compile()

graph = create_reviewer_graph()

if __name__ == "__main__":
    # This is just for testing the graph creation
    print("Graph created successfully!")
    print(graph)