from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.messages import SystemMessage
from States.state import ReviewState
from utils.path_utils import normalize_file_path
from utils.logger import get_logger
from llm_config import get_llm
log=get_logger()
llm= get_llm()

def retrieve_guidelines(state: ReviewState) -> ReviewState:
    file = state.files[state.current_file_index]
    chunk = file.chunks[state.current_chunk_index]
    path = normalize_file_path(file.to_file)
    guidelines_store = state.guidelines_store


    if not guidelines_store:
        chunk.guidelines = "No guidelines found for this chunk."
        return state;

    if chunk.content and not state.llm_response:
        log.info(f"Retrieving guidelines based on code chunk for file: {path}")
        search_context = f"code chunk: {chunk.content}\n"
    elif chunk.content and  state.llm_response:
        log.info(f"Retrieving guidelines based on code chunk and llm response for file: {path}")
        search_context = f"review comment : {state.llm_response}\n code chunk : {chunk.content}"
    elif chunk.content and  state.llm_response and state.review_feedback:
        log.info(f"Retrieving guidelines based on code chunk and llm response and feedback provide for file: {path}")
        search_context = f" review coment : {state.llm_response}\n code chunk : {chunk.content}\n suggestions/feedback : {state.llm_response.model_dump_json(indent=2)}"
    else:
        search_context = f"code chunk: {chunk.content}\n"

    guidelines = guidelines_store.get_relevant_guidelines(search_context, path)
    # we can use this not to enrich the chunk with guidelines
    chunk.guidelines = "\n".join(guidelines)

    log.info("Using AI Summarizing Guidelines to follow in consise manner or to pick the best one")

    messages = [
        SystemMessage(
            content="You're an expert AI assistant who is capable of summarizing the guidelines in a concise manner and generating the  summary based on text given. make sure to include all and give summary in 200 words or less"),
        HumanMessage(
            content=f"Code Path: {path}\nCode Chunk:\n{chunk.content}\n\nRelated Guidelines:\n{chunk.guidelines}")
    ]

    response_summary: AIMessage = llm.invoke(messages)
    summary_text = response_summary.content.strip()
    chunk.guidelines = summary_text  # Overwrite with concise summary if desired
    state.messages.append(HumanMessage(content=f"Guidelines to follow: {summary_text} in file: {file.to_file}"))

    log.info(f"Retrieved guidelines for file {file.to_file} : {summary_text}")

    return state
