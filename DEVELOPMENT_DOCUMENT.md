# AIgenteur Debrief — Development Document

> Technical specification for building AIgenteur Debrief: a structured expertise‑elicitation system that produces agent configuration files for OpenClaw, Hermes Agent, and other agent frameworks.

---

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Tech Stack](#2-tech-stack)
3. [Core Modules](#3-core-modules)
4. [Data Models](#4-data-models)
5. [Elicitation Engine](#5-elicitation-engine)
6. [Configuration File Generator](#6-configuration-file-generator)
7. [Framework Adapters](#7-framework-adapters)
8. [Knowledge Store Integration](#8-knowledge-store-integration)
9. [API Design](#9-api-design)
10. [Installation & CLI](#10-installation--cli)
11. [File & Directory Structure](#11-file--directory-structure)
12. [Implementation Phases](#12-implementation-phases)
13. [Testing Strategy](#13-testing-strategy)

---

## 1. System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AIgenteur Debrief System                             │
│                                                                              │
│  ┌──────────────────┐         ┌──────────────────────────────────────────┐  │
│  │  FRONTEND         │         │         BACKEND (Python FastAPI)         │  │
│  │  Next.js (React)  │  REST/  │                                          │  │
│  │                   │  WS     │  ┌────────────────┐  ┌──────────────┐   │  │
│  │  - Interview UI   │◀──────▶│  │  API Routes     │  │  WebSocket   │   │  │
│  │  - Dashboard      │         │  │  (FastAPI)      │  │  Manager     │   │  │
│  │  - Config viewer  │         │  └───────┬────────┘  └──────┬───────┘   │  │
│  │  - Export panel   │         │          │                   │           │  │
│  └──────────────────┘         │  ┌───────▼───────────────────▼───────┐   │  │
│                                │  │       Elicitation Engine          │   │  │
│                                │  │  - Conversation Controller       │   │  │
│                                │  │  - Follow-up Engine              │   │  │
│                                │  │  - Session Manager               │   │  │
│                                │  │  - 5-Layer State Machine         │   │  │
│                                │  └───────┬──────────────────────────┘   │  │
│                                │          │                               │  │
│                                │  ┌───────▼──────────────────────────┐   │  │
│                                │  │       Knowledge Synthesizer       │   │  │
│                                │  └───────┬──────────────────────────┘   │  │
│                                │          │                               │  │
│                                └──────────┼───────────────────────────────┘  │
│                                           │                                  │
│  ┌────────────────┐            ┌──────────┼──────────────┐                  │
│  │  Redis          │            │          │              │                  │
│  │  - Celery broker│            ▼          ▼              ▼                  │
│  │  - Session cache│  ┌─────────────┐ ┌──────────┐ ┌──────────────┐        │
│  │  - Rate limiting│  │ Knowledge   │ │ Config   │ │ Framework    │        │
│  └────────────────┘  │ Store       │ │ Generator│ │ Adapters     │        │
│                       │             │ │          │ │              │        │
│  ┌────────────────┐  │ - PostgreSQL│ │ soul.md  │ │ - OpenClaw   │        │
│  │  Celery Workers │  │ - pgvector  │ │ identity │ │ - Hermes     │        │
│  │  - Synthesis    │  │ - MCP API   │ │ user.md  │ │ - Manus      │        │
│  │  - Config gen   │  │             │ │ heartbeat│ │ - NemoClaw   │        │
│  │  - Embeddings   │  │             │ │ memory   │ │ - Generic    │        │
│  └────────────────┘  └─────────────┘ └──────────┘ └──────────────┘        │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │              OpenRouter — Multi-Model LLM Layer                      │  │
│  │                                                                      │  │
│  │   ┌────────────┐   ┌────────────┐   ┌──────────────────────┐        │  │
│  │   │ Tier 1:    │   │ Tier 2:    │   │ Tier 3:              │        │  │
│  │   │ FAST       │   │ DEEP       │   │ SYNTHESIS            │        │  │
│  │   │            │   │            │   │                      │        │  │
│  │   │ Qwen 3.5   │   │ KIMI K2.5  │   │ GLM 5                │        │  │
│  │   │ (~300B)    │   │            │   │                      │        │  │
│  │   │            │   │            │   │                      │        │  │
│  │   │ Follow-up  │   │ Interview  │   │ Knowledge synthesis  │        │  │
│  │   │ scoring,   │   │ questions, │   │ Config generation,   │        │  │
│  │   │ validation │   │ probing,   │   │ complex reasoning,   │        │  │
│  │   │            │   │ analysis   │   │ structural mapping   │        │  │
│  │   └────────────┘   └────────────┘   └──────────────────────┘        │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Tech Stack

### Frontend

| Layer | Technology | Rationale |
|---|---|---|
| **Framework** | Next.js 15 (App Router) | SSR, streaming, React Server Components |
| **Language** | TypeScript | Type safety for API contracts |
| **Styling** | Vanilla CSS (or Tailwind if preferred) | Full design control |
| **State** | Zustand or React Context | Lightweight, interview session state |
| **Real-time** | WebSocket (native) | Streaming interview responses |
| **Testing** | Playwright + Vitest | E2E and component tests |

### Backend

| Layer | Technology | Rationale |
|---|---|---|
| **Framework** | FastAPI (Python 3.12+) | Async-native, auto OpenAPI docs, WebSocket support |
| **Task Queue** | Celery 5.x | Heavy async jobs: synthesis, config gen, embedding |
| **Broker / Cache** | Redis 7+ | Celery broker, session cache, rate limiting, pub/sub for WS |
| **Database** | PostgreSQL 16 + pgvector | Structured data + vector similarity search in one DB |
| **ORM** | SQLAlchemy 2.0 + Alembic | Async ORM, migrations |
| **Config Templating** | Jinja2 | Markdown template rendering (Python native) |
| **MCP Server** | `mcp` Python SDK | Expose knowledge store to any MCP client |
| **Testing** | pytest + httpx + pytest-celery | Unit, integration, async tests |

### AI / LLM Layer

| Layer | Technology | Rationale |
|---|---|---|
| **Provider** | **Any OpenAI-compatible API** | Provider-agnostic; user chooses their provider during setup |
| **SDK** | `litellm` (unified multi-provider SDK) | Single interface for 100+ providers — OpenRouter, OpenAI, Anthropic, Ollama, etc. |
| **Embeddings** | Provider-specific or local `sentence-transformers` | For vector search in pgvector |

### Supported LLM Providers

AIgenteur Debrief is **provider-agnostic**. It works with any provider that exposes an OpenAI-compatible `/v1/chat/completions` endpoint.

The full list below is the **union of providers supported by OpenClaw and Hermes Agent**, verified against their actual source code:
- OpenClaw: [`.env.example`](https://github.com/openclaw/openclaw/blob/main/.env.example) (lines 42–62)
- Hermes: [`agent/model_metadata.py`](https://github.com/NousResearch/hermes-agent/blob/main/agent/model_metadata.py) `_PROVIDER_PREFIXES` + `_URL_TO_PROVIDER`

| Provider | Type | Models | Setup | Source |
|---|---|---|---|---|
| **OpenRouter** | Cloud aggregator | 200+ models (GPT, Claude, Gemini, Qwen, KIMI, GLM, etc.) | API key | Both |
| **OpenAI** | Cloud | GPT-4o, GPT-4.5, GPT-5, o1, o3 | API key | Both |
| **Anthropic** | Cloud | Claude 3.5 Sonnet, Claude Opus 4.6 | API key | Both |
| **Google (Gemini)** | Cloud | Gemini 3.1 Pro, Gemini 2.5 Flash, Gemma 4 | API key | Both |
| **Alibaba Cloud (DashScope)** | Cloud | Qwen 3.5, Qwen 3.6, Qwen 3 Coder | API key | Hermes |
| **Moonshot AI (Kimi)** | Cloud | KIMI K2.5, KIMI K2 Thinking | API key | Hermes |
| **ZhipuAI (z.ai)** | Cloud | GLM 5, GLM 5 Turbo | API key | Both |
| **DeepSeek** | Cloud | DeepSeek V3.2, DeepSeek R1 | API key | Hermes |
| **xAI (Grok)** | Cloud | Grok 4, Grok 3, Grok Code Fast | API key | Hermes |
| **MiniMax** | Cloud | M2.5, M2.7 series | API key | Both |
| **Xiaomi (MiMo)** | Cloud | MiMo V2 Flash, MiMo V2 Pro | API key | Hermes |
| **Arcee AI** | Cloud | Trinity series | API key | Hermes |
| **Amazon Bedrock** | Cloud | Claude, Llama, Mistral via AWS | AWS credentials | Hermes |
| **Mistral AI** | Cloud | Mistral Large, Codestral | API key | Hermes |
| **Nous Portal** | Cloud | Hermes fine-tuned models | API key | Hermes |
| **GitHub Copilot** | Cloud | Via GitHub Models | GitHub auth | Hermes |
| **Fireworks AI** | Cloud | Hosted open models at high speed | API key | Hermes |
| **OpenCode** | Cloud | Zen, Go variants | API key | Hermes |
| **Ollama** | Local | Llama 3.3, Qwen 3.5, Mistral, any GGUF | No key needed | Both |
| **vLLM** | Local/self-hosted | Any HuggingFace model at high throughput | No key needed | Hermes |
| **llama.cpp / LM Studio / LocalAI** | Local | Any GGUF/GGML model | No key needed | Hermes |
| **LiteLLM Proxy** | Self-hosted proxy | Any of the above behind a unified endpoint | Self-hosted | — |

### Multi-Model Tiering Strategy

Different tasks require different levels of "thinking." The tier system routes to the optimal model per task:

| Tier | Role | Use Case | Default Model |
|---|---|---|---|
| **Tier 1: FAST** | Quick classification | Specificity scoring, vague-term detection, follow-up classification | `qwen/qwen3.5-397b-a17b` (via OpenRouter) |
| **Tier 2: DEEP** | Conversation | Interview dialogue, adaptive probing, nuanced follow-ups | `moonshotai/kimi-k2.5` (via OpenRouter) |
| **Tier 3: SYNTHESIS** | Heavy reasoning | Knowledge synthesis, config generation, cross-layer analysis | `z-ai/glm-5` (via OpenRouter) |

**Users can override any tier with any provider/model.** Examples:
- All 3 tiers → local Ollama with `qwen3.5:72b` (fully offline, zero API cost)
- Tier 1 → Ollama (free), Tier 2 → Anthropic Claude, Tier 3 → OpenAI GPT-4o
- All 3 tiers → OpenRouter (single API key, easiest setup)

```python
# Provider abstraction using litellm
from litellm import completion

# Provider configuration — user sets during `debrief setup`
PROVIDER_CONFIG = {
    "fast": {
        "model": "openrouter/qwen/qwen3.5-397b-a17b",  # Default
        "max_tokens": 2048,
        "temperature": 0.3,
        "use_for": [
            "specificity_scoring",
            "vague_term_detection",
            "response_classification",
            "quick_validation",
        ],
    },
    "deep": {
        "model": "openrouter/moonshotai/kimi-k2.5",     # Default
        "max_tokens": 4096,
        "temperature": 0.7,
        "use_for": [
            "interview_conversation",
            "adaptive_probing",
            "follow_up_generation",
            "layer_transitions",
        ],
    },
    "synthesis": {
        "model": "openrouter/z-ai/glm-5",               # Default
        "max_tokens": 8192,
        "temperature": 0.4,
        "use_for": [
            "knowledge_synthesis",
            "config_generation",
            "cross_layer_analysis",
            "structural_reasoning",
        ],
    },
}

# Examples of user overrides:
# "model": "ollama/qwen3.5:72b"           → local Ollama
# "model": "anthropic/claude-3.5-sonnet"   → direct Anthropic API
# "model": "openai/gpt-4o"                → direct OpenAI API
# "model": "deepseek/deepseek-r1"          → DeepSeek API
# "model": "bedrock/claude-3.5-sonnet"     → AWS Bedrock
# "model": "dashscope/qwen-max"            → Alibaba DashScope

async def call_llm(tier: str, messages: list, **kwargs) -> str:
    """Unified LLM call — works with any provider via litellm."""
    config = PROVIDER_CONFIG[tier]
    response = await completion(
        model=config["model"],
        messages=messages,
        max_tokens=config["max_tokens"],
        temperature=config["temperature"],
        **kwargs,
    )
    return response.choices[0].message.content
```

### Infrastructure

| Component | Technology | Rationale |
|---|---|---|
| **Containerization** | Docker + Docker Compose | Reproducible dev/prod environments |
| **Reverse Proxy** | Nginx (optional) | SSL termination, static file serving |
| **Process Manager** | Supervisor or systemd | Keep Celery workers alive |

---

## 3. Core Modules

### 3.1 Module Map

```
backend/
├── app/
│   ├── main.py                        # FastAPI app entry point
│   ├── config.py                      # Settings (pydantic-settings)
│   ├── dependencies.py                # Dependency injection
│   │
│   ├── core/
│   │   ├── elicitation_engine.py       # 5-layer interview state machine
│   │   ├── follow_up_engine.py        # Specificity analysis & probing
│   │   ├── conversation_controller.py # LLM conversation management
│   │   ├── session_manager.py         # Redis-backed session state
│   │   ├── knowledge_synthesizer.py   # Transcript → structured knowledge
│   │   └── question_banks/
│   │       ├── layer_1_rhythms.py
│   │       ├── layer_2_decisions.py
│   │       ├── layer_3_dependencies.py
│   │       ├── layer_4_friction.py
│   │       └── layer_5_leverage.py
│   │
│   ├── llm/
│   │   ├── router.py                  # Model tier router (fast/deep/synthesis)
│   │   ├── openrouter_client.py       # OpenRouter API client
│   │   └── prompts.py                 # System prompts & templates
│   │
│   ├── generators/
│   │   ├── config_generator.py        # Orchestrator
│   │   ├── template_renderer.py       # Jinja2 rendering
│   │   ├── templates/
│   │   │   ├── soul.md.j2
│   │   │   ├── identity.md.j2
│   │   │   ├── user.md.j2
│   │   │   ├── heartbeat.md.j2
│   │   │   └── memory.md.j2
│   │   └── adapters/
│   │       ├── base.py                # Abstract adapter interface
│   │       ├── openclaw_adapter.py
│   │       ├── hermes_adapter.py
│   │       ├── manus_adapter.py
│   │       ├── nemoclaw_adapter.py
│   │       └── generic_adapter.py
│   │
│   ├── knowledge/
│   │   ├── store.py                   # PostgreSQL + pgvector CRUD
│   │   ├── embeddings.py              # Vector embedding generation
│   │   ├── search.py                  # Semantic search
│   │   └── mcp_server.py             # MCP endpoint for agent access
│   │
│   ├── api/
│   │   ├── routes/
│   │   │   ├── sessions.py            # Interview session endpoints
│   │   │   ├── knowledge.py           # Knowledge base endpoints
│   │   │   ├── generate.py            # Config generation endpoints
│   │   │   └── health.py              # Health check
│   │   └── websocket.py              # WebSocket for streaming interview
│   │
│   ├── models/
│   │   ├── database.py                # SQLAlchemy models
│   │   └── schemas.py                 # Pydantic request/response schemas
│   │
│   ├── tasks/
│   │   ├── celery_app.py              # Celery configuration
│   │   ├── synthesis_tasks.py         # Knowledge synthesis (async)
│   │   ├── generation_tasks.py        # Config file generation (async)
│   │   └── embedding_tasks.py         # Embedding computation (async)
│   │
│   └── utils/
│       ├── markdown.py
│       ├── validation.py
│       └── logger.py
│
frontend/
├── src/
│   ├── app/                           # Next.js App Router
│   │   ├── layout.tsx
│   │   ├── page.tsx                   # Landing / dashboard
│   │   ├── interview/
│   │   │   └── [sessionId]/page.tsx   # Interview conversation UI
│   │   ├── knowledge/
│   │   │   └── page.tsx               # Knowledge base browser
│   │   └── export/
│   │       └── page.tsx               # Config generation & download
│   ├── components/
│   │   ├── InterviewChat.tsx          # Main chat interface
│   │   ├── LayerProgress.tsx          # 5-layer progress indicator
│   │   ├── KnowledgeCard.tsx          # Knowledge entry display
│   │   ├── ConfigPreview.tsx          # Generated config preview
│   │   └── FrameworkSelector.tsx      # OpenClaw/Hermes/etc picker
│   ├── hooks/
│   │   ├── useWebSocket.ts           # WS connection to backend
│   │   └── useSession.ts             # Session state management
│   └── lib/
│       └── api.ts                     # Backend API client
```

### 3.2 Module Responsibilities

| Module | Responsibility | LLM Tier |
|---|---|---|
| **Elicitation Engine** | Implements the 5‑layer interview protocol. Manages which layer is active, what questions to ask, when to move to the next layer. | Tier 2 (DEEP) |
| **Follow‑up Engine** | Analyzes each user response for specificity. Detects vague answers and generates targeted follow‑ups. | Tier 1 (FAST) for scoring, Tier 2 (DEEP) for follow-up generation |
| **Conversation Controller** | Manages the LLM conversation. Handles context window limits, summarization of earlier turns, system prompt construction. | Tier 2 (DEEP) |
| **Session Manager** | Persists interview state to Redis (hot) and PostgreSQL (cold). Supports pause/resume. Tracks progress across layers. | — |
| **Knowledge Synthesizer** | Post‑processes the raw interview transcript into structured JSON knowledge entries. Runs as **Celery task**. | Tier 3 (SYNTHESIS) |
| **Config Generator** | Takes synthesized knowledge and renders framework‑specific configuration files from Jinja2 templates. Runs as **Celery task**. | Tier 3 (SYNTHESIS) |
| **Knowledge Store** | PostgreSQL + pgvector for durable, searchable knowledge. Exposed via MCP. | — |

### 3.3 Why Celery + Redis?

| Job | Why Async? |
|---|---|
| **Knowledge Synthesis** | Processes full interview transcript (potentially 100+ turns). Multiple LLM calls. Takes 30–120 seconds. |
| **Config Generation** | Renders templates + validates output + writes files. Multiple LLM calls for smart mapping. |
| **Embedding Computation** | Generates vector embeddings for all knowledge entries. Batch operation. |
| **Re-interviews / Diffs** | Compares new interview data with existing knowledge. Computationally heavy. |

Redis also serves as:
- **Session cache** — Active interview state for sub-second reads during conversation
- **Rate limiter** — Per-user OpenRouter API rate limiting
- **Pub/Sub** — Push Celery task results to frontend via WebSocket

---

## 4. Data Models (Pydantic + SQLAlchemy)

### 4.1 Interview Session

```python
from enum import StrEnum
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class ElicitationLayer(StrEnum):
    OPERATING_RHYTHMS = "operating_rhythms"
    RECURRING_DECISIONS = "recurring_decisions"
    DEPENDENCIES = "dependencies"
    FRICTION_POINTS = "friction_points"
    LEVERAGE_OPPORTUNITIES = "leverage_opportunities"


class LayerStatus(StrEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class SessionStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"


class LayerProgress(BaseModel):
    status: LayerStatus = LayerStatus.NOT_STARTED
    questions_asked: int = 0
    follow_ups_triggered: int = 0
    depth_score: float = 0.0          # 0-10, how specific the answers are


class ConversationTurn(BaseModel):
    role: str                          # "system" | "assistant" | "user"
    content: str
    timestamp: datetime
    layer: ElicitationLayer
    is_follow_up: bool = False
    model_used: str | None = None      # Which LLM tier handled this turn
    metadata: dict | None = None


class InterviewSession(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    user_id: str
    status: SessionStatus = SessionStatus.IN_PROGRESS
    started_at: datetime = Field(default_factory=datetime.utcnow)
    last_active_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    current_layer: ElicitationLayer = ElicitationLayer.OPERATING_RHYTHMS
    layer_progress: dict[ElicitationLayer, LayerProgress] = {}
    transcript: list[ConversationTurn] = []
```

### 4.2 Synthesized User Knowledge

```python
from typing import Literal


# --- Layer 1: Operating Rhythms ---

class TimeBlock(BaseModel):
    start_time: str                    # "09:00"
    end_time: str                      # "10:30"
    activity: str
    day_of_week: list[str]
    flexibility: Literal["rigid", "flexible", "optional"]
    notes: str = ""


class WeeklyPattern(BaseModel):
    day_of_week: str
    theme: str
    key_activities: list[str]


class EnergyPattern(BaseModel):
    peak_hours: str
    low_hours: str
    deep_work_blocks: str


class OperatingRhythms(BaseModel):
    daily_routine: list[TimeBlock]
    weekly_patterns: list[WeeklyPattern]
    monthly_recurrences: list[dict]    # Flexible schema
    energy_map: EnergyPattern
    communication_windows: list[dict]


# --- Layer 2: Recurring Decisions ---

class Decision(BaseModel):
    description: str
    frequency: Literal["daily", "weekly", "monthly", "quarterly", "ad_hoc"]
    difficulty: Literal["easy", "moderate", "hard", "judgment_call"]
    inputs: list[str]
    output_format: str
    stakeholders: list[str]
    example_good: str
    example_bad: str


class DecisionFramework(BaseModel):
    name: str
    trigger: str
    criteria: str
    default_action: str
    escalation_trigger: str


class QualityBar(BaseModel):
    task_type: str
    standard: str


class EscalationRule(BaseModel):
    condition: str
    action: str


class RecurringDecisions(BaseModel):
    decisions: list[Decision]
    decision_frameworks: list[DecisionFramework]
    quality_bars: list[QualityBar]
    escalation_rules: list[EscalationRule]


# --- Layer 3: Dependencies ---

class PersonDependency(BaseModel):
    name: str
    role: str
    what_you_need: str
    handoff_method: str
    typical_latency: str


class Dependencies(BaseModel):
    people: list[PersonDependency]
    tools: list[dict]
    data_sources: list[dict]
    upstream_handoffs: list[dict]
    downstream_handoffs: list[dict]


# --- Layer 4: Friction ---

class FrictionItem(BaseModel):
    description: str
    frequency: str
    time_impact: str                   # "~2 hours/week"
    current_workaround: str | None = None
    root_cause: str | None = None
    delegatable: bool


class FrictionPoints(BaseModel):
    time_wasters: list[FrictionItem]
    recurring_blockers: list[FrictionItem]
    process_gaps: list[FrictionItem]
    communication_friction: list[FrictionItem]


# --- Layer 5: Leverage ---

class LeverageItem(BaseModel):
    description: str
    estimated_impact: str
    current_time_spent: str
    agent_suitability: Literal["high", "medium", "low"]
    prerequisites: list[str]


class LeverageOpportunities(BaseModel):
    high_roi_tasks: list[LeverageItem]
    automation_candidates: list[LeverageItem]
    delegation_priorities: list[LeverageItem]
    skill_gaps: list[str]


# --- Meta ---

class RoleDescription(BaseModel):
    title: str
    summary: str
    core_responsibilities: list[str]
    success_metrics: list[str]
    reporting_structure: str


class TonePreferences(BaseModel):
    formality_level: Literal["casual", "professional", "formal"]
    communication_style: str
    audience_adaptation: dict[str, str]  # audience → tone


# --- Top-Level Knowledge Model ---

class UserKnowledge(BaseModel):
    user_id: str
    generated_at: datetime
    version: int = 1

    operating_rhythms: OperatingRhythms
    recurring_decisions: RecurringDecisions
    dependencies: Dependencies
    friction_points: FrictionPoints
    leverage_opportunities: LeverageOpportunities

    role: RoleDescription
    industry: str
    team_context: dict
    tone_preferences: TonePreferences
```

### 4.3 Agent Configuration Output

```python
class SoulConfig(BaseModel):
    role: str
    mission: str
    boundaries: list[str]
    tone_guidelines: str
    decision_framework: str
    escalation_policy: str
    quality_standards: str
    trusted_sources: list[str]
    skeptical_of: list[str]
    autonomy_level: Literal["low", "medium", "high"]


class IdentityConfig(BaseModel):
    name: str
    personality: str
    constraints: list[str]
    audience_tones: dict[str, str]


class UserConfig(BaseModel):
    name: str
    role: str
    preferences: list[str]
    schedule_patterns: str
    communication_style: str
    decision_patterns: str
    known_frictions: list[str]
    leverage_areas: list[str]


class HeartbeatTask(BaseModel):
    description: str
    trigger: str
    action: str
    priority: Literal["critical", "high", "medium", "low"]


class HeartbeatConfig(BaseModel):
    check_interval_minutes: int = 30
    tasks: list[HeartbeatTask]
    cron_expression: str


class MemoryConfig(BaseModel):
    initial_seeds: list[str]
    learning_directives: list[str]
    retention_policy: str


class AgentConfig(BaseModel):
    soul: SoulConfig
    identity: IdentityConfig
    user: UserConfig
    heartbeat: HeartbeatConfig
    memory: MemoryConfig
```

### 4.4 SQLAlchemy Database Models

```python
from sqlalchemy import Column, String, Text, Float, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import DeclarativeBase
import uuid


class Base(DeclarativeBase):
    pass


class SessionModel(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False)
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    current_layer = Column(String, nullable=False)
    layer_progress = Column(JSONB, default={})
    transcript = Column(JSONB, default=[])  # Full conversation
    metadata_ = Column("metadata", JSONB, default={})


class KnowledgeEntryModel(Base):
    __tablename__ = "knowledge_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    subcategory = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    structured_data = Column(JSONB, nullable=True)
    source_session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"))
    confidence = Column(Float, default=1.0)
    embedding = Column(Vector(1536), nullable=True)   # pgvector
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    version = Column(Integer, default=1)
```

---

## 5. Elicitation Engine

### 5.1 Interview Protocol

The engine implements a **state machine** driving the interview through five layers.

```
┌──────────────────┐
│  LAYER 1:        │
│  Operating       │──────────▶ depth score ≥ 7?
│  Rhythms         │                │
└──────────────────┘           yes ─┤─ no → follow-up
                                    ▼
                           ┌──────────────────┐
                           │  LAYER 2:        │
                           │  Recurring       │──────────▶ depth score ≥ 7?
                           │  Decisions       │                │
                           └──────────────────┘           yes ─┤─ no → follow-up
                                                               ▼
                                                      ┌──────────────────┐
                                                      │  LAYER 3:        │
                                                      │  Dependencies    │──▶ ...
                                                      └──────────────────┘
                                                               ▼
                                                      ┌──────────────────┐
                                                      │  LAYER 4:        │
                                                      │  Friction Points │──▶ ...
                                                      └──────────────────┘
                                                               ▼
                                                      ┌──────────────────┐
                                                      │  LAYER 5:        │
                                                      │  Leverage        │──▶ COMPLETE
                                                      └──────────────────┘
```

### 5.2 Question Design Principles

Each layer uses three types of questions:

1. **Opener** — Broad, inviting question to start the layer.
   > "Walk me through a typical Monday. Not the idealized version — the real one."

2. **Probe** — Targeted follow‑ups based on the user's response.
   > "You mentioned checking dashboards first thing. Which specific dashboards? What numbers are you looking at? What would cause you to take action?"

3. **Validator** — Tests specificity. Can the answer be turned into a checklist?
   > "If I had to do this task for you tomorrow, would I know exactly when to start, what to check, and when it's done?"

### 5.3 Follow‑Up Engine

The follow‑up engine uses the LLM to classify each response on a **specificity scale**:

```python
class SpecificityAnalysis(BaseModel):
    score: float                            # 1-10
    is_actionable: bool                     # Could an agent execute this?
    is_triggerable: bool                    # Has a clear trigger condition?
    is_verifiable: bool                     # Has a clear "done" condition?
    vague_terms: list[str]                  # Words that need unpacking
    suggested_follow_ups: list[str]         # Auto-generated follow-ups
```

**Trigger rules for follow‑up:**
- Score < 5 → Mandatory follow‑up ("Can you be more specific about...?")
- Score 5–7 → Optional follow‑up ("Just to make sure I've got this right...?")
- Score > 7 → Accept and move on
- Detected vague terms → Targeted probe ("You said 'handle marketing' — what does that look like hour by hour?")

**Model routing:** Specificity scoring uses **Tier 1 (Qwen 3.5)** for speed. Follow-up generation uses **Tier 2 (KIMI K2.5)** for nuance.

### 5.4 System Prompt Architecture

```python
SYSTEM_PROMPT = """
You are an expertise elicitation interviewer. Your job is to extract
operational knowledge from the user — the kind of tacit, compressed
expertise that makes them effective at their job but that they struggle
to articulate.

## Your Approach
- You are warm, curious, and thorough — like a great journalist.
- You ask ONE question at a time. Never ask multiple questions.
- You listen carefully and pick up on specifics to probe deeper.
- You never accept vague answers. "I handle marketing" → "Walk me
  through exactly what you check, in what order, on a Monday morning."
- You use the user's own language back to them.
- You occasionally summarize what you've learned to confirm accuracy.

## Current Layer: {current_layer}
## Layer Description: {layer_description}
## Questions Asked So Far: {question_count}
## Depth Score: {depth_score}/10
## Key Topics Still Uncovered: {uncovered_topics}

## Previous Context Summary:
{context_summary}

## Instructions for This Turn:
{turn_instructions}
"""

# This prompt is sent to Tier 2 (KIMI K2.5) — the "deep" conversational model
```

### 5.5 Layer‑Specific Question Banks

#### Layer 1: Operating Rhythms

```typescript
const LAYER_1_QUESTIONS = {
  openers: [
    "Let's start with your daily rhythm. Walk me through a typical workday — from when you first check your phone or computer to when you close things down for the night.",
    "How does your week flow? Are all days similar, or do certain days have a different flavor?"
  ],
  probes: {
    morning_routine: "You mentioned {activity}. What specifically are you checking or doing? What would make you stop and change your plan?",
    meetings: "How many meetings in a typical day? Which ones do you actually need to be in, and which ones could you skip?",
    deep_work: "When do you do your best thinking? What conditions need to be true for that to happen?",
    end_of_day: "How do you decide when you're 'done' for the day? Is there a specific signal or does it just fade out?",
    monthly_rhythms: "Are there things that happen monthly or quarterly that disrupt or define your rhythm?",
    energy: "When in the day are you sharpest? When do you hit a wall? How do you currently handle the low-energy parts?"
  },
  validators: [
    "If I had to live your Monday for you, would I know exactly what to do from 8 AM to 6 PM based on what you've told me?",
    "Let me play it back: {summary}. What did I miss or get wrong?"
  ]
};
```

#### Layer 2: Recurring Decisions

```typescript
const LAYER_2_QUESTIONS = {
  openers: [
    "Now let's talk about the decisions you make regularly. What are the judgment calls that come up every day or every week — the ones you've gotten so good at that you barely think about them anymore?"
  ],
  probes: {
    inputs: "For that decision, what information do you actually look at? Where does it come from?",
    criteria: "What makes you go one way versus another? Is there a threshold, a gut check, or a formula?",
    easy_vs_hard: "Which decisions feel automatic to you now? Which ones still make you pause?",
    consequences: "What happens downstream when you make that call? Who does it affect?",
    quality: "How do you know when you've done a 'good enough' job on {task}? What's the bar?"
  ],
  validators: [
    "Could a sharp colleague handle this decision correctly 80% of the time with just the criteria you've described?",
    "What would a common mistake look like if someone made this decision without your experience?"
  ]
};
```

#### Layer 3: Dependencies

```typescript
const LAYER_3_QUESTIONS = {
  openers: [
    "Let's map out who and what you depend on. Who do you need things from to do your job? And who depends on you?"
  ],
  probes: {
    people: "When you need {thing} from {person}, how does that handoff typically work? How long does it take?",
    tools: "Which tools are absolutely essential? Which ones are annoying but necessary?",
    data: "Where does the data you need actually live? How current is it? How much do you trust it?",
    bottlenecks: "Where does the chain break most often? What's the usual cause?",
    communication: "How do you prefer to receive information? Push (notifications) or pull (you go check)?"
  ],
  validators: [
    "If I mapped all the inputs and outputs for a typical week, would this cover it?",
    "Who would notice first if you stopped doing your job for a day?"
  ]
};
```

#### Layer 4: Friction Points

```typescript
const LAYER_4_QUESTIONS = {
  openers: [
    "Now the fun part — what annoys you? What are the recurring time-wasters, the things that make you think 'there has to be a better way'?"
  ],
  probes: {
    frequency: "How often does {friction} happen? Daily? Weekly?",
    time_impact: "Roughly how much time does it cost you each week?",
    workaround: "Do you currently have a workaround? What does it look like?",
    root_cause: "Why does this keep happening? Is it a people problem, a tool problem, or a process problem?",
    delegation: "If you could hand this off to someone (or something) reliable, would you? What would they need to know?"
  },
  validators: [
    "If I could eliminate three of these tomorrow, which three would give you the most time back?",
    "Are there frictions you've just accepted that you've stopped noticing?"
  ]
};
```

#### Layer 5: Leverage & Optimization

```typescript
const LAYER_5_QUESTIONS = {
  openers: [
    "Last layer. Given everything you've told me — your rhythms, decisions, dependencies, and frictions — where do you see the biggest opportunity for leverage? What would you delegate first if you had a reliable, context-aware agent?"
  ],
  probes: {
    high_roi: "Which of your recurring tasks would have the highest ROI if automated well?",
    agent_fit: "For {task}, what would the agent need to know to handle it without checking with you?",
    guardrails: "What should the agent absolutely NOT do? Where are the landmines?",
    success_criteria: "If the agent did {task} perfectly, how would you verify it? What would 'done' look like?",
    evolution: "How would you want the agent to improve over time? What should it be learning from you?"
  },
  validators: [
    "Based on everything, here are the top 5 things I think an agent could handle for you. Does this list feel right?",
    "If I set up an agent tonight with everything you've told me, what's the first task you'd want it to attempt tomorrow morning?"
  ]
};
```

---

## 6. Configuration File Generator

### 6.1 Template Rendering Pipeline

```
UserKnowledge ──▶ Template Selector ──▶ Variable Mapper ──▶ Jinja2 Renderer ──▶ Validator ──▶ Output Files
                                                                │
                                                    Runs as Celery task
                                                    Uses Tier 3 (GLM 5)
                                                    for smart variable mapping
```

### 6.2 Template: `soul.md.j2`

```jinja2
# Soul

## Role
You are {{ role.title }} — {{ role.summary }}.

## Core Mission
{{ derived_mission }}

## Responsibilities
{% for resp in role.core_responsibilities %}
- {{ resp }}
{% endfor %}

## Decision Framework
{% for fw in recurring_decisions.decision_frameworks %}
### {{ fw.name }}
- **When:** {{ fw.trigger }}
- **Criteria:** {{ fw.criteria }}
- **Default action:** {{ fw.default_action }}
- **Escalate when:** {{ fw.escalation_trigger }}
{% endfor %}

## Quality Standards
{% for qb in recurring_decisions.quality_bars %}
- **{{ qb.task_type }}:** {{ qb.standard }}
{% endfor %}

## Tone & Communication
- Default tone: {{ tone_preferences.formality_level }}
- Style: {{ tone_preferences.communication_style }}
{% for audience, tone in tone_preferences.audience_adaptation.items() %}
- With {{ audience }}: {{ tone }}
{% endfor %}

## Boundaries
{% for boundary in soul.boundaries %}
- {{ boundary }}
{% endfor %}

## Trusted Sources
{% for source in soul.trusted_sources %}
- {{ source }}
{% endfor %}

## Sources to Treat with Skepticism
{% for source in soul.skeptical_of %}
- {{ source }}
{% endfor %}

## Autonomy Policy
Level: {{ soul.autonomy_level }}
{{ soul.escalation_policy }}
```

### 6.3 Template: `heartbeat.md.j2`

```jinja2
# Heartbeat

Check every {{ heartbeat.check_interval_minutes }} minutes.

## Priority Tasks
{% for task in heartbeat.tasks %}
### {{ task.priority }}: {{ task.description }}
- **Trigger:** {{ task.trigger }}
- **Action:** {{ task.action }}
{% endfor %}

## Daily Rhythm
{% for block in operating_rhythms.daily_routine %}
- {{ block.start_time }}–{{ block.end_time }}: {{ block.activity }} ({{ block.flexibility }})
{% endfor %}

## Weekly Patterns
{% for pattern in operating_rhythms.weekly_patterns %}
- **{{ pattern.day_of_week }}:** {{ pattern.theme }}
{% endfor %}
```

### 6.4 Template: `user.md.j2`

```jinja2
# User Profile

## Identity
- **Name:** {{ user.name }}
- **Role:** {{ role.title }}
- **Industry:** {{ industry }}

## Communication Preferences
- **Style:** {{ tone_preferences.communication_style }}
- **Formality:** {{ tone_preferences.formality_level }}
- **Best contact times:** {% for w in operating_rhythms.communication_windows %}{{ w.start }}–{{ w.end }}{% if not loop.last %}, {% endif %}{% endfor %}

## Schedule & Energy
- **Peak focus:** {{ operating_rhythms.energy_map.peak_hours }}
- **Low energy:** {{ operating_rhythms.energy_map.low_hours }}
- **Meeting-free blocks:** {{ operating_rhythms.energy_map.deep_work_blocks }}

## Decision Patterns
{% for d in recurring_decisions.decisions %}
- **{{ d.description }}** ({{ d.frequency }}, {{ d.difficulty }})
{% endfor %}

## Known Friction Points
{% for f in friction_points.time_wasters %}
- {{ f.description }} (~{{ f.time_impact }})
{% endfor %}

## Leverage Priorities
{% for l in leverage_opportunities.delegation_priorities %}
1. {{ l.description }} — estimated impact: {{ l.estimated_impact }}
{% endfor %}
```

### 6.5 Template: `identity.md.j2`

```jinja2
# Identity

## Name
{{ identity.name }}

## Personality
{{ identity.personality }}

## Constraints
{% for c in identity.constraints %}
- {{ c }}
{% endfor %}

## Audience-Aware Tone
{% for audience, tone in identity.audience_tones.items() %}
- **{{ audience }}:** {{ tone }}
{% endfor %}
```

### 6.6 Template: `memory.md.j2`

```jinja2
# Memory

## Initial Knowledge Seeds
{% for seed in memory.initial_seeds %}
- {{ seed }}
{% endfor %}

## Learning Directives
What to learn and remember over time:
{% for directive in memory.learning_directives %}
- {{ directive }}
{% endfor %}

## Retention Policy
{{ memory.retention_policy }}
```

---

## 7. Framework Adapters

Each adapter maps the universal `AgentConfig` to the specific format expected by a target framework.

### Framework Config Reference

| Framework | Language | Config Format | What We Generate |
|---|---|---|---|
| **OpenClaw** | TypeScript/Node.js | Multiple `.md` files in `.openclaw/` dir | `soul.md`, `identity.md`, `user.md`, `heartbeat.md`, `memory.md` |
| **Hermes Agent** | Python | System prompt (`.md`) + JSON files | `system_prompt.md`, `tools.json`, `context.json` |
| **Manus** | Python | Context injection format | Context payload JSON |
| **NemoClaw** | TypeScript | Enterprise config templates | YAML + policy files |
| **Generic** | Any | JSON + YAML + README | `agent-config.json`, `agent-config.yaml`, `README.md` |

**Key architecture notes for adapters:**
- **OpenClaw** uses a 7‑stage ReAct loop (Normalize → Route → Assemble Context → Infer → ReAct → Load Skills → Persist Memory). Its `heartbeat.md` file is natively consumed by a built‑in cron scheduler — our Layer 1 rhythms map directly here.
- **Hermes Agent** has a 3‑layer persistent memory (Working → Episodic → Long‑term via FTS5/SQLite). Since Hermes is also Python, we have an opportunity for deeper integration beyond file generation — directly seeding its FTS5 long‑term memory store with knowledge entries.
- Both frameworks support **MCP** — our MCP knowledge server can feed data to either at runtime, not just at config time.

### 7.1 Adapter Interface

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class GeneratedFile:
    path: str              # Relative path (e.g., ".openclaw/soul.md")
    content: str           # File content
    description: str       # What the file does


@dataclass
class GeneratedFiles:
    files: list[GeneratedFile]
    setup_script: str | None = None


class FrameworkAdapter(ABC):
    name: str
    version: str

    @abstractmethod
    def generate(self, config: AgentConfig, knowledge: UserKnowledge) -> GeneratedFiles:
        """Generate all configuration files for this framework."""
        ...

    @abstractmethod
    def validate(self, files: GeneratedFiles) -> dict:
        """Validate that the generated files are correct."""
        ...

    @abstractmethod
    def get_setup_instructions(self) -> str:
        """Return setup instructions for this framework."""
        ...
```

### 7.2 OpenClaw Adapter

```python
from jinja2 import Environment, FileSystemLoader

jinja_env = Environment(loader=FileSystemLoader("app/generators/templates"))


class OpenClawAdapter(FrameworkAdapter):
    name = "OpenClaw"
    version = "1.x"

    def generate(self, config: AgentConfig, knowledge: UserKnowledge) -> GeneratedFiles:
        ctx = {**config.model_dump(), **knowledge.model_dump()}
        return GeneratedFiles(
            files=[
                GeneratedFile(
                    path=".openclaw/soul.md",
                    content=jinja_env.get_template("soul.md.j2").render(ctx),
                    description="Agent role, tone, boundaries, and decision framework",
                ),
                GeneratedFile(
                    path=".openclaw/identity.md",
                    content=jinja_env.get_template("identity.md.j2").render(ctx),
                    description="Agent name and personality constraints",
                ),
                GeneratedFile(
                    path=".openclaw/user.md",
                    content=jinja_env.get_template("user.md.j2").render(ctx),
                    description="Detailed human profile",
                ),
                GeneratedFile(
                    path=".openclaw/heartbeat.md",
                    content=jinja_env.get_template("heartbeat.md.j2").render(ctx),
                    description="Periodic task checklist (every 30 min)",
                ),
                GeneratedFile(
                    path=".openclaw/memory.md",
                    content=jinja_env.get_template("memory.md.j2").render(ctx),
                    description="Memory bootstrap and learning directives",
                ),
            ],
            setup_script='''#!/bin/bash
# OpenClaw Configuration Generated by AIgenteur Debrief
echo "Files generated in .openclaw/"
echo "1. Review the generated files"
echo "2. Place them in your OpenClaw configuration directory"
echo "3. Restart your OpenClaw instance"
''',
        )
```

### 7.3 Hermes Agent Adapter

```python
import json


class HermesAdapter(FrameworkAdapter):
    name = "Hermes Agent"
    version = "1.x"

    def generate(self, config: AgentConfig, knowledge: UserKnowledge) -> GeneratedFiles:
        system_prompt = self._build_system_prompt(config, knowledge)
        tool_config = self._build_tool_config(knowledge)

        return GeneratedFiles(
            files=[
                GeneratedFile(
                    path="hermes/system_prompt.md",
                    content=system_prompt,
                    description="Hermes system prompt incorporating soul + identity + user context",
                ),
                GeneratedFile(
                    path="hermes/tools.json",
                    content=json.dumps(tool_config, indent=2),
                    description="Tool definitions based on user workflows and dependencies",
                ),
                GeneratedFile(
                    path="hermes/context.json",
                    content=json.dumps(knowledge.model_dump(), indent=2, default=str),
                    description="Structured context for the Hermes agent",
                ),
            ]
        )

    def _build_system_prompt(self, config: AgentConfig, knowledge: UserKnowledge) -> str:
        boundaries = "\n".join(f"- {b}" for b in config.soul.boundaries)
        return f"""# Agent Configuration

## Role
{config.soul.role}

## Mission
{config.soul.mission}

## Persona
Name: {config.identity.name}
{config.identity.personality}

## User Context
{config.user.name} — {config.user.role}
Communication style: {config.user.communication_style}
Schedule patterns: {config.user.schedule_patterns}

## Decision Framework
{config.soul.decision_framework}

## Boundaries
{boundaries}

## Quality Standards
{config.soul.quality_standards}
"""
```

### 7.4 Generic Adapter (JSON/YAML)

```python
import json
import yaml


class GenericAdapter(FrameworkAdapter):
    name = "Generic"
    version = "1.0"

    def generate(self, config: AgentConfig, knowledge: UserKnowledge) -> GeneratedFiles:
        data = {
            "config": config.model_dump(),
            "knowledge": knowledge.model_dump(mode="json"),
        }
        return GeneratedFiles(
            files=[
                GeneratedFile(
                    path="agent-config.json",
                    content=json.dumps(data, indent=2, default=str),
                    description="Complete agent configuration as JSON",
                ),
                GeneratedFile(
                    path="agent-config.yaml",
                    content=yaml.dump(data, default_flow_style=False, sort_keys=False),
                    description="Complete agent configuration as YAML",
                ),
                GeneratedFile(
                    path="README.md",
                    content=self._generate_readme(config),
                    description="Instructions for using the generic config",
                ),
            ]
        )
```

---

## 8. Knowledge Store Integration

### 8.1 Storage: PostgreSQL + pgvector

Using PostgreSQL instead of SQLite gives us:
- **pgvector** for native vector similarity search (no separate vector DB)
- **JSONB** columns for flexible structured data
- **Concurrent access** from Celery workers, API, and MCP server simultaneously
- **Full-text search** via `tsvector` as a bonus

The SQLAlchemy models are defined in Section 4.4. Key queries:

```python
from sqlalchemy import select, func
from pgvector.sqlalchemy import Vector


async def semantic_search(
    session,
    query_embedding: list[float],
    category: str | None = None,
    limit: int = 5,
) -> list[KnowledgeEntryModel]:
    """Search knowledge entries by vector similarity."""
    stmt = (
        select(KnowledgeEntryModel)
        .order_by(
            KnowledgeEntryModel.embedding.cosine_distance(query_embedding)
        )
        .limit(limit)
    )
    if category:
        stmt = stmt.where(KnowledgeEntryModel.category == category)

    result = await session.execute(stmt)
    return result.scalars().all()
```

### 8.2 Redis Usage

```python
import redis.asyncio as redis

redis_client = redis.Redis(host="localhost", port=6379, db=0)

# --- Session Cache (hot state during interview) ---

async def cache_session(session_id: str, data: dict, ttl: int = 3600):
    """Cache active interview session for sub-second reads."""
    await redis_client.setex(
        f"session:{session_id}",
        ttl,
        json.dumps(data, default=str),
    )

async def get_cached_session(session_id: str) -> dict | None:
    data = await redis_client.get(f"session:{session_id}")
    return json.loads(data) if data else None

# --- Rate Limiting ---

async def check_rate_limit(user_id: str, max_requests: int = 60) -> bool:
    """Per-user OpenRouter rate limiting (requests per minute)."""
    key = f"ratelimit:{user_id}"
    count = await redis_client.incr(key)
    if count == 1:
        await redis_client.expire(key, 60)
    return count <= max_requests
```

### 8.3 MCP Server

Exposes the knowledge store to any MCP‑compatible agent:

```python
from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("debrief-knowledge")


@server.tool()
async def search_knowledge(
    query: str,
    category: str | None = None,
    limit: int = 5,
) -> list[TextContent]:
    """Search the user's elicited knowledge base."""
    embedding = await generate_embedding(query)
    results = await semantic_search(db_session, embedding, category, limit)
    return [
        TextContent(type="text", text=json.dumps(r.structured_data))
        for r in results
    ]


@server.tool()
async def get_user_profile() -> TextContent:
    """Get the full synthesized user profile."""
    profile = await knowledge_store.get_user_profile()
    return TextContent(type="text", text=profile.model_dump_json())


@server.tool()
async def get_operating_rhythms() -> list[TextContent]:
    """Get the user's operating rhythms and schedule patterns."""
    entries = await knowledge_store.get_by_category("rhythm")
    return [
        TextContent(type="text", text=json.dumps(e.structured_data))
        for e in entries
    ]
```

---

## 9. API Design (FastAPI)

### 9.1 REST Endpoints

```python
# backend/app/api/routes/sessions.py

from fastapi import APIRouter, Depends
from uuid import UUID

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

@router.post("/")                                  # Start new interview session
async def create_session(req: CreateSessionRequest): ...

@router.get("/{session_id}")                       # Get session status/progress
async def get_session(session_id: UUID): ...

@router.post("/{session_id}/respond")              # Submit user response
async def respond(session_id: UUID, req: RespondRequest): ...

@router.post("/{session_id}/pause")                # Pause session
async def pause_session(session_id: UUID): ...

@router.post("/{session_id}/resume")               # Resume session
async def resume_session(session_id: UUID): ...
```

```python
# backend/app/api/routes/knowledge.py

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])

@router.get("/")                                   # Get all knowledge entries
async def list_knowledge(): ...

@router.get("/search")                             # Semantic search
async def search_knowledge(q: str, category: str | None = None): ...

@router.get("/profile")                            # Get synthesized user profile
async def get_profile(): ...
```

```python
# backend/app/api/routes/generate.py

router = APIRouter(prefix="/api/generate", tags=["generate"])

@router.post("/{framework}")                       # Generate config (async via Celery)
async def generate_config(framework: str): ...

@router.get("/{framework}/preview")                # Preview without saving
async def preview_config(framework: str): ...

@router.get("/frameworks")                         # List supported frameworks
async def list_frameworks(): ...

@router.get("/tasks/{task_id}")                    # Poll Celery task status
async def get_task_status(task_id: str): ...
```

### 9.2 WebSocket (Streaming Interview)

```python
# backend/app/api/websocket.py

from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws/interview/{session_id}")
async def interview_websocket(websocket: WebSocket, session_id: str):
    await websocket.accept()
    try:
        while True:
            # Receive user message
            user_message = await websocket.receive_text()

            # Process through elicitation engine
            async for chunk in elicitation_engine.process_turn(
                session_id=session_id,
                user_message=user_message,
            ):
                # Stream response chunks to frontend
                await websocket.send_json({
                    "type": "chunk",
                    "content": chunk.content,
                    "layer": chunk.layer,
                    "depth_score": chunk.depth_score,
                })

            # Send turn-complete signal with progress
            await websocket.send_json({
                "type": "turn_complete",
                "layer_progress": engine.get_progress(session_id),
            })
    except WebSocketDisconnect:
        await session_manager.pause(session_id)
```

### 9.3 Celery Tasks

```python
# backend/app/tasks/celery_app.py

from celery import Celery

celery_app = Celery(
    "debrief",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    task_time_limit=300,           # 5 min max per task
    worker_prefetch_multiplier=1,  # Fair scheduling
)
```

```python
# backend/app/tasks/synthesis_tasks.py

@celery_app.task(bind=True)
def synthesize_knowledge(self, session_id: str):
    """Convert interview transcript to structured UserKnowledge.
    Uses Tier 3 (GLM 5) for complex structural reasoning."""
    self.update_state(state="SYNTHESIZING")
    session = load_session(session_id)
    knowledge = knowledge_synthesizer.synthesize(
        transcript=session.transcript,
        model_tier="synthesis",  # GLM 5
    )
    store_knowledge(session.user_id, knowledge)
    return {"status": "complete", "entries_created": len(knowledge.entries)}
```

```python
# backend/app/tasks/generation_tasks.py

@celery_app.task(bind=True)
def generate_config_files(self, user_id: str, framework: str):
    """Generate agent config files for a specific framework.
    Uses Tier 3 (GLM 5) for smart variable mapping."""
    self.update_state(state="GENERATING")
    knowledge = load_user_knowledge(user_id)
    config = config_generator.generate(knowledge, model_tier="synthesis")
    adapter = get_adapter(framework)
    files = adapter.generate(config, knowledge)
    save_generated_files(user_id, framework, files)
    return {"status": "complete", "files": [f.path for f in files.files]}
```

---

## 10. Installation & CLI

### One-Command Install

Like OpenClaw (`curl -fsSL https://openclaw.ai/install.sh | bash`) and Hermes Agent (`curl -fsSL .../install.sh | bash`), AIgenteur Debrief must be installable with a single copy-paste:

```bash
curl -fsSL https://raw.githubusercontent.com/aigenteur/debrief/main/install.sh | bash
```

**What the install script does:**

```
1. Check prerequisites (Python 3.11+, Docker, Node.js 20+)
   └── If missing: print clear instructions per OS (macOS/Linux/WSL2)

2. Clone the repo to ~/.debrief/
   └── git clone https://github.com/aigenteur/debrief.git ~/.debrief

3. Create Python virtual environment
   └── python -m venv ~/.debrief/.venv

4. Install backend dependencies
   └── pip install -r requirements.txt  (includes litellm, fastapi, celery, etc.)

5. Install frontend dependencies
   └── cd frontend && npm install

6. Copy .env.example → .env

7. Add `debrief` CLI to PATH
   └── ln -s ~/.debrief/cli.py /usr/local/bin/debrief
   └── Or add to .bashrc/.zshrc

8. Print: "✅ Installed! Run `debrief setup` to configure."
```

### Interactive Setup Wizard

After install, the user runs:

```bash
debrief setup
```

**Setup wizard flow:**

```
┌─────────────────────────────────────────────────────────┐
│  AIgenteur Debrief — Setup Wizard                       │
│                                                         │
│  Step 1/3: LLM Provider                                │
│                                                         │
│  How do you want to power the AI?                      │
│                                                         │
│  ❯ OpenRouter (easiest — one key for all models)       │
│    OpenAI                                               │
│    Anthropic                                            │
│    Google (Gemini)                                       │
│    Ollama (local — free, fully offline)                 │
│    DeepSeek                                             │
│    Alibaba Cloud (DashScope / Qwen)                    │
│    Moonshot AI (Kimi)                                   │
│    ZhipuAI (GLM)                                        │
│    Custom endpoint (vLLM, llama.cpp, LM Studio)        │
│                                                         │
│  Step 2/3: API Key                                     │
│  Paste your API key: sk-or-...                         │
│  (Ollama/local: skipped — no key needed)               │
│                                                         │
│  Step 3/3: Model Selection                             │
│  Use recommended models? (Y/n)                         │
│  ❯ Yes — use defaults for my provider                  │
│    No — let me pick models for each tier               │
│                                                         │
│  ✅ Configuration saved to ~/.debrief/.env              │
│  ✅ Starting services...                                │
│                                                         │
│  Run `debrief start` to begin your first interview.    │
└─────────────────────────────────────────────────────────┘
```

### CLI Commands

```bash
debrief setup          # Interactive provider/model configuration
debrief start          # Start all services (Docker Compose up) + open browser
debrief stop           # Stop all services
debrief interview      # Start a new interview session (opens browser)
debrief export         # Export configs for a framework
debrief status         # Show running services, active sessions, model config
debrief model          # Change LLM provider/models interactively
debrief doctor         # Check installation health (DB, Redis, LLM connectivity)
```

### Quick Start (README copy-paste)

```bash
# Install
curl -fsSL https://raw.githubusercontent.com/aigenteur/debrief/main/install.sh | bash

# Configure (pick your LLM provider)
debrief setup

# Start your first debrief
debrief start
```

Three commands. Under 2 minutes. Works with any LLM provider.

---

## 11. File & Directory Structure

```
debrief/
├── docker-compose.yml                     # PostgreSQL, Redis, backend, frontend, Celery
├── .env.example
├── README.md
│
├── backend/                               # Python FastAPI
│   ├── pyproject.toml                     # Dependencies (uv/poetry)
│   ├── alembic.ini                        # DB migrations config
│   ├── alembic/
│   │   └── versions/                      # Migration files
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                        # FastAPI app + startup/shutdown
│   │   ├── config.py                      # pydantic-settings
│   │   ├── dependencies.py               # DI (DB session, Redis, etc.)
│   │   │
│   │   ├── core/
│   │   │   ├── elicitation_engine.py      # 5-layer interview state machine
│   │   │   ├── follow_up_engine.py       # Specificity analysis & probing
│   │   │   ├── conversation_controller.py # LLM conversation management
│   │   │   ├── session_manager.py        # Redis (hot) + PostgreSQL (cold)
│   │   │   ├── knowledge_synthesizer.py  # Transcript → structured knowledge
│   │   │   └── question_banks/
│   │   │       ├── layer_1_rhythms.py
│   │   │       ├── layer_2_decisions.py
│   │   │       ├── layer_3_dependencies.py
│   │   │       ├── layer_4_friction.py
│   │   │       └── layer_5_leverage.py
│   │   │
│   │   ├── llm/
│   │   │   ├── router.py                 # Tier routing (fast/deep/synthesis)
│   │   │   ├── openrouter_client.py      # OpenRouter API client
│   │   │   └── prompts.py               # System prompts
│   │   │
│   │   ├── generators/
│   │   │   ├── config_generator.py       # Orchestrator
│   │   │   ├── template_renderer.py      # Jinja2 rendering
│   │   │   ├── templates/
│   │   │   │   ├── soul.md.j2
│   │   │   │   ├── identity.md.j2
│   │   │   │   ├── user.md.j2
│   │   │   │   ├── heartbeat.md.j2
│   │   │   │   └── memory.md.j2
│   │   │   └── adapters/
│   │   │       ├── base.py
│   │   │       ├── openclaw_adapter.py
│   │   │       ├── hermes_adapter.py
│   │   │       ├── manus_adapter.py
│   │   │       ├── nemoclaw_adapter.py
│   │   │       └── generic_adapter.py
│   │   │
│   │   ├── knowledge/
│   │   │   ├── store.py                  # PostgreSQL + pgvector CRUD
│   │   │   ├── embeddings.py            # Vector embedding generation
│   │   │   ├── search.py                # Semantic search
│   │   │   └── mcp_server.py           # MCP endpoint
│   │   │
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── sessions.py
│   │   │   │   ├── knowledge.py
│   │   │   │   ├── generate.py
│   │   │   │   └── health.py
│   │   │   └── websocket.py            # WebSocket for streaming interview
│   │   │
│   │   ├── models/
│   │   │   ├── database.py              # SQLAlchemy models
│   │   │   └── schemas.py               # Pydantic request/response schemas
│   │   │
│   │   ├── tasks/
│   │   │   ├── celery_app.py            # Celery configuration
│   │   │   ├── synthesis_tasks.py       # Knowledge synthesis (async)
│   │   │   ├── generation_tasks.py      # Config file generation (async)
│   │   │   └── embedding_tasks.py       # Embedding computation (async)
│   │   │
│   │   └── utils/
│   │       ├── markdown.py
│   │       ├── validation.py
│   │       └── logger.py
│   │
│   └── tests/
│       ├── conftest.py                   # Fixtures (test DB, Redis mock)
│       ├── unit/
│       │   ├── test_elicitation_engine.py
│       │   ├── test_follow_up_engine.py
│       │   ├── test_knowledge_synthesizer.py
│       │   └── test_config_generator.py
│       ├── integration/
│       │   ├── test_interview_flow.py
│       │   └── test_adapter_output.py
│       └── fixtures/
│           ├── sample_transcript.json
│           ├── sample_knowledge.json
│           └── expected_configs/
│
├── frontend/                              # Next.js
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.ts
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx                   # Dashboard
│   │   │   ├── interview/
│   │   │   │   └── [sessionId]/page.tsx   # Interview chat UI
│   │   │   ├── knowledge/
│   │   │   │   └── page.tsx               # Knowledge browser
│   │   │   └── export/
│   │   │       └── page.tsx               # Config generation & download
│   │   ├── components/
│   │   │   ├── InterviewChat.tsx
│   │   │   ├── LayerProgress.tsx
│   │   │   ├── KnowledgeCard.tsx
│   │   │   ├── ConfigPreview.tsx
│   │   │   └── FrameworkSelector.tsx
│   │   ├── hooks/
│   │   │   ├── useWebSocket.ts
│   │   │   └── useSession.ts
│   │   └── lib/
│   │       └── api.ts                     # Backend API client
│   └── public/
│
└── docs/
    ├── PROJECT_DOCUMENT.md
    ├── DEVELOPMENT_DOCUMENT.md
    └── ARCHITECTURE.md
```

---

## 12. Implementation Phases

### Phase 1: Infrastructure & Backend Foundation (Week 1–2)

> **Goal:** Docker Compose running with FastAPI, PostgreSQL, Redis, Celery. OpenRouter client working.

- [ ] Set up monorepo structure (`backend/`, `frontend/`)
- [ ] Create `docker-compose.yml` (PostgreSQL + pgvector, Redis, backend, Celery worker)
- [ ] Set up FastAPI project with `pyproject.toml` (uv or poetry)
- [ ] Configure SQLAlchemy 2.0 + Alembic migrations
- [ ] Create database models (sessions, knowledge_entries)
- [ ] Implement OpenRouter client with tier routing (fast/deep/synthesis)
- [ ] Set up Celery with Redis broker
- [ ] Health check endpoint + OpenRouter connectivity test
- [ ] Test: All services start, DB migrations run, OpenRouter responds

**Deliverable:** `docker compose up` starts everything. `GET /api/health` returns OK.

---

### Phase 2: Core Interview Engine (Week 2–3)

> **Goal:** Working interview flow via API — all 5 layers with session persistence.

- [ ] Build elicitation engine state machine (5 layers)
- [ ] Implement question banks for all layers
- [ ] Build conversation controller with context window management
- [ ] Implement session manager (Redis hot cache + PostgreSQL cold storage)
- [ ] Wire up interview endpoints (`POST /api/sessions`, `POST /api/sessions/:id/respond`)
- [ ] Implement WebSocket endpoint for streaming interview responses
- [ ] Test: Full interview flow end-to-end via API

**Deliverable:** Can run a full interview via `httpx` or Postman.

---

### Phase 3: Follow‑Up Intelligence + Multi-Model Routing (Week 3–4)

> **Goal:** Smart follow-ups using tiered models. Tier 1 (Qwen) scores, Tier 2 (KIMI) probes.

- [ ] Implement specificity analysis using Tier 1 (Qwen 3.5) — fast scoring
- [ ] Build vague‑term detector
- [ ] Implement follow-up generation using Tier 2 (KIMI K2.5) — nuanced probing
- [ ] Add depth scoring per layer
- [ ] Add model usage tracking (which tier, token count, cost)
- [ ] Test: Compare interview depth with/without follow-ups
- [ ] Test: Verify correct model routing per task type

**Deliverable:** Significantly more specific interview outputs. Cost per interview tracked.

---

### Phase 4: Knowledge Synthesis + Celery Pipeline (Week 4–5)

> **Goal:** Transcripts → structured `UserKnowledge` via Celery tasks using Tier 3 (GLM 5).

- [ ] Implement knowledge synthesizer using Tier 3 (GLM 5)
- [ ] Create Celery task for async synthesis
- [ ] Build PostgreSQL + pgvector knowledge store
- [ ] Implement embedding generation (Celery task)
- [ ] Build semantic search endpoint
- [ ] Wire up knowledge API endpoints
- [ ] Test: Knowledge extraction accuracy on sample transcripts

**Deliverable:** After interview, `POST /api/sessions/:id/synthesize` → Celery job → searchable knowledge.

---

### Phase 5: Config File Generation (Week 5–6)

> **Goal:** Generate production‑ready config files for OpenClaw, Hermes, and others.

- [ ] Build Jinja2 template renderer
- [ ] Create `.j2` templates for all 5 config files
- [ ] Implement OpenClaw adapter
- [ ] Implement Hermes Agent adapter
- [ ] Implement generic JSON/YAML adapter
- [ ] Create Celery task for async generation
- [ ] Build config file validator
- [ ] Test: Generated files pass schema validation

**Deliverable:** `POST /api/generate/openclaw` → Celery job → downloadable `.openclaw/` directory.

---

### Phase 6: Next.js Frontend (Week 6–8)

> **Goal:** Full web UI for the interview experience, knowledge browsing, and config export.

- [ ] Initialize Next.js 15 project with App Router
- [ ] Build interview chat UI with WebSocket streaming
- [ ] Implement 5-layer progress indicator
- [ ] Build knowledge browser with search
- [ ] Build config generator UI with framework selector
- [ ] Implement config preview and download
- [ ] Build dashboard (session history, progress)
- [ ] Responsive design + dark mode
- [ ] Test: Playwright E2E tests

**Deliverable:** Beautiful web app for the full interview → export workflow.

---

### Phase 7: MCP Server & Additional Adapters (Week 8–9)

> **Goal:** Knowledge accessible to downstream agents via MCP.

- [ ] Implement MCP server with search/profile/rhythms tools
- [ ] Build remaining framework adapters (Manus, NemoClaw)
- [ ] Integration test: OpenClaw agent queries knowledge via MCP
- [ ] Test: MCP tools return correct data

**Deliverable:** A running MCP server that any agent can query.

---

### Phase 8: Polish & Docs (Week 9–10)

- [ ] Comprehensive README with quickstart
- [ ] Docker deployment guide
- [ ] Usage examples for each framework
- [ ] Sample outputs (redacted)
- [ ] Performance optimization (connection pooling, caching)
- [ ] Error handling hardening
- [ ] Rate limiting and cost controls for OpenRouter

---

## 13. Testing Strategy

### 12.1 Unit Tests (pytest)

| Module | What to Test |
|---|---|
| Elicitation Engine | Layer transitions, question selection, progress tracking |
| Follow‑Up Engine | Specificity scoring, vague‑term detection, follow‑up quality |
| Knowledge Synthesizer | Extraction accuracy from sample transcripts |
| Config Generator | Template rendering, variable mapping |
| Framework Adapters | Output format correctness, schema validation |
| Session Manager | Redis cache + PostgreSQL persistence, pause/resume |
| OpenRouter Client | Model routing, fallback handling, error recovery |
| Celery Tasks | Task execution, state updates, result storage |

### 12.2 Integration Tests

- **Full Interview Flow:** Simulate a complete interview with pre‑scripted responses. Verify transcript, knowledge extraction, and config generation.
- **Adapter Parity:** Same input knowledge should produce valid configs for every supported framework.
- **MCP Round‑Trip:** Start MCP server → query tools → verify responses.
- **Celery Pipeline:** Start interview → complete → trigger synthesis task → verify knowledge store.
- **WebSocket Flow:** Connect → send message → receive streaming response → verify layer progress.

### 12.3 Quality Metrics

```python
class ConfigQualityScore(BaseModel):
    specificity: float      # How specific are the generated instructions? (1-10)
    actionability: float    # Could an agent act on these? (1-10)
    coverage: float         # How many layers are represented? (1-10)
    consistency: float      # Do the files reference each other correctly? (1-10)
    overall: float          # Weighted average
```

### 12.4 Running Tests

```bash
# Backend unit tests
cd backend && pytest tests/unit/ -v

# Backend integration tests (requires Docker services)
cd backend && pytest tests/integration/ -v

# Full e2e (requires OpenRouter API key)
cd backend && pytest tests/ -v --run-e2e

# Frontend tests
cd frontend && npx playwright test

# Quality scoring on sample outputs
cd backend && python -m pytest tests/quality/ -v
```

---

## Appendix A: Environment Variables

```env
# ============================================================
# LLM Provider Configuration
# AIgenteur Debrief is provider-agnostic. Configure your preferred
# provider(s) below. Uses litellm model naming convention.
# ============================================================

# Option A: OpenRouter (easiest — single key for all models)
OPENROUTER_API_KEY=sk-or-...
MODEL_TIER_FAST=openrouter/qwen/qwen3.5-397b-a17b
MODEL_TIER_DEEP=openrouter/moonshotai/kimi-k2.5
MODEL_TIER_SYNTHESIS=openrouter/z-ai/glm-5

# Option B: Direct provider APIs (mix and match)
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
# GOOGLE_API_KEY=...
# DEEPSEEK_API_KEY=...
# DASHSCOPE_API_KEY=...              # Alibaba Cloud / Qwen
# MOONSHOT_API_KEY=...               # Kimi
# ZHIPUAI_API_KEY=...                # GLM
# MODEL_TIER_FAST=openai/gpt-4o-mini
# MODEL_TIER_DEEP=anthropic/claude-3.5-sonnet
# MODEL_TIER_SYNTHESIS=openai/gpt-4o

# Option C: Local models (fully offline, zero API cost)
# OLLAMA_API_BASE=http://localhost:11434
# MODEL_TIER_FAST=ollama/qwen3.5:14b
# MODEL_TIER_DEEP=ollama/qwen3.5:72b
# MODEL_TIER_SYNTHESIS=ollama/qwen3.5:72b

# Option D: Self-hosted (vLLM, llama.cpp, LM Studio)
# CUSTOM_API_BASE=http://localhost:8080/v1
# MODEL_TIER_FAST=openai/my-local-model        # litellm treats custom endpoints as openai-compatible
# MODEL_TIER_DEEP=openai/my-local-model
# MODEL_TIER_SYNTHESIS=openai/my-local-model

# Embedding
EMBEDDING_MODEL=openai/text-embedding-3-small   # Or local sentence-transformers

# PostgreSQL
DATABASE_URL=postgresql+asyncpg://debrief:password@localhost:5432/debrief_db

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# FastAPI
API_HOST=0.0.0.0
API_PORT=8000

# Next.js Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# MCP Server
MCP_PORT=3100

# Rate Limiting
RATE_LIMIT_PER_USER=60                    # Requests per minute per user
```

## Appendix B: Key Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Frontend / Backend split | **Next.js + FastAPI** | Best-in-class for each role: React SSR + Python async API |
| AI Provider | **OpenRouter** (single API) | Unified access to KIMI K2.5, GLM 5, Qwen 3.5 — no multi-provider SDK needed |
| Multi-model strategy | **3 tiers** (fast/deep/synthesis) | Different tasks need different thinking depth; saves cost on simple tasks |
| Interview via LLM vs. scripted questions | **LLM-driven** with question banks as guidance | Scripted interviews feel robotic; LLM enables natural follow-ups |
| Single agent vs. multi-agent interview | **Single agent** | Keeps the experience coherent; multi-agent adds complexity without benefit here |
| Knowledge storage | **PostgreSQL + pgvector** | Structured + vector search in one DB; concurrent access from API + Celery |
| Async heavy tasks | **Celery + Redis** | Synthesis and config gen take 30–120s; non-blocking for the user |
| Session hot state | **Redis** | Sub-second reads during active interview; TTL auto-cleanup |
| Template engine | **Jinja2** | Python-native, powerful, familiar; easy for users to customize |
| Framework adapter pattern | **ABC + pluggable implementations** | New frameworks can be added without touching core code |

## Appendix C: Docker Compose (Development)

```yaml
version: "3.9"

services:
  db:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: debrief
      POSTGRES_PASSWORD: password
      POSTGRES_DB: debrief_db
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      - db
      - redis
    volumes:
      - ./backend:/app

  celery-worker:
    build: ./backend
    command: celery -A app.tasks.celery_app worker --loglevel=info --concurrency=4
    env_file: .env
    depends_on:
      - db
      - redis
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    command: npm run dev
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
      - NEXT_PUBLIC_WS_URL=ws://localhost:8000
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules

volumes:
  pgdata:
```

---

## Appendix D: Clean-Room Implementation Policy

### Rule

**No verbatim code from OpenClaw or Hermes Agent may be used in AIgenteur Debrief.**

Both projects are open source (OpenClaw: MIT, Hermes Agent: MIT), but to maintain full IP independence and avoid any licensing ambiguity, this project follows a **clean-room implementation** approach.

### What IS allowed

- **Read** OpenClaw/Hermes source code to understand:
  - Config file formats and directory structures (so our adapters produce compatible output)
  - Provider API patterns (which endpoints they call, what headers they send)
  - CLI UX patterns (how `openclaw onboard` and `hermes setup` flow works)
  - Architecture decisions (how they handle model routing, context management, etc.)
- **Reference** their documentation, READMEs, and public APIs
- **Cite** specific files as sources for config format specifications (as we do in Section 7)

### What is NOT allowed

- Copy-pasting any function, class, or code block verbatim
- Translating their TypeScript/Python code line-by-line into our codebase
- Reusing their prompt templates, system prompts, or template strings
- Embedding their proprietary assets (logos, brand names beyond factual references)

### Rationale

1. **IP independence** — AIgenteur Debrief is its own product with its own codebase
2. **Quality** — Reimplementing from spec forces us to understand the problem, not just copy a solution
3. **No license debt** — Even though both are MIT, clean-room avoids any future disputes if licenses change or additional restrictions are added
4. **Adapter accuracy** — Our adapters need to produce *compatible output*, not replicate *internal implementation*

### Source References (for config format specs only)

| Framework | What We Reference | Source File | Purpose |
|---|---|---|---|
| OpenClaw | `.openclaw/` directory structure | [`AGENTS.md`](https://github.com/openclaw/openclaw/blob/main/AGENTS.md) | Know what files to generate |
| OpenClaw | Provider env vars | [`.env.example`](https://github.com/openclaw/openclaw/blob/main/.env.example) | Provider compatibility list |
| Hermes | Provider prefixes | [`agent/model_metadata.py`](https://github.com/NousResearch/hermes-agent/blob/main/agent/model_metadata.py) | Provider compatibility list |
| Hermes | Config file format | [`pyproject.toml`](https://github.com/NousResearch/hermes-agent/blob/main/pyproject.toml) | Know what files to generate |
| Hermes | Memory store schema | [`hermes/memory/`](https://github.com/NousResearch/hermes-agent/tree/main/hermes) | FTS5 seed format |

---

*Development Document Version: 2.0 — April 2026*
