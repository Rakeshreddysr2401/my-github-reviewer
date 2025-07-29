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
from graph import graph

log = get_logger()


def main():
    """Main function to execute the code review process."""
    log.info("\n" + "=" * 100 + " STARTED CODE REVIEW " + "=" * 100 + "\n")

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
            "checkpointer": checkpointer,
            "configurable": {
                "thread_id": checkpoint_id
            }
        }

        final_state = None
        try:
            final_state = graph.invoke(initial_state, config)
        except GraphRecursionError:
            log.warning("Recursion error detected. Check your graph configuration for stop conditions.")
            sys.exit(1)

        # Extract final state object
        if isinstance(final_state, dict):
            final_state_obj = ReviewState(**final_state)
        else:
            final_state_obj = final_state

        # The git_comment_sender node has already handled posting comments
        # Check the final response for success/failure
        if final_state_obj.final_response:
            log.info(f"Review process completed: {final_state_obj.final_response}")
            if "Failed" in final_state_obj.final_response:
                sys.exit(1)
        else:
            log.info("Review process completed successfully")

        log.info("\n" + "=" * 100 + " COMPLETED CODE REVIEW " + "=" * 100 + "\n")

    except Exception as error:
        log.exception(f"Error in main: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()