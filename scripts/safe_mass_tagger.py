import os
import argparse
import hashlib
import json
from datetime import datetime

MARKDOWN_TAG = """\n<!-- GEMINI-VERIFICATION-METADATA:BEGIN
contract: GEMINI-VERIFICATION-CONTRACT
review_state: pending
verification_status: null
verified_at: null
evidence: []
GEMINI-VERIFICATION-METADATA:END -->\n"""

def get_file_hash(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def process_markdown_file(filepath, dry_run=True):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if "<!-- GEMINI-VERIFICATION-METADATA:BEGIN" in content:
        return "skipped", None # Already tagged

    if not dry_run:
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(MARKDOWN_TAG)

    return "modified", None

def process_structured_file(filepath, dry_run=True):
    # For structured files like json, csv, we append to a sidecar JSONL file
    sidecar_path = filepath + ".verification.jsonl"

    file_hash = get_file_hash(filepath)

    # Check if this exact hash is already tagged in the sidecar
    if os.path.exists(sidecar_path):
        with open(sidecar_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    record = json.loads(line)
                    if record.get("content_hash") == file_hash:
                        return "skipped", None # Already tagged for this exact state
                except:
                    pass

    metadata_record = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "file_path": filepath,
        "content_hash": file_hash,
        "contract": "GEMINI-VERIFICATION-CONTRACT",
        "review_state": "pending",
        "verification_status": None,
        "verified_at": None,
        "evidence": []
    }

    if not dry_run:
        with open(sidecar_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(metadata_record) + "\n")

    return "modified", None

def main():
    parser = argparse.ArgumentParser(description="Safe Mass-Tagging Script for Gemini Verification")
    parser.add_argument("target", help="Directory or file to process")
    parser.add_argument("--apply", action="store_true", help="Apply changes. If not set, runs in dry-run mode.")
    args = parser.parse_args()

    dry_run = not args.apply

    if dry_run:
        print("=== DRY RUN MODE === No files will be modified.")

    if not os.path.exists(args.target):
        print(f"Error: Target '{args.target}' does not exist.")
        return

    files_to_process = []
    if os.path.isfile(args.target):
        files_to_process.append(args.target)
    else:
        for root, dirs, files in os.walk(args.target):
            # Explicitly skip hidden directories like .git
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            if "venv" in dirs:
                dirs.remove("venv")

            for file in files:
                if file.endswith((".md", ".json", ".csv")):
                    files_to_process.append(os.path.join(root, file))

    stats = {"scanned": len(files_to_process), "modified": 0, "skipped": 0, "failed": 0}
    errors = []

    for filepath in files_to_process:
        try:
            if filepath.endswith(".md"):
                status, err = process_markdown_file(filepath, dry_run)
            else:
                status, err = process_structured_file(filepath, dry_run)

            if status == "modified":
                stats["modified"] += 1
                if dry_run:
                    print(f"[DRY-RUN] Would modify: {filepath}")
                else:
                    print(f"Modified: {filepath}")
            elif status == "skipped":
                stats["skipped"] += 1

        except Exception as e:
            stats["failed"] += 1
            errors.append(f"{filepath}: {str(e)}")

    print("\n=== Summary ===")
    print(f"Mode: {'DRY RUN' if dry_run else 'APPLY'}")
    print(f"Scanned:  {stats['scanned']}")
    print(f"Modified: {stats['modified']}")
    print(f"Skipped:  {stats['skipped']} (already tagged)")
    print(f"Failed:   {stats['failed']}")

    if errors:
        print("\n=== Errors ===")
        for error in errors:
            print(error)

if __name__ == "__main__":
    main()
