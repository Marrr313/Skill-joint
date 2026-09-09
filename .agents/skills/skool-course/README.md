# skool-course

A [Claude Code](https://claude.com/claude-code) skill that creates and updates courses on [Skool.com](https://www.skool.com) by driving a real browser through the Chrome DevTools MCP server.

Skool has no public API for course content, so the only way to populate a classroom is through the UI. This skill turns that into a repeatable procedure: it opens each lesson, sets the body via the TipTap editor instance, fires the one real keystroke React needs to enable the SAVE button, saves, and verifies the content survived a reload. It also handles creating modules (folders) and adding new pages inside them.

The three-step save procedure is the load-bearing part. Setting content with JavaScript alone updates the DOM but leaves React unaware, so SAVE stays disabled and the lesson is silently lost on navigation. The skill documents exactly which step prevents that and why no JavaScript-only substitute works.

## What's inside

- `SKILL.md`: the skill definition, input formats, the three-step lesson update procedure, the full course creation flow, and error recovery.
- `references/skool-structure.md`: the detailed playbook, holding verified code snippets for every operation, Chrome setup, page states, module three-dot menu automation, the HTML content format the editor accepts, timing and throughput numbers, and a troubleshooting table.

## Install

This skill ships inside the [NulightJens/jensai-skills](https://github.com/NulightJens/jensai-skills) monorepo. Install it with:

```bash
npx skills@latest add NulightJens/jensai-skills
```

Or copy this folder into your Claude Code skills directory:

```bash
cp -R skool-course ~/.claude/skills/skool-course
```

Claude Code auto-discovers skills by their `SKILL.md` front matter.

## Use

Before running, start a dedicated Chrome instance with remote debugging enabled and log into your Skool group in it:

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9333 \
  --user-data-dir="$HOME/.chrome-skool-automation" \
  --no-first-run \
  "https://www.skool.com/"
```

Point the Chrome DevTools MCP server at `http://127.0.0.1:9333`, open your classroom page, then ask Claude to "create a skool course", "publish this course to Skool", or "update my skool lessons". Hand it a structured markdown file, a directory of lesson drafts, or just describe the modules and lessons conversationally.

## A note on selectors

Skool is a React single-page app and its DOM class names, styled-component hashes, and SVG path data change whenever Skool ships a frontend update. The procedures here find elements dynamically wherever that is possible, matching on visible text, on the live editor instance, on button state. A few anchors are necessarily literal, and `references/skool-structure.md` names each one so you know where to look when a run stops finding something. If a step reports "not found" while the page looks correct in a screenshot, take a snapshot, read the current attribute off the live page, and refresh the selector.

## License

MIT, see [LICENSE](LICENSE).

Built by [Jens Heitmann](https://www.instagram.com/jens.heitmann), part of the JensAI skills collection.
