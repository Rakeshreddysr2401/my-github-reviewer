from States.state import ReviewState
from services.model_services.chatmodel import get_ai_response
from utils.path_utils import normalize_file_path


def code_reviewer(state: ReviewState) -> ReviewState:
    pr_details = state.pr_details
    file = state.files[state.current_file_index]
    chunk = file.chunks[state.current_chunk_index]
    normalized_path = normalize_file_path(file.to_file)
    guidelines_available = chunk.guidelines is not None and chunk.guidelines.strip() != ""
    formatted_changes = []
    for change in chunk.changes:
        prefix = f"{change.line_number} " if change.line_number else ""
        formatted_changes.append(f"{prefix}{change.content}")
    formatted_chunk = "\n".join(formatted_changes)

    prompt_parts = [
        "Your task is reviewing pull requests according to our coding guidelines.",
        "Instructions:",
        "- Respond in this JSON format: {\"reviews\": [{\"lineNumber\": <line_number>, \"reviewComment\": \"<review comment>\"}]}",
        "- Only reference added lines (those starting with '+') in the diff.",
        "- Only add a comment if improvement is needed (bugs, performance, security, style).",
        "- Use GitHub Markdown formatting.",
        "- Do NOT suggest adding comments in the code.",
    ]

    if guidelines_available:
        prompt_parts.append("\nRelevant coding guidelines:\n" + chunk.guidelines)
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

    # Embed the diff
    prompt_parts.append("Git diff to review (format: line_number content):\n")
    prompt_parts.append("```diff\n" + formatted_chunk + "\n```")

    final_prompt = "\n".join(prompt_parts)

    state.current_prompt = final_prompt;
    state.llm_response = get_ai_response(state.current_prompt)
    return state




