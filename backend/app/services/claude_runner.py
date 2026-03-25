import asyncio
import json
import logging
import os
from typing import AsyncIterator

from app.config import settings

logger = logging.getLogger(__name__)


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
        """Spawn claude -p, stream NDJSON events. Retries without session-id on lock conflict."""
        if is_first_turn:
            prompt = f"/{self.skill_name} {user_message}" if user_message else f"/{self.skill_name}"
        else:
            prompt = user_message

        async for event in self._run(prompt, use_session_id=bool(self.claude_session_id)):
            yield event

    async def _run(self, prompt: str, use_session_id: bool) -> AsyncIterator[dict]:
        cmd = [
            str(settings.CLAUDE_BIN),
            "-p",
            "--output-format", "stream-json",
            "--verbose",
            "--permission-mode", "acceptEdits",
        ]

        if use_session_id and self.claude_session_id:
            cmd.extend(["--session-id", self.claude_session_id])

        cmd.append(prompt)

        self.proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(settings.PROJECT_ROOT),
            env=os.environ.copy(),
        )

        got_events = False
        try:
            async for event in self._read_stream():
                if event.get("type") == "system" and event.get("subtype") == "init":
                    self.claude_session_id = event.get("session_id")
                got_events = True
                yield event
        except asyncio.CancelledError:
            await self.cancel()
            raise

        await self.proc.wait()

        if self.proc.returncode and self.proc.returncode != 0:
            stderr_data = await self.proc.stderr.read() if self.proc.stderr else b""
            stderr_str = stderr_data.decode(errors="replace").strip()

            # Session locked — retry without --session-id (starts fresh conversation)
            if "already in use" in stderr_str and use_session_id:
                logger.warning("Session locked, retrying with --continue flag")
                self.claude_session_id = None
                async for event in self._run_with_continue(prompt):
                    yield event
                return

            yield {
                "type": "error",
                "message": stderr_str[:500] if stderr_str else f"Claude exited with code {self.proc.returncode}",
            }

    async def _run_with_continue(self, prompt: str) -> AsyncIterator[dict]:
        """Retry using --continue instead of --session-id."""
        cmd = [
            str(settings.CLAUDE_BIN),
            "-p",
            "--output-format", "stream-json",
            "--verbose",
            "--permission-mode", "acceptEdits",
            "--continue",
            prompt,
        ]

        self.proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(settings.PROJECT_ROOT),
            env=os.environ.copy(),
        )

        try:
            async for event in self._read_stream():
                if event.get("type") == "system" and event.get("subtype") == "init":
                    self.claude_session_id = event.get("session_id")
                yield event
        except asyncio.CancelledError:
            await self.cancel()
            raise

        await self.proc.wait()

        if self.proc.returncode and self.proc.returncode != 0:
            stderr_data = await self.proc.stderr.read() if self.proc.stderr else b""
            stderr_str = stderr_data.decode(errors="replace").strip()
            yield {
                "type": "error",
                "message": stderr_str[:500] if stderr_str else f"Claude exited with code {self.proc.returncode}",
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
                yield json.loads(line_str)
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
