
import sys
from services.code_reviewer import review_code_by_llm
from services.create_comment import create_comment
from services.diff_parser import parse_diff
from services.get_diff import get_diff
from services.git_review_comment_sender import create_review_comment
from services.pr_details import PRDetails, get_pr_details
from utils.file_filters import get_exclude_patterns_from_env, filter_files_by_exclude_patterns
from utils.logger import get_logger
log = get_logger()

def main():
    print("=============STARTED CODE REVIEW PROCESS================")
    """Main function to execute the code review process."""
    try:
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
        comments = review_code_by_llm(filtered_diff, pr_details)
        if comments:
            try:
                review_id = create_review_comment(pr_details, comments)
                log.info(f"Successfully posted review with ID: {review_id}")
            except Exception as e:
                log.error(f"Failed to post comments: {e}")
                sys.exit(1)
        else:
            log.warning("No issues found, no comments to post")
        print("=============CODE REVIEW PROCESS COMPLETED================")

    except Exception as error:
        log.exception(f"Error in main: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
