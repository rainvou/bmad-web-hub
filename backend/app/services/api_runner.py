import logging
import time
from pathlib import Path
from typing import AsyncIterator

import anthropic

from app.config import settings

logger = logging.getLogger(__name__)


def _load_skill_prompt(skill_name: str) -> str:
    """Load SKILL.md + workflow.md + step files as system prompt."""
    skill_dir = settings.SKILLS_DIR / skill_name
    if not skill_dir.exists():
        return ""

    parts: list[str] = []

    # Load SKILL.md
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        parts.append(skill_md.read_text(encoding="utf-8"))

    # Load workflow.md
    workflow_md = skill_dir / "workflow.md"
    if workflow_md.exists():
        parts.append(f"\n---\n## WORKFLOW\n\n{workflow_md.read_text(encoding='utf-8')}")

    # Load step files
    steps_dir = skill_dir / "steps"
    if steps_dir.exists():
        for step_file in sorted(steps_dir.glob("*.md")):
            parts.append(f"\n---\n## {step_file.stem}\n\n{step_file.read_text(encoding='utf-8')}")

    # Load any CSV resources (e.g., brainstorming techniques)
    for csv_file in sorted(skill_dir.glob("*.csv")):
        parts.append(f"\n---\n## {csv_file.stem}\n\n{csv_file.read_text(encoding='utf-8')}")

    return "\n".join(parts)


class APIRunner:
    """Manages Claude API calls for a session using the Anthropic SDK."""

    def __init__(self, skill_name: str):
        self.skill_name = skill_name
        self.client = anthropic.AsyncAnthropic(
            api_key=settings.ANTHROPIC_API_KEY,
            base_url=settings.ANTHROPIC_BASE_URL,
        )
        self.system_prompt = _load_skill_prompt(skill_name)
        self.conversation: list[dict] = []
        self._cancelled = False

    async def invoke(self, user_message: str) -> AsyncIterator[dict]:
        """Send message and stream response chunks."""
        self._cancelled = False
        self.conversation.append({"role": "user", "content": user_message})

        start = time.monotonic()

        try:
            async with self.client.messages.stream(
                model=settings.CLAUDE_MODEL,
                max_tokens=16384,
                system=self.system_prompt,
                messages=self.conversation,
            ) as stream:
                full_text = ""
                async for text in stream.text_stream:
                    if self._cancelled:
                        await stream.response.close()
                        break
                    full_text += text
                    yield {"type": "text_delta", "text": text}

                # Get final message for usage
                if not self._cancelled:
                    message = await stream.get_final_message()
                    duration_ms = int((time.monotonic() - start) * 1000)

                    input_tokens = message.usage.input_tokens
                    output_tokens = message.usage.output_tokens
                    # Approximate cost (Sonnet pricing)
                    cost = (input_tokens * 3 / 1_000_000) + (output_tokens * 15 / 1_000_000)

                    self.conversation.append({"role": "assistant", "content": full_text})

                    yield {
                        "type": "result",
                        "content": full_text,
                        "usage": {
                            "cost_usd": round(cost, 6),
                            "duration_ms": duration_ms,
                            "input_tokens": input_tokens,
                            "output_tokens": output_tokens,
                        },
                    }

        except anthropic.APIError as e:
            yield {"type": "error", "message": f"API error: {e.message}"}
        except Exception as e:
            logger.exception("APIRunner error")
            yield {"type": "error", "message": str(e)}

    def cancel(self):
        self._cancelled = True


# Registry of active runners (session_id -> runner)
active_api_runners: dict[str, APIRunner] = {}
