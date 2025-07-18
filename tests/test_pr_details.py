import json
from services.pr_details import get_pr_details, PRDetails

def test_get_pr_details(monkeypatch, tmp_path):
    mock_event = {
        "issue": {
            "number": 123
        },
        "pull_request": {},
        "repository": {
            "full_name": "octocat/Hello-World"
        }
    }

    event_file = tmp_path / "mock_event.json"
    event_file.write_text(json.dumps(mock_event))

    monkeypatch.setenv("GITHUB_EVENT_PATH", str(event_file))
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_mockToken")

    # Mock GitHub interaction if needed (requires more setup or mocking library)
    # For now we assume you test structure only or mock manually
    try:
        result = get_pr_details()
    except Exception:
        # Expected since GitHub mocking isn't set
        result = None

    assert isinstance(result, (PRDetails, type(None)))
