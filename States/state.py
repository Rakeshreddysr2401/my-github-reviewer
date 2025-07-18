# services/diff_parser/models.py

class Chunk:
    """Represents a chunk/hunk in a diff."""
    def __init__(self):
        self.content = ""
        self.changes = []
        self.source_start = 0
        self.source_length = 0
        self.target_start = 0
        self.target_length = 0

class Change:
    """Represents a single change line in a diff."""
    def __init__(self, content="", line_number=None):
        self.content = content
        self.line_number = line_number
        self.diff_position = None

class File:
    """Represents a file in a diff."""
    def __init__(self):
        self.from_file = None
        self.to_file = None
        self.chunks = []
