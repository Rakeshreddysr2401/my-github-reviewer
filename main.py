# main.py
import sys
from uuid import uuid4

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
from reviewer_graph import review_graph
from reply_graph import reply_graph

log = get_logger()


def pr_review():
    """Main function to execute the code review process."""
    log.info("\n" + "=" * 100 + " STARTED CODE REVIEW " + "=" * 100 + "\n")

    try:
        # Initialize guideline store if enabled
        guideline_store = None
        if os.environ.get('USE_VECTORSTORE', 'false').lower() == 'true':
            log.info("Using vectorstore for coding guidelines")
            try:
                guideline_store = ensure_vectorstore_exists_and_get()
            except Exception as e:
                log.warning(f"Failed to initialize vectorstore: {e}. Continuing without guidelines.")

        # Get PR details and diff
        pr_details: PRDetails = get_pr_details()
        diff = get_diff(pr_details)

        if not diff:
            log.warning("No diff found, nothing to review")
            return

        # Parse and filter diff
        parsed_diff = parse_diff(diff)
        if not parsed_diff:
            log.warning("Failed to parse diff")
            return

        filtered_diff = filter_files_by_exclude_patterns(parsed_diff)

        if not filtered_diff:
            log.warning("No files to analyze after filtering")
            return

        # Initialize state
        initial_state = ReviewState(
            pr_details=pr_details,
            files=filtered_diff,
            comments=[],
            guidelines_store=guideline_store
        )

        # Run the graph
        checkpointer = MemorySaver()
        checkpoint_id = uuid4()

        config = {
            "configurable": {
                "thread_id": str(checkpoint_id)
            }
        }

        try:
            final_state = review_graph.invoke(initial_state, config)
        except GraphRecursionError as e:
            log.error(f"Graph recursion error: {e}")
            return
        except Exception as e:
            log.error(f"Error running review graph: {e}")
            raise

        log.info("\n" + "=" * 100 + " COMPLETED INITIAL CODE REVIEW " + "=" * 100 + "\n")
        return final_state

    except Exception as error:
        log.exception(f"Error in initial review: {error}")
        sys.exit(1)


def pr_comment_reply():
    """Main function to execute the comment reply process."""
    log.info("\n" + "=" * 100 + " STARTED REPLY REVIEW" + "=" * 100 + "\n")

    try:
        pr_details: PRDetails = get_pr_details()

        if not pr_details.comment_id:
            log.error("No comment ID found for reply mode")
            return

        # Initialize state
        initial_state = ReviewState(
            pr_details=pr_details,
        )

        # Run the graph
        checkpointer = MemorySaver()
        checkpoint_id = uuid4()
        config = {
            "configurable": {
                "thread_id": str(checkpoint_id)
            }
        }

        try:
            final_state = reply_graph.invoke(initial_state, config)
        except Exception as e:
            log.error(f"Error running reply graph: {e}")
            raise

        log.info("\n" + "=" * 100 + " COMPLETED REVIEW REPLY" + "=" * 100 + "\n")
        return final_state

    except Exception as error:
        log.exception(f"Error in reply process: {error}")
        sys.exit(1)