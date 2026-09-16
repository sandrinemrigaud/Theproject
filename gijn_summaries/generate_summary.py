#!/usr/bin/env python3
"""Generate a GIJN masterclass YouTube summary from a video transcript.

Usage:
    python generate_summary.py transcript.txt \
        --speaker "Thin Lei Win" \
        --role "lead reporter at Lighthouse Reports" \
        --output Thin_Lei_Win_summary.docx

Requires ANTHROPIC_API_KEY in the environment. See README.md.
"""

import argparse
import json
import os
import sys

import anthropic

from docx_writer import DEFAULT_CREDITS, build_docx
from style_guide import SUBMIT_SUMMARY_TOOL, SYSTEM_PROMPT
from transcript_utils import load_transcript

DEFAULT_MODEL = "claude-sonnet-5"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("transcript", help="Path to the transcript (.txt, .srt or .vtt)")
    parser.add_argument("--speaker", help="Speaker's full name, if known ahead of time")
    parser.add_argument(
        "--role", help="Speaker's role/title and organization, if known ahead of time"
    )
    parser.add_argument(
        "--format",
        choices=["tips_and_tools", "in_conversation_with", "auto"],
        default="auto",
        help="Force a summary format instead of letting the model decide (default: auto)",
    )
    parser.add_argument(
        "--output",
        help="Output .docx path (default: derived from the speaker's name)",
    )
    parser.add_argument(
        "--credits",
        help="Path to a JSON file overriding the default credits block",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Claude model (default: {DEFAULT_MODEL})")
    parser.add_argument(
        "--json-out",
        help="Optional path to also dump the raw structured summary as JSON",
    )
    return parser.parse_args()


def load_credits(path: str | None) -> dict:
    if not path:
        return dict(DEFAULT_CREDITS)
    with open(path, encoding="utf-8") as f:
        overrides = json.load(f)
    credits = dict(DEFAULT_CREDITS)
    credits.update(overrides)
    return credits


def generate_summary(
    transcript_text: str,
    speaker: str | None,
    role: str | None,
    fmt: str,
    model: str,
) -> dict:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit(
            "ANTHROPIC_API_KEY is not set. Export it before running this script "
            "(see README.md)."
        )

    client = anthropic.Anthropic(api_key=api_key)

    known_bits = []
    if speaker:
        known_bits.append(f"Speaker name: {speaker}")
    if role:
        known_bits.append(f"Speaker role/organization: {role}")
    if fmt != "auto":
        known_bits.append(
            f"Use the '{fmt}' format regardless of your own judgment."
        )
    known = "\n".join(known_bits)

    user_prompt = (
        (known + "\n\n" if known else "")
        + "Transcript:\n\n"
        + transcript_text
    )

    response = client.messages.create(
        model=model,
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        tools=[SUBMIT_SUMMARY_TOOL],
        tool_choice={"type": "tool", "name": "submit_summary"},
        messages=[{"role": "user", "content": user_prompt}],
    )

    for block in response.content:
        if block.type == "tool_use" and block.name == "submit_summary":
            return block.input

    sys.exit("Claude did not return a structured summary. Try again.")


def default_output_path(summary: dict) -> str:
    name = summary["speaker_name"].strip().replace(" ", "_")
    return f"{name}_summary.docx"


def main() -> None:
    args = parse_args()

    transcript_text = load_transcript(args.transcript)
    if not transcript_text:
        sys.exit(f"Transcript file '{args.transcript}' is empty or unreadable.")

    summary = generate_summary(
        transcript_text=transcript_text,
        speaker=args.speaker,
        role=args.role,
        fmt=args.format,
        model=args.model,
    )

    credits = load_credits(args.credits)
    output_path = args.output or default_output_path(summary)
    build_docx(summary, credits, output_path)

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"Format used: {summary['format']} ({summary['format_rationale']})")
    print(f"Proposed title: {summary['proposed_title']}")
    print(f"YouTube title: {summary['youtube_title']}")
    print(f"Saved summary to: {output_path}")


if __name__ == "__main__":
    main()
