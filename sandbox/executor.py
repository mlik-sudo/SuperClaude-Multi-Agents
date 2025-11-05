"""Execution sandbox utilities for SuperClaude."""
from __future__ import annotations

import asyncio
import json
import os
import shutil
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

DEFAULT_WORKSPACE = Path(__file__).resolve().parent / "generated"


@dataclass(slots=True)
class ExecutionResult:
    """Represents the outcome of executing generated code inside the sandbox."""

    success: bool
    stdout: str
    stderr: str
    exit_code: int
    duration_seconds: float
    error_message: Optional[str] = None
    code_path: Optional[Path] = None


class CodeExecutor:
    """Execute generated code in a constrained environment."""

    def __init__(
        self,
        timeout: int = 300,
        workspace_dir: Optional[Path] = None,
        keep_files: bool = False,
    ) -> None:
        self.timeout = timeout
        self.keep_files = keep_files
        self.workspace = Path(workspace_dir) if workspace_dir else DEFAULT_WORKSPACE
        self.workspace.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    async def execute_python(self, code: str, name: Optional[str] = None) -> ExecutionResult:
        """Execute Python code inside the sandbox."""

        file_path = self._write_code_file(code, suffix=".py", name=name)
        start_time = time.perf_counter()
        try:
            process = await asyncio.create_subprocess_exec(
                sys.executable,
                "-u",
                str(file_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.workspace),
            )

            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    process.communicate(), timeout=self.timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                duration = time.perf_counter() - start_time
                self._cleanup_file(file_path)
                return ExecutionResult(
                    success=False,
                    stdout="",
                    stderr=f"Execution timed out after {self.timeout}s",
                    exit_code=-1,
                    duration_seconds=duration,
                    error_message=f"Timeout after {self.timeout}s",
                    code_path=file_path if self.keep_files else None,
                )

            stdout = stdout_bytes.decode("utf-8", errors="replace") if stdout_bytes else ""
            stderr = stderr_bytes.decode("utf-8", errors="replace") if stderr_bytes else ""
            exit_code = process.returncode or 0
            duration = time.perf_counter() - start_time
            success = exit_code == 0
            error_message = stderr if not success else None

            return ExecutionResult(
                success=success,
                stdout=stdout,
                stderr=stderr,
                exit_code=exit_code,
                duration_seconds=duration,
                error_message=error_message,
                code_path=file_path if self.keep_files else None,
            )
        except Exception as exc:  # pragma: no cover - defensive guard
            duration = time.perf_counter() - start_time
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=str(exc),
                exit_code=-1,
                duration_seconds=duration,
                error_message=str(exc),
                code_path=file_path if self.keep_files else None,
            )
        finally:
            if not self.keep_files:
                self._cleanup_file(file_path)

    async def execute_deno(self, code: str, name: Optional[str] = None) -> ExecutionResult:
        """Execute Deno (TypeScript/JavaScript) code when available."""

        if shutil.which("deno") is None:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="Deno binary not found in PATH",
                exit_code=-1,
                duration_seconds=0.0,
                error_message="Deno runtime unavailable",
            )

        file_path = self._write_code_file(code, suffix=".ts", name=name or "script")
        start_time = time.perf_counter()
        try:
            process = await asyncio.create_subprocess_exec(
                "deno",
                "run",
                "--quiet",
                str(file_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.workspace),
            )
            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    process.communicate(), timeout=self.timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                duration = time.perf_counter() - start_time
                self._cleanup_file(file_path)
                return ExecutionResult(
                    success=False,
                    stdout="",
                    stderr=f"Execution timed out after {self.timeout}s",
                    exit_code=-1,
                    duration_seconds=duration,
                    error_message=f"Timeout after {self.timeout}s",
                    code_path=file_path if self.keep_files else None,
                )

            stdout = stdout_bytes.decode("utf-8", errors="replace") if stdout_bytes else ""
            stderr = stderr_bytes.decode("utf-8", errors="replace") if stderr_bytes else ""
            exit_code = process.returncode or 0
            duration = time.perf_counter() - start_time
            success = exit_code == 0
            error_message = stderr if not success else None

            return ExecutionResult(
                success=success,
                stdout=stdout,
                stderr=stderr,
                exit_code=exit_code,
                duration_seconds=duration,
                error_message=error_message,
                code_path=file_path if self.keep_files else None,
            )
        finally:
            if not self.keep_files:
                self._cleanup_file(file_path)

    def cleanup(self) -> None:
        """Remove generated artifacts from the workspace when keep_files=False."""

        if self.keep_files:
            return

        for item in self.workspace.glob("*"):
            if item.is_file():
                try:
                    item.unlink()
                except OSError:
                    continue

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _write_code_file(self, code: str, suffix: str, name: Optional[str]) -> Path:
        identifier = uuid.uuid4().hex[:8]
        base_name = name or "script"
        file_name = f"{base_name}_{identifier}{suffix}"
        path = self.workspace / file_name
        path.write_text(code, encoding="utf-8")
        return path

    def _cleanup_file(self, path: Path) -> None:
        if self.keep_files:
            return
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass
