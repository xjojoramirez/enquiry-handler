---
name: result-card
description: Use when rendering classification results after analysing an enquiry
---

# Result Card

## Overview
Displays the full classification result: type badge, confidence meter, priority, summary, entities table, recommended team, and suggested response.

## Props
| Prop | Type | Description |
|------|------|-------------|
| `result` | ClassifyResponse | The classification result object |

## Sub-components
- `ClassificationBadge` — coloured badge for enquiry type
- `ConfidenceMeter` — visual confidence bar (0.0–1.0)
