from utils.logger import get_logger
from typing import List, Dict, Any
from States.state import File, Chunk
from utils.path_utils import normalize_file_path

log = get_logger()


def create_comment(file: File, chunk: Chunk, ai_responses: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """Creates comment objects from AI responses."""
    comments = []

    log.debug(f"Creating comments for {len(ai_responses)} AI responses")

    # Create a lookup of line numbers to changes
    line_map = {
        change.line_number: change
        for change in chunk.changes
        if change.line_number is not None
    }

    log.debug("Line map:")
    for line_num, change in sorted(line_map.items()):
        log.debug(f"Line {line_num}: {change.content}")

    for ai_response in ai_responses:
        try:
            line_number = int(ai_response["lineNumber"])
            log.debug(f"Processing AI response for line {line_number}")

            if line_number not in line_map:
                log.warning(f"Line {line_number} not found in the diff")
                continue

            change = line_map[line_number]

            if not change.content.startswith("+"):
                log.warning(f"Line {line_number} is not an added line: {change.content}")
                continue

            path = normalize_file_path(file.to_file)
            comment = {
                "body": ai_response["reviewComment"],
                "path": path,
                "line": line_number,
            }

            log.debug(f"Created comment: {comment}")
            comments.append(comment)

        except (KeyError, TypeError, ValueError) as e:
            log.error(f"Error creating comment from AI response: {e}, Response: {ai_response}")

    log.debug(f"Created {len(comments)} valid comments")
    return comments
