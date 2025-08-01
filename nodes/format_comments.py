from States.state import ReviewState
from utils.github_utils.create_comment import create_comment
from utils.logger import get_logger
from utils.path_utils import normalize_file_path

log = get_logger()

def format_comments_node(state: ReviewState) -> ReviewState:
    file = state.files[state.current_file_index]
    chunk = file.chunks[state.current_chunk_index]

    line_map = {
        change.line_number: change
        for change in chunk.changes
        if change.line_number is not None
    }

    for ai_response in state.llm_response.reviews:
        try:
            if ai_response.lineNumber is None or ai_response.reviewComment is None:
                continue

            line_number = int(ai_response.lineNumber)
            if line_number not in line_map:
                continue

            change = line_map[line_number]
            if not change.content.startswith("+"):
                continue

            path = normalize_file_path(file.to_file)
            comment = {
                "body": ai_response.reviewComment.strip(),
                "path": path,
                "line": line_number,
            }

            state.comments = [comment]  # Only the current one to send
            return state  # 🚨 Return early after one comment

        except Exception as e:
            log.error(f"Error processing comment: {e}, Response: {ai_response}")

    # If no valid comment found in this chunk, move to next chunk
    state.comments = []
    return state

