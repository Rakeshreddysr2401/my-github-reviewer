# nodes/retrieve_guidelines.py
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from States.state import ReviewState
from utils.path_utils import normalize_file_path
from utils.logger import get_logger
from llm_config import get_llm

log = get_logger()
llm = get_llm()


def retrieve_guidelines(state: ReviewState) -> ReviewState:
    """Retrieve and summarize relevant coding guidelines for the current chunk."""
    if not state.files or state.current_file_index >= len(state.files):
        log.warning("No valid file to process")
        return state

    file = state.files[state.current_file_index]

    if not file.chunks or state.current_chunk_index >= len(file.chunks):
        log.warning("No valid chunk to process")
        return state

    chunk = file.chunks[state.current_chunk_index]
    path = normalize_file_path(file.to_file)
    guidelines_store = state.guidelines_store

    if not guidelines_store:
        chunk.guidelines = "No guidelines found for this chunk."
        return state

    # Build search context based on available information
    search_context_parts = [f"code chunk: {chunk.content}"]

    if state.llm_response:
        search_context_parts.append(f"review comment: {state.llm_response.model_dump_json()}")

    if state.review_feedback:
        search_context_parts.append(f"feedback: {state.review_feedback.model_dump_json()}")

    search_context = "\n".join(search_context_parts)

    log.info(f"Retrieving guidelines for file: {path}")

    try:
        guidelines = guidelines_store.get_relevant_guidelines(search_context, path)
        chunk.guidelines = "\n".join(guidelines) if guidelines else "No relevant guidelines found."

        if chunk.guidelines and chunk.guidelines != "No relevant guidelines found.":
            log.info("Using AI to summarize guidelines")

            messages = [
                SystemMessage(
                    content="You're an expert AI assistant who summarizes coding guidelines concisely. "
                            "Provide a summary in 200 words or less, focusing on the most relevant points."
                ),
                HumanMessage(
                    content=f"Code Path: {path}\nCode Chunk:\n{chunk.content}\n\nRelated Guidelines:\n{chunk.guidelines}"
                )
            ]

            response_summary: AIMessage = llm.invoke(messages)
            summary_text = response_summary.content.strip()
            chunk.guidelines = summary_text

            state.messages.append(HumanMessage(content=f"Guidelines to follow: {summary_text} in file: {file.to_file}"))
            log.info(f"Retrieved and summarized guidelines for file {file.to_file}\nSummary: {summary_text}")
        else:
            state.messages.append(HumanMessage(content=f"No specific guidelines found for file: {file.to_file}"))
            log.info(f"No guidelines found for file {file.to_file}")

    except Exception as e:
        log.error(f"Error retrieving guidelines: {e}")
        chunk.guidelines = "Error retrieving guidelines."

    return state