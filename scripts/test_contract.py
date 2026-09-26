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

def test_opus_5_5_case():
    case = load_test_case(os.path.join(TEST_DIR, "opus-5-5-case.md"))

    compliant = case.get("Compliant Candidate Response", "")
    assert "CONTRADICTED" in compliant, "Compliant response must contain CONTRADICTED verdict"
    assert "Date:" in compliant, "Compliant response must contain verification date"
    assert "official Anthropic channels" in compliant or "first-party" in compliant, "Compliant response must cite first-party sources"

    failing = case.get("Failing Candidate Response", "")
    assert "UNVERIFIED" in failing or "CONTRADICTED" in failing
    assert "training data" in failing.lower() or "does not exist" in failing.lower()

def test_stale_model_case():
    case = load_test_case(os.path.join(TEST_DIR, "stale-model-case.md"))

    compliant = case.get("Compliant Candidate Response", "")
    assert "VERIFIED" in compliant
    assert "Date:" in compliant

    failing = case.get("Failing Candidate Response", "")
    assert "CONTRADICTED" in failing
    assert "not a real model" in failing.lower()

def test_fake_quote_case():
    case = load_test_case(os.path.join(TEST_DIR, "fake-quote-case.md"))

    compliant = case.get("Compliant Candidate Response", "")
    assert "CONTRADICTED" in compliant
    assert "container" in compliant.lower() or "artifact" in compliant.lower() or "screenshot" in compliant.lower()
    assert "substantive claim" in compliant.lower() or "quote" in compliant.lower()

    failing = case.get("Failing Candidate Response", "")
    assert "CONTRADICTED" in failing
    assert "fake and manipulated" in failing.lower()

def validate_candidate_response_file(filepath):
    print(f"Validating external candidate response file: {filepath}")
    if not os.path.exists(filepath):
        print(f"Error: File {filepath} not found.")
        return False

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    verdicts = ["VERIFIED", "PARTIALLY VERIFIED", "UNVERIFIED", "CONTRADICTED"]
    has_verdict = any(v in content for v in verdicts)
    if has_verdict:
        print("Validation Passed: Found standardized verdict.")
        return True
    else:
        print("Validation Failed: Missing standardized verdict.")
        return False

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
