"""Loading and light normalization of masterclass transcripts (.txt/.srt/.vtt)."""

import re
from pathlib import Path

_SRT_INDEX_RE = re.compile(r"^\d+$")
_TIMECODE_RE = re.compile(
    r"(\d{2}:\d{2}:\d{2}[.,]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[.,]\d{3})"
)


def load_transcript(path: str) -> str:
    """Return the transcript text, with timestamps preserved as `[start --> end]`
    markers ahead of each line when the source is .srt/.vtt, so the model can
    still locate a featured quote. Plain .txt files are returned unchanged."""
    p = Path(path)
    suffix = p.suffix.lower()
    raw = p.read_text(encoding="utf-8", errors="replace")

    if suffix not in (".srt", ".vtt"):
        return raw.strip()

    lines = raw.splitlines()
    out = []
    current_stamp = None
    for line in lines:
        line = line.strip()
        if not line or line.upper() == "WEBVTT" or _SRT_INDEX_RE.match(line):
            continue
        m = _TIMECODE_RE.search(line)
        if m:
            current_stamp = f"[{_to_short(m.group(1))} --> {_to_short(m.group(2))}]"
            continue
        if current_stamp:
            out.append(f"{current_stamp} {line}")
        else:
            out.append(line)
    return "\n".join(out).strip()


def _to_short(timecode: str) -> str:
    """HH:MM:SS,mmm -> MM:SS (drop hours when zero, drop milliseconds)."""
    timecode = timecode.replace(",", ".")
    hh, mm, ss = timecode.split(":")
    ss = ss.split(".")[0]
    if hh == "00":
        return f"{mm}:{ss}"
    return f"{hh}:{mm}:{ss}"
