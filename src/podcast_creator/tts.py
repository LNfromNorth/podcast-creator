"""Helpers for text-to-speech provider integration."""

import os
from pathlib import Path
from typing import Any, Dict

import httpx
from esperanto import AIFactory

QWEN_TTS_PROVIDER = "qwen"
QWEN_TTS_PROVIDER_ALIASES = {"qwen", "qwen-tts"}
QWEN_TTS_DEFAULT_MODEL = "qwen3-tts-flash"
QWEN_TTS_DEFAULT_BASE_URL = "https://dashscope.aliyuncs.com/api/v1"
QWEN_TTS_DEFAULT_VOICES = {
    "Cherry": "Cherry",
    "Serena": "Serena",
    "Ethan": "Ethan",
    "Chelsie": "Chelsie",
    "Dylan": "Dylan",
    "Jada": "Jada",
    "Sunny": "Sunny",
}


def normalize_tts_provider(provider: str) -> str:
    """Normalize provider names so aliases resolve consistently."""
    normalized = provider.strip().lower().replace("_", "-")
    if normalized in QWEN_TTS_PROVIDER_ALIASES:
        return QWEN_TTS_PROVIDER
    return normalized


def _resolve_qwen_endpoint(base_url: str) -> str:
    """Resolve a Qwen TTS endpoint from a base URL or full endpoint."""
    normalized = base_url.rstrip("/")
    if normalized.endswith("/generation"):
        return normalized
    return f"{normalized}/services/aigc/multimodal-generation/generation"


async def generate_speech_file(
    provider: str,
    model_name: str,
    text: str,
    voice: str,
    output_file: Path,
    tts_config: Dict[str, Any] | None = None,
) -> None:
    """Generate a speech file for a supported provider."""
    normalized_provider = normalize_tts_provider(provider)
    if normalized_provider == QWEN_TTS_PROVIDER:
        await generate_qwen_speech_file(
            model_name=model_name,
            text=text,
            voice=voice,
            output_file=output_file,
            tts_config=tts_config,
        )
        return

    provider_config = dict(tts_config or {})
    api_key = provider_config.pop("api_key", None)
    base_url = provider_config.pop("base_url", None)
    tts_model = AIFactory.create_text_to_speech(
        normalized_provider,
        model_name,
        api_key=api_key,
        base_url=base_url,
        **provider_config,
    )
    await tts_model.agenerate_speech(text=text, voice=voice, output_file=output_file)


async def generate_qwen_speech_file(
    model_name: str,
    text: str,
    voice: str,
    output_file: Path,
    tts_config: Dict[str, Any] | None = None,
) -> None:
    """Generate speech with Qwen TTS via DashScope HTTP APIs."""
    config = dict(tts_config or {})
    api_key = config.pop("api_key", None) or os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError(
            "Qwen TTS requires DASHSCOPE_API_KEY or tts_config['api_key']."
        )

    base_url = (
        config.pop("base_url", None)
        or os.getenv("QWEN_TTS_BASE_URL")
        or os.getenv("DASHSCOPE_BASE_URL")
        or QWEN_TTS_DEFAULT_BASE_URL
    )
    endpoint = _resolve_qwen_endpoint(base_url)
    timeout = float(config.pop("timeout", 120.0))

    request_input = {
        "text": text,
        "voice": voice,
    }

    if language_type := config.pop("language_type", None):
        request_input["language_type"] = language_type

    payload: Dict[str, Any] = {
        "model": model_name or QWEN_TTS_DEFAULT_MODEL,
        "input": request_input,
    }
    if config:
        payload["parameters"] = config

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        audio_url = (
            data.get("output", {})
            .get("audio", {})
            .get("url")
        )
        if not audio_url:
            raise RuntimeError("Qwen TTS response did not include output.audio.url.")

        audio_response = await client.get(audio_url)
        audio_response.raise_for_status()

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_bytes(audio_response.content)
