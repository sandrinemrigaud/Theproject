"""Renders a generated summary into the same plain-text .docx layout used by
the GIJN masterclass summary archive (title / summary / credits / separator /
YouTube title / YouTube summary / credits)."""

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


def _add_credits(doc: Document, credits: dict) -> None:
    doc.add_paragraph("Credits:")
    doc.add_paragraph("")
    for role, names in credits.items():
        if not names:
            continue
        if role == "With the support of":
            doc.add_paragraph(f"With the support of {names}")
        else:
            doc.add_paragraph(f"{role}: {names}")


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
    doc.add_paragraph("YOUTUBE TITLE")
    doc.add_paragraph("")
    doc.add_paragraph(summary["youtube_title"])
    doc.add_paragraph("")
    doc.add_paragraph("YOUTUBE SUMMARY")
    doc.add_paragraph("")
    for para in summary["youtube_summary_paragraphs"]:
        doc.add_paragraph(para)
        doc.add_paragraph("")

    _add_credits(doc, credits)

    doc.save(output_path)
