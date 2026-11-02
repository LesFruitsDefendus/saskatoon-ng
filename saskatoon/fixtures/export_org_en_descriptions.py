#!/usr/bin/env python3
"""Export English descriptions from member-organization.json to a markdown file.

Description fields are stored as Quill JSON ({"delta": "...", "html": "..."}).
Plain text is taken from the delta ops, falling back to stripped HTML.
Email addresses and phone numbers are redacted from the output.

Usage:
    ./export_descriptions_en.py [input.json] [output.md]
"""

import html
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT = SCRIPT_DIR / "member-organization.json"
DEFAULT_OUTPUT = SCRIPT_DIR / "member-organization-descriptions-en.md"

FIELDS = [
    "description_en",
    "beneficiary_description_en",
    "equipment_description_en",
]

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
# North American numbers: optional +1, optional parentheses around area code,
# space/dot/dash separators, optional extension (ext, x, poste, #)
PHONE_RE = re.compile(
    r"(?<![\w])(?:\+?1[\s.-]?)?(?:\(\d{3}\)|\d{3})[\s.-]?\d{3}[\s.-]?\d{4}"
    r"(?:\s*(?:ext\.?|x|poste|#)\s*\d{1,6})?(?!\d)",
    re.IGNORECASE,
)


def to_text(value):
    """Convert a stored Quill field value to plain text."""
    if not value:
        return ""
    try:
        data = json.loads(value)
    except (TypeError, ValueError):
        return str(value).strip()
    if not isinstance(data, dict):
        return str(data).strip()

    delta = data.get("delta")
    if delta:
        try:
            ops = json.loads(delta).get("ops", [])
            # Non-string inserts (images, embeds) are skipped
            return "".join(
                op["insert"] for op in ops if isinstance(op.get("insert"), str)
            ).strip()
        except (TypeError, ValueError, AttributeError):
            pass

    raw_html = data.get("html") or ""
    raw_html = re.sub(r"</p>|<br\s*/?>", "\n", raw_html)
    return html.unescape(re.sub(r"<[^>]+>", "", raw_html)).strip()


def redact(text):
    """Replace email addresses and phone numbers with placeholders."""
    text = EMAIL_RE.sub("[email redacted]", text)
    return PHONE_RE.sub("[phone redacted]", text)


def main():
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUTPUT

    with open(input_path, encoding="utf-8") as f:
        records = json.load(f)

    blocks = []
    for record in records:
        if record.get("model") != "member.organization":
            continue
        fields = record["fields"]
        lines = [f"# [{record['pk']}] {fields.get('civil_name', '')}"]
        for field in FIELDS:
            text = redact(to_text(fields.get(field)))
            if text:
                lines.append(f"\n## {field}\n{text}")
        blocks.append("\n".join(lines))

    output_path.write_text("\n\n\n".join(blocks) + "\n", encoding="utf-8")
    print(f"Exported {len(blocks)} organizations to {output_path}")


if __name__ == "__main__":
    main()
