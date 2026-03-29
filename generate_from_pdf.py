#!/usr/bin/env python3
"""Generate a podcast from a PDF file without using the Web UI."""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from podcast_creator import create_podcast
from podcast_creator.resources.streamlit_app.utils.content_extractor import ContentExtractor
from podcast_creator.transcript_utils import transcript_json_to_text

DIALOGUE_FORMS = {
    "tech_discussion": "tech_discussion_deepseek",
    "solo_expert": "solo_expert_deepseek",
    "business_analysis": "business_analysis_deepseek",
    "diverse_panel": "diverse_panel_deepseek",
}


def resolve_episode_profile(dialogue_form: str) -> str:
    if dialogue_form in DIALOGUE_FORMS:
        return DIALOGUE_FORMS[dialogue_form]
    # Allow passing full profile name directly
    return dialogue_form


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a podcast from a PDF using DeepSeek models.",
    )
    parser.add_argument(
        "--pdf",
        required=True,
        help="PDF file path",
    )
    parser.add_argument(
        "--dialogue",
        required=True,
        choices=sorted(DIALOGUE_FORMS.keys()) + ["tech_discussion_deepseek", "solo_expert_deepseek", "business_analysis_deepseek", "diverse_panel_deepseek"],
        help="Dialogue form (maps to a DeepSeek episode profile)",
    )
    parser.add_argument(
        "--language",
        default="",
        help="Language code or name (e.g., zh, zh-CN, en, Spanish)",
    )
    parser.add_argument(
        "--output-name",
        required=True,
        help="Episode name and output folder name",
    )
    parser.add_argument(
        "--briefing",
        default="",
        help="Optional briefing text to override the profile default",
    )
    parser.add_argument(
        "--output-root",
        default="output",
        help="Root output directory (default: output)",
    )
    parser.add_argument(
        "--log-llm",
        action="store_true",
        help="Log LLM requests/responses to output/log",
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    episode_profile = resolve_episode_profile(args.dialogue)

    content = await ContentExtractor.extract_from_file(str(pdf_path))
    if not ContentExtractor.validate_content(content):
        raise ValueError("Extracted content is too short or invalid for podcast generation")

    output_dir = Path(args.output_root) / args.output_name
    output_dir.mkdir(parents=True, exist_ok=True)

    result = await create_podcast(
        content=content,
        briefing=args.briefing or None,
        episode_name=args.output_name,
        output_dir=str(output_dir),
        episode_profile=episode_profile,
        language=args.language or None,
        enable_llm_logging=args.log_llm,
    )

    transcript_json_path = output_dir / "transcript.json"
    transcript_text_path = output_dir / "transcript.txt"
    if transcript_json_path.exists():
        transcript_json_to_text(transcript_json_path, transcript_text_path)

    print("✅ Podcast generated successfully")
    print(f"📁 Output dir: {result['output_dir']}")
    print(f"🎵 Final audio: {result['final_output_file_path']}")
    print(f"💬 Transcript segments: {len(result['transcript'])}")
    if transcript_json_path.exists():
        print(f"📝 Transcript text: {transcript_text_path}")


if __name__ == "__main__":
    asyncio.run(main())
