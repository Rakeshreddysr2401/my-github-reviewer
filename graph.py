from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
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
import os

MAX_RETRIES = int(os.getenv("MAX_LOOP", "2"))


def create_reviewer_graph():
    def mode_router(state: ReviewState) -> str:
        return {
            "initial_review": "get_next_chunk",
            "reply_mode": "reply_handler"
        }.get(state.mode, END)

    def get_next_chunk_branch(state: ReviewState) -> str:
        if state.done:
            if state.current_file_index >= len(state.files):
                return "git_comment_sender"
            else:
                return "reviewer_agent"
        return "reviewer_agent"

    def reply_handler_branch(state: ReviewState) -> str:
        return END if state.done else "conversation_agent"

    def conversation_agent_branch(state: ReviewState) -> str:
        return "reply_sender" if state.current_thread_index >= len(state.conversation_threads) else "conversation_agent"

    def guidelines_transition(state: ReviewState) -> str:
        return state.next_agent if state.next_agent in ["reviewer_agent", "feedback_agent"] else END

    def feedback_agent_transition(state: ReviewState) -> str:
        if state.satisfied or state.retry_count > MAX_RETRIES:
            return "format_comments"
        return "reviewer_agent"

    def reviewer_agent_transition(state: ReviewState) -> str:
        return "retrieve_guidelines" if state.retry_count == 0 and state.guidelines_store else "feedback_agent"

    builder = StateGraph(ReviewState)
    builder.add_node("mode_router", lambda state: state)
    builder.add_node("get_next_chunk", get_next_chunk)
    builder.add_node("retrieve_guidelines", retrieve_guidelines)
    builder.add_node("reviewer_agent", reviewer_agent)
    builder.add_node("feedback_agent", feedback_agent)
    builder.add_node("format_comments", format_comments_node)
    builder.add_node("git_comment_sender", git_comment_sender_node)
    builder.add_node("reply_handler", reply_handler_node)
    builder.add_node("conversation_agent", conversation_agent_node)
    builder.add_node("reply_sender", reply_sender_node)

    builder.set_entry_point("mode_router")

    builder.add_conditional_edges("mode_router", mode_router, {
        "get_next_chunk": "get_next_chunk",
        "reply_handler": "reply_handler",
        END: END
    })

    builder.add_conditional_edges("get_next_chunk", get_next_chunk_branch, {
        "git_comment_sender": "git_comment_sender",
        "reviewer_agent": "reviewer_agent"
    })

    builder.add_conditional_edges("retrieve_guidelines", guidelines_transition, {
        "reviewer_agent": "reviewer_agent",
        "feedback_agent": "feedback_agent",
        END: END
    })

    builder.add_conditional_edges("reviewer_agent", reviewer_agent_transition, {
        "feedback_agent": "feedback_agent",
        "retrieve_guidelines": "retrieve_guidelines"
    })

    builder.add_conditional_edges("feedback_agent", feedback_agent_transition, {
        "retrieve_guidelines": "retrieve_guidelines",
        "reviewer_agent": "reviewer_agent",
        "format_comments": "format_comments",
        END: END
    })

    builder.add_edge("format_comments", "get_next_chunk")
    builder.add_edge("git_comment_sender", END)

    builder.add_conditional_edges("reply_handler", reply_handler_branch, {
        "conversation_agent": "conversation_agent",
        END: END
    })

    builder.add_conditional_edges("conversation_agent", conversation_agent_branch, {
        "conversation_agent": "conversation_agent",
        "reply_sender": "reply_sender"
    })

    builder.add_edge("reply_sender", END)

    return builder


def create_graph_with_saver():
    saver = SqliteSaver.from_directory("state_db")
    return create_reviewer_graph().compile(checkpointer=saver)


graph = create_graph_with_saver()
