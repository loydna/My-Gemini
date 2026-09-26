import os
import json
import pytest
import shutil
import tempfile
from scripts.safe_mass_tagger import process_markdown_file, process_structured_file, MARKDOWN_TAG

@pytest.fixture
def temp_workspace():
    # Create a temporary directory
    workspace = tempfile.mkdtemp()
    yield workspace
    # Cleanup after test
    shutil.rmtree(workspace)

def test_markdown_dry_run(temp_workspace):
    md_path = os.path.join(temp_workspace, "test.md")
    with open(md_path, "w") as f:
        f.write("# Hello\nThis is a test.")

    status, _ = process_markdown_file(md_path, dry_run=True)
    assert status == "modified"

    # Verify file was not actually modified
    with open(md_path, "r") as f:
        content = f.read()
    assert "GEMINI-VERIFICATION-METADATA" not in content

def test_markdown_apply_idempotent(temp_workspace):
    md_path = os.path.join(temp_workspace, "test.md")
    original_content = "# Hello\nThis is a test."
    with open(md_path, "w") as f:
        f.write(original_content)

    # First apply
    status, _ = process_markdown_file(md_path, dry_run=False)
    assert status == "modified"

    with open(md_path, "r") as f:
        content = f.read()
    assert content.endswith(MARKDOWN_TAG)

    # Second apply (idempotency check)
    status2, _ = process_markdown_file(md_path, dry_run=False)
    assert status2 == "skipped"

    with open(md_path, "r") as f:
        content2 = f.read()

    # Content should be exactly the same as after the first apply
    assert content == content2

def test_structured_file_apply_idempotent(temp_workspace):
    json_path = os.path.join(temp_workspace, "data.json")
    with open(json_path, "w") as f:
        f.write('{"key": "value"}')

    sidecar_path = json_path + ".verification.jsonl"

    # Dry run
    status, _ = process_structured_file(json_path, dry_run=True)
    assert status == "modified"
    assert not os.path.exists(sidecar_path)

    # First apply
    status2, _ = process_structured_file(json_path, dry_run=False)
    assert status2 == "modified"
    assert os.path.exists(sidecar_path)

    with open(sidecar_path, "r") as f:
        lines = f.readlines()
    assert len(lines) == 1

    # Second apply (idempotency check for same content)
    status3, _ = process_structured_file(json_path, dry_run=False)
    assert status3 == "skipped"

    with open(sidecar_path, "r") as f:
        lines2 = f.readlines()
    assert len(lines2) == 1 # Still 1 line

    # Change content of json, apply again -> should append new record because content hash changed
    with open(json_path, "w") as f:
        f.write('{"key": "new_value"}')

    status4, _ = process_structured_file(json_path, dry_run=False)
    assert status4 == "modified"

    with open(sidecar_path, "r") as f:
        lines3 = f.readlines()
    assert len(lines3) == 2 # Now 2 lines
