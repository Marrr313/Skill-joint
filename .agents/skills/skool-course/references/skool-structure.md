# Skool Automation: Battle-Tested Patterns

> Distilled from real automation sessions populating 68+ lessons. Every pattern below has been verified with saves persisting after page reloads.

## Platform Details

- **Editor**: TipTap/ProseMirror wrapped in React (`skool-editor2` class)
- **Framework**: React SPA. DOM changes do NOT trigger React state unless real input events fire
- **URL pattern**: `https://www.skool.com/{group-slug}/classroom/{course-id}?md={lesson-id}`
- **No public API**: Browser automation is the only way to create/edit course content

## Chrome Setup

Run a dedicated Chrome instance for automation, with its own profile directory:

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9333 \
  --user-data-dir="$HOME/.chrome-skool-automation" \
  --no-first-run \
  "https://www.skool.com/"
```

Point the Chrome DevTools MCP server at `http://127.0.0.1:9333` in your MCP config.

**Use a separate profile, never the browser you work in.** The profile above is persistent, so the Skool login survives reboots: log in once and reuse it. If port 9333 is not listening, launch the isolated instance again rather than restarting an existing browser to add the debugging flag.

---

## The 3-Step Lesson Update Procedure (PROVEN)

This is the reliable flow for updating any lesson's content. Every step is required. Do NOT skip Step 2.

### Step 1: Open Editor & Set Content

**1a. Click the pencil/edit button** (pages load in view mode after navigation):

```javascript
// evaluate_script
() => {
  const btns = document.querySelectorAll('button');
  for (const b of btns) {
    const p = b.querySelector('svg path');
    if (p && p.getAttribute('d')?.startsWith('M19.2555')) {
      const r = b.getBoundingClientRect();
      if (r.y > 100 && r.y < 300) { b.click(); return 1; }
    }
  }
  return 0;
}
```

**1b. Wait for editor to mount** (required, since the editor mounts async after the pencil click):

```javascript
// evaluate_script
() => {
  return new Promise((resolve) => {
    const check = () => {
      const el = document.querySelector('.tiptap.ProseMirror.skool-editor2');
      if (el && el.editor) resolve(1);
      else setTimeout(check, 300);
    };
    check();
    setTimeout(() => resolve(0), 5000);
  });
}
```

If returns `0`, retry pencil click or take a screenshot to check page state.

**1c. Set content and focus**:

```javascript
// evaluate_script
() => {
  const el = document.querySelector('.tiptap.ProseMirror.skool-editor2');
  el.editor.commands.setContent(`<h2>Title</h2><p>Content here...</p>`);
  el.focus();
  el.editor.commands.focus('end');
  return { set: true, length: el.textContent.length };
}
```

### Step 2: Trigger React Dirty State

```
type_text: " "
```

This physically types a space at the cursor position. React detects the keyboard input and marks the editor as dirty. The SAVE button becomes enabled.

**CRITICAL**: Without this step, `setContent()` updates the DOM but React doesn't know. SAVE stays disabled. Clicking it does nothing. Content is lost on navigation.

**DO NOT substitute** with `el.dispatchEvent()`, `el.focus()`, `document.execCommand()`, or any JavaScript-only approach. Only the MCP `type_text` tool fires real keyboard events that React's synthetic event system picks up.

### Step 3: Click SAVE

```javascript
// evaluate_script
() => {
  const btns = document.querySelectorAll('button');
  for (const b of btns) {
    if (b.textContent.trim() === 'SAVE' && !b.disabled) {
      b.click();
      return 'SAVED';
    }
  }
  return 'save still disabled';
}
```

If returns `'save still disabled'`, Step 2 didn't work. Retry `type_text " "`.

---

## Navigating Between Lessons

```javascript
// navigate_page
{ url: "https://www.skool.com/{group-slug}/classroom/{course-id}?md={lesson-id}", type: "url" }
```

After navigation, pages load in **view mode**. Wait for the page title before clicking pencil:

```javascript
// wait_for
{ text: ["Lesson Title Here"], timeout: 5000 }
```

---

## Page States

### View Mode (after navigation)
- Lesson title + content shown read-only
- Two buttons top-right: completion checkmark + pencil (edit)
- No editor toolbar, no SAVE/CANCEL

### Edit Mode (after clicking pencil)
- Editor toolbar visible (H1-H4, B, I, S, code, lists, quote, image, link, video)
- Title field editable (input element)
- Content area is TipTap editor (contenteditable)
- Bottom bar: ADD dropdown, Published toggle, CANCEL, SAVE
- SAVE is **disabled** until React detects a change (see Step 2)

---

## Creating New Lessons (Pages)

### Method 1: Three-Dot Menu on Module Header (PROVEN, AUTOMATED)

Each module/folder in the sidebar has a **three-dot menu** inside `MenuItemTitleWrapper`. The button exists in the DOM but only renders visually on CSS `:hover`, so click it directly via JS. No hover needed.

