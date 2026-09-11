"""One-off: typographic apostrophes in the interactive page's prose.

Replaces ASCII ' with U+2019 everywhere OUTSIDE <script>...</script> blocks
(the embedded JSON and JS must keep their bytes). Runs as a file, never as a
heredoc -- the site's shell-escaping incident is why this rule exists.
"""
import re
from pathlib import Path

PAGE = Path(__file__).resolve().parent.parent / "interactive" / "anomaly-detection.html"

html = PAGE.read_text(encoding="utf-8")
parts = re.split(r"(<script\b.*?</script>)", html, flags=re.DOTALL)
fixed = 0
for i, part in enumerate(parts):
    if part.startswith("<script"):
        continue
    n = part.count("'")
    if n:
        parts[i] = part.replace("'", "’")
        fixed += n
PAGE.write_text("".join(parts), encoding="utf-8", newline="\n")
print(f"Replaced {fixed} straight apostrophes outside script blocks.")
