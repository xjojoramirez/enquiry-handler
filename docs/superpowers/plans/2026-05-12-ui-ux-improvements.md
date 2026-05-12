# UI/UX Improvements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure the enquiry handler layout from vertical (textarea top, results bottom, history sidebar) to side-by-side (large textarea left, results right, no history).

**Architecture:** Single-page React app with Tailwind CSS. No routing, no state management library. Layout changes are purely within `App.jsx` and `EnquiryForm.jsx`. Dead code removal in `api.js`.

**Tech Stack:** React 18, Vite 6, Tailwind CSS 3

---

### Task 1: Remove unused API functions

**Files:**
- Modify: `frontend/src/api.js:22-34`

- [ ] **Step 1: Remove dead code from api.js**

Remove the `submitEnquiry`, `listEnquiries`, and `getEnquiry` functions. Keep only the `request` helper and `classify`.

Replace the content of `frontend/src/api.js` with:

```js
const BASE = '/api';

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function classify(text) {
  return request('/classify', {
    method: 'POST',
    body: JSON.stringify({ text }),
  });
}
```

- [ ] **Step 2: Verify the file parses**

```bash
node -c /home/jojo/dev-opencode/enquiry-handler/frontend/src/api.js
```

Expected: no output (syntax OK).

- [ ] **Step 3: Commit**

```bash
git add frontend/src/api.js
git commit -m "chore: remove unused API functions (submitEnquiry, listEnquiries, getEnquiry)"
```

---

### Task 2: Widen the enquiry form textarea

**Files:**
- Modify: `frontend/src/skills/enquiry-form/EnquiryForm.jsx:13-19`

- [ ] **Step 1: Update textarea height**

Change the textarea `className` from `h-28` to `min-h-[70vh]` so it fills most of the viewport height.

Before:
```jsx
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Paste a client enquiry here..."
        className="w-full h-28 rounded-lg border border-gray-300 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y"
        disabled={loading}
      />
```

After:
```jsx
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Paste a client enquiry here..."
        className="w-full min-h-[70vh] rounded-lg border border-gray-300 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y"
        disabled={loading}
      />
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/skills/enquiry-form/EnquiryForm.jsx
git commit -m "feat: widen enquiry textarea to fill viewport height"
```

---

### Task 3: Restructure App layout (side-by-side, remove history)

**Files:**
- Modify: `frontend/src/App.jsx`
- Delete: `frontend/src/skills/enquiry-history/` (entire directory)

- [ ] **Step 1: Delete the enquiry-history directory**

```bash
rm -rf /home/jojo/dev-opencode/enquiry-handler/frontend/src/skills/enquiry-history/
```

- [ ] **Step 2: Rewrite App.jsx**

Replace the entire `App.jsx` content with:

```jsx
import { useState } from 'react';
import EnquiryForm from './skills/enquiry-form/EnquiryForm';
import ResultCard from './skills/result-card/ResultCard';
import LoadingSpinner from './skills/shared/LoadingSpinner';
import ErrorBanner from './skills/shared/ErrorBanner';
import { classify } from './api';

export default function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleAnalyse(text) {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await classify(text);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <h1 className="text-xl font-bold text-gray-800">AI Enquiry Handler</h1>
          <p className="text-sm text-gray-500">Strata Management Consultants</p>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-6">
        <div className="flex flex-col md:flex-row gap-6">
          <div className="flex-1">
            <EnquiryForm onSubmit={handleAnalyse} loading={loading} />
          </div>
          <div className="flex-1">
            {loading && <LoadingSpinner />}
            {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}
            {result && !loading && <ResultCard result={result} />}
          </div>
        </div>
      </main>
    </div>
  );
}
```

Key changes from original:
- Removed `EnquiryHistory` import and usage
- Wrapped columns in `flex flex-col md:flex-row gap-6` for responsive stacking
- Left column gets `flex-1` with `EnquiryForm`
- Right column gets `flex-1` with results/loading/error

- [ ] **Step 3: Verify the app builds**

```bash
cd /home/jojo/dev-opencode/enquiry-handler/frontend && npx vite build 2>&1 | tail -5
```

Expected: Build succeeds with no errors.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/App.jsx
git rm -r frontend/src/skills/enquiry-history/
git commit -m "feat: restructure layout to side-by-side, remove history sidebar"
```

---

### Plan Self-Review

1. **Spec coverage:** All spec requirements covered — new layout (Task 3), taller textarea (Task 2), dead code removal (Task 1), history removal (Task 3).
2. **Placeholder scan:** No TBDs, TODOs, or vague instructions. All code is concrete.
3. **Type consistency:** `classify` is the only API function used, imported correctly in App.jsx. State variables (`result`, `loading`, `error`) consistent across tasks.
