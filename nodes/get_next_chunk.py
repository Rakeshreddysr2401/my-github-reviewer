from langchain_core.messages import SystemMessage
from States.state import ReviewState
from utils.logger import get_logger
from utils.path_utils import normalize_file_path

log=get_logger()

def get_next_chunk(state: ReviewState) -> ReviewState:
    while state.current_file_index < len(state.files):
        file = state.files[state.current_file_index]
        if state.current_chunk_index < len(file.chunks):
            log.info(f"\n---------------------------------------------------------------------------STARTED REVIEWING   {normalize_file_path(file.to_file)} FOR  CHUNK  {state.current_chunk_index+1}---------------------------------------------------------\n")
            log.info(f"Started Processing file: {file.to_file}, chunk index: {state.current_chunk_index}")
            state.retry_count = 0  # Reset retry count for new chunk
            state.next_agent="reviewer_agent"  # Set next agent to reviewer_agent
            state.messages = [SystemMessage(content="you are an AI assistant here observe all this history messages between a git code reviewer and a feedbacker and act according ")]
            return state  # Valid chunk found
        else:
            state.current_chunk_index = 0
            state.current_file_index += 1
    # No more chunks
    log.info("Finished All the files and chunks, Ending the state machine.")
    state.done = True
    return state
