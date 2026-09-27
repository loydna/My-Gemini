# Domain Rules: GitHub

## Repository Lookup
Always query the live GitHub API or website for current repository existence, state, and recent commits.

## Namespace Verification
Verify the organization or user namespace matches expected authoritative ownership.

## Commit Verification
Use specific commit hashes or tags when validating code state, rather than general repository existence, to avoid temporal ambiguity.
