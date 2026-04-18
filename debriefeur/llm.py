"""LLM Router — provider-agnostic model routing via litellm.

Routes requests to the correct model tier:
  - fast:      Classification, scoring (cheap, fast)
  - deep:      Conversation, probing (nuanced)
  - synthesis: Knowledge synthesis, config gen (thorough)
"""

import logging
from typing import Any

import litellm

from debriefeur.config import load_config

logger = logging.getLogger(__name__)
litellm.suppress_debug_info = True

TIER_DEFAULTS = {
    "fast": {"max_tokens": 2048, "temperature": 0.3},
    "deep": {"max_tokens": 4096, "temperature": 0.7},
    "synthesis": {"max_tokens": 8192, "temperature": 0.4},
}


class LLMRouter:
    """Routes LLM calls to the appropriate model tier."""

    def __init__(self) -> None:
        config = load_config()
        self._models = {
            "fast": config["model_tier_fast"],
            "deep": config["model_tier_deep"],
            "synthesis": config["model_tier_synthesis"],
        }

    async def complete(
        self,
        tier: str,
        messages: list[dict[str, str]],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        response_format: dict | None = None,
        **kwargs: Any,
    ) -> str:
        """Send a completion request to the specified tier's model."""
        model = self._models[tier]
        defaults = TIER_DEFAULTS[tier]

        call_params = {
            "model": model,
            "messages": messages,
            "temperature": temperature if temperature is not None else defaults["temperature"],
            "max_tokens": max_tokens if max_tokens is not None else defaults["max_tokens"],
        }
        if response_format:
            call_params["response_format"] = response_format
        call_params.update(kwargs)

        response = await litellm.acompletion(**call_params)
        return response.choices[0].message.content or ""

    async def complete_fast(self, messages: list[dict], **kw: Any) -> str:
        return await self.complete("fast", messages, **kw)

    async def complete_deep(self, messages: list[dict], **kw: Any) -> str:
        return await self.complete("deep", messages, **kw)

    async def complete_synthesis(self, messages: list[dict], **kw: Any) -> str:
        return await self.complete("synthesis", messages, **kw)

    async def health_check(self) -> dict:
        try:
            await litellm.acompletion(
                model=self._models["fast"],
                messages=[{"role": "user", "content": "Say ok"}],
                max_tokens=5,
                temperature=0,
            )
            return {"status": "ok", "model": self._models["fast"]}
        except Exception as e:
            return {"status": "error", "error": str(e)}
