import asyncio
import json
import os
from pathlib import Path
from typing import AsyncIterator

from app.config import settings


class ClaudeRunner:
    """Manages a claude -p subprocess for a single conversation turn."""

    def __init__(
        self,
        skill_name: str,
        claude_session_id: str | None = None,
    ):
        self.skill_name = skill_name
        self.claude_session_id = claude_session_id
        self.proc: asyncio.subprocess.Process | None = None

    async def invoke(self, user_message: str, is_first_turn: bool = False) -> AsyncIterator[dict]:
        """Spawn claude -p, stream NDJSON events."""
        if is_first_turn:
            if user_message:
                prompt = f"/{self.skill_name} {user_message}"
            else:
                prompt = f"/{self.skill_name}"
        else:
            prompt = user_message

        cmd = [
            str(settings.CLAUDE_BIN),
            "-p",
            "--output-format", "stream-json",
            "--verbose",
        ]

        if self.claude_session_id:
            cmd.extend(["--session-id", self.claude_session_id])

        cmd.append(prompt)

        env = os.environ.copy()

        self.proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(settings.PROJECT_ROOT),
            env=env,
        )

        try:
            async for event in self._read_stream():
                # Capture claude session id from init event
                if event.get("type") == "system" and event.get("subtype") == "init":
                    self.claude_session_id = event.get("session_id")

                yield event
        except asyncio.CancelledError:
            await self.cancel()
            raise

        # Wait for process to finish
        await self.proc.wait()

        if self.proc.returncode and self.proc.returncode != 0:
            stderr_data = await self.proc.stderr.read() if self.proc.stderr else b""
            yield {
                "type": "error",
                "message": f"Claude process exited with code {self.proc.returncode}: {stderr_data.decode(errors='replace')[:500]}",
            }

    async def _read_stream(self) -> AsyncIterator[dict]:
        """Read stdout line by line, parse NDJSON."""
        if not self.proc or not self.proc.stdout:
            return

        while True:
            line = await self.proc.stdout.readline()
            if not line:
                break

            line_str = line.decode("utf-8").strip()
            if not line_str:
                continue

            try:
                event = json.loads(line_str)
                yield event
            except json.JSONDecodeError:
                continue

    async def cancel(self) -> None:
        """Terminate the running subprocess."""
        if self.proc and self.proc.returncode is None:
            self.proc.terminate()
            try:
                await asyncio.wait_for(self.proc.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                self.proc.kill()
                await self.proc.wait()


# Registry of active runners (session_id -> runner)
active_runners: dict[str, ClaudeRunner] = {}
