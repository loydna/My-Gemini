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
    r"contract: GEMINI-VERIFICATION-CONTRACT\n"
    r"review_state: (pending|reviewed)\n"
    r"verification_status: (VERIFIED|PARTIALLY VERIFIED|UNVERIFIED|CONTRADICTED|null)\n"
    r"verified_at: (.*?)\n"
    r"evidence: (.*?)\n"
    r"GEMINI-VERIFICATION-METADATA:END -->"
)

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

        blocks = METADATA_REGEX.findall(content)

        # Check for multiple blocks
        if len(blocks) > 1:
            errors.append(f"{filepath}: Multiple verification metadata blocks found. Only one is allowed.")

        # If there's exactly one block, validate the status constraints
        if len(blocks) == 1:
            review_state, verification_status, verified_at, evidence = blocks[0]

            # If review_state is pending, status should probably be null, but let's just check allowed values
            allowed_statuses = ["VERIFIED", "PARTIALLY VERIFIED", "UNVERIFIED", "CONTRADICTED", "null"]
            if verification_status not in allowed_statuses:
                errors.append(f"{filepath}: Invalid verification_status '{verification_status}'. Allowed: {allowed_statuses}")

            if verification_status in ["VERIFIED", "PARTIALLY VERIFIED", "UNVERIFIED", "CONTRADICTED"]:
                if evidence == "[]" or not evidence.strip():
                     errors.append(f"{filepath}: Evidence must be provided when verification_status is set to {verification_status}.")

    except Exception as e:
        errors.append(f"Error reading {filepath}: {str(e)}")

    return errors

def main():
    print("Linting contract files...")
    all_errors = []

    # 1. Check required files
    all_errors.extend(lint_required_files())

    # 2. Lint all markdown files for metadata
    for root, _, files in os.walk("."):
        # Skip hidden dirs and venv
        if "/." in root or "\\." in root or "venv" in root:
            continue

        for file in files:
            if file.endswith(".md"):
                filepath = os.path.join(root, file)
                # print(f"Linting {filepath}")
                all_errors.extend(lint_markdown_file(filepath))

    if all_errors:
        print("\nLinting failed with the following errors:")
        for error in all_errors:
            print(f" - {error}")
        sys.exit(1)

    print("Linting passed successfully.")
    sys.exit(0)

if __name__ == "__main__":
    main()
