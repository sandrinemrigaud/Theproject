"""Renders a generated summary into the same plain-text .docx layout used by
the GIJN masterclass summary archive (title / summary / credits / separator /
YouTube titles / YouTube summary / credits), plus a plain .txt companion file
containing just the YouTube-ready block for pasting into the video's
description box."""

from docx import Document

DEFAULT_CREDITS = {
    "Interview": "Sarah Ulrich",
    "Video Editing": "Quentin Egloff",
    "Music": "Lionel Marçal",
    "Filming": "Ron Lopez, Reynald Ramirez, Hashim Hakeem",
    "Supervision and Coordination": "Sandrine Rigaud",
    "Special Thanks": "Glenn Chong",
    "With the support of": "The Konrad-Adenauer-Stiftung",
}


def _credits_lines(credits: dict) -> list[str]:
    lines = ["Credits:", ""]
    for role, names in credits.items():
        if not names:
            continue
        if role == "With the support of":
            lines.append(f"With the support of {names}")
        else:
            lines.append(f"{role}: {names}")
    return lines


def _add_credits(doc: Document, credits: dict) -> None:
    for line in _credits_lines(credits):
        doc.add_paragraph(line)


def build_docx(summary: dict, credits: dict, output_path: str) -> None:
    doc = Document()

    if summary.get("tools_mentioned"):
        doc.add_paragraph("Tools:")
        doc.add_paragraph("")
        for tool in summary["tools_mentioned"]:
            line = tool["name"]
            if tool.get("url"):
                line += f": {tool['url']}"
            doc.add_paragraph(line)
        doc.add_paragraph("")

    doc.add_paragraph(summary["speaker_name"].upper())
    doc.add_paragraph("")
    doc.add_paragraph(summary["proposed_title"])
    doc.add_paragraph("")
    for para in summary["summary_paragraphs"]:
        doc.add_paragraph(para)
        doc.add_paragraph("")

    if summary.get("featured_quote"):
        q = summary["featured_quote"]
        doc.add_paragraph("////")
        doc.add_paragraph("")
        doc.add_paragraph(f"{q['timestamp_start']} - {q['timestamp_end']}")
        doc.add_paragraph("")
        doc.add_paragraph(f"“{q['quote']}”")
        doc.add_paragraph("")

    _add_credits(doc, credits)

    doc.add_paragraph("")
    doc.add_paragraph("////")
    doc.add_paragraph("")
    doc.add_paragraph("YOUTUBE TITLE OPTIONS")
    doc.add_paragraph("")
    for i, title in enumerate(summary["youtube_titles"], start=1):
        doc.add_paragraph(f"{i}. {title}")
    doc.add_paragraph("")
    doc.add_paragraph("YOUTUBE SUMMARY")
    doc.add_paragraph("")
    for para in summary["youtube_summary_paragraphs"]:
        doc.add_paragraph(para)
        doc.add_paragraph("")

    _add_credits(doc, credits)

    doc.save(output_path)


def build_youtube_txt(summary: dict, credits: dict, output_path: str) -> None:
    """Write a plain-text file with just the YouTube-ready block: the 5 title
    options, the summary, the tools list (if any) and the credits -- ready to
    copy-paste straight into the YouTube title/description fields."""
    lines: list[str] = ["YOUTUBE TITLE OPTIONS", ""]
    for i, title in enumerate(summary["youtube_titles"], start=1):
        lines.append(f"{i}. {title}")
    lines.append("")

    lines.append("YOUTUBE SUMMARY")
    lines.append("")
    for para in summary["youtube_summary_paragraphs"]:
        lines.append(para)
        lines.append("")

    if summary.get("tools_mentioned"):
        lines.append("Tools:")
        for tool in summary["tools_mentioned"]:
            line = tool["name"]
            if tool.get("url"):
                line += f": {tool['url']}"
            lines.append(line)
        lines.append("")

    lines.extend(_credits_lines(credits))

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).rstrip() + "\n")
