# src/github/review_commenter.py
from typing import List, Dict, Any


from services.github_client import gh
from utils.logger import get_logger

log = get_logger()


def create_review_comment(
        owner: str,
        repo: str,
        pull_number: int,
        comments: List[Dict[str, Any]],
):
    """Creates a pull request review with comments on specific lines."""
    print(f"Creating PR review with {len(comments)} comments")

    if not comments:
        print("WARNING: No comments to post, skipping")
        return

    # Group comments by file for better reporting
    comments_by_file = {}
    for comment in comments:
        file_path = comment.get('path', 'Unknown')
        if file_path not in comments_by_file:
            comments_by_file[file_path] = []
        comments_by_file[file_path].append(comment)

    # Print comment distribution
    print("Comments distribution by file:")
    for file_path, file_comments in comments_by_file.items():
        print(f"  - {file_path}: {len(file_comments)} comments")

    try:
        # Initialize GitHub client and get repository
        log.debug(f"Getting repo object for {owner}/{repo}...")
        repo_obj = gh.get_repo(f"{owner}/{repo}")
        log.debug(f"Getting PR #{pull_number}...")
        pr = repo_obj.get_pull(pull_number)
        log.debug(f"Successfully retrieved PR: {pr.title}")

        # Format comments for the review
        formatted_comments = []

        for comment in comments:
            path = comment.get('path')
            line = comment.get('line')
            body = comment.get('body')

            if not path or not line or not body:
                log.debug(f"Skipping comment with missing data: path={path}, line={line}")
                continue

            formatted_comment = {
                'path': path,
                'line': line,
                'body': body
            }

            log.info(f"Adding comment for {path}:{line}")
            formatted_comments.append(formatted_comment)

        if not formatted_comments:
            print("WARNING: No valid comments to post")
            return
        log.debug(f"The review comments are : {formatted_comments}")
        # Create the pull request review with all comments
        review = pr.create_review(
            body="Code review by OpenAI",
            event="COMMENT",
            comments=formatted_comments
        )

        print(f"Successfully created PR review with ID: {review.id}")
        return review.id

    except Exception as e:
        print(f"ERROR: Failed to create PR review: {str(e)}")

        # Try fallback method - post comments individually
        try:
            log.error("Using fallback: Posting comments individually")
            comment_ids = []

            for comment in comments:
                path = comment.get('path')
                line = comment.get('line')
                body = comment.get('body')

                if not path or not line or not body:
                    continue

                try:
                    pr_comment = pr.create_comment(
                        body=body,
                        path=path,
                        line=line
                    )
                    comment_ids.append(pr_comment.id)
                    log.error(f"Created individual comment on {path}:{line}")
                except Exception as comment_error:
                    log.error(f"Failed to create individual comment: {str(comment_error)}")

            if comment_ids:
                print(f"Created {len(comment_ids)} individual comments")
                return comment_ids
            else:
                raise Exception("Failed to create any individual comments")

        except Exception as e2:
            log.debug(f"Individual comment fallback failed: {str(e2)}")

            # Final fallback - post a consolidated issue comment
            try:
                log.info("Using final fallback: Posting consolidated issue comment")

                # Group comments by file
                comment_body = "# Claude Code Review Results\n\n"

                for file_path, file_comments in comments_by_file.items():
                    comment_body += f"## File: {file_path}\n\n"

                    # Sort comments by line number
                    file_comments.sort(key=lambda c: c.get('line', 0))

                    for comment in file_comments:
                        line_num = comment.get('line', 'N/A')
                        comment_body += f"### Line {line_num}\n\n"
                        comment_body += f"{comment.get('body', '')}\n\n"
                        comment_body += "---\n\n"

                # Create the fallback comment
                fallback_comment = pr.create_issue_comment(comment_body)
                print(f"Created fallback consolidated comment with ID: {fallback_comment.id}")
                return [fallback_comment.id]

            except Exception as e3:
                log.error(f"All fallback methods failed: {str(e3)}")
                raise Exception(f"Failed to create any type of comments: {str(e)}")
