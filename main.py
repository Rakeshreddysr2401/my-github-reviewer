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
    """Enhanced main function with comprehensive error handling."""
    log.info("\n" + "=" * 100 + " STARTED CODE REVIEW " + "=" * 100 + "\n")

    try:
        # Initialize guideline store if enabled
        guideline_store = None
        if os.environ.get('USE_VECTORSTORE', 'false').lower() == 'true':
            log.info("🔍 Initializing vectorstore for coding guidelines")
            try:
                guideline_store = ensure_vectorstore_exists_and_get()
                log.info("✅ Guideline store initialized successfully")
            except Exception as e:
                log.warning(f"⚠️ Failed to initialize guideline store: {e}")

        # Get PR details and diff
        pr_details: PRDetails = get_pr_details()
        log.info(f"📋 Processing PR #{pr_details.pull_number}: {pr_details.title}")

        diff = get_diff(pr_details)
        if not diff:
            log.warning("⚠️ No diff found, nothing to review")
            return {"status": "no_diff", "message": "No changes to review"}

        # Parse and filter diff
        parsed_diff = parse_diff(diff)
        if not parsed_diff:
            log.warning("⚠️ Failed to parse diff")
            return {"status": "parse_error", "message": "Could not parse diff"}

        filtered_diff = filter_files_by_exclude_patterns(parsed_diff)
        if not filtered_diff:
            log.warning("⚠️ No files to analyze after filtering")
            return {"status": "no_files", "message": "No files to review after filtering"}

        log.info(f"📁 Reviewing {len(filtered_diff)} files")

        # Initialize state with error handling
        initial_state = ReviewState(
            pr_details=pr_details,
            files=filtered_diff,
            comments=[],
            guidelines_store=guideline_store
        )

        # Run the graph with enhanced configuration
        checkpointer = MemorySaver()
        checkpoint_id = uuid4()

        config = {
            "checkpointer": checkpointer,
            "configurable": {
                "thread_id": str(checkpoint_id)
            },
            "recursion_limit": 50  # Prevent infinite loops
        }

        log.info("🚀 Starting review workflow")
        final_state = review_graph.invoke(initial_state, config)

        log.info("\n" + "=" * 100 + " ✅ COMPLETED CODE REVIEW " + "=" * 100 + "\n")
        return {
            "status": "success",
            "final_state": final_state,
            "message": final_state.final_response or "Review completed successfully"
        }

    except GraphRecursionError as e:
        log.error(f"❌ Graph recursion limit exceeded: {e}")
        return {"status": "recursion_error", "message": "Review workflow exceeded recursion limit"}

    except Exception as error:
        log.exception(f"❌ Critical error in code review: {error}")
        return {"status": "error", "message": f"Review failed: {str(error)}"}


def pr_comment_reply():
    """Enhanced reply function with comprehensive error handling."""
    log.info("\n" + "=" * 100 + " STARTED REPLY REVIEW" + "=" * 100 + "\n")

    try:
        pr_details: PRDetails = get_pr_details()
        log.info(f"💬 Processing reply for PR #{pr_details.pull_number}")

        if not pr_details.comment_id:
            log.error("❌ No comment ID provided for reply")
            return {"status": "no_comment_id", "message": "No comment ID available"}

        # Initialize state
        initial_state = ReviewState(pr_details=pr_details)

        # Run the reply graph
        checkpointer = MemorySaver()
        checkpoint_id = uuid4()

        config = {
            "checkpointer": checkpointer,
            "configurable": {
                "thread_id": str(checkpoint_id)
            },
            "recursion_limit": 20
        }

        log.info("🚀 Starting reply workflow")
        final_state = reply_graph.invoke(initial_state, config)

        log.info("\n" + "=" * 100 + " ✅ COMPLETED REVIEW REPLY" + "=" * 100 + "\n")
        return {
            "status": "success",
            "final_state": final_state,
            "message": final_state.final_response or "Reply sent successfully"
        }

    except Exception as error:
        log.exception(f"❌ Critical error in reply process: {error}")
        return {"status": "error", "message": f"Reply failed: {str(error)}"}

