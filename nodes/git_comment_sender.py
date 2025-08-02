# nodes/git_comment_sender.py
from States.state import ReviewState
from utils.logger import get_logger

log = get_logger()


def git_comment_sender(state: ReviewState) -> ReviewState:
    comments = state.comments
    pr = state.pr_details.pr_obj

    if not comments:
        log.debug("No comment to post for this chunk")
        state.comments = []
        state.current_chunk_index += 1
        return state

    try:
        commit_sha = pr.head.sha  # Get the latest commit SHA
        comment = comments[0]

        # Validate required fields
        if not all(key in comment for key in ["body", "path", "line"]):
            log.error(f"Invalid comment structure: {comment}")
            state.final_response = "Failed to post comment: missing required fields"
            state.comments = []
            state.current_chunk_index += 1
            return state

        comment_obj = pr.create_review_comment(
            body=comment["body"],
            commit=commit_sha,
            path=comment["path"],
            line=comment["line"],
            side="RIGHT"
        )

        comment_id = comment_obj.id
        log.info(f"Posted comment to {comment['path']}:{comment['line']} (ID: {comment_id})")

        # Store comment metadata for potential replies
        # You can implement Redis or database storage here
        # redis_memory[str(comment_id)] = {
        #     "body": comment["body"],
        #     "path": comment["path"],
        #     "line": comment["line"],
        #     "file_path": comment["path"],
        #     "line_number": comment["line"],
        #     "comments": comment["body"]
        # }

        state.final_response = f"Posted comment to {comment['path']}:{comment['line']}"

    except Exception as e:
        log.error(f"Failed to post comment: {e}")
        state.final_response = f"Failed to post comment: {str(e)}"

    # Clear comments and move to next chunk
    state.comments = []
    state.current_chunk_index += 1
    return state