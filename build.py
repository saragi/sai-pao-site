"""Builds the public Sai Pao pages from the app repo's approved legal text.

Usage: python3 build.py [path to sai-pao repo]   (default ../sai-pao)
Handles only the Markdown the legal docs use: headings, paragraphs,
bullet lists, pipe tables, **bold** and [links](url).
"""
import html
import pathlib
import re
import sys

APP = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "../sai-pao")
OUT = pathlib.Path(__file__).parent

STYLE = """
:root{--ink:#0b1418;--soft:#56646A;--brand:#0b6d71;--line:#DDE7E8;--bg:#F4F8F8}
@media (prefers-color-scheme: dark){:root{--ink:#F4F8F8;--soft:#9fb0b4;--brand:#6FB9BD;--line:#22343a;--bg:#0b1418}}
*{box-sizing:border-box}html,body{overflow-wrap:anywhere}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.75 'Prompt',sans-serif}
main{max-width:720px;margin:0 auto;padding:40px 16px 80px}
h1{font-size:28px;line-height:1.3;margin:0 0 16px}h2{font-size:20px;margin:32px 0 8px}
a{color:var(--brand)}p,li{color:var(--ink)}
table{width:100%;table-layout:fixed;border-collapse:collapse;margin:12px 0;font-size:15px}
th,td{text-align:left;vertical-align:top;padding:8px;border-bottom:1px solid var(--line)}
.nav{font-size:14px;margin-bottom:32px}.nav a{margin-right:16px}
footer{margin-top:48px;font-size:14px;color:var(--soft)}
"""


def inline(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', text)


def render(md: str) -> tuple[str, str]:
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    out, title, lines, i = [], "", md.splitlines(), 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line:
            i += 1
        elif line.startswith("# "):
            title = line[2:]
            out.append(f"<h1>{inline(title)}</h1>")
            i += 1
        elif line.startswith("## "):
            out.append(f"<h2>{inline(line[3:])}</h2>")
            i += 1
        elif line.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(f"<li>{inline(lines[i][2:])}</li>")
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip("|").split("|")]
                if not all(set(c) <= set("-: ") for c in cells):
                    tag = "th" if not rows else "td"
                    rows.append("<tr>" + "".join(f"<{tag}>{inline(c)}</{tag}>" for c in cells) + "</tr>")
                i += 1
            out.append("<table>" + "".join(rows) + "</table>")
        else:
            para = []
            while i < len(lines) and lines[i].strip() and not lines[i].startswith(("#", "- ", "|")):
                para.append(lines[i].strip())
                i += 1
            out.append(f"<p>{inline(' '.join(para))}</p>")
    return title, "\n".join(out)


def page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="th"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Prompt:wght@400;600;700&display=swap" rel="stylesheet">
<style>{STYLE}</style></head>
<body><main>
<div class="nav"><a href="/">สายเป่า</a><a href="/privacy/">นโยบายความเป็นส่วนตัว</a><a href="/terms/">ข้อกำหนดการใช้งาน</a></div>
{body}
<footer>ติดต่อ <a href="mailto:support@sai-pao.com">support@sai-pao.com</a></footer>
</main></body></html>
"""


for slug, src in (("privacy", "privacy-th.md"), ("terms", "terms-th.md")):
    title, body = render((APP / "docs/legal" / src).read_text(encoding="utf-8"))
    (OUT / slug).mkdir(exist_ok=True)
    (OUT / slug / "index.html").write_text(page(title, body), encoding="utf-8")

(OUT / "index.html").write_text(
    page(
        "สายเป่า (Sai Pao)",
        "<h1>สายเป่า (Sai Pao)</h1>\n"
        "<p>แอปสำหรับร้านค้าใช้บันทึกเวลาเข้างาน งานประจำวัน และตารางกะของพนักงาน</p>",
    ),
    encoding="utf-8",
)
