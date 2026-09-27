# Agentic Design Patterns & Gemini Verification Contract — Agent Guide

A skill library derived from "Agentic Design Patterns" (21 chapters) and the immutable Gemini Verification Contract.
Each chapter -> one self-contained skill in `skills/`.

## Gemini Verification Contract: Acceptance & Execution Rules
When working in this repository on tasks related to factual claims, contract validation, or model output generation, all agents (including Jules) MUST adhere to the following workflow:
1. **List Assumptions:** Explicitly state any assumptions regarding the environment, the models, or the historical timeline.
2. **Identify Sources:** For every factual claim, provide a verifiable source link (e.g., a URL to a first-party announcement). Do NOT self-certify or claim you "searched" without providing the specific URL.
3. **Try a Counterexample:** Actively construct deceptive or adversarial test cases (e.g., a response that claims "source: trust me" or hides a verdict inside a blockquote) and demonstrate that the system rejects them.
4. **Report Unverified Claims:** Explicitly state what remains unverified or unknown. Do not describe a green CI run as proof of factual accuracy; CI only proves code structure, not live semantic behavior.

## Navigate
1. Read `manifest.json` for the skill index.
2. Pick the skills that match your role.
3. Load `skills/<id>/SKILL.md`. Load `references/` only if you need detail.

## Role -> Skills
- planner:  routing, planning, multi-agent, goal-setting, a2a, resource-aware-optimization, prioritization, exploration-discovery
- executor: prompt-chaining, routing, parallelization, tool-use, multi-agent, mcp, a2a
- critic:   reflection, learning-adaptation, reasoning-techniques, evaluation-monitoring, exploration-discovery
- memory:   memory-management, learning-adaptation, mcp, rag
- safety:   exception-handling, human-in-the-loop, guardrails

## Rules
- Do not load the entire PDF during normal execution. Use the compact skills first; consult canonical PDF-derived source slices whenever fidelity, ambiguity, provenance, or missing detail requires it. PDF is mostly for Human use
- Do not load all skills at once. Lazy-load only.
- Update `manifest.json` when adding a skill (check: `python3 tools/validate.py`).
- See `models/` for per-model guidance (Fable 5.1, Grok 4.6, Muse).
