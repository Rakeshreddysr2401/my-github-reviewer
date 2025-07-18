from typing import Optional

from States.state import File, Chunk
from utils.logger import get_logger
from utils.path_utils import normalize_file_path

log = get_logger()

def create_prompt(file: File, chunk: Chunk, pr_details: PRDetails, guidelines_store: Optional[object] = None) -> str:
    """
    Creates a natural language prompt for an AI model to review a specific code chunk in a pull request.
    The prompt includes file diffs, optional coding guidelines, and PR metadata.
    """
    try:
        # Normalize path for consistency
        normalized_path = normalize_file_path(file.to_file)
        log.debug(f"Normalized file path: {normalized_path}")

        # Fetch relevant coding guidelines
        guidelines_text = ""
        if guidelines_store:
            log.debug(f"Fetching guidelines for: {normalized_path}")
            relevant_guidelines = guidelines_store.get_relevant_guidelines(
                code_snippet=chunk.content,
                file_path=normalized_path
            )
            guidelines_text = "\n".join(relevant_guidelines)
            log.debug(f"Found {len(relevant_guidelines)} relevant guidelines")
        else:
            log.debug("No guideline store found. Skipping guidelines context.")

        # Format code diff with line numbers
        formatted_changes = []
        for change in chunk.changes:
            prefix = f"{change.line_number} " if change.line_number else ""
            formatted_changes.append(f"{prefix}{change.content}")
        formatted_chunk = "\n".join(formatted_changes)
        log.debug(f"Formatted {len(chunk.changes)} code changes.")

        # Construct prompt step by step
        prompt_parts = [
            "Your task is reviewing pull requests according to our coding guidelines.",
            "Instructions:",
            "- Respond in this JSON format: {\"reviews\": [{\"lineNumber\": <line_number>, \"reviewComment\": \"<review comment>\"}]}",
            "- Only reference added lines (those starting with '+') in the diff.",
            "- Only add a comment if improvement is needed (bugs, performance, security, style).",
            "- Use GitHub Markdown formatting.",
            "- Do NOT suggest adding comments in the code.",
        ]

        # Append guideline context
        if guidelines_text:
            prompt_parts.append("\nRelevant coding guidelines:\n" + guidelines_text)
        else:
            prompt_parts.append("\nNo specific coding guidelines provided. Review based on best practices and quality.")

        # Add PR context and diff
        prompt_parts.append(f'\nReview the following code diff in file: "{normalized_path}"')
        prompt_parts.append(f"Pull request title: {pr_details.title}")
        prompt_parts.append("Pull request description:\n---")
        prompt_parts.append(pr_details.description or "No description provided")
        prompt_parts.append("---")

        # Embed the diff
        prompt_parts.append("Git diff to review (format: line_number content):\n")
        prompt_parts.append("```diff\n" + formatted_chunk + "\n```")

        final_prompt = "\n".join(prompt_parts)
        log.debug(f"Prompt created successfully. Length: {len(final_prompt)} characters")

        return final_prompt

    except Exception as e:
        log.exception("Failed to create review prompt")
        raise RuntimeError(f"Prompt creation failed for {file.to_file}") from e
