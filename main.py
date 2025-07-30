import sys
import os
from uuid import uuid4

from States.state import ReviewState
from services.git_services.get_diff import get_diff
from services.git_services.get_pr_details import get_pr_details, PRDetails
from utils.github_utils.diff_parser import parse_diff
from utils.file_filters import filter_files_by_exclude_patterns
from utils.logger import get_logger
from utils.vectorstore_utils import ensure_vectorstore_exists_and_get
from graph import graph  # your compiled langgraph
from langgraph.checkpoint.sqlite import SqliteSaver

log = get_logger()

DB_DIR = "state_db"


def run_initial_review():
    log.info("\n" + "=" * 100 + " STARTED INITIAL CODE REVIEW " + "=" * 100 + "\n")

    try:
        guideline_store = None
        if os.environ.get("USE_VECTORSTORE", "false").lower() == "true":
            guideline_store = ensure_vectorstore_exists_and_get()

        pr_details: PRDetails = get_pr_details()
        diff = get_diff(pr_details)
        if not diff:
            log.warning("No diff found, nothing to review")
            return

        parsed_diff = parse_diff(diff)
        filtered_diff = filter_files_by_exclude_patterns(parsed_diff)
        if not filtered_diff:
            log.warning("No files to analyze after filtering")
            return

        checkpoint_id = os.environ.get("THREAD_ID", str(uuid4()))

        initial_state = ReviewState(
            pr_details=pr_details,
            files=filtered_diff,
            comments=[],
            guidelines_store=guideline_store,
            mode="initial_review"
        )

        config = {
            "checkpointer": SqliteSaver.from_directory(DB_DIR),
            "configurable": {
                "thread_id": checkpoint_id
            }
        }

        final_state = graph.invoke(initial_state, config)
        log.info("✅ Completed Initial Code Review")
        return final_state

    except Exception as e:
        log.exception(f"🚨 Error in initial review: {e}")
        sys.exit(1)


def run_reply_mode():
    log.info("\n" + "=" * 100 + " STARTED REPLY MODE " + "=" * 100 + "\n")

    try:
        pr_details = get_pr_details()
        reply_comment_id = os.environ.get("REPLY_COMMENT_ID")
        if not reply_comment_id:
            raise ValueError("REPLY_COMMENT_ID not provided for reply mode")

        checkpoint_id = os.environ.get("THREAD_ID")
        if not checkpoint_id:
            raise ValueError("THREAD_ID is required for reply mode to restore previous thread state")

        reply_state = ReviewState(
            pr_details=pr_details,
            files=[],  # Not needed in reply mode
            comments=[],
            reply_comment_id=reply_comment_id,
            mode="reply_mode"
        )

        config = {
            "checkpointer": SqliteSaver.from_directory(DB_DIR),
            "configurable": {
                "thread_id": checkpoint_id
            }
        }

        final_state = graph.invoke(reply_state, config)
        log.info("✅ Completed Reply Mode")
        return final_state

    except Exception as e:
        log.exception(f"🚨 Error in reply mode: {e}")
        sys.exit(1)


def main():
    mode = os.environ.get("MODE", "initial_review")
    if mode == "initial_review":
        run_initial_review()
    elif mode == "reply_mode":
        run_reply_mode()
    else:
        log.error(f"Unknown MODE: {mode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
