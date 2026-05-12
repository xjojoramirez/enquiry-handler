---
name: classification
description: Use when analysing client enquiries for type, priority, summary, and suggested response
---

# Classification

## Overview
Core AI skill that takes raw enquiry text, checks for gibberish, calls the configured LLM, and returns structured JSON with classification, priority, summary, entities, and suggested response.

## When to Use
- Processing a new client enquiry
- Re-analysing an existing enquiry (cached by text hash)

## Quick Reference

| Function | Input | Output |
|----------|-------|--------|
| `classify_enquiry(text)` | Raw text | dict with classification, priority, summary, entities, recommended_team, suggested_response |
| `GibberishDetector.is_gibberish(text)` | Raw text | bool |

## Dependencies
- `app.config.settings` — LLM model name, API key, base URL
- External LLM API (OpenCode Go or compatible)
