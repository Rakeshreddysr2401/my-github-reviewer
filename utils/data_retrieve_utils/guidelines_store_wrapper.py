# utils/data_retrieve_utils/guideline_store_wrapper.py

from typing import List
from utils.data_retrieve_utils.retrieve_instructions_from_db import retrieve_instructions

class GuidelineStore:
    def get_relevant_guidelines(self, code_snippet: str, file_path: str) -> List[str]:
        # You can enhance logic here by extracting topic from file_path if needed
        return retrieve_instructions(file_path=file_path, query=code_snippet)
