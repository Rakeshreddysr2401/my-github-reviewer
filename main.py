
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
    log.info(
        "\n--------------------------------------------------------------------------- STARTED CODE REVIEWING ---------------------------------------------------------\n")
    """Main function to execute the code review process."""
    try:
        # ✅ Ensure vectorstore and get the handle
        guideline_store = None
        if os.environ.get('USE_VECTORSTORE', 'false').lower() == 'true':
            log.info("Using vectorstore for coding guidelines")
            guideline_store=ensure_vectorstore_exists_and_get()
        #Used to get PR details
        pr_details: PRDetails = get_pr_details()
        #Used to get difference in PR
        diff = get_diff(pr_details)
        if not diff:
            log.warning("No diff found, nothing to review")
            return
        #Used to parse the diff into a structured format
        parsed_diff = parse_diff(diff)
        #List of Files to Include
        filtered_diff = filter_files_by_exclude_patterns(parsed_diff)
        if not filtered_diff:
            log.warning("No files to analyze after filtering")
            return

        initial_state = ReviewState(
            pr_details=pr_details,
            files=parsed_diff,
            comments=[],
            guidelines_store=guideline_store
        )
        # thread_id = str(uuid4())
        # config = {"configurable": {"thread_id": thread_id}}
        config = {"checkpointer": None}


        final_state = graph.invoke(initial_state,config)
        final_state_obj = ReviewState(**final_state)
        print(final_state_obj.comments)
        comments = final_state_obj.comments
        if comments:
            try:
                review_id = create_review_comment(pr_details, comments)
                log.info(f"Successfully posted review with ID: {review_id}")
            except Exception as e:
                log.error(f"Failed to post comments: {e}")
                sys.exit(1)
        else:
            log.warning("No issues found, no comments to post")
        log.info(
            "\n--------------------------------------------------------------------------- ENDED REVIEWING THE CODE---------------------------------------------------------\n")

    except Exception as error:
        log.exception(f"Error in main: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
