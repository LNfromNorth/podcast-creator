"""Utilities for working with transcript files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, Tuple, Union


def _normalize_transcript_payload(payload: Union[dict, list]) -> list:
    if isinstance(payload, dict):
        if "transcript" in payload:
            payload = payload["transcript"]
        elif "segments" in payload:
            payload = payload["segments"]
        elif "dialogues" in payload:
            payload = payload["dialogues"]
        else:
            raise ValueError("Unsupported transcript JSON format (missing transcript list).")

    if not isinstance(payload, list):
        raise ValueError("Unsupported transcript JSON format (expected a list).")

    return payload


def extract_dialogue_entries(payload: Union[dict, list]) -> List[Tuple[str, str]]:
    entries = []
    items = _normalize_transcript_payload(payload)

    for item in items:
        if not isinstance(item, dict):
            continue

        speaker = item.get("speaker") or item.get("name") or ""
        text = item.get("dialogue") or item.get("text") or item.get("content")

        if text is None:
            continue

        entries.append((speaker, str(text)))

    if not entries:
        raise ValueError("No dialogue entries found in transcript JSON.")

    return entries


def render_transcript_text(
    entries: Iterable[Tuple[str, str]],
    include_speaker: bool = True,
    separator: str = ": ",
) -> str:
    lines = []
    for speaker, text in entries:
        if include_speaker and speaker:
            lines.append(f"{speaker}{separator}{text}")
        else:
            lines.append(text)
    return "\n".join(lines) + "\n"


def transcript_json_to_text(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    include_speaker: bool = True,
    separator: str = ": ",
) -> Path:
    input_path = Path(input_path)
    output_path = Path(output_path)

    payload = json.loads(input_path.read_text(encoding="utf-8"))
    entries = extract_dialogue_entries(payload)
    text = render_transcript_text(entries, include_speaker=include_speaker, separator=separator)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")
    return output_path
