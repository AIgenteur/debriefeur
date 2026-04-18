# AIgenteur Debrief — Project Document

> **"The first agent you run should not be your assistant. It should be a tool to prepare you to run agents the way you want."**

---

## 1. Executive Summary

**AIgenteur Debrief** is a free, open‑source expertise‑elicitation tool built by **AIgenteur** that extracts tacit operational knowledge from a human and converts it into machine‑consumable artefacts that can immediately provision any downstream agent framework — [OpenClaw](https://github.com/open-claw), [Hermes Agent](https://github.com/hermes-agent), Manus, NemoClaw, Claude Dispatch, and any agent that reads Markdown or JSON configuration.

Most agent products today compete on the **implementation layer** — ease of install, model selection, security, cloud-vs-local. The real bottleneck is **upstream**: the human must describe their work, judgment patterns, and operating rhythm clearly enough that an agent can run with it. Almost no product in the market addresses this. AIgenteur Debrief does.

**Strategic context:** This is not a SaaS product. It is a **self‑hosted, open‑source tool** that serves as the flagship project of the AIgenteur ecosystem — demonstrating deep agent expertise, providing genuine standalone value, and naturally funneling users toward [AIgenteur Academy](https://skool.com/aigenteur) (free community) and [AIgenteur Insider](https://skool.com/aigenteur-insider) (paid community) for ongoing guidance.

---

## 2. Problem Statement

### 2.1 The "Now What?" Gap

The most common message in OpenClaw community forums is:

> *"I installed it. Now what?"*

Installation is solved — it takes 10 seconds. But productive use requires:

| Requirement | Current State |
|---|---|
| Deep understanding of one's own workflows | Rarely articulated |
| Explicit decision frameworks | Locked in tacit expertise |
| Structured operating rhythms | Exists only in the user's head |
| Dependency maps (people, data, tools) | Never documented |
| Friction points & leverage opportunities | Felt but not catalogued |

### 2.2 The Tacit Knowledge Trap

Knowledge work has a structural property that makes it uniquely resistant to delegation:

- **The more senior and valuable you become, the more your work migrates from explicit processes to tacit judgment.**
- Expertise develops by compressing conscious steps into automatic patterns ("compiled from source code into machine code").
- The people with the **most to gain** from agent delegation carry the **highest ratio** of tacit‑to‑explicit knowledge — the cold‑start problem hits them hardest.

### 2.3 Real‑World Evidence

- **Brad Mills** spent 40 hours writing standards, accountability rules, definitions of done, and transcribing 200 hours of video into a knowledge base — and it still didn't work. He ended up micromanaging the agent harder than any human.
- A user asked an agent to write five cold‑email variants — the agent reported "done" and wrote nothing. His workaround: a second adversarial auditor agent.
- A team rollout failed because nobody had mapped workflows, decisions, or data needs in advance.
- Someone is selling a **$49 pack of pre‑written config files** — and it sells. That gap between "installed" and "useful" is large enough to build a business around.

### 2.4 Why Existing Products Don't Solve This

| Product | What It Solves | What It Doesn't |
|---|---|---|
| **OpenClaw** | Infinite configurability, local-first, free | Cold start is entirely on the user |
| **Manus (Meta)** | Easier setup, auto sub‑agents, security | Lacks deep initial context capture |
| **Perplexity Personal Computer** | Dedicated Mac Mini, 20 Frontier models, orchestrator | Same cold‑start wall |
| **NemoClaw (NVIDIA)** | Enterprise security guardrails | Punts operating instructions to enterprise |
| **Claude Dispatch** | Mobile‑first, easy messaging | Text messages fail without deep context |
| **Hosted wrappers** (StartClaw, MyClaw, SimpleClaw, etc.) | One‑click deploy, pre‑configured personas | Generic configs, not personal |

**Every product competes on installation. None compete on intent elicitation.**

---

## 3. Solution: AIgenteur Debrief

### 3.1 Core Concept

An AI agent modeled after **expertise elicitation researchers** (a real discipline). It asks the right questions, in the right order, with the right follow‑ups, to extract operational knowledge the user carries but cannot access on their own.

This is **not** the same as asking three questions on install ("Who am I? Who are you? What is my job?"). It is a deep, structured, ~45‑minute conversation.

### 3.2 The Five Elicitation Layers

```
┌─────────────────────────────────────────────┐
│  Layer 1: Operating Rhythms                 │
│  What are your days, weeks, months really    │
│  like? Not the calendar version — the real   │
│  one.                                        │
├─────────────────────────────────────────────┤
│  Layer 2: Recurring Decisions                │
│  What judgment calls do you make? Which are  │
│  easy? Hard? What inputs do you need?        │
├─────────────────────────────────────────────┤
│  Layer 3: Dependencies                       │
│  Who do you need things from, and when?      │
│  What are the upstream/downstream handoffs?  │
├─────────────────────────────────────────────┤
│  Layer 4: Friction Points                    │
│  Recurring annoyances that eat your time.    │
│  Where do things break or slow down?         │
├─────────────────────────────────────────────┤
│  Layer 5: Leverage & Optimization            │
│  Where do you see disproportionate returns?  │
│  What would you delegate first if you could? │
└─────────────────────────────────────────────┘
```

### 3.3 Outputs

The agent produces **two classes of output**:

#### A. Structured Knowledge Map (Primary Output)
A searchable, structured database of how the user works — their decisions, patterns, leverage points. This is the *more valuable* output. It is:
- Stored in a personal knowledge store (e.g., Open Brain)
- Accessible to any agent via MCP (Model Context Protocol)
- Durable, searchable, and accumulating over time

#### B. Agent Configuration Files (Secondary Output)
Auto‑generated Markdown files ready for immediate use in any agent framework:

| File | Purpose | Contents |
|---|---|---|
| `soul.md` | Agent's "job description" | Role, tone, boundaries, decision framework, escalation rules, quality bar |
| `identity.md` | Agent's persona | Name, personality constraints, audience‑aware tone rules |
| `user.md` | Human's profile | Preferences, schedule patterns, communication style, judgment patterns |
| `heartbeat.md` | Periodic checklist | Tasks the agent reviews every 30 minutes, cron rhythm |
| `memory.md` | Memory bootstrap | Initial knowledge seeds, trusted data sources, skepticism flags |

#### C. Framework‑Specific Exports
The same elicited knowledge, formatted for:
- **OpenClaw** — `.openclaw/` directory with standard files
- **Hermes Agent** — system prompt + tool definitions
- **Manus** — context injection format
- **NemoClaw** — enterprise config templates
- **Generic** — JSON/YAML for custom frameworks

### 3.4 Design Principles

1. **Interview, don't interrogate.** The agent should feel like a thoughtful colleague, not a form.
2. **Follow‑up is everything.** Surface‑level answers ("I handle marketing") must be decomposed into specific, triggerable, verifiable steps.
3. **The conversation IS the product.** The config files are a convenience. The real value is the structured self‑knowledge.
4. **Respect the user's time.** Target 45 minutes for a full elicitation. Allow resumable sessions.
5. **Grow over time.** Support re‑interviews as the user's role and context evolve.

### 3.5 Target Framework Profiles

AIgenteur Debrief generates configs for these downstream frameworks. Understanding their architecture determines how we format our output.

#### OpenClaw

| Aspect | Detail |
|---|---|
| **Language** | TypeScript + Swift |
| **Runtime** | Node.js (long‑lived gateway process, always‑on) |
| **Architecture** | 3 layers: **Channel** (messaging adapters — WhatsApp, Telegram, Slack, Discord, Signal, iMessage) → **Brain** (session serialization, context assembly, model inference) → **Body** (tools/skills, shell, browser, files) |
| **Agent Loop** | 7‑stage ReAct: Normalize → Route → Assemble Context → Infer → ReAct → Load Skills → Persist Memory |
| **Config format** | Structured **Markdown** files in a `.openclaw/` directory |
| **Config files** | `soul.md`, `identity.md`, `user.md`, `heartbeat.md`, `memory.md`, `SKILL.md` |
| **Persistence** | Local‑first — markdown/YAML files on disk |
| **LLM** | Model‑agnostic — GPT, Claude, Gemini, Ollama, LM Studio |
| **Proactive behavior** | Built‑in heartbeat + cron scheduler for autonomous tasks without user prompting |
| **MCP** | Supported |
| **License** | MIT |
| **GitHub stars** | 250,000+ |

**Our integration:** Drop‑in `.openclaw/` directory with `soul.md`, `identity.md`, `user.md`, `heartbeat.md`, `memory.md`. Files are rendered from Jinja2 templates. The heartbeat file maps directly to the user's operating rhythms from Layer 1. Decision frameworks from Layer 2 feed into `soul.md`.

#### Hermes Agent (Nous Research)

| Aspect | Detail |
|---|---|
| **Language** | **Python** |
| **Runtime** | Persistent background process (designed to run 24/7 on a VPS or Docker) |
| **Architecture** | Self‑improving learning loop — completes tasks, extracts successful patterns, stores as reusable markdown "skills" |
| **Memory** | 3‑layer: **Working** (current task) → **Episodic** (conversation history) → **Long‑term** (facts, preferences, skills via FTS5/SQLite) |
| **Config format** | System prompt (markdown) + tool definitions (JSON) + structured context (JSON) |
| **Tools** | 40+ built‑in — shell commands, SSH, browser automation (Playwright) |
| **Channels** | CLI, Telegram, Discord, Slack, WhatsApp, Signal |
| **LLM** | Model‑agnostic — OpenRouter, Nous Portal, Ollama, vLLM, llama.cpp (200+ models) |
| **MCP** | Supported |
| **Deployment** | Self‑hosted — Linux VPS ($5 Hetzner), Docker, serverless (Modal, Daytona) |
| **License** | MIT |

**Our integration:** Three files — `system_prompt.md` (combined soul + identity + user context), `tools.json` (tool definitions mapped from user workflows/dependencies), `context.json` (structured knowledge base). Since Hermes is Python, there's also an opportunity for deeper integration: directly injecting knowledge entries into Hermes's FTS5 long‑term memory store.

#### Key Differences That Affect Our Adapters

| Dimension | OpenClaw | Hermes |
|---|---|---|
| Config structure | Multiple separate markdown files | Single system prompt + JSON |
| Heartbeat/scheduler | Dedicated `heartbeat.md` file, cron‑native | No equivalent — schedule via tool instructions in system prompt |
| Memory bootstrap | `memory.md` with learning directives | Long‑term memory seeded via FTS5 entries |
| Skills | `SKILL.md` files with metadata | Self‑generated skill files from learning loop |
| Language match with our backend | Different (TypeScript vs. our Python) | Same (Python ↔ Python) — deeper integration possible |

---

## 4. Target Users

### 4.1 Primary — Tool Users
- Knowledge workers who have installed (or want to install) an agent and hit the "now what?" wall.
- Senior professionals whose expertise is deeply tacit — managers, engineers, product managers, salespeople, executives.
- Members of the **AIgenteur Academy** community looking for practical agent tooling.

### 4.2 Secondary — Community Funnel
- People who discover the GitHub repo, use the tool, and want deeper guidance → **AIgenteur Academy** (free Skool).
- Academy members who want advanced customization, industry‑specific question packs, and direct support → **AIgenteur Insider** (paid).
- Agent framework creators who want to reduce churn from "installed but never used" — potential partnership/embed opportunities.

---

## 5. Success Metrics

### 5.1 Product Metrics

| Metric | Target |
|---|---|
| Time from install to first productive agent use | < 60 minutes (interview + provisioning) |
| Config file quality score (rubric‑based) | ≥ 8/10 on specificity, actionability, coverage |
| User retention on downstream agents (30‑day) | ≥ 60% daily use |
| Elicitation depth (layers covered) | 5/5 within 45 minutes |
| Re‑interview rate | ≥ 1 per quarter (sign of ongoing value) |

### 5.2 Community & Marketing Metrics

| Metric | Target | Why It Matters |
|---|---|---|
| GitHub stars | 5,000 in first 6 months | Social proof, discoverability |
| GitHub forks | 500+ | Community engagement signal |
| README → Academy click‑through | ≥ 5% of repo visitors | Top of funnel |
| Academy → Insider conversion | ≥ 8% of free members | Revenue driver |
| "Made with AIgenteur Debrief" mentions | Tracked | Organic reach |
| Community PRs / issues | Active | Reduces maintenance burden |

---

## 6. Architecture Overview

```
                    ┌──────────────────┐
                    │   User (Human)   │
                    └────────┬─────────┘
                             │
                    conversation (voice/text)
                             │
                    ┌────────▼─────────┐
                    │  Interviewer     │
                    │  Agent           │
                    │                  │
                    │  - Elicitation   │
                    │    Engine        │
                    │  - Follow-up     │
                    │    Logic         │
                    │  - Layer         │
                    │    Tracker       │
                    └────────┬─────────┘
                             │
               ┌─────────────┼─────────────┐
               ▼             ▼             ▼
     ┌─────────────┐ ┌─────────────┐ ┌───────────────┐
     │ Knowledge   │ │ Config File │ │ Framework     │
     │ Store       │ │ Generator   │ │ Adapters      │
     │ (Open Brain)│ │             │ │               │
     │             │ │ soul.md     │ │ OpenClaw      │
     │ Structured  │ │ identity.md │ │ Hermes Agent  │
     │ JSON/DB     │ │ user.md     │ │ Manus         │
     │ via MCP     │ │ heartbeat.md│ │ NemoClaw      │
     │             │ │ memory.md   │ │ Custom/JSON   │
     └─────────────┘ └─────────────┘ └───────────────┘
```

---

## 7. Competitive Landscape & Positioning

AIgenteur Debrief is **not competing** with OpenClaw, Manus, Perplexity, or Claude Dispatch. It is **upstream** of all of them. It makes all of them work better.

```
 ┌──────────────────────────────────────────────────────────┐
 │              The Agent Value Chain                        │
 │                                                          │
 │  ┌──────────────┐    ┌───────────────┐    ┌───────────┐ │
 │  │ INTERVIEWER  │───▶│ CONFIGURATION │───▶│  AGENT    │ │
 │  │ (elicitation)│    │ (provisioning)│    │ (runtime) │ │
 │  └──────────────┘    └───────────────┘    └───────────┘ │
 │                                                          │
 │  ◄── THIS PROJECT ──►  ◄── THIS PROJECT ──►  OpenClaw  │
 │                                                 Hermes   │
 │                                                 Manus    │
 │                                                 etc.     │
 └──────────────────────────────────────────────────────────┘
```

---

## 8. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Users abandon the interview midway (45 min is long) | Resumable sessions; show progress; preview output live |
| Elicited knowledge is too shallow | Aggressive follow‑up questions; "not specific enough" detection |
| Config files become stale vs. evolving workflows | Re‑interview reminders; diff‑based updates |
| Privacy concerns (deep personal/work knowledge) | Local‑first processing; no cloud required; user owns all data |
| Framework format drift (OpenClaw changes its schema) | Adapter pattern; each framework is a pluggable exporter |
| Open‑source project goes unmaintained | Community contributions; focused scope (interview + generate — not a full agent) |
| Tool gets forked without attribution | MIT license is fine — forks still drive awareness; brand is in the quality |

---

## 9. Distribution & Community Strategy

### 9.1 Why Open Source

This tool is **not a software business.** A single user runs it once, maybe quarterly. The value is in what it proves: that AIgenteur understands agents at a level deeper than anyone selling $49 config packs.

Open source is the **highest‑trust marketing channel** that exists. Nobody thinks "they're trying to sell me" when they find a free GitHub tool. They think "these people know what they're doing."

### 9.2 The Funnel

```
┌─────────────────────────────────────────────────────────────────┐
│                    AIgenteur Community Funnel                    │
│                                                                 │
│  GitHub Repo (free, open source)                                │
│  "Stop staring at blank config files."                         │
│       │                                                         │
│       ▼                                                         │
│  User installs → runs interview → gets production configs       │
│  "Wow, this actually works. Who made this?"                    │
│       │                                                         │
│       ▼                                                         │
│  AIgenteur Academy (free Skool community)                      │
│  General discussion, basic support, "show your config" threads │
│       │                                                         │
│       ▼                                                         │
│  AIgenteur Insider (paid community)                            │
│  Advanced question packs, industry templates, direct support,  │
│  video walkthroughs, early access to new adapters              │
│       │                                                         │
│       ▼                                                         │
│  Courses, consulting, enterprise advisory (future)             │
└─────────────────────────────────────────────────────────────────┘
```

### 9.3 Touchpoints Within the Tool

Subtle, non‑pushy brand presence:

| Touchpoint | What | Why |
|---|---|---|
| **Generated file footer** | `# Generated by AIgenteur Debrief — github.com/aigenteur/debrief` | Every config file becomes a micro‑ad |
| **Post‑interview screen** | "Want to customize this further? Join AIgenteur Academy →" | Natural moment of high trust |
| **README** | Badges + links to Skool communities | Standard open‑source practice |
| **GitHub Discussions** | Light support; deep questions → "Join the community" | Funnels engaged users |
| **Example outputs** | Showcase real (anonymized) configs | Social proof of quality |

### 9.4 Insider‑Exclusive Content (Paid Community Value)

The open‑source tool is complete and useful on its own. The paid community adds:

| Exclusive Content | Why Users Pay |
|---|---|
| **Industry question packs** | Pre‑built Layer 1–5 questions for SaaS PMs, realtors, content creators, devs, etc. |
| **Advanced prompt engineering** | Custom system prompts for deeper elicitation |
| **Config walkthroughs** | Video breakdowns: "Here's how I tuned my soul.md for X use case" |
| **Priority adapter access** | New framework adapters (e.g., Claude Dispatch, new OpenClaw versions) released to Insiders first |
| **"Roast my config" sessions** | Community‑reviewed config files — real feedback from experienced users |
| **Direct support** | Help debugging agent behavior back to config quality |

### 9.5 Community‑Driven Development

Open‑source contributions reduce maintenance burden and increase reach:

| Contribution Type | Benefit |
|---|---|
| **New framework adapters** | Community builds adapters for frameworks we don't cover |
| **Industry question banks** | Domain experts contribute questions for their field |
| **Translations** | Interviews in Spanish, Portuguese, Japanese, etc. |
| **Bug reports & fixes** | Community QA at scale |
| **"Made with" showcase** | Users share their configs → social proof → more stars |

---

## 10. Future Vision

- **Voice‑first interviews** — speak your expertise, don't type it.
- **Screen observation** — watch the user work for a day and auto‑generate elicitation questions.
- **Continuous elicitation** — the interviewer notices when the downstream agent fails and asks targeted follow‑ups to fill knowledge gaps. This is the feature that makes single‑user usage **recurring** instead of one‑time.
- **Agent performance scoring** — correlate elicitation depth with agent task success rates.
- **Community config gallery** — anonymized, high‑quality configs shared across the AIgenteur community.
- **Framework partnerships** — OpenClaw / Hermes embed the interview flow into their onboarding.

---

*Document Version: 2.0 — April 2026*
*Built by AIgenteur — [Academy](https://skool.com/aigenteur) | [Insider](https://skool.com/aigenteur-insider)*
