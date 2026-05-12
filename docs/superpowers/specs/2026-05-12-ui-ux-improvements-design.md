# UI/UX Improvements — Enquiry Handler

## Overview

Restructure the main layout from a textarea-top/results-bottom + history sidebar to a side-by-side layout with a large textarea on the left and results on the right. Remove the history sidebar entirely.

## Layout

```
+------------------------------------------------------------------+
| Header: "AI Enquiry Handler"                                      |
|         "Strata Management Consultants"                            |
+------------------------------------------------------------------+
|                                                                   |
| +-- flex-1 (left) ---------------+ +-- flex-1 (right) ---------+ |
| |                                 | |                            | |
| |  Large textarea                 | |  ResultCard (sticky)       | |
| |  (min-h-[70vh], w-full)         | |  - ClassificationBadge    | |
| |                                 | |  - Priority               | |
| |  [Analyse Enquiry] button       | |  - ConfidenceMeter        | |
| |                                 | |  - Summary                | |
| |                                 | |  - Entities table         | |
| |                                 | |  - Recommended Team       | |
| |                                 | |  - Suggested Response     | |
| |                                 | |                            | |
| +----------------------------------+ +---------------------------+ |
+------------------------------------------------------------------+
```

## Changes

### Remove
- `EnquiryHistory` component and all its files
- `listEnquiries`, `submitEnquiry`, `getEnquiry` from `api.js` (dead code)
- History import and sidebar from `App.jsx`

### Modify `App.jsx`
- Change `flex` layout: no sidebar, two `flex-1` columns with `gap-6`
- Left column: EnquiryForm with taller textarea
- Right column: ResultCard (conditionally rendered)
- Make layout responsive: stacks vertically on small screens (`flex-col md:flex-row`)

### Modify `EnquiryForm.jsx`
- Increase textarea to `min-h-[70vh]` (most of viewport height)
- Keep button below textarea

### Files to modify:
1. `src/App.jsx` — new layout, remove history
2. `src/api.js` — remove unused functions
3. `src/skills/enquiry-form/EnquiryForm.jsx` — taller textarea
4. `src/skills/enquiry-history/` — delete directory

### Files unchanged:
- `ResultCard.jsx`, `ClassificationBadge.jsx`, `ConfidenceMeter.jsx` — no changes needed
- `LoadingSpinner.jsx`, `ErrorBanner.jsx` — no changes needed
