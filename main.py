# main.py (improved)
import sys
from uuid import uuid4
from States.state import ReviewState
from utils.github_utils.diff_parser import parse_diff
from services.git_services.get_diff import get_diff
from services.git_services.git_review_comment_sender import create_review_comment
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
            files=filtered_diff,  # Use filtered diff
            comments=[],
            guidelines_store=guideline_store
        )

        # Run the graph
        config = {"checkpointer": None}
        final_state = graph.invoke(initial_state, config)

        # Extract final state object
        if isinstance(final_state, dict):
            final_state_obj = ReviewState(**final_state)
        else:
            final_state_obj = final_state

        comments = final_state_obj.comments
        log.info(f"Generated {len(comments)} total comments")

        if comments:
            try:
                review_id = create_review_comment(pr_details, comments)
                log.info(f"Successfully posted review with ID: {review_id}")
            except Exception as e:
                log.error(f"Failed to post comments: {e}")
                sys.exit(1)
        else:
            log.info("No issues found, no comments to post")

        log.info("\n" + "=" * 100 + " COMPLETED CODE REVIEW " + "=" * 100 + "\n")

    except Exception as error:
        log.exception(f"Error in main: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()