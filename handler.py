# handler.py - ENHANCED ERROR HANDLING
import os
import sys

from utils.logger import get_logger
from main import pr_review, pr_comment_reply

log = get_logger()


def handler():
    """Enhanced handler with comprehensive error handling and logging."""
    try:
        mode = os.environ.get("MODE", "").lower().strip()

        if not mode:
            raise ValueError("MODE environment variable is required")

        log.info(f"🚀 Starting handler in {mode.upper()} mode")

        if mode == "review":
            log.info("📋 Starting code review process")
            result = pr_review()
            log.info(f"✅ Review completed with status: {result.get('status', 'unknown')}")
            return result

        elif mode == "reply":
            log.info("💬 Starting comment reply process")
            result = pr_comment_reply()
            log.info(f"✅ Reply completed with status: {result.get('status', 'unknown')}")
            return result

        else:
            raise ValueError(f"Unknown mode: '{mode}'. Expected 'review' or 'reply'.")

    except Exception as e:
        log.exception(f"❌ Handler failed: {e}")
        return {"status": "handler_error", "message": str(e)}


if __name__ == "__main__":
    result = handler()
    # Exit with appropriate code based on result
    if result.get("status") == "success":
        log.info("🎉 Process completed successfully")
        sys.exit(0)
    else:
        log.error(f"💥 Process failed: {result.get('message', 'Unknown error')}")
        sys.exit(1)