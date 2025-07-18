from typing import List, Dict, Any

from States.state import File
from core.prompt_creator import create_prompt
from services.chatmodel import get_ai_response
from services.create_comment import create_comment
from services.pr_details import PRDetails
from utils.logger import get_logger
import os
from utils.path_utils import normalize_file_path

log = get_logger()

def analyze_code(parsed_diff: List[File], pr_details: PRDetails) -> List[Dict[str, Any]]:
    """Analyzes the code changes using Claude and generates review comments."""
    log.info("Starting analyze_code")
    log.info(f"Number of files to analyze: {len(parsed_diff)}")

    comments = []

    # Get max files to process from environment variable or use a reasonable default
    max_files = int(os.environ.get('MAX_FILES_TO_REVIEW', '10'))
    log.debug(f"Max files to review: {max_files}")

    # Keep track of the number of API calls to avoid rate limiting
    api_call_count = 0
    max_api_calls = int(os.environ.get('MAX_API_CALLS', '20'))
    log.debug(f"Max API calls allowed: {max_api_calls}")

    for file_index, file in enumerate(parsed_diff):
        if file_index >= max_files:
            log.info(f"Reached max files limit ({max_files}). Stopping analysis.")
            break

        normalized_path = normalize_file_path(file.to_file)
        log.info(f"Processing file {file_index + 1}/{min(len(parsed_diff), max_files)}: {normalized_path}")

        if not normalized_path or normalized_path == "/dev/null":
            log.debug(f"Skipping file with invalid path: {normalized_path}")
            continue

        if not file.chunks:
            log.warning(f"File {normalized_path} has no chunks to analyze. Skipping.")
            continue

        log.debug(f"File {normalized_path} has {len(file.chunks)} chunks")

        for chunk_index, chunk in enumerate(file.chunks):
            if not chunk.changes:
                log.debug(f"Chunk {chunk_index + 1} in file {normalized_path} has no changes. Skipping.")
                continue

            if api_call_count >= max_api_calls:
                log.warning(f"Reached API call limit ({max_api_calls}). Stopping analysis.")
                break

            log.debug(f"Processing chunk {chunk_index + 1}/{len(file.chunks)} with {len(chunk.changes)} changes")
            prompt = create_prompt(file, chunk, pr_details)
            log.debug(f"Created prompt of length {len(prompt)}")

            ai_responses = get_ai_response(prompt)
            api_call_count += 1
            log.info(f"AI generated {len(ai_responses)} comments (API call {api_call_count}/{max_api_calls})")

            new_comments = create_comment(file, chunk, ai_responses)
            comments.extend(new_comments)
            log.debug(f"Added {len(new_comments)} new comments")

        if api_call_count >= max_api_calls:
            log.warning(f"API call limit of {max_api_calls} reached. Some chunks may be skipped.")
            break

    log.info(f"Final comments count: {len(comments)}")
    if comments:
        log.debug("Sample comments:")
        for i, comment in enumerate(comments[:3]):
            log.debug(f"Comment {i + 1}: {comment['path']}:{comment.get('line', 'N/A')} - {comment['body'][:50]}...")

    return comments
