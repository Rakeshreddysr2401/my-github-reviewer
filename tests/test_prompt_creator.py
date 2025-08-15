import pytest

from States.state import File, Change, Chunk
from prompts.prompt_creator import create_prompt

from unittest.mock import MagicMock

from services.git_services.get_pr_details import PRDetails


@pytest.fixture
def dummy_data():
    file = File(to_file="src/utils/math.py")

    chunk = Chunk(
        content="def add(a, b): return a + b",
        changes=[
            Change(line_number=1, content="+def add(a, b): return a + b"),
            Change(line_number=2, content="+# simple add function")
        ]
    )

    pr_details = PRDetails(
        title="Add add function",
        description="This PR adds a basic addition utility."
    )

    return file, chunk, pr_details


def test_create_prompt_with_guidelines(dummy_data):
    file, chunk, pr_details = dummy_data

    mock_guideline_store = MagicMock()
    mock_guideline_store.get_relevant_guidelines.return_value = [
        "Use type hints",
        "Avoid inline comments"
    ]

    prompt = create_prompt(file, chunk, pr_details, mock_guideline_store)

    assert "Use type hints" in prompt
    assert "Avoid inline comments" in prompt
    assert "def add(a, b): return a + b" in prompt
    assert '"lineNumber": <line_number>' in prompt
    assert pr_details.title in prompt
    assert pr_details.description in prompt
    assert "```diff" in prompt


def test_create_prompt_without_guidelines(dummy_data):
    file, chunk, pr_details = dummy_data

    prompt = create_prompt(file, chunk, pr_details)

    assert "No specific coding guidelines provided" in prompt
    assert "def add(a, b): return a + b" in prompt
    assert pr_details.title in prompt
    assert pr_details.description in prompt
    assert "```diff" in prompt


def test_create_prompt_with_empty_description(dummy_data):
    file, chunk, _ = dummy_data

    pr_details = PRDetails(
        title="Fix add function bug",
        description=None
    )

    prompt = create_prompt(file, chunk, pr_details)

    assert "No description provided" in prompt
    assert pr_details.title in prompt


def test_create_prompt_formatting_error(monkeypatch, dummy_data):
    file, chunk, pr_details = dummy_data

    # Simulate an exception in normalize_file_path
    monkeypatch.setattr("prompts.prompt_creator.normalize_file_path", lambda _: (_ for _ in ()).throw(ValueError("Path error")))

    with pytest.raises(RuntimeError) as exc_info:
        create_prompt(file, chunk, pr_details)

    assert "Prompt creation failed" in str(exc_info.value)
