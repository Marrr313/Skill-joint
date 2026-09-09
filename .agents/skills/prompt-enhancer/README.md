# prompt-enhancer

A [Claude Code](https://claude.com/claude-code) skill that transforms raw, unstructured prompts into well-organized, XML-structured prompts that maximize AI response quality.

It applies a 10-component framework (Task Context, Tone Context, Background Data, Detailed Task & Rules, Examples, Conversation History, Immediate Task, Thinking Step-by-Step, Output Formatting, Prefilled Response) and selects only the components relevant to a given prompt. It ships ready-to-use templates for minimal, standard, and comprehensive enhancements, plus a worked before/after example.

## What's inside

- `SKILL.md` — the framework, enhancement process, output templates, and best practices. Pure methodology with no external dependencies.

## Install

Copy this folder into your Claude Code skills directory:

```bash
cp -R prompt-enhancer ~/.claude/skills/prompt-enhancer
```

Or include it in a plugin's `skills/` directory. Claude Code auto-discovers skills by their `SKILL.md` front matter.

## Use

Ask Claude to "enhance this prompt", "improve my prompt", "make this prompt better", "structure this prompt", or "turn this into an XML prompt". Claude analyzes the original, applies the relevant components, and returns the enhanced prompt with a summary of the improvements.

## Credit

Prompt structure based on Anthropic's prompt engineering guidance.

## License

MIT — see [LICENSE](LICENSE).
