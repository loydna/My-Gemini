# Gemini Verification Contract Integration

This repository strictly implements a verification doctrine designed to prevent Large Language Models (LLMs), specifically Gemini, from making negative assertions (e.g., claiming a model or tool "does not exist") based solely on stale internal training data.

The canonical contract and its core constitutional rules reside in `contracts/GEMINI-VERIFICATION-CONTRACT/CORE.md`.

## Integration for Gemini CLI

When using a Gemini CLI tool pointing at this repository, you must explicitly import the verification contract rules as context for the session.

Example using context import:
```bash
gemini chat --context @contracts/GEMINI-VERIFICATION-CONTRACT/CORE.md
```

You can verify the rules have been loaded by inspecting the active memory:
```bash
gemini /memory show
```

## Integration for Gemini Apps (Gems)

To utilize this verification contract persistently within a consumer Gemini environment (e.g., Gemini Advanced Gems):
1. Create a new Gem.
2. Copy the contents of `contracts/GEMINI-VERIFICATION-CONTRACT/prompts/GEMINI_EVIDENCE_AUDITOR.md` into the Gem's system instructions.
3. Attach `CORE.md` and `DOMAIN-RULES/` files as grounding documents if supported by your Gem configuration.

**Important Note on Persistence:** Do not claim or assume that this verification contract is actively persistent or successfully guiding the Gem's behavior until you have manually run tests (like the scenarios in `TESTS/`) and confirmed the Gem adheres to the required pipeline, refuses self-certified freshness, and properly utilizes external retrieval. Offline tests in this repository only validate the structural rules and expected outputs, they cannot prove live API/Gem configurations are correctly applied.
