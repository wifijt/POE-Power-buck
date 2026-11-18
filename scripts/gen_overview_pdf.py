#!/usr/bin/env python3
"""docs/board_overview.md -> docs/board_overview.pdf (US Letter, for printing or showing an inspector).

Markdown -> HTML with a print stylesheet -> PDF through headless Chromium (Playwright for Node).
Relative links become links to the GitHub repository, so they still work from the PDF.

Needs: pip install markdown, and Node with the playwright package (npx playwright install chromium).
    python3 scripts/gen_overview_pdf.py
"""
import json
import os
import re
import subprocess
import tempfile

import markdown

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DOCS = os.path.join(ROOT, "docs")
SRC = os.path.join(DOCS, "board_overview.md")
OUT = os.path.join(DOCS, "board_overview.pdf")
REPO = "https://github.com/wifijt/POE-Power-buck/blob/main/"

CSS = """
@page { size: Letter; margin: 0.55in 0.6in 0.6in 0.6in; }
* { box-sizing: border-box; }
body { font-family: "Inter", "Liberation Sans", Arial, sans-serif; font-size: 9.6pt; line-height: 1.38;
       color: #1d2733; margin: 0; }
h1 { font-size: 18pt; margin: 0 0 4pt 0; color: #0f1b2a; letter-spacing: -0.2pt; }
h2 { font-size: 11.5pt; margin: 13pt 0 5pt 0; padding-bottom: 2pt; border-bottom: 1.2pt solid #e07a1f;
     color: #0f1b2a; break-after: avoid; overflow: hidden; }
p { margin: 0 0 6pt 0; }
ul { margin: 0 0 6pt 0; padding-left: 15pt; }
li { margin: 1.5pt 0; }
li > ul { margin: 2pt 0 0 0; }
a { color: #1f5f99; text-decoration: none; }
code { font-family: "JetBrains Mono", "DejaVu Sans Mono", monospace; font-size: 8.6pt; }
img.board { float: right; width: 1.75in; margin: 2pt 0 6pt 14pt; border: 0.6pt solid #c9d2dc; border-radius: 3pt; }
table { border-collapse: collapse; width: 100%; margin: 2pt 0 6pt 0; break-inside: auto; }
tr { break-inside: avoid; }
td { border-top: 0.5pt solid #d6dde5; padding: 3pt 6pt; vertical-align: top; }
td:first-child { font-weight: 600; width: 1.55in; color: #0f1b2a; }
thead { display: none; }
.foot { margin-top: 12pt; font-size: 8pt; color: #6b7785; border-top: 0.5pt solid #d6dde5; padding-top: 4pt; }
"""


def build_html():
    md = open(SRC, encoding="utf-8").read()
    # Python-Markdown wants 4-space indents for nested lists; the source uses 2 (GitHub style)
    md = re.sub(r"^(  )+(?=[*-] )", lambda m: "    " * (len(m.group(0)) // 2), md, flags=re.M)
    # the board photo floats beside the intro instead of taking a full-width line
    md = re.sub(r"^!\[board\]\(board_top\.png\)\s*$", "", md, flags=re.M)
    md = re.sub(r"\]\(\.\./([^)]+)\)", lambda m: "](%s%s)" % (REPO, m.group(1)), md)
    md = re.sub(r"\]\(((?!https?:)[^)#]+\.(?:pdf|png|md))\)", lambda m: "](%sdocs/%s)" % (REPO, m.group(1)), md)
    body = markdown.markdown(md, extensions=["tables", "sane_lists"])
    # put the photo right after the title
    body = body.replace("</h1>", '</h1>\n<img class="board" src="board_top.png" alt="board">', 1)
    return ("<!doctype html><html><head><meta charset='utf-8'><style>%s</style></head><body>%s"
            "<div class='foot'>Source: %sdocs/board_overview.md</div></body></html>" % (CSS, body, REPO))


def main():
    html = os.path.join(DOCS, ".board_overview.tmp.html")   # in docs/ so the image path resolves
    with open(html, "w", encoding="utf-8") as f:
        f.write(build_html())
    js = """
const {chromium} = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://' + %s, {waitUntil: 'load'});
  await p.pdf({path: %s, format: 'Letter', printBackground: true, preferCSSPageSize: true});
  await b.close();
})();
""" % (json.dumps(html), json.dumps(OUT))
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
            f.write(js)
        subprocess.run(["node", f.name], check=True)
    finally:
        os.unlink(html)
        os.unlink(f.name)
    print("wrote", os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    main()
