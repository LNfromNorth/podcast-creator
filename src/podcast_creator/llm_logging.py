"""Utilities for logging LLM requests and responses to disk."""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class LLMLogEntry:
    stage: str
    kind: str  # "request" or "response"
    payload: Dict[str, Any]
    meta: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "stage": self.stage,
            "kind": self.kind,
            "payload": self.payload,
            "meta": self.meta or {},
        }


class LLMRequestLogger:
    """Write LLM request/response logs into output/log."""

    def __init__(self, output_dir: Path) -> None:
        self.log_dir = output_dir / "log"
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def _write(self, entry: LLMLogEntry) -> Path:
        safe_stage = entry.stage.replace(" ", "_")
        filename = f"{safe_stage}_{entry.kind}_{uuid.uuid4().hex}.json"
        path = self.log_dir / filename
        path.write_text(json.dumps(entry.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def log_request(self, stage: str, payload: Dict[str, Any], meta: Optional[Dict[str, Any]] = None) -> Path:
        return self._write(LLMLogEntry(stage=stage, kind="request", payload=payload, meta=meta))

    def log_response(self, stage: str, payload: Dict[str, Any], meta: Optional[Dict[str, Any]] = None) -> Path:
        return self._write(LLMLogEntry(stage=stage, kind="response", payload=payload, meta=meta))


def get_llm_logger(output_dir: Path, enabled: bool) -> Optional[LLMRequestLogger]:
    if not enabled:
        return None
    return LLMRequestLogger(output_dir)
