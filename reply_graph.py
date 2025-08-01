# reviewer_graph.py
from langgraph.graph import StateGraph, END
from States.state import ReviewState
from nodes.get_history import get_history
from nodes.conversation_agent import conversation_agent
from nodes.reply_sender import reply_sender
from utils.logger import get_logger
import os

log = get_logger()
MAX_RETRIES = int(os.getenv("MAX_LOOP", "2"))


def create_reply_graph():
    """Create and configure the LangGraph state machine for code review."""

    builder = StateGraph(ReviewState)

    # Add nodes
    builder.add_node("get_history",get_history)
    builder.add_node("conversation_agent", conversation_agent)
    builder.add_node("reply_sender", reply_sender)

    builder.set_entry_point("get_history")

    builder.add_edge("get_history", "conversation_agent")

    builder.add_edge("conversation_agent", "reply_sender")

    builder.add_edge("reply_sender", END)

    return builder.compile()


reply_graph = create_reply_graph()

if __name__ == "__main__":
    print("Graph created successfully!")
    print(reply_graph)