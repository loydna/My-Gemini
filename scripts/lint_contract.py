import os
import sys
import re

REQUIRED_FILES = [
    "contracts/GEMINI-VERIFICATION-CONTRACT/CORE.md",
    "contracts/GEMINI-VERIFICATION-CONTRACT/AMENDMENTS.md",
    "contracts/GEMINI-VERIFICATION-CONTRACT/VERSION.yaml"
]

METADATA_REGEX = re.compile(
    r"<!-- GEMINI-VERIFICATION-METADATA:BEGIN\n"
    r"contract: (.*?)\n"
    r"review_state: (.*?)\n"
    r"verification_status: (.*?)\n"
    r"verified_at: (.*?)\n"
    r"evidence: (.*?)\n"
    r"GEMINI-VERIFICATION-METADATA:END -->"
)

# A looser regex just to catch the presence of any block that might be malformed
BLOCK_START_REGEX = re.compile(r"<!-- GEMINI-VERIFICATION-METADATA:BEGIN")

def lint_required_files():
    errors = []
    for filepath in REQUIRED_FILES:
        if not os.path.exists(filepath):
            errors.append(f"Missing required contract file: {filepath}")
    return errors

def lint_markdown_file(filepath):
    errors = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        blocks_started = len(BLOCK_START_REGEX.findall(content))
        blocks = METADATA_REGEX.findall(content)

        if blocks_started > len(blocks):
            errors.append(f"{filepath}: Found a GEMINI-VERIFICATION-METADATA block that is malformed or missing fields.")

        if len(blocks) > 1:
            errors.append(f"{filepath}: Multiple verification metadata blocks found. Only one is allowed.")

        if len(blocks) == 1:
            contract_name, review_state, verification_status, verified_at, evidence = blocks[0]

            if contract_name != "GEMINI-VERIFICATION-CONTRACT":
                errors.append(f"{filepath}: Invalid contract name '{contract_name}'.")

            if review_state not in ["pending", "reviewed"]:
                errors.append(f"{filepath}: Invalid review_state '{review_state}'.")

            allowed_statuses = ["VERIFIED", "PARTIALLY VERIFIED", "UNVERIFIED", "CONTRADICTED", "null"]
            if verification_status not in allowed_statuses:
                errors.append(f"{filepath}: Invalid verification_status '{verification_status}'. Allowed: {allowed_statuses}")

            if review_state == "pending" and verification_status != "null":
                errors.append(f"{filepath}: Inconsistent state: review_state is 'pending' but verification_status is '{verification_status}'. Must be 'null'.")

            if verification_status in ["VERIFIED", "PARTIALLY VERIFIED", "UNVERIFIED", "CONTRADICTED"]:
                if review_state != "reviewed":
                     errors.append(f"{filepath}: Inconsistent state: verification_status is '{verification_status}' but review_state is not 'reviewed'.")
                if evidence == "[]" or not evidence.strip():
                     errors.append(f"{filepath}: Evidence must be provided when verification_status is set to {verification_status}.")

    except Exception as e:
        errors.append(f"Error reading {filepath}: {str(e)}")

    return errors

def main(test_mode=False, directory="."):
    if not test_mode:
        print("Linting contract files (Note: Linting only checks metadata syntax/state, not semantic compliance with CORE.md).")

    all_errors = []

    # 1. Check required files (only if we're linting the real repo root)
    if directory == ".":
        all_errors.extend(lint_required_files())

    # 2. Lint all markdown files for metadata
    for root, dirs, files in os.walk(directory):
        if "/." in root or "\\." in root or "venv" in root:
            continue

        for file in files:
            if file.endswith(".md"):
                filepath = os.path.join(root, file)
                all_errors.extend(lint_markdown_file(filepath))

    if all_errors:
        if not test_mode:
            print("\nLinting failed with the following errors:")
            for error in all_errors:
                print(f" - {error}")
            sys.exit(1)
        return all_errors

    if not test_mode:
        print("Linting passed successfully.")
        sys.exit(0)
    return []

if __name__ == "__main__":
    main()
