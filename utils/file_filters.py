# utils/file_filter.py
import os
import fnmatch
from typing import List
from States.state import File
from utils.logger import get_logger

log = get_logger()


def get_exclude_patterns_from_env(env_var: str = "INPUT_EXCLUDE") -> List[str]:
    raw = os.environ.get(env_var, "")
    if raw.strip():
        patterns = [p.strip() for p in raw.split(",") if p.strip()]
        log.debug(f"Processed exclude file patterns: {patterns}")
        return patterns
    return []


def filter_files_by_exclude_patterns(files: List[File],exclude_patterns:List[str]=get_exclude_patterns_from_env()) -> List[File]:
    filtered = []
    for file in files:
        file_path = file.to_file
        should_exclude = any(fnmatch.fnmatch(file_path, pattern) for pattern in exclude_patterns)
        if should_exclude:
            log.debug(f"Excluding file: {file_path}")
            continue
        filtered.append(file)
        log.debug(f"Including file: {file_path}")

    log.debug(f"Files to analyze after filtering: {[f.to_file for f in filtered]}")
    return filtered


