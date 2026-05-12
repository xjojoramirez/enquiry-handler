---
name: skills-reorganization
description: Use when restructuring enquiry-handler project to follow superpowers skill plugin layout
---

# Skills Reorganization Design

## Overview

Reorganize the enquiry-handler project to follow the superpowers skill plugin pattern — self-contained modules with sidecar documentation (`SKILL.md`), mirroring code and docs in a consistent tree.

## Scope

- **Backend**: Flatten `app/` into `app/skills/` with modules: `classification`, `storage`, `api`
- **Frontend**: Move `components/` into `src/skills/` with modules: `enquiry-form`, `result-card`, `enquiry-history`
- **Docs**: Create `docs/skills/`, `docs/specs/`, `docs/architecture/`, `docs/operations/`
- **SKILL.md files**: Add entrypoint docs at every module level
- **No functional changes**: Pure reorganization, all imports updated

## Backend Structure

```
app/
├── main.py                              # FastAPI app, imports from skills
├── __init__.py
├── config/
│   ├── __init__.py
│   └── settings.py                      # Unchanged
└── skills/
    ├── __init__.py
    ├── classification/
    │   ├── __init__.py
    │   ├── ai_service.py                # classify_enquiry, GibberishDetector, extract_json
    │   ├── schemas.py                   # ClassifyRequest, ClassifyResponse, ClassificationResult
    │   └── SKILL.md
    ├── storage/
    │   ├── __init__.py
    │   ├── enquiry_store.py             # EnquiryStore (save, get, list)
    │   ├── database.py                  # asyncpg pool
    │   ├── migrations.py                # Schema init
    │   └── SKILL.md
    └── api/
        ├── __init__.py
        ├── routers.py                   # All endpoints (was enquiries.py)
        ├── webhook.py                   # _fire_webhook helper
        └── SKILL.md

tests/
├── __init__.py
└── skills/
    ├── classification/
    │   └── test_classification.py       # Existing tests, relocated
    └── storage/
        └── test_storage.py
```

### Import changes

| Current path | New path |
|---|---|
| `app.services.ai_service` | `app.skills.classification.ai_service` |
| `app.models.schemas` | `app.skills.classification.schemas` |
| `app.services.enquiry_store` | `app.skills.storage.enquiry_store` |
| `app.db.database` | `app.skills.storage.database` |
| `app.db.migrations` | `app.skills.storage.migrations` |
| `app.routers.enquiries` | `app.skills.api.routers` |

## Frontend Structure

```
src/
├── main.jsx                              # Unchanged
├── index.css                             # Unchanged
├── api.js                                # Unchanged
├── App.jsx                               # Updated import paths
└── skills/
    ├── enquiry-form/
    │   ├── EnquiryForm.jsx               # From components/
    │   └── SKILL.md
    ├── result-card/
    │   ├── ResultCard.jsx                # From components/
    │   ├── ClassificationBadge.jsx       # From components/
    │   ├── ConfidenceMeter.jsx           # From components/
    │   └── SKILL.md
    └── enquiry-history/
        ├── EnquiryHistory.jsx            # From components/
        └── SKILL.md
```

### Import changes

| File | Old import | New import |
|---|---|---|
| `App.jsx` | `./components/EnquiryForm` | `./skills/enquiry-form/EnquiryForm` |
| `App.jsx` | `./components/ResultCard` | `./skills/result-card/ResultCard` |
| `App.jsx` | `./components/EnquiryHistory` | `./skills/enquiry-history/EnquiryHistory` |
| `ResultCard.jsx` | `./ClassificationBadge` | `../result-card/ClassificationBadge` |
| `ResultCard.jsx` | `./ConfidenceMeter` | `../result-card/ConfidenceMeter` |

## Documentation Structure

```
docs/
├── superpowers/
│   └── specs/
│       └── YYYY-MM-DD-<topic>-design.md
├── skills/
│   ├── backend/
│   │   ├── classification/README.md
│   │   ├── storage/README.md
│   │   └── api/README.md
│   ├── frontend/
│   │   ├── enquiry-form/README.md
│   │   ├── result-card/README.md
│   │   └── enquiry-history/README.md
│   └── deploy/README.md
├── architecture/overview.md
└── operations/troubleshooting.md
```

## SKILL.md Format (template)

```yaml
---
name: <kebab-case-skill-name>
description: Use when <triggering conditions for this module>
---

# <Skill Name>

## Overview
One-paragraph description of the module's purpose.

## When to Use
- Bullet list of scenarios

## Quick Reference
Key APIs, configs, or entry points.

## Dependencies
- What other skills/modules this depends on
- External services (e.g. LLM API, PostgreSQL)
</parameter>
