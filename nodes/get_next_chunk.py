from langchain_core.messages import SystemMessage
from States.state import ReviewState


def get_next_chunk(state: ReviewState) -> ReviewState:
    while state.current_file_index < len(state.files):
        file = state.files[state.current_file_index]
        if state.current_chunk_index < len(file.chunks):
            state.messages = [SystemMessage(content="you are an AI assistant here observe all this history messages between a git code reviewer and a feedbacker and act according ")]
            return state  # Valid chunk found
        else:
            state.current_chunk_index = 0
            state.current_file_index += 1
    # No more chunks
    state.done = True
    return state
