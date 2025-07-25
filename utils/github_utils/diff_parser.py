# services/diff_parser.py

import re
from typing import List

from States.state import File,Change,Chunk
from utils.logger import get_logger
from utils.path_utils import normalize_file_path

log = get_logger()

def parse_diff(diff_text: str) -> List[File]:
    files = []
    current_file = None
    current_chunk = None
    target_line_number = 0

    print("======================Starting to parse diff====================")
    lines = diff_text.splitlines()
    line_index = 0
    in_binary_file = False

    while line_index < len(lines):
        line = lines[line_index]

        if line.startswith("Binary files") or line.startswith("GIT binary patch"):
            in_binary_file = True
            log.debug(f"Skipping binary file content: {line}")
            line_index += 1
            continue

        if line.startswith("diff --git"):
            in_binary_file = False
            if current_file:
                if current_chunk:
                    current_file.chunks.append(current_chunk)
                    current_chunk = None
                files.append(current_file)
                log.debug(f"Added file to list: {current_file.to_file} with {len(current_file.chunks)} chunks")

            #Starting New File
            current_file = File()
            parts = line.split()
            if len(parts) >= 3:
                if parts[2].startswith("a/"):
                    current_file.from_file = parts[2]
                if len(parts) > 3 and parts[3].startswith("b/"):
                    current_file.to_file = parts[3]
        #Adding From and To File
        elif line.startswith("--- ") and current_file:
            current_file.from_file = line[4:].strip()

        elif line.startswith("+++ ") and current_file:
            current_file.to_file = line[4:].strip()
        #Adding Some File Related Information
        #Adding New Chunk
        elif line.startswith("@@") and not in_binary_file and current_file:
            if current_chunk:
                current_file.chunks.append(current_chunk)
            current_chunk = Chunk()
            current_chunk.content = line

            match = re.match(r'@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@', line)
            if match:
                current_chunk.source_start = int(match.group(1))
                current_chunk.target_start = int(match.group(2))
                target_line_number = current_chunk.target_start
            else:
                current_chunk.source_start = 1
                current_chunk.target_start = 1
                target_line_number = 1
        #Adding Changes to Chunk
        elif current_chunk and current_file and not in_binary_file:
            current_chunk.content += "\n" + line

            if line.startswith(" ") or line.startswith("+"):
                change = Change(content=line, line_number=target_line_number)
                current_chunk.changes.append(change)
                current_chunk.formatted_chunk.append(f"{target_line_number}{line}")
                target_line_number += 1
            elif line.startswith("-"):
                change = Change(content=line)
                current_chunk.changes.append(change)
                current_chunk.formatted_chunk.append(f"{line}")

        line_index += 1

    if current_file:
        if current_chunk:
            current_file.chunks.append(current_chunk)
        files.append(current_file)

    files = [f for f in files if f.to_file]

    # Assign diff positions
    for file in files:
        position_counter = 0
        for chunk in file.chunks:
            position_counter += 1
            for change in chunk.changes:
                position_counter += 1
                change.diff_position = position_counter

    log.debug(f"Diff parsing complete. Found {len(files)} files.")
    for file in files:
        log.debug(f"File: {normalize_file_path(file.to_file)} with {len(file.chunks)} chunks")

    return files
