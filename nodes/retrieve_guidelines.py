from States.state import ReviewState
from utils.path_utils import normalize_file_path

def retrieve_guidelines(state: ReviewState) -> ReviewState:
    file = state.files[state.current_file_index]
    chunk = file.chunks[state.current_chunk_index]
    path = normalize_file_path(file.to_file)
    guidelines_store = state.guidelines_store

    if guidelines_store:
        guidelines = guidelines_store.get_relevant_guidelines(chunk.content, path)
        #we can use this not to enrich the chunk with guidelines
        chunk.guidelines = "\n".join(guidelines)
    else:
        chunk.guidelines = "No guidelines available for this chunk."
    return state
