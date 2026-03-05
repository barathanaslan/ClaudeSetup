---
name: gemini-api
description: Google Gemini API integration patterns. Use when code imports google.generativeai, google.genai, or the user mentions Gemini, Google AI, or any Gemini model name (Flash, Pro, etc.). TRIGGER on any LLM API work involving Google models.
user-invocable: false
---

# Gemini API Integration

## Critical Rules

### 1. NEVER Override the User's Model Choice
If the user says "Gemini 3.0 Flash", use exactly that string. Do NOT substitute with a model you know. Your training data is outdated — the user knows which models exist NOW.

### 2. NEVER Assume API Patterns From Memory
The `google-genai` library changes frequently. Before writing ANY Gemini code:
- **Web search** for current API documentation
- Search: `google genai python <feature> site:googleapis.github.io` or `site:ai.google.dev`
- Verify exact import paths, class names, method signatures

### 3. Use google-genai (NOT google-generativeai)
The old `google-generativeai` package is **deprecated**. The new unified SDK is:
```bash
pip install google-genai
```
```python
from google import genai
from google.genai import types
```
If a project uses the old library, suggest migrating.

### 4. Model Name Format
- Model names change constantly. Do NOT hardcode from memory.
- Ask the user or web search for the exact model string
- Use the user's exact string — never "correct" it

### 5. Always Handle Errors
- Rate limits (429): exponential backoff
- Quota exceeded: graceful error message
- Log the model name being used so the user can verify

## Reference Links (web search these, not your memory)

- **Official SDK docs**: https://googleapis.github.io/python-genai/
- **SDK GitHub + codegen_instructions.md**: https://github.com/googleapis/python-genai
- **Gemini API quickstart**: https://ai.google.dev/gemini-api/docs/quickstart
- **Available models list**: https://ai.google.dev/gemini-api/docs/models
- **API changelog**: https://ai.google.dev/gemini-api/docs/changelog
- **Migration guide** (old → new SDK): https://ai.google.dev/gemini-api/docs/migrate
- **Imagen/image generation**: https://ai.google.dev/gemini-api/docs/image-generation

When unsure about any API detail, fetch: `https://raw.githubusercontent.com/googleapis/python-genai/main/codegen_instructions.md` — this is the official reference the SDK maintainers keep updated.

## Reference Patterns

See [references/gemini-patterns.md](references/gemini-patterns.md) for verified API patterns.

**These patterns may become outdated. When in doubt, web search.**
The cost of a 5-second search is nothing compared to a broken pipeline.
