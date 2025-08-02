# nodes/reply_sender.py - FIXED VERSION
from States.state import ReviewState
from utils.logger import get_logger

log = get_logger()


def reply_sender(state: ReviewState) -> ReviewState:
    """Send reply to GitHub comment thread with proper error handling and fallback strategies."""
    log.info("🚀 Starting reply sender...")

    if not state.generated_reply:
        log.warning("⚠️ No reply generated to send")
        state.final_response = "No reply to send"
        return state

    log.info(f"📝 Generated reply: {state.generated_reply[:100]}...")

    try:
        pr = state.pr_details.pr_obj
        comment_id = state.pr_details.comment_id
        parent_comment_id = state.pr_details.parent_comment_id

        if not comment_id:
            log.error("❌ No comment ID available for reply")
            state.final_response = "No comment ID for reply"
            return state

        # Strategy 1: Try to find the target comment (parent or current)
        target_id = parent_comment_id if parent_comment_id else comment_id
        log.info(f"🔍 Looking for comment ID: {target_id} (parent: {parent_comment_id}, current: {comment_id})")

        # Find the original comment to reply to
        review_comments = list(pr.get_review_comments())
        original_comment = None

        for comment in review_comments:
            if comment.id == target_id:
                original_comment = comment
                log.info(f"✅ Found target comment on {comment.path}:{comment.line}")
                break

        if original_comment:
            # Strategy 1: Create threaded review comment reply
            try:
                reply_comment = pr.create_review_comment(
                    body=state.generated_reply,
                    commit=pr.head.sha,
                    path=original_comment.path,
                    line=original_comment.line,
                    side="RIGHT",
                    in_reply_to=target_id
                )

                log.info(f"✅ Posted threaded reply ID {reply_comment.id} to comment {target_id}")
                state.final_response = f"Successfully posted threaded reply to comment {target_id}"
                return state

            except Exception as e:
                log.warning(f"⚠️ Threaded reply failed: {e}")
                # Continue to fallback strategy

        else:
            log.warning(f"⚠️ Comment ID {target_id} not found in review comments")

        # Strategy 2: Fallback to issue comment with user reference
        log.info("🔄 Falling back to issue comment...")

        # Get the user who made the original comment if possible
        user_login = pr.user.login  # Default to PR author

        # Try to find the actual comment author from all PR comments
        try:
            all_comments = list(pr.get_issue_comments()) + list(pr.get_review_comments())
            for comment in all_comments:
                if comment.id == target_id:
                    user_login = comment.user.login
                    break
        except Exception as e:
            log.warning(f"⚠️ Could not find comment author: {e}")

        # Create issue comment with user mention
        formatted_reply = f"@{user_login} **Reply to your comment:**\n\n{state.generated_reply}"

        issue_comment = pr.create_issue_comment(body=formatted_reply)

        log.info(f"✅ Posted fallback issue comment ID {issue_comment.id}")
        state.final_response = f"Posted reply as issue comment {issue_comment.id} (fallback method)"

    except Exception as e:
        log.error(f"❌ All reply strategies failed: {e}")
        log.error(
            f"Debug info - PR: {pr.number if pr else 'None'}, Comment ID: {comment_id}, Parent ID: {parent_comment_id if parent_comment_id else 'None'}")

        # Last resort: Try basic issue comment without user mention
        try:
            basic_reply = f"**Code Review Reply:**\n\n{state.generated_reply}"
            basic_comment = pr.create_issue_comment(body=basic_reply)
            log.info(f"✅ Posted basic issue comment ID {basic_comment.id} as last resort")
            state.final_response = f"Posted basic reply comment {basic_comment.id} (last resort)"
        except Exception as final_e:
            log.error(f"❌ Even basic comment failed: {final_e}")
            state.final_response = f"Failed to post reply: {str(e)}"

    return state