**Step 1. Click the module's dropdown button** (replace the title string with your module's name):
```javascript
// evaluate_script
() => {
  const wrappers = document.querySelectorAll('.styled__MenuItemTitleWrapper-sc-1wvgzj7-6');
  for (const w of wrappers) {
    const titleEl = w.querySelector('.styled__MenuItemTitle-sc-1wvgzj7-8');
    if (titleEl && titleEl.textContent.trim() === 'Getting Started') {
      w.scrollIntoView({ block: 'center' });
      const dropBtn = w.querySelector('.styled__DropdownButton-sc-1c1jt59-9');
      if (dropBtn) { dropBtn.click(); return 'clicked'; }
    }
  }
  return 'not found';
}
```

The `styled__*-sc-*` class hashes are generated by styled-components and change when Skool rebuilds its frontend. If this returns `'not found'`, snapshot the sidebar and read the current class names off the module row.

**Step 2. Click "Add page in folder" from the dropdown:**
```javascript
// evaluate_script
() => {
  const allDivs = document.querySelectorAll('div');
  for (const d of allDivs) {
    if (d.textContent.trim() === 'Add page in folder' && d.children.length === 0) {
      d.parentElement.click();
      return 'clicked';
    }
  }
  return 'not found';
}
```

**Step 3. Wait for navigation to the new page, then edit:**
- The browser auto-navigates to the new "New page" inside the target module
- Click pencil, wait for editor + title input
- Set title using native React setter: `Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(inp, 'New Title')` + dispatch `input` event
- Set content via `el.editor.commands.setContent(html)`, type_text " ", click SAVE

**Dropdown menu options:** Edit folder, Add page in folder, Duplicate folder, Delete folder

### Method 2: Repurpose Orphan "New page" Entries

Modules often carry blank "New page" entries left over from initial setup. Navigate to them, enter edit mode, change the title, add content, and save.

To change the title in edit mode, find the Title input:
```javascript
// After entering edit mode, the title input is visible
() => {
  const inputs = document.querySelectorAll('input');
  for (const inp of inputs) {
    if (inp.value === 'New page' || inp.placeholder?.includes('Title')) {
      inp.focus();
      inp.select();
      return { found: true, currentValue: inp.value };
    }
  }
  return { found: false };
}
```
Then `type_text` the new title.

---

## Content Format (HTML)

The TipTap editor accepts standard HTML via `setContent()`:

```html
<h2>Heading 2</h2>
<p>Paragraph with <strong>bold</strong> and <code>inline code</code>.</p>
<ol><li>Ordered list item</li></ol>
<ul><li>Unordered list item with <strong>bold label:</strong> description</li></ul>
<br> <!-- line break within a block -->
```

**Entities**: Use `&amp;` for `&` in HTML strings.
**Tested size**: Up to ~3,200 characters / ~500 words per lesson. No issues.

---

## Verification

Reload the page and check content persisted:

```javascript
// navigate_page
{ type: "reload" }

// wait_for
{ text: ["Expected Heading Text"], timeout: 5000 }
```

**Schedule**: Verify every 10 lessons or at the end of each module.

---

## Timing & Throughput

| Operation | Wait Method | Timeout |
|-----------|-----------|---------|
| Page navigation | `wait_for` with lesson title | 5000ms |
| Pencil click to editor mount | Promise polling (300ms intervals) | 5000ms |
| setContent to type_text | None needed (immediate) | n/a |
| SAVE click to next navigation | None needed (immediate) | n/a |

**Throughput**: ~20-30 seconds per lesson. 68 lessons completed in a single session (~30 min).

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `{ ready: false }` after setContent | Editor not mounted | Click pencil first, wait with Promise poll |
| `'save still disabled'` | React didn't detect change | Retry `type_text " "` |
| Content gone after navigation | SAVE never fired | Always verify SAVE returned `'SAVED'` |
| `el.editor` is null | Editor DOM exists but TipTap not attached | Wait longer with Promise poll |
| Pencil click `return 0` | SVG path changed or page still loading | `wait_for` page title first, then retry |
| Page opens directly in edit mode | Some pages auto-open in edit mode | Skip pencil, go directly to setContent |

---

## Course Hierarchy

```
Group (your-group)
└── Classroom (tab)
    └── Course (<course-id>)
        ├── Standalone pages (outside any module)
        └── Modules/Folders (collapsible sections)
            └── Lessons/Pages (individual content pages)
```

## Content Features (Manual Only)

These cannot be automated via Chrome DevTools:
- **Drip content**: Module unlock timing (X days after join)
- **Level gating**: Course locked behind membership levels
- **Video upload**: Native HD video per page
- **Attachments**: PDF uploads alongside lessons
- **Drag-and-drop reordering**: Lesson/module order in sidebar

## No Public API, and What That Costs

Skool has no public API for course CRUD, so browser automation is the only approach. That makes every selector in this file a dependency on Skool's current frontend build.

Prefer dynamic discovery: match on visible text, on the live editor instance, on button state. Reserve hardcoded selectors for the cases where nothing else identifies the element. Three anchors here are literal and worth checking first when a run breaks:

- the pencil button's SVG path prefix `M19.2555`
- the editor class `.tiptap.ProseMirror.skool-editor2`
- the styled-components sidebar hashes (`styled__MenuItemTitleWrapper-sc-*`, `styled__MenuItemTitle-sc-*`, `styled__DropdownButton-sc-*`)

All three were stable across the sessions that produced this document, and all three are exactly the kind of thing a Skool release renames. When one drifts, take a snapshot, read the current attribute off the live page, and update it here. The procedures themselves have proven durable even when the selectors have not.
