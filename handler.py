import os
from utils.logger import get_logger
from main import pr_review, pr_comment_reply
log=get_logger()


def handler():
    mode=os.environ("MODE").lower()
    if mode == "review":
        log.info("Starting code review process")
        return pr_review()
    elif mode == "reply":
        log.info("Starting comment reply process")
        return pr_comment_reply()
    else:
        raise ValueError(f"Unknown mode: {mode}. Expected 'review' or 'reply'.")