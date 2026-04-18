"""Debriefeur CLI — main entry point.

Install: pip install debriefeur
Usage:   debrief              # Start interactive interview
         debrief setup        # Configure LLM provider
         debrief export <id>  # Export config files
         debrief sessions     # List past sessions
         debrief status       # Check LLM connectivity
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from debriefeur.config import get_debrief_home, load_config

console = Console()


def main():
    parser = argparse.ArgumentParser(
        prog="debriefeur",
        description="Debriefeur — Extract your expertise into agent configs",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("setup", help="Configure your LLM provider")
    subparsers.add_parser("status", help="Check LLM connectivity")
    subparsers.add_parser("sessions", help="List past sessions")

    export_p = subparsers.add_parser("export", help="Export config files")
    export_p.add_argument("session_id", help="Session ID")
    export_p.add_argument("--framework", "-f", choices=["openclaw", "hermes", "generic"], default="generic")
    export_p.add_argument("--output", "-o", default="./output")

    args = parser.parse_args()

    if args.command == "setup":
        cmd_setup()
    elif args.command == "status":
        asyncio.run(cmd_status())
    elif args.command == "sessions":
        cmd_sessions()
    elif args.command == "export":
        asyncio.run(cmd_export(args))
    else:
        # Default: start interactive interview
        asyncio.run(cmd_interview())


# ─── Provider Registry ───────────────────────────────────────────────
# All 22+ providers from DEVELOPMENT_DOCUMENT.md, verified against
# OpenClaw .env.example + Hermes model_metadata.py source code.
#
# Each entry: (display_name, description, env_var_name, fast_model, deep_model, synthesis_model)
# For local/custom, env_var_name is None (special handling).

CLOUD_PROVIDERS = [
    ("OpenRouter",         "One key, 200+ models (recommended)", "OPENROUTER_API_KEY",
     "openrouter/qwen/qwen3.5-397b-a17b", "openrouter/moonshotai/kimi-k2.5", "openrouter/z-ai/glm-5"),
    ("OpenAI",             "GPT-4o, GPT-4o-mini, o3",           "OPENAI_API_KEY",
     "openai/gpt-4o-mini", "openai/gpt-4o", "openai/gpt-4o"),
    ("Anthropic",          "Claude 3.5 Sonnet, Haiku",           "ANTHROPIC_API_KEY",
     "anthropic/claude-3-haiku-20240307", "anthropic/claude-3.5-sonnet", "anthropic/claude-3.5-sonnet"),
    ("Google Gemini",      "Gemini 2.5 Pro, Flash",              "GEMINI_API_KEY",
     "gemini/gemini-2.5-flash", "gemini/gemini-2.5-pro", "gemini/gemini-2.5-pro"),
    ("DeepSeek",           "DeepSeek-V3, R1",                    "DEEPSEEK_API_KEY",
     "deepseek/deepseek-chat", "deepseek/deepseek-chat", "deepseek/deepseek-reasoner"),
    ("xAI (Grok)",         "Grok-3, Grok-3-mini",               "XAI_API_KEY",
     "xai/grok-3-mini", "xai/grok-3", "xai/grok-3"),
    ("Moonshot AI (Kimi)", "Kimi-K2.5",                          "MOONSHOT_API_KEY",
     "moonshot/moonshot-v1-auto", "moonshot/kimi-k2.5", "moonshot/kimi-k2.5"),
    ("Qwen (Alibaba)",     "Qwen3.5, Qwen-Max",                 "DASHSCOPE_API_KEY",
     "qwen/qwen-turbo", "qwen/qwen-plus", "qwen/qwen-max"),
    ("ZhipuAI (GLM)",      "GLM-5, GLM-5 Turbo",                "ZHIPUAI_API_KEY",
     "zhipuai/glm-5-turbo", "zhipuai/glm-5", "zhipuai/glm-5"),
    ("Groq",               "Fast inference, Llama 3.3",          "GROQ_API_KEY",
     "groq/llama-3.3-70b-versatile", "groq/llama-3.3-70b-versatile", "groq/llama-3.3-70b-versatile"),
    ("Mistral AI",         "Mistral Large, Codestral",           "MISTRAL_API_KEY",
     "mistral/mistral-small-latest", "mistral/mistral-large-latest", "mistral/mistral-large-latest"),
    ("Fireworks AI",       "Fast hosted open models",            "FIREWORKS_AI_API_KEY",
     "fireworks_ai/accounts/fireworks/models/llama-v3p3-70b-instruct",
     "fireworks_ai/accounts/fireworks/models/llama-v3p3-70b-instruct",
     "fireworks_ai/accounts/fireworks/models/llama-v3p3-70b-instruct"),
    ("Amazon Bedrock",     "Claude, Llama via AWS",              "AWS_ACCESS_KEY_ID",
     "bedrock/anthropic.claude-3-haiku-20240307-v1:0",
     "bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0",
     "bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0"),
    ("MiniMax",            "MiniMax-M2.5 series",                "MINIMAX_API_KEY",
     "minimax/MiniMax-Text-01", "minimax/MiniMax-Text-01", "minimax/MiniMax-Text-01"),
    ("Nous Portal",        "Hermes fine-tuned models",           "NOUS_API_KEY",
     "nous/hermes-3-llama-3.1-405b", "nous/hermes-3-llama-3.1-405b", "nous/hermes-3-llama-3.1-405b"),
    ("OpenCode",           "Zen, Go variants",                   "OPENCODE_API_KEY",
     "opencode/zen-small", "opencode/zen-large", "opencode/zen-large"),
]

LOCAL_PROVIDERS = [
    ("Ollama",             "Fully offline, zero cost",           "OLLAMA"),
    ("vLLM",               "High-throughput self-hosted",        "VLLM"),
    ("llama.cpp / LM Studio / LocalAI", "Any GGUF model",       "CUSTOM"),
]


def cmd_setup():
    """Interactive setup wizard."""
    console.print(Panel.fit(
        "[bold magenta]Debriefeur[/] — Setup Wizard",
        border_style="magenta",
    ))

    console.print("\n[bold]Select your LLM provider:[/]\n")

    # Cloud providers
    console.print("  [dim]── Cloud Providers ──[/]")
    for i, (name, desc, *_) in enumerate(CLOUD_PROVIDERS, 1):
        num = f"{i:>2}"
        console.print(f"  [cyan]{num}[/]. [bold]{name:<22}[/] — {desc}")

    # Local providers
    console.print()
    console.print("  [dim]── Local / Self-hosted ──[/]")
    offset = len(CLOUD_PROVIDERS)
    for i, (name, desc, _) in enumerate(LOCAL_PROVIDERS, offset + 1):
        num = f"{i:>2}"
        console.print(f"  [cyan]{num}[/]. [bold]{name:<22}[/] — {desc}")

    choice = console.input("\n[bold]Your choice [1]: [/]").strip() or "1"

    try:
        idx = int(choice)
    except ValueError:
        idx = 1

    lines = []

    if 1 <= idx <= len(CLOUD_PROVIDERS):
        # Cloud provider — ask for API key, set model tiers
        name, desc, env_var, fast, deep, synth = CLOUD_PROVIDERS[idx - 1]

        if env_var == "AWS_ACCESS_KEY_ID":
            # AWS Bedrock needs two keys
            key = console.input("[bold]AWS Access Key ID: [/]").strip()
            secret = console.input("[bold]AWS Secret Access Key: [/]").strip()
            region = console.input("[bold]AWS Region [us-east-1]: [/]").strip() or "us-east-1"
            lines.append(f"AWS_ACCESS_KEY_ID={key}")
            lines.append(f"AWS_SECRET_ACCESS_KEY={secret}")
            lines.append(f"AWS_REGION_NAME={region}")
        else:
            key = console.input(f"[bold]{name} API key: [/]").strip()
            lines.append(f"{env_var}={key}")

        lines.append(f"MODEL_TIER_FAST={fast}")
        lines.append(f"MODEL_TIER_DEEP={deep}")
        lines.append(f"MODEL_TIER_SYNTHESIS={synth}")

    elif idx == offset + 1:
        # Ollama
        url = console.input("[bold]Ollama URL [http://localhost:11434]: [/]").strip() or "http://localhost:11434"
        model = console.input("[bold]Model [qwen3.5:14b]: [/]").strip() or "qwen3.5:14b"
        lines.append(f"OLLAMA_API_BASE={url}")
        lines.append(f"MODEL_TIER_FAST=ollama/{model}")
        lines.append(f"MODEL_TIER_DEEP=ollama/{model}")
        lines.append(f"MODEL_TIER_SYNTHESIS=ollama/{model}")

    elif idx == offset + 2:
        # vLLM
        url = console.input("[bold]vLLM server URL [http://localhost:8000]: [/]").strip() or "http://localhost:8000"
        model = console.input("[bold]Model name: [/]").strip()
        lines.append(f"OPENAI_API_BASE={url}/v1")
        lines.append(f"MODEL_TIER_FAST=openai/{model}")
        lines.append(f"MODEL_TIER_DEEP=openai/{model}")
        lines.append(f"MODEL_TIER_SYNTHESIS=openai/{model}")

    elif idx == offset + 3:
        # llama.cpp / LM Studio / LocalAI / any custom
        url = console.input("[bold]API base URL (e.g. http://localhost:1234/v1): [/]").strip()
        model = console.input("[bold]Model name: [/]").strip()
        key = console.input("[bold]API key (leave empty if none): [/]").strip()
        if key:
            lines.append(f"OPENAI_API_KEY={key}")
        lines.append(f"OPENAI_API_BASE={url}")
        lines.append(f"MODEL_TIER_FAST=openai/{model}")
        lines.append(f"MODEL_TIER_DEEP=openai/{model}")
        lines.append(f"MODEL_TIER_SYNTHESIS=openai/{model}")

    else:
        console.print(f"[yellow]Unknown choice, defaulting to OpenRouter.[/]")
        key = console.input("[bold]OpenRouter API key: [/]").strip()
        lines.append(f"OPENROUTER_API_KEY={key}")
        lines.append("MODEL_TIER_FAST=openrouter/qwen/qwen3.5-397b-a17b")
        lines.append("MODEL_TIER_DEEP=openrouter/moonshotai/kimi-k2.5")
        lines.append("MODEL_TIER_SYNTHESIS=openrouter/z-ai/glm-5")

    env_path = get_debrief_home() / ".env"
    env_path.write_text("\n".join(lines) + "\n")

    console.print(f"\n[green]✅ Saved to {env_path}[/]")
    console.print("\n[bold]Next:[/] Just run [cyan]debrief[/] to start your first interview!\n")


async def cmd_status():
    """Check LLM connectivity."""
    from debriefeur.llm import LLMRouter

    console.print(Panel.fit("[bold]Debriefeur — Status[/]", border_style="blue"))

    config = load_config()
    console.print(f"\n  Config dir: [cyan]{get_debrief_home()}[/]")
    console.print(f"  Fast model: [cyan]{config['model_tier_fast']}[/]")
    console.print(f"  Deep model: [cyan]{config['model_tier_deep']}[/]")
    console.print(f"  Synth model: [cyan]{config['model_tier_synthesis']}[/]")

    console.print("\n  Checking LLM connectivity...", end=" ")
    llm = LLMRouter()
    result = await llm.health_check()
    if result["status"] == "ok":
        console.print("[green]✅ Connected[/]")
    else:
        console.print(f"[red]❌ {result.get('error', 'Failed')}[/]")
        console.print("\n  Run [cyan]debrief setup[/] to configure your provider.")


def cmd_sessions():
    """List past sessions."""
    from debriefeur.sessions import list_sessions

    sessions = list_sessions()
    if not sessions:
        console.print("\nNo sessions yet. Run [cyan]debrief[/] to start one!\n")
        return

    table = Table(title="Past Sessions")
    table.add_column("ID", style="cyan")
    table.add_column("Status")
    table.add_column("Layer")
    table.add_column("Questions", justify="right")
    table.add_column("Started")

    for s in sessions:
        status_icon = "✅" if s["status"] == "completed" else "⏳" if s["status"] == "in_progress" else "⏸️"
        table.add_row(
            s["id"],
            f"{status_icon} {s['status']}",
            s["layer"].replace("_", " ").title(),
            str(s["questions"]),
            s["started_at"][:16],
        )

    console.print(table)
    console.print(f"\n  Export: [cyan]debrief export <ID> --framework openclaw[/]\n")


async def cmd_export(args):
    """Export config files."""
    from debriefeur.adapters import generate
    from debriefeur.sessions import load_session

    session = load_session(args.session_id)
    if not session:
        console.print(f"[red]Session '{args.session_id}' not found.[/]")
        return

    console.print(f"\n[bold]Generating {args.framework} config...[/]\n")

    # Extract knowledge from transcript
    knowledge = _extract_knowledge(session)
    files = generate(args.framework, knowledge)

    out_dir = Path(args.output)
    for f in files:
        path = out_dir / f.filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f.content)
        console.print(f"  [green]✅[/] {path} — {f.description}")

    console.print(f"\n[bold green]Done![/] Files saved to [cyan]{out_dir}/[/]\n")


async def cmd_interview():
    """Run an interactive interview in the terminal."""
    from debriefeur.engine import ElicitationEngine, LAYER_NAMES
    from debriefeur.llm import LLMRouter
    from debriefeur.sessions import create_session_id, save_session

    # Check config exists
    env_path = get_debrief_home() / ".env"
    if not env_path.exists() and not os.environ.get("OPENROUTER_API_KEY") and not os.environ.get("OPENAI_API_KEY"):
        console.print("\n[yellow]No provider configured yet.[/]")
        console.print("Run [cyan]debrief setup[/] first, or set OPENROUTER_API_KEY.\n")
        return

    console.print(Panel.fit(
        "[bold magenta]Debriefeur[/]\n[dim]Expertise → Agent Configuration[/]",
        border_style="magenta",
    ))

    llm = LLMRouter()
    engine = ElicitationEngine(llm)

    session_id = create_session_id()
    session = engine.new_session()

    console.print(f"\n[dim]Session: {session_id}[/]\n")

    # Opening message
    opening = await engine.generate_opening(session)
    console.print(Markdown(opening))
    console.print()

    save_session(session_id, session)

    # Interview loop
    while session["status"] == "in_progress":
        try:
            user_input = console.input("[bold green]You:[/] ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("/quit", "/exit", "/q"):
                session["status"] = "paused"
                save_session(session_id, session)
                console.print(f"\n[yellow]⏸️  Paused.[/] Session saved: [cyan]{session_id}[/]\n")
                break

            console.print()
            with console.status("[dim]Thinking...[/]"):
                result = await engine.process_response(user_input, session)

            save_session(session_id, session)

            # Show layer + depth
            layer_name = LAYER_NAMES.get(result["layer"], result["layer"])
            depth = result["depth_score"]
            follow = " [dim](follow-up)[/]" if result["is_follow_up"] else ""
            console.print(f"[dim]{layer_name} · depth {depth:.1f}/10{follow}[/]\n")

            console.print(Markdown(result["message"]))
            console.print()

        except KeyboardInterrupt:
            session["status"] = "paused"
            save_session(session_id, session)
            console.print(f"\n\n[yellow]⏸️  Paused.[/] Session: [cyan]{session_id}[/]")
            console.print(f"Resume anytime — your progress is saved.\n")
            break
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/]")
            console.print("Retrying... (Ctrl+C to pause)\n")

    if session["status"] == "completed":
        console.print(Panel.fit(
            f"[bold green]Interview complete![/]\n\n"
            f"Export: [cyan]debrief export {session_id} --framework openclaw[/]",
            border_style="green",
        ))

    save_session(session_id, session)


def _extract_knowledge(session: dict) -> dict:
    """Extract structured knowledge from session transcript."""
    knowledge: dict = {
        "operating_rhythms": {"daily_routine": [], "weekly_patterns": [], "energy_map": {}},
        "recurring_decisions": {"decisions": [], "decision_frameworks": []},
        "dependencies": {"tool_ecosystem": [], "information_flows": []},
        "friction_points": {"time_wasters": [], "delegation_barriers": []},
        "leverage_opportunities": {"automation_candidates": [], "impact_priorities": []},
    }
    for turn in session.get("transcript", []):
        if turn.get("role") == "user":
            layer = turn.get("layer", "operating_rhythms")
            content = turn.get("content", "")[:500]
            if layer in knowledge:
                # Add to first list in that layer
                first_key = next(iter(knowledge[layer]))
                if isinstance(knowledge[layer][first_key], list):
                    knowledge[layer][first_key].append({"description": content})
    return knowledge


if __name__ == "__main__":
    main()
