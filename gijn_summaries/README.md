# GIJN Masterclass Summaries

Generates a YouTube-ready summary for a GIJN Masterclass video from its
transcript, matching the existing editorial style used across the series
(proposed title, summary, credits, then a YouTube-specific titles/summary
block). Produces both a `.docx` (full archive layout) and a plain `.txt`
file with just the YouTube block, ready to paste into YouTube's title and
description fields. The YouTube title comes as 5 distinct options to choose
from, not a single suggestion.

The tool automatically distinguishes two summary formats, modeled on the
archive of past summaries:

- **`tips_and_tools`** — practical, hands-on masterclasses that teach a
  replicable investigative technique (e.g. using archives, sourcing data,
  producing a podcast). Titles are skill-oriented; the guest's name is
  secondary. May include a `Tools:` section listing concrete resources
  mentioned in the talk.
- **`in_conversation_with`** — masterclasses built around a high-profile
  guest (e.g. a Nobel laureate) whose name and authority are the draw.
  Titles are thematic, and the YouTube titles lead with the guest's name.

The model decides which format fits based on the transcript, unless you
force one with `--format`.

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
```

## Usage

```bash
python generate_summary.py transcript.txt \
    --speaker "Thin Lei Win" \
    --role "lead reporter at Lighthouse Reports" \
    --output Thin_Lei_Win_summary.docx
```

- `transcript.txt` can be plain text, `.srt`, or `.vtt`. Timestamps in
  `.srt`/`.vtt` files are kept (in short `MM:SS` form) so the model can
  propose a timestamped `featured_quote` when a good standalone soundbite
  exists.
- `--speaker` / `--role` are optional hints; if omitted, the model infers
  them from the transcript.
- `--format tips_and_tools` or `--format in_conversation_with` forces a
  format instead of letting the model choose.
- `--credits path/to/credits.json` overrides any of the default credits
  (interview, editing, music, filming, supervision, special thanks,
  support), e.g.:

  ```json
  { "Interview": "Sarah Ulrich", "Filming": "Ron Lopez, Reynald Ramirez" }
  ```

- `--json-out summary.json` also dumps the raw structured summary, useful
  for reviewing or feeding into another tool before trusting the `.docx`.
- `--txt-output path/to/file.txt` overrides where the plain-text YouTube
  block is saved (default: same name as `--output` with `_youtube.txt`
  instead of `.docx`).

## Output

Two files are always generated:

- **`.docx`** mirroring the archive's layout: speaker name, proposed title,
  summary paragraphs, an optional featured quote with timestamps, the
  credits block, a `////` separator, then `YOUTUBE TITLE OPTIONS` (5
  numbered options) / `YOUTUBE SUMMARY`, and the credits block again.
- **`.txt`** with just the YouTube block: the 5 title options, the summary,
  the tools list (if any) and the credits — nothing else — so it can be
  copy-pasted directly into YouTube's title/description fields without
  opening Word.

Always review the generated text before publishing — the model is grounded
in the transcript but titles and framing are worth a human pass.
