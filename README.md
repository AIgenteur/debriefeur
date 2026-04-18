# Debriefeur

> Extract your operational expertise → Generate AI agent configurations

**Debriefeur** is an open-source expertise-elicitation tool that interviews you about your daily operations, decisions, and workflows — then generates ready-to-use configuration files for [OpenClaw](https://github.com/openclaw/openclaw), [Hermes Agent](https://github.com/NousResearch/hermes-agent), or any agent framework.

## Install

```bash
pip install debriefeur
```

That's it. No Docker, no database, no servers.

## Quick Start

```bash
# 1. Configure your LLM provider (one time)
debriefeur setup

# 2. Start your interview
debrief
```

## What It Does

1. **Interviews you** through 5 structured layers (~20 min)
2. **Scores specificity** — never accepts vague answers
3. **Generates config files** for your chosen framework

### The 5 Layers

| Layer | What We Explore |
|---|---|
| ⏰ Operating Rhythms | Daily/weekly routines, energy patterns |
| ⚖️ Recurring Decisions | Decision frameworks, quality bars |
| 🔗 Dependencies | Tools, information flows, team |
| ⚡ Friction Points | Time wasters, delegation barriers |
| 🚀 Leverage Opportunities | Automation candidates, high-impact areas |

## Supported Providers

Works with **any** LLM via [litellm](https://github.com/BerriAI/litellm):

- **OpenRouter** (recommended) — one key, 200+ models
- **OpenAI, Anthropic, Google** — direct API
- **DeepSeek, Qwen, Kimi, GLM** — direct or via OpenRouter
- **Ollama** — fully offline, no API key
- **vLLM, llama.cpp, LM Studio** — self-hosted

## Commands

```bash
debrief              # Start interactive interview
debriefeur setup        # Configure LLM provider
debriefeur sessions     # List past sessions
debriefeur export <id> --framework openclaw   # Export for OpenClaw
debriefeur export <id> --framework hermes     # Export for Hermes Agent
debriefeur export <id> --framework generic    # Export JSON + Markdown
debriefeur status       # Check LLM connectivity
```

## Output Formats

| Framework | Files Generated |
|---|---|
| **OpenClaw** | `.openclaw/soul.md`, `user.md`, `heartbeat.md` |
| **Hermes Agent** | `system_prompt.md`, `context.json` |
| **Generic** | `knowledge_export.json`, `agent_brief.md` |

## How It Works

```
pip install debriefeur
         ↓
    debriefeur setup          →  ~/.debriefeur/.env
         ↓
    debriefeur                 →  Interactive interview (terminal)
         ↓
    debriefeur export <id>    →  ./output/.openclaw/soul.md, etc.
```

All state stored in `~/.debrief/` — sessions as JSON files, config as `.env`.
No database. No servers. Like how OpenClaw uses `~/.openclaw/` and Hermes uses `~/.hermes/`.

## From Source

```bash
git clone https://github.com/aigenteur/debrief.git
cd debrief
pip install -e ".[dev]"
debriefeur setup
debrief
```

## Community

- 🎓 **AIgenteur Academy** — [skool.com/aigenteur](https://skool.com/aigenteur)
- 🔒 **AIgenteur Insider** — Premium community for advanced agent builders

## License

MIT
