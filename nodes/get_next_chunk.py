# nodes/get_next_chunk.py
from langchain_core.messages import SystemMessage
from States.state import ReviewState
from utils.logger import get_logger
from utils.path_utils import normalize_file_path

log = get_logger()


def get_next_chunk(state: ReviewState) -> ReviewState:
    """Move to the next chunk/file for processing."""
    while state.current_file_index < len(state.files):
        file = state.files[state.current_file_index]
        if state.current_chunk_index < len(file.chunks):
            log.info(f"\n{'='*50} REVIEWING {normalize_file_path(file.to_file)} CHUNK {state.current_chunk_index+1} {'='*50}\n")
            log.info(f"Processing file: {file.to_file}, chunk index: {state.current_chunk_index}")
            state.retry_count = 0
            state.satisfied = False
            state.review_feedback = None
            state.llm_response = None
            state.next_agent = "reviewer_agent"
            state.messages = [SystemMessage(content="You are an AI assistant. Observe the conversation history between a git code reviewer and feedback agent.")]
            return state
        else:
            state.current_chunk_index = 0
            state.current_file_index += 1

    log.info("Finished processing all files and chunks.")
    state.done = True
    return state