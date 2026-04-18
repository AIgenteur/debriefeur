"""Elicitation Engine — 5-layer interview state machine.

Stores session state as JSON files in ~/.debrief/sessions/.
No database needed.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any

from debriefeur.llm import LLMRouter
from debriefeur.prompts import (
    FOLLOW_UP_GENERATOR,
    INTERVIEWER_SYSTEM,
    LAYER_DESCRIPTIONS,
    SPECIFICITY_SCORER,
)

logger = logging.getLogger(__name__)

LAYERS = [
    "operating_rhythms",
    "recurring_decisions",
    "dependencies",
    "friction_points",
    "leverage_opportunities",
]

LAYER_NAMES = {
    "operating_rhythms": "⏰ Operating Rhythms",
    "recurring_decisions": "⚖️ Recurring Decisions",
    "dependencies": "🔗 Dependencies",
    "friction_points": "⚡ Friction Points",
    "leverage_opportunities": "🚀 Leverage Opportunities",
}

MIN_DEPTH = 6.0
MAX_QUESTIONS = 15
MIN_QUESTIONS = 3

TOPIC_MAP = {
    "operating_rhythms": ["daily routine", "weekly patterns", "energy patterns", "communication windows"],
    "recurring_decisions": ["decision triggers", "evaluation criteria", "good vs bad", "escalation rules"],
    "dependencies": ["tool ecosystem", "information flows", "human dependencies", "failure modes"],
    "friction_points": ["time wasters", "dreaded tasks", "delegation barriers", "bottlenecks"],
    "leverage_opportunities": ["high-volume tasks", "pattern-based work", "automation candidates"],
}


class ElicitationEngine:
    """Drives the 5-layer interview, storing state in-memory & disk."""

    def __init__(self, llm: LLMRouter) -> None:
        self.llm = llm

    def new_session(self) -> dict:
        """Create a new session state dict."""
        return {
            "status": "in_progress",
            "current_layer": LAYERS[0],
            "layer_progress": {},
            "transcript": [],
            "started_at": datetime.now(timezone.utc).isoformat(),
        }

    async def generate_opening(self, session: dict) -> str:
        """Return the first message to the user."""
        opening = (
            "Welcome to your AIgenteur Debrief session! 🎯\n\n"
            "I'm going to help you articulate the knowledge that lives in your head — "
            "the routines, decisions, and judgment calls that make you effective.\n\n"
            "We'll explore five areas, starting with your daily rhythms. "
            "There are no wrong answers.\n\n"
            "**Walk me through a typical workday, from when you first sit down "
            "to when you wrap up.** What does the rhythm look like?"
        )
        session["transcript"].append({
            "role": "assistant",
            "content": opening,
            "layer": LAYERS[0],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        session["layer_progress"][LAYERS[0]] = {
            "status": "in_progress", "questions_asked": 0,
            "follow_ups": 0, "depth_score": 0.0,
        }
        return opening

    async def process_response(self, user_response: str, session: dict) -> dict:
        """Process user response, return {message, layer, depth, status, is_follow_up}."""
        layer = session["current_layer"]
        lp = session["layer_progress"].setdefault(layer, {
            "status": "in_progress", "questions_asked": 0,
            "follow_ups": 0, "depth_score": 0.0,
        })

        # Record user turn
        session["transcript"].append({
            "role": "user", "content": user_response,
            "layer": layer, "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        # Score specificity (Tier 1 — fast)
        score_data = await self._score(user_response, session["transcript"])
        score = score_data.get("score", 5.0)
        vague = score_data.get("vague_terms", [])

        # Update depth (weighted moving average)
        n = lp["questions_asked"] + 1
        lp["depth_score"] = (lp["depth_score"] * (n - 1) + score) / n
        lp["questions_asked"] = n

        is_follow_up = False

        # Low specificity? Follow up
        if score < 5.0 and lp["follow_ups"] < 3:
            is_follow_up = True
            lp["follow_ups"] += 1
            message = await self._follow_up(user_response, session["transcript"], vague, score)

        # Advance layer?
        elif (lp["depth_score"] >= MIN_DEPTH and n >= MIN_QUESTIONS) or n >= MAX_QUESTIONS:
            lp["status"] = "completed"
            next_layer = self._next_layer(layer)

            if next_layer:
                session["current_layer"] = next_layer
                session["layer_progress"].setdefault(next_layer, {
                    "status": "in_progress", "questions_asked": 0,
                    "follow_ups": 0, "depth_score": 0.0,
                })
                message = await self._transition(layer, next_layer, session["transcript"])
            else:
                session["status"] = "completed"
                message = (
                    "We've covered all five areas! 🎉\n\n"
                    "Your knowledge has been captured. Run `debrief export` to generate "
                    "config files for OpenClaw, Hermes Agent, or any framework.\n\n"
                    "Join the community → https://skool.com/aigenteur"
                )
        else:
            message = await self._next_question(layer, session["transcript"], lp)

        # Record assistant turn
        session["transcript"].append({
            "role": "assistant", "content": message,
            "layer": session["current_layer"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "is_follow_up": is_follow_up,
        })

        return {
            "message": message,
            "layer": session["current_layer"],
            "depth_score": lp["depth_score"],
            "status": session["status"],
            "is_follow_up": is_follow_up,
        }

    async def _score(self, response: str, transcript: list) -> dict:
        last_q = ""
        for t in reversed(transcript):
            if t["role"] == "assistant":
                last_q = t["content"]
                break
        prompt = SPECIFICITY_SCORER.format(response=response, question=last_q)
        try:
            result = await self.llm.complete_fast(
                [{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )
            return json.loads(result)
        except Exception:
            return {"score": 5.0, "vague_terms": []}

    async def _follow_up(self, response: str, transcript: list, vague: list, score: float) -> str:
        last_q = ""
        for t in reversed(transcript):
            if t["role"] == "assistant":
                last_q = t["content"]
                break
        prompt = FOLLOW_UP_GENERATOR.format(
            original_question=last_q, user_response=response,
            vague_terms=", ".join(vague) or "general vagueness", score=score,
        )
        return await self.llm.complete_deep([{"role": "user", "content": prompt}])

    async def _next_question(self, layer: str, transcript: list, lp: dict) -> str:
        recent = transcript[-10:]
        context = "\n".join(f"{'Q' if t['role']=='assistant' else 'A'}: {t['content'][:200]}" for t in recent)
        uncovered = self._uncovered(layer, transcript)

        prompt = INTERVIEWER_SYSTEM.format(
            layer=layer, layer_description=LAYER_DESCRIPTIONS.get(layer, ""),
            question_count=lp["questions_asked"], depth_score=f"{lp['depth_score']:.1f}",
            uncovered_topics=", ".join(uncovered) or "exploring deeper",
            context_summary=context,
            turn_instructions="Ask the next natural question. Build on what they shared.",
        )
        return await self.llm.complete_deep([
            {"role": "system", "content": prompt},
            {"role": "user", "content": "Generate the next interview question."},
        ])

    async def _transition(self, from_layer: str, to_layer: str, transcript: list) -> str:
        prompt = (
            f"We just finished '{from_layer.replace('_',' ')}'. "
            f"Transition smoothly to '{to_layer.replace('_',' ')}': "
            f"{LAYER_DESCRIPTIONS.get(to_layer, '')}\n\n"
            f"Write a brief transition (2-3 sentences) then an opening question."
        )
        return await self.llm.complete_deep([{"role": "user", "content": prompt}])

    def _next_layer(self, current: str) -> str | None:
        try:
            idx = LAYERS.index(current)
            return LAYERS[idx + 1] if idx + 1 < len(LAYERS) else None
        except ValueError:
            return None

    def _uncovered(self, layer: str, transcript: list) -> list[str]:
        text = " ".join(t["content"].lower() for t in transcript if t.get("layer") == layer)
        return [t for t in TOPIC_MAP.get(layer, []) if not any(w in text for w in t.split())]
