# main.py
import sys
from uuid import uuid4
import time

from langgraph.checkpoint.memory import MemorySaver
from langgraph.errors import GraphRecursionError

from States.state import ReviewState
from utils.github_utils.diff_parser import parse_diff
from services.git_services.get_diff import get_diff
from services.git_services.get_pr_details import PRDetails, get_pr_details
from utils.file_filters import filter_files_by_exclude_patterns
from utils.logger import get_logger
import os
from utils.vectorstore_utils import ensure_vectorstore_exists_and_get
from graph import graph

log = get_logger()


def run_initial_review():
    """Run the initial code review process."""
    log.info("\n" + "=" * 100 + " STARTED INITIAL CODE REVIEW " + "=" * 100 + "\n")

    try:
        # Initialize guideline store if enabled
        guideline_store = None
        if os.environ.get('USE_VECTORSTORE', 'false').lower() == 'true':
            log.info("Using vectorstore for coding guidelines")
            guideline_store = ensure_vectorstore_exists_and_get()

        # Get PR details and diff
        pr_details: PRDetails = get_pr_details()
        diff = get_diff(pr_details)

        if not diff:
            log.warning("No diff found, nothing to review")
            return

        # Parse and filter diff
        parsed_diff = parse_diff(diff)
        filtered_diff = filter_files_by_exclude_patterns(parsed_diff)

        if not filtered_diff:
            log.warning("No files to analyze after filtering")
            return

        # Initialize state for initial review
        initial_state = ReviewState(
            pr_details=pr_details,
            files=filtered_diff,
            comments=[],
            guidelines_store=guideline_store,
            mode="initial_review"
        )

        # Run the graph
        checkpointer = MemorySaver()
        checkpoint_id = uuid4()

        config = {
            "checkpointer": checkpointer,
            "configurable": {
                "thread_id": checkpoint_id
            }
        }

        final_state = graph.invoke(initial_state, config)

        log.info("\n" + "=" * 100 + " COMPLETED INITIAL CODE REVIEW " + "=" * 100 + "\n")
        return final_state

    except Exception as error:
        log.exception(f"Error in initial review: {error}")
        sys.exit(1)


def run_reply_monitoring():
    """Monitor for user replies and respond to them."""
    log.info("\n" + "=" * 100 + " STARTED REPLY MONITORING " + "=" * 100 + "\n")

    pr_details = get_pr_details()

    while True:
        try:
            # Initialize state for reply mode
            reply_state = ReviewState(
                pr_details=pr_details,
                files=[],  # Not needed for reply mode
                mode="reply_mode"
            )

            checkpointer = MemorySaver()
            checkpoint_id = uuid4()

            config = {
                "checkpointer": checkpointer,
                "configurable": {
                    "thread_id": checkpoint_id
                }
            }

            # Run the graph in reply mode
            final_state = graph.invoke(reply_state, config)

            # Wait before checking again
            time.sleep(60)  # Check every minute

        except KeyboardInterrupt:
            log.info("Reply monitoring stopped by user")
            break
        except Exception as error:
            log.exception(f"Error in reply monitoring: {error}")
            time.sleep(60)  # Wait before retrying


def main():
    """Main function to handle both initial review and reply monitoring."""
    mode = os.environ.get("MODE", "initial_review")

    if mode == "initial_review":
        run_initial_review()
    elif mode == "reply_monitor":
        run_reply_monitoring()
    elif mode == "both":
        # Run initial review first
        run_initial_review()
        # Then start monitoring for replies
        run_reply_monitoring()
    else:
        log.error(f"Unknown mode: {mode}")
        sys.exit(1)


if __name__ == "__main__":
    main()