# Alternative approach if the above doesn't work - using issue comments instead
def reply_sender_alternative(state: ReviewState) -> ReviewState:
    """Alternative reply sender using issue comments instead of review comments."""
    log.info("Using alternative reply method (issue comments)...")

    if not state.generated_reply:
        log.warning("No reply generated to send")
        state.final_response = "No reply to send"
        return state

    try:
        pr = state.pr_details.pr_obj
        comment_id = state.pr_details.comment_id

        if not comment_id:
            log.error("No comment ID available for reply")
            state.final_response = "No comment ID for reply"
            return state

        # Format reply to reference the original comment
        formatted_reply = f"@{pr.user.login} {state.generated_reply}"

        # Create an issue comment (simpler approach)
        issue_comment = pr.create_issue_comment(body=formatted_reply)

        log.info(f"✅ Successfully posted issue comment reply ID {issue_comment.id}")
        state.final_response = f"Successfully posted reply as issue comment {issue_comment.id}"

    except Exception as e:
        log.error(f"❌ Failed to send issue comment: {e}")
        state.final_response = f"Failed to post issue comment: {str(e)}"

    return state


# Enhanced version with better error handling and fallback
def enhanced_reply_sender(state: ReviewState) -> ReviewState:
    """Enhanced reply sender with multiple fallback strategies."""
    log.info("🚀 Starting enhanced reply sender...")

    if not state.generated_reply:
        log.warning("⚠️ No reply generated to send")
        state.final_response = "No reply to send"
        return state

    log.info(f"📝 Reply content: {state.generated_reply[:100]}...")

    pr = state.pr_details.pr_obj
    comment_id = state.pr_details.comment_id
    parent_comment_id = state.pr_details.parent_comment_id

    # Strategy 1: Try threaded review comment reply
    if parent_comment_id or comment_id:
        try:
            result = _try_review_comment_reply(state, pr, parent_comment_id or comment_id)
            if result:
                return result
        except Exception as e:
            log.warning(f"⚠️ Review comment reply failed: {e}")

    # Strategy 2: Try issue comment as fallback
    try:
        result = _try_issue_comment_reply(state, pr)
        if result:
            return result
    except Exception as e:
        log.error(f"❌ Issue comment fallback failed: {e}")

    # Strategy 3: Last resort - general issue comment
    try:
        formatted_reply = f"**Reply to comment:** {state.generated_reply}"
        issue_comment = pr.create_issue_comment(body=formatted_reply)

        log.info(f"✅ Posted general issue comment ID {issue_comment.id}")
        state.final_response = f"Posted reply as general comment {issue_comment.id}"
        return state

    except Exception as e:
        log.error(f"❌ All reply strategies failed: {e}")
        state.final_response = f"Failed to post reply: {str(e)}"
        return state


def _try_review_comment_reply(state: ReviewState, pr, target_comment_id) -> ReviewState:
    """Try to create a threaded review comment reply."""
    log.info(f"🔍 Attempting review comment reply to ID {target_comment_id}")

    # Find the original comment
    review_comments = list(pr.get_review_comments())
    original_comment = None

    for comment in review_comments:
        if comment.id == target_comment_id:
            original_comment = comment
            break

    if not original_comment:
        log.warning(f"⚠️ Comment ID {target_comment_id} not found in review comments")
        return None

    # Create threaded reply
    reply_comment = pr.create_review_comment(
        body=state.generated_reply,
        commit=pr.head.sha,
        path=original_comment.path,
        line=original_comment.line,
        side="RIGHT",
        in_reply_to=target_comment_id
    )

    log.info(f"✅ Posted threaded review comment ID {reply_comment.id}")
    state.final_response = f"Posted threaded reply {reply_comment.id}"
    return state


def _try_issue_comment_reply(state: ReviewState, pr) -> ReviewState:
    """Try to create an issue comment reply."""
    log.info("🔍 Attempting issue comment reply")

    # Format with user mention for better UX
    user_login = pr.user.login
    formatted_reply = f"@{user_login} {state.generated_reply}"

    issue_comment = pr.create_issue_comment(body=formatted_reply)

    log.info(f"✅ Posted issue comment ID {issue_comment.id}")
    state.final_response = f"Posted issue comment reply {issue_comment.id}"
    return state


# Use this as your main reply_sender function
reply_sender = enhanced_reply_sender