import os
import argparse
import pytest
import re

TEST_DIR = "contracts/GEMINI-VERIFICATION-CONTRACT/TESTS"

def load_test_case(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    sections = {}
    current_section = None

    for line in content.split('\n'):
        if line.startswith('## '):
            current_section = line[3:].strip()
            sections[current_section] = []
        elif current_section:
            sections[current_section].append(line)

    for k, v in sections.items():
        sections[k] = '\n'.join(v).strip()

    return sections

def _validate_compliant_response(content, expected_verdict, required_evidence_keywords):
    lines = content.strip().split('\n')
    verdict_line_found = False
    for line in lines:
        if line.startswith("VERDICT:"):
            verdict_line_found = True
            assert expected_verdict in line, f"Expected verdict {expected_verdict} in line: {line}"
            break
    assert verdict_line_found, "Compliant response must contain a line starting with 'VERDICT:'"

    date_line_found = any(line.startswith("Date:") for line in lines)
    assert date_line_found, "Compliant response must contain a line starting with 'Date:'"

    evidence_found = any(keyword.lower() in content.lower() for keyword in required_evidence_keywords)
    assert evidence_found, f"Compliant response must cite evidence (expected keywords: {required_evidence_keywords})"

def _validate_failing_response(content, unexpected_verdicts, required_failure_keywords):
    lines = content.strip().split('\n')
    verdict_line_found = False
    for line in lines:
        if line.startswith("VERDICT:"):
            verdict_line_found = True
            for unexpected in unexpected_verdicts:
                # Use regex or word boundary to ensure we don't match 'VERIFIED' inside 'UNVERIFIED'
                import re
                assert not re.search(r'\b' + unexpected + r'\b', line), f"Failing response should not have verdict {unexpected}"
            break

    failure_reason_found = any(keyword.lower() in content.lower() for keyword in required_failure_keywords)
    assert failure_reason_found, f"Failing response did not contain expected failure language: {required_failure_keywords}"

def test_opus_5_5_case():
    case = load_test_case(os.path.join(TEST_DIR, "opus-5-5-case.md"))

    compliant = case.get("Compliant Candidate Response", "")
    _validate_compliant_response(compliant, "CONTRADICTED", ["anthropic channels", "first-party"])

    failing = case.get("Failing Candidate Response", "")
    _validate_failing_response(failing, ["VERIFIED"], ["training data", "does not exist"])

def test_stale_model_case():
    case = load_test_case(os.path.join(TEST_DIR, "stale-model-case.md"))

    compliant = case.get("Compliant Candidate Response", "")
    _validate_compliant_response(compliant, "VERIFIED", ["official channels", "https://ai.meta.com"])

    failing = case.get("Failing Candidate Response", "")
    _validate_failing_response(failing, ["VERIFIED"], ["not a real model", "internal knowledge"])

def test_fake_quote_case():
    case = load_test_case(os.path.join(TEST_DIR, "fake-quote-case.md"))

    compliant = case.get("Compliant Candidate Response", "")
    _validate_compliant_response(compliant, "CONTRADICTED", ["container", "artifact", "substantive claim"])

    failing = case.get("Failing Candidate Response", "")
    _validate_failing_response(failing, ["VERIFIED"], ["fake and manipulated"])

def validate_candidate_response_file(filepath):
    print(f"Validating external candidate response file: {filepath}")
    if not os.path.exists(filepath):
        print(f"Error: File {filepath} not found.")
        return False

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check that a verdict is properly formatted on its own line and not inside quotes
    lines = content.split('\n')
    verdict_line = None
    for line in lines:
        if line.strip().startswith("VERDICT:"):
            verdict_line = line.strip()
            break

    if not verdict_line:
        print("Validation Failed: Missing VERDICT: line. Cannot be a bare word or inside a quote.")
        return False

    verdicts = ["VERIFIED", "PARTIALLY VERIFIED", "UNVERIFIED", "CONTRADICTED"]
    has_valid_verdict = any(v in verdict_line for v in verdicts)
    if not has_valid_verdict:
        print(f"Validation Failed: Invalid verdict in line '{verdict_line}'")
        return False

    # Heuristic for evidence
    if "http" not in content and "search" not in content.lower() and "source" not in content.lower():
        print("Validation Failed: Missing evidence (URL or source citation).")
        return False

    # Note: an offline test cannot prove a live search occurred.
    print("Validation Passed: Format and heuristic evidence checks passed (offline check only).")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run contract tests or validate a candidate response.")
    parser.add_argument("--validate", help="Path to a candidate response file to validate.")
    args = parser.parse_args()

    if args.validate:
        success = validate_candidate_response_file(args.validate)
        exit(0 if success else 1)
    else:
        # Default behavior is just to let pytest pick it up or provide help
        print("To run tests, use `pytest scripts/test_contract.py`.")
        print("To validate a file, use `python scripts/test_contract.py --validate <filepath>`.")
