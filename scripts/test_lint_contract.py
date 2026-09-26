import os
import pytest
import tempfile
import shutil
from scripts.lint_contract import lint_markdown_file

@pytest.fixture
def temp_workspace():
    workspace = tempfile.mkdtemp()
    yield workspace
    shutil.rmtree(workspace)

def test_lint_passing_block(temp_workspace):
    md_path = os.path.join(temp_workspace, "test.md")
    with open(md_path, "w") as f:
        f.write("""
<!-- GEMINI-VERIFICATION-METADATA:BEGIN
contract: GEMINI-VERIFICATION-CONTRACT
review_state: pending
verification_status: null
verified_at: null
evidence: []
GEMINI-VERIFICATION-METADATA:END -->
""")
    errors = lint_markdown_file(md_path)
    assert not errors

def test_lint_failing_malformed_block(temp_workspace):
    md_path = os.path.join(temp_workspace, "test.md")
    with open(md_path, "w") as f:
        f.write("""
<!-- GEMINI-VERIFICATION-METADATA:BEGIN
contract: GEMINI-VERIFICATION-CONTRACT
review_state: pending
""")
    errors = lint_markdown_file(md_path)
    assert len(errors) == 1
    assert "malformed or missing fields" in errors[0]

def test_lint_failing_duplicate_blocks(temp_workspace):
    md_path = os.path.join(temp_workspace, "test.md")
    with open(md_path, "w") as f:
        f.write("""
<!-- GEMINI-VERIFICATION-METADATA:BEGIN
contract: GEMINI-VERIFICATION-CONTRACT
review_state: pending
verification_status: null
verified_at: null
evidence: []
GEMINI-VERIFICATION-METADATA:END -->
<!-- GEMINI-VERIFICATION-METADATA:BEGIN
contract: GEMINI-VERIFICATION-CONTRACT
review_state: pending
verification_status: null
verified_at: null
evidence: []
GEMINI-VERIFICATION-METADATA:END -->
""")
    errors = lint_markdown_file(md_path)
    assert any("Multiple verification metadata blocks found" in e for e in errors)

def test_lint_failing_inconsistent_state(temp_workspace):
    md_path = os.path.join(temp_workspace, "test.md")
    with open(md_path, "w") as f:
        f.write("""
<!-- GEMINI-VERIFICATION-METADATA:BEGIN
contract: GEMINI-VERIFICATION-CONTRACT
review_state: pending
verification_status: VERIFIED
verified_at: 2024-05-15
evidence: [https://example.com]
GEMINI-VERIFICATION-METADATA:END -->
""")
    errors = lint_markdown_file(md_path)
    assert any("Inconsistent state" in e for e in errors)
    assert any("review_state is 'pending' but verification_status is 'VERIFIED'" in e for e in errors)

def test_lint_failing_missing_evidence(temp_workspace):
    md_path = os.path.join(temp_workspace, "test.md")
    with open(md_path, "w") as f:
        f.write("""
<!-- GEMINI-VERIFICATION-METADATA:BEGIN
contract: GEMINI-VERIFICATION-CONTRACT
review_state: reviewed
verification_status: VERIFIED
verified_at: 2024-05-15
evidence: []
GEMINI-VERIFICATION-METADATA:END -->
""")
    errors = lint_markdown_file(md_path)
    assert any("Evidence must be provided" in e for e in errors)
