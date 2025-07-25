from States.state import ReviewState


def get_next_chunk(state: ReviewState) -> ReviewState:
    while state.current_file_index < len(state.files):
        file = state.files[state.current_file_index]
        if state.current_chunk_index < len(file.chunks):
            return state  # Valid chunk found
        else:
            state.current_chunk_index = 0
            state.current_file_index += 1
    # No more chunks
    state.done = True
    return state
