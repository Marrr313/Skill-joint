# saas-study

A [Claude Code](https://claude.com/claude-code) skill that studies a SaaS product end to end and writes an evidence folder you can actually reason from: what the product does, what it's built on, which third-party providers it leans on, what its own API surface looks like, and how it prices and meters the thing.

It runs in four phases. Phase 1 harvests the public surface (robots.txt, sitemap, a scored list of the pages worth reading). Phase 2 captures those pages, with a fast bulk-curl path for static marketing sites and a browser path for everything else. Phase 2.5 is the part that makes the rest worth doing: Claude reads the public surface and writes a `GAMEPLAN.md`, a numbered capture plan with a hypothesis per feature, before touching the signed-in app. Phase 3 executes that plan against your own signed-in browser through the chrome-devtools MCP: you drive the clicks, the skill records network traffic, response bodies, screenshots, and HTML, then reports which predicted endpoints hit and which missed. Phase 4 synthesizes everything into a `BRIEF.md` plus machine-readable JSON.

The output is deliberately token-tiered so a later session can read the brief without dragging raw HTML into context.

Scope: this is for "should I build this?" and "how would I clone this?" research. It does not replicate proprietary content, scrape for resale, evade bot management, or fuzz endpoints, and it will stop and hand control back to you if a captcha appears.

## What's inside

- `SKILL.md`: the four-phase workflow, the Chrome attach troubleshooting, the authed-capture loop, and the stealth rules.
- `scripts/`: 17 Python scripts doing the deterministic work. `new_study.py` scaffolds the study folder, `fetch_public.py` harvests robots and sitemap over stdlib urllib, `scrub_network.py` strips Authorization / Cookie / JWT / key material out of captured traffic, and `render_brief.py` renders the final brief.
- Fingerprinters: `fingerprint_providers.py` (hosts to vendors), `fingerprint_csp.py` (one Content-Security-Policy header usually names the entire third-party allowlist, including providers the browser never fetches directly), `fingerprint_tech.py` (framework, hosting, UI library, with marketing site and app reported separately), and `fingerprint_data_shapes.py` (vendors the app proxies server-side, detected from the shape of response bodies).
- `references/providers.json`: the provider catalog behind the host fingerprinter, spanning payments, auth, analytics, error tracking, support, affiliate tracking, CDNs, and LLM APIs.
- `references/gameplan-template.md`: the calibration shape for the gameplan, including the auth-cookie decode step and the mandatory sidebar enumeration walk.
- `templates/BRIEF.md.j2`: the brief template, ending in a publication checklist so you know what to review before sharing a study.
- `config/stealth.json`: three pacing profiles (fast, balanced, high) controlling delays, request ceilings, and scroll behavior.

## Install

This skill ships inside the [NulightJens/jensai-skills](https://github.com/NulightJens/jensai-skills) monorepo. Install everything at once:

```bash
npx skills@latest add NulightJens/jensai-skills
```

Or copy just this folder into your Claude Code skills directory:

```bash
cp -R saas-study ~/.claude/skills/saas-study
```

Claude Code auto-discovers skills by their `SKILL.md` front matter, so it works from a plugin's `skills/` directory too.

Two things to set up before the first run:

**Python packages.** Most scripts are stdlib-only. Three need `trafilatura`, `beautifulsoup4`, `lxml`, and `jinja2`:

```bash
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements.txt
```

Or `python3 -m pip install trafilatura beautifulsoup4 lxml jinja2` into whatever Python you already use. `scripts/install.sh [venv-path]` does the venv route and prints the interpreter path. Screenshot redaction is optional and additionally wants `pillow` + `pytesseract` plus a system `tesseract` binary.

**The chrome-devtools MCP**, enabled in your Claude Code session via the `/mcp` menu. It attaches to a Chrome instance running with a remote debugging port; `SKILL.md` covers launching one on a separate profile and the three attach failures worth recognizing on sight.

## Use

Ask Claude to "study saas [url]", "deep-dive this SaaS", or "what's this app built on", or run `/saas-study <url>`.

```
/saas-study example.com
/saas-study example.com --stealth=high
/saas-study example.com --no-authed
/saas-study example.com --library-root ~/research/saas
/saas-study example.com --redact "name=<your name>,email=<your email>"
```

Studies are written to `./saas-library/<domain>/<YYYY-MM-DD>/` in the current working directory. Override with `--library-root` or the `SAAS_STUDY_LIBRARY` environment variable. The folder is gitignored on creation, network logs are scrubbed of credentials, session cookies never reach disk, and the first authed run shows a consent prompt explaining exactly what gets captured. Pass `--no-authed` to stay entirely on the public surface.

Expect to be involved during Phase 3. The skill does not click through the app for you: it prints each gameplan step, waits while you perform the action in your own browser, then captures the delta. It also checks the app's credit or quota state first and asks how much of your trial budget to spend, because a careless walk through a gameplan can burn a trial in five minutes.

Between the gameplan and the brief, the two files worth reading are `GAMEPLAN-EXECUTED.md` (predicted versus observed, plus the endpoints nobody predicted) and `BRIEF.md`. Keep the dated study folder as pure observation; anything you build from it belongs in the sibling `-derived/` folder the skill creates for exactly that purpose.

## License

MIT, see [LICENSE](LICENSE).

Built by [Jens Heitmann](https://www.instagram.com/jens.heitmann), part of the JensAI skills collection.
