#!/usr/bin/env python3
"""Convert old-version finance daily MD reports to styled HTML.

Reads old_20260817.md / old_20260818.md / old_20260819.md,
generates self-contained HTML files with the same visual style
as the v2.0 formal version (dark/light theme, signal cards, etc.)
"""

import re
import os
import html

# ── Config ──────────────────────────────────────────────────────
REPO = r"C:\Users\Administrator\.local\share\TeleAgent\TeleAgent的工作空间\.temp\finance-daily-repo"
DOCS_DIR = os.path.join(REPO, "docs")
ARCHIVES_DIR = os.path.join(REPO, "archives")

REPORTS = [
    {
        "md_file": "old_20260817.md",
        "date_str": "2026年8月17日 周一",
        "date_short": "08-17",
        "archive_dir": "2026-08-17-old",
        "html_filename": "每日金融信号日报_20260817.html",
        "subtitle": "数据截至8月14日收盘 / 8月15日发布",
        "version": "v1.0 旧版日报",
    },
    {
        "md_file": "old_20260818.md",
        "date_str": "2026年8月18日 周二",
        "date_short": "08-18",
        "archive_dir": "2026-08-18-old",
        "html_filename": "每日金融信号日报_20260818.html",
        "subtitle": "数据截至8月17日收盘 / 8月18日早盘",
        "version": "v1.0 旧版日报",
    },
    {
        "md_file": "old_20260819.md",
        "date_str": "2026年8月19日 周三",
        "date_short": "08-19",
        "archive_dir": "2026-08-19-old",
        "html_filename": "每日金融信号日报_20260819.html",
        "subtitle": "数据截止：2026年8月18日收盘 / 8月19日早盘前",
        "version": "v1.0 旧版日报",
    },
]

# ── CSS (extracted from formal version, simplified for old reports) ──
CSS = """
:root {
  --primary: #0d47a1; --primary-light: #e3f2fd; --primary-dark: #0a3d91;
  --text: #202124; --text-secondary: #5f6368; --text-tertiary: #9aa0a6;
  --bg: #f5f7fa; --card-bg: #ffffff; --card-bg-hover: #fafbfc;
  --border: #d5dce6; --border-light: #e8eaed;
  --tag-bg: #e3f2fd; --tag-text: #0d47a1;
  --signal-green: #2e7d32; --signal-yellow: #f9a825; --signal-red: #c62828;
  --summary-bg: linear-gradient(135deg, #0d47a1, #1a237e);
  --shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04);
  --shadow-hover: 0 8px 24px rgba(0,0,0,0.12), 0 2px 6px rgba(0,0,0,0.08);
  --radius: 12px; --radius-sm: 8px;
  --grade-s: #1b5e20; --grade-a: #0d47a1; --grade-b: #e65100; --grade-c: #616161;
}
html.dark {
  --primary: #90caf9; --primary-light: #0d2b45; --primary-dark: #64b5f6;
  --text: #e8eaed; --text-secondary: #9aa0a6; --text-tertiary: #5f6368;
  --bg: #121212; --card-bg: #1e1e1e; --card-bg-hover: #262626;
  --border: #3c4043; --border-light: #2d2d2d;
  --tag-bg: #0d2b45; --tag-text: #90caf9;
  --signal-green: #66bb6a; --signal-yellow: #ffa726; --signal-red: #ef5350;
  --summary-bg: linear-gradient(135deg, #0d47a1, #4a148c);
  --grade-s: #66bb6a; --grade-a: #90caf9; --grade-b: #ffcc80; --grade-c: #bdbdbd;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; -webkit-font-smoothing: antialiased; transition: background 0.3s, color 0.3s; padding: 16px; }
.page-layout { max-width: 800px; margin: 0 auto; }
header { text-align: center; padding: 28px 0 20px; }
header h1 { font-size: 26px; font-weight: 700; background: linear-gradient(135deg, #0d47a1, #7b1fa2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
header .subtitle { color: var(--text-secondary); font-size: 14px; margin-top: 6px; }
header .report-meta { display: flex; justify-content: center; gap: 16px; margin-top: 10px; font-size: 12px; color: var(--text-tertiary); flex-wrap: wrap; }
.version-badge { display: inline-block; background: #e65100; color: #fff; font-size: 11px; font-weight: 600; padding: 2px 10px; border-radius: 10px; margin-top: 8px; }
.theme-toggle { position: fixed; top: 16px; right: 16px; z-index: 100; width: 40px; height: 40px; border-radius: 50%; border: 1px solid var(--border); background: var(--card-bg); color: var(--text); font-size: 18px; cursor: pointer; display: flex; align-items: center; justify-content: center; box-shadow: var(--shadow); transition: all 0.2s; }
.theme-toggle:hover { box-shadow: var(--shadow-hover); transform: scale(1.1); }
.back-to-top { position: fixed; bottom: 24px; right: 24px; z-index: 100; width: 40px; height: 40px; border-radius: 50%; border: 1px solid var(--border); background: var(--card-bg); color: var(--text); font-size: 18px; cursor: pointer; display: none; align-items: center; justify-content: center; box-shadow: var(--shadow); transition: all 0.2s; }
.back-to-top:hover { box-shadow: var(--shadow-hover); transform: scale(1.1); }
.back-to-top.visible { display: flex; }
.main-quote { background: var(--summary-bg); color: #fff; border-radius: var(--radius); padding: 18px 24px; margin-bottom: 16px; box-shadow: var(--shadow); }
.main-quote .quote-text { font-size: 15px; font-weight: 600; line-height: 1.7; }
.backtest-card { background: var(--card-bg); border-radius: var(--radius); box-shadow: var(--shadow); overflow: hidden; margin-bottom: 16px; }
.backtest-header { padding: 12px 18px; font-size: 14px; font-weight: 700; color: #00838f; border-bottom: 1px solid var(--border); }
.backtest-item { padding: 12px 18px; border-bottom: 1px solid var(--border-light); }
.backtest-item:last-child { border-bottom: none; }
.backtest-title { font-size: 13px; font-weight: 600; color: var(--text); margin-bottom: 4px; }
.backtest-detail { font-size: 12px; color: var(--text-secondary); line-height: 1.7; }
.backtest-detail table { width: 100%; border-collapse: collapse; margin-top: 6px; }
.backtest-detail th { background: var(--primary-light); color: var(--primary-dark); padding: 6px 8px; text-align: left; font-size: 11px; font-weight: 600; }
.backtest-detail td { padding: 6px 8px; border-bottom: 1px solid var(--border-light); font-size: 11px; }
.backtest-tag { display: inline-block; padding: 1px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; margin-left: 4px; }
.backtest-hit { background: rgba(46,125,50,0.12); color: #2e7d32; }
.backtest-partial { background: rgba(249,168,37,0.12); color: #f9a825; }
.backtest-miss { background: rgba(198,40,40,0.12); color: #c62828; }
.section-title { font-size: 13px; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 2px; margin: 16px 0 12px; padding-bottom: 6px; border-bottom: 2px solid var(--border); }
.signal-card { background: var(--card-bg); border-radius: var(--radius); box-shadow: var(--shadow); margin-bottom: 16px; overflow: hidden; transition: box-shadow 0.3s, transform 0.3s; }
.signal-card:hover { box-shadow: var(--shadow-hover); transform: translateY(-2px); }
.signal-card .signal-header { display: flex; align-items: center; gap: 10px; padding: 14px 20px 0; flex-wrap: wrap; }
.signal-card .signal-num { width: 26px; height: 26px; border-radius: 50%; background: var(--primary); color: #fff; font-size: 13px; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.signal-card .signal-title { font-size: 16px; font-weight: 700; }
.signal-card .signal-body { padding: 12px 20px 18px; }
.signal-table { width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 10px; }
.signal-table th { background: var(--primary-light); color: var(--primary-dark); padding: 8px 10px; text-align: left; font-weight: 600; }
.signal-table td { padding: 8px 10px; border-bottom: 1px solid var(--border-light); }
.signal-table tr:last-child td { border-bottom: none; }
.plain-talk { font-size: 13px; color: var(--text-secondary); background: var(--primary-light); border-radius: var(--radius-sm); padding: 10px 14px; line-height: 1.7; margin-bottom: 10px; }
.plain-talk .plain-label { font-weight: 700; color: var(--primary); margin-right: 4px; }
.source-note { font-size: 11px; color: var(--text-tertiary); margin-top: 6px; }
.summary-card { background: var(--card-bg); border-radius: var(--radius); box-shadow: var(--shadow); overflow: hidden; margin-bottom: 16px; }
.summary-card .summary-header { padding: 12px 18px; font-size: 14px; font-weight: 700; color: #00695c; border-bottom: 1px solid var(--border); }
.summary-card table { width: 100%; border-collapse: collapse; font-size: 13px; }
.summary-card th { background: rgba(0,105,92,0.08); color: #00695c; padding: 8px 10px; text-align: left; font-weight: 600; }
.summary-card td { padding: 8px 10px; border-bottom: 1px solid var(--border-light); }
.summary-card tr:last-child td { border-bottom: none; }
html.dark .summary-card th { background: rgba(0,105,92,0.15); }
.source-summary { background: var(--card-bg); border-radius: var(--radius); box-shadow: var(--shadow); overflow: hidden; margin-bottom: 16px; }
.source-summary .ss-header { padding: 12px 18px; font-size: 14px; font-weight: 700; color: #00695c; border-bottom: 1px solid var(--border); }
.source-summary table { width: 100%; border-collapse: collapse; font-size: 12px; }
.source-summary th { background: rgba(0,105,92,0.08); color: #00695c; padding: 8px 10px; text-align: left; font-weight: 600; }
.source-summary td { padding: 6px 10px; border-bottom: 1px solid var(--border-light); }
.source-summary tr:last-child td { border-bottom: none; }
html.dark .source-summary th { background: rgba(0,105,92,0.15); }
.disclaimer { background: var(--card-bg); border-radius: var(--radius); box-shadow: var(--shadow); padding: 20px 24px; margin: 16px 0; }
.disclaimer h3 { font-size: 14px; font-weight: 700; color: var(--text-secondary); margin-bottom: 10px; }
.disclaimer p { font-size: 12px; color: var(--text-tertiary); line-height: 1.8; margin-bottom: 6px; }
.disclaimer .disclaimer-tag { display: inline-block; background: rgba(198,40,40,0.08); color: var(--signal-red); font-size: 11px; font-weight: 600; padding: 2px 10px; border-radius: 10px; margin-bottom: 8px; }
footer { text-align: center; padding: 24px 0 32px; color: var(--text-secondary); font-size: 12px; }
@media (max-width: 600px) { header h1 { font-size: 22px; } .signal-card .signal-header { padding: 12px 16px 0; } .signal-card .signal-body { padding: 10px 16px 14px; } header .report-meta { flex-direction: column; gap: 4px; } }
"""

# ── JS ──────────────────────────────────────────────────────────
JS = """
function toggleTheme(){var h=document.documentElement,b=document.getElementById('themeToggle');if(h.classList.contains('dark')){h.classList.remove('dark');h.classList.add('light');b.innerHTML='\\u263E';localStorage.setItem('theme','light');}else{h.classList.remove('light');h.classList.add('dark');b.innerHTML='\\u2600';localStorage.setItem('theme','dark');}}
(function(){var s=localStorage.getItem('theme');if(s==='dark'){document.documentElement.classList.add('dark');document.getElementById('themeToggle').innerHTML='\\u2600';}else if(s==='light'){document.documentElement.classList.add('light');}})();
function scrollToTop(){window.scrollTo({top:0,behavior:'smooth'});}
window.addEventListener('scroll',function(){var bt=document.getElementById('backToTop');if(window.scrollY>400){bt.classList.add('visible');}else{bt.classList.remove('visible');}});
"""


def escape_html(text):
    """Escape HTML special chars but keep the text readable."""
    return html.escape(text).replace("&#x27;", "'").replace("&quot;", '"')


def md_table_to_html(table_lines):
    """Convert markdown table lines to HTML table string."""
    if not table_lines:
        return ""

    rows = []
    for line in table_lines:
        line = line.strip()
        if line.startswith("|"):
            line = line[1:]
        if line.endswith("|"):
            line = line[:-1]
        cells = [c.strip() for c in line.split("|")]
        rows.append(cells)

    # Skip separator row (contains --- or :)
    data_rows = []
    header = rows[0] if rows else []
    for r in rows[1:]:
        if all(re.match(r'^[-:]+$', c) for c in r if c):
            continue
        data_rows.append(r)

    html_parts = ['<table class="signal-table">']
    # Header
    html_parts.append("<thead><tr>")
    for h in header:
        html_parts.append(f"<th>{escape_html(h)}</th>")
    html_parts.append("</tr></thead>")
    # Body
    html_parts.append("<tbody>")
    for r in data_rows:
        html_parts.append("<tr>")
        for c in r:
            html_parts.append(f"<td>{escape_html(c)}</td>")
        html_parts.append("</tr>")
    html_parts.append("</tbody></table>")
    return "\n".join(html_parts)


def parse_md_content(md_text):
    """Parse the old-version markdown into structured sections."""
    lines = md_text.split("\n")
    sections = []
    current_section = None
    in_table = False
    table_lines = []
    plain_talk_lines = []
    other_lines = []

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Detect section headers (## **1. xxx or ## **一、xxx or **1. xxx etc.)
        header_match = re.match(r'^(?:#{1,3}\s+)?\*{0,2}([\d一二三四五六七八九十]+[、.．]\s*.+?)\*{0,2}\s*$', stripped)

        # Check if this is a top-level heading like ## **一句话总结** or **二、历史预测回测验证**
        if stripped.startswith("##") or (stripped.startswith("**") and header_match):
            # Save current section
            if current_section:
                if in_table and table_lines:
                    current_section["tables"].append(md_table_to_html(table_lines))
                    table_lines = []
                    in_table = False
                if plain_talk_lines:
                    current_section["plain_talk"] = "\n".join(plain_talk_lines)
                    plain_talk_lines = []
                if other_lines:
                    current_section["other_text"] = "\n".join(other_lines)
                    other_lines = []
                sections.append(current_section)

            # Extract title
            title = stripped.lstrip("#").strip().strip("*").strip()
            current_section = {
                "title": title,
                "tables": [],
                "plain_talk": "",
                "other_text": "",
            }
            in_table = False
            table_lines = []
            plain_talk_lines = []
            other_lines = []
            continue

        if current_section is None:
            # Lines before first section (title, date, subtitle)
            continue

        # Check for table
        if stripped.startswith("|"):
            if not in_table:
                # Save any accumulated plain talk or other text first
                if plain_talk_lines:
                    current_section["plain_talk"] = "\n".join(plain_talk_lines)
                    plain_talk_lines = []
                if other_lines:
                    current_section["other_text"] = "\n".join(other_lines)
                    other_lines = []
                in_table = True
                table_lines = []
            table_lines.append(stripped)
            continue
        else:
            if in_table:
                # End of table
                current_section["tables"].append(md_table_to_html(table_lines))
                table_lines = []
                in_table = False

        # Check for plain talk (大白话)
        if "大白话" in stripped:
            plain_talk_lines.append(stripped)
            continue

        # Source notes (lines starting with > or containing 来源)
        if stripped.startswith(">") or stripped.startswith("\\>"):
            current_section["source_note"] = stripped.lstrip("\\>").strip()
            continue

        # Other text (央行动向, etc.)
        if stripped and not stripped.startswith("AI生成") and not stripped.startswith("AIGC"):
            other_lines.append(stripped)

    # Save last section
    if current_section:
        if in_table and table_lines:
            current_section["tables"].append(md_table_to_html(table_lines))
        if plain_talk_lines:
            current_section["plain_talk"] = "\n".join(plain_talk_lines)
        if other_lines:
            current_section["other_text"] = "\n".join(other_lines)
        sections.append(current_section)

    return sections


def extract_oneline_summary(md_text):
    """Extract the one-line summary from the markdown."""
    # Look for 一句话总结 section
    match = re.search(r'(?:一句话总结|综合判断.*?一句话总结)[：:】\s]*\n*(.+?)(?:\n\n|\n##|\n\*\*[二三四五六七八九十]|\Z)', md_text, re.DOTALL)
    if match:
        text = match.group(1).strip()
        # Clean up markdown formatting
        text = re.sub(r'\*+', '', text)
        text = text.replace("\n", " ").strip()
        if len(text) > 500:
            text = text[:500] + "..."
        return text

    # Fallback: first paragraph after the date line
    lines = md_text.split("\n")
    for i, line in enumerate(lines):
        if "一句话总结" in line:
            # Get next non-empty line
            for j in range(i+1, min(i+5, len(lines))):
                t = lines[j].strip()
                if t and not t.startswith("##") and not t.startswith("**"):
                    return t[:500]

    return "详见正文"


def render_section_html(section):
    """Render a parsed section as HTML."""
    title = section["title"]
    html_parts = []

    # Determine if this is a numbered signal section
    num_match = re.match(r'^[\d]+[、.．]\s*', title)

    if num_match:
        num = num_match.group(0).strip().rstrip("、.．")
        clean_title = title[num_match.end():].strip()
        html_parts.append('<div class="signal-card">')
        html_parts.append(f'  <div class="signal-header">')
        html_parts.append(f'    <span class="signal-num">{escape_html(num)}</span>')
        html_parts.append(f'    <span class="signal-title">{escape_html(clean_title)}</span>')
        html_parts.append('  </div>')
        html_parts.append('  <div class="signal-body">')

        for table_html in section["tables"]:
            html_parts.append(table_html)

        if section["plain_talk"]:
            pt = section["plain_talk"]
            # Remove "大白话：" prefix if present (handle **大白话：** and 大白话：** etc.)
            pt = re.sub(r'^\*{0,2}大白话\*{0,2}[：:]\s*', '', pt)
            pt = re.sub(r'^大白话[：:]\s*', '', pt)
            pt = re.sub(r'\*+', '', pt).strip()
            html_parts.append(f'<div class="plain-talk"><span class="plain-label">大白话：</span>{escape_html(pt)}</div>')

        if section["other_text"]:
            other = section["other_text"]
            other = re.sub(r'\*{0,2}央行(动向|公开市场操作)[：:]\*{0,2}\s*', '<strong>央行动向：</strong>', other)
            other = re.sub(r'\*+', '', other)
            # Split by double newlines for paragraphs
            paras = [p.strip() for p in other.split("\n") if p.strip()]
            for p in paras:
                if p.startswith("<strong>"):
                    html_parts.append(f'<div class="plain-talk">{p}</div>')
                else:
                    html_parts.append(f'<div class="plain-talk">{escape_html(p)}</div>')

        if section.get("source_note"):
            html_parts.append(f'<div class="source-note">{escape_html(section["source_note"])}</div>')

        html_parts.append('  </div>')
        html_parts.append('</div>')
    else:
        # Non-numbered section (一句话总结, 回测, 综合判断, 来源清单, etc.)
        lower_title = title.lower()

        if "回测" in title or "预测" in title:
            html_parts.append('<div class="backtest-card">')
            html_parts.append(f'  <div class="backtest-header">{escape_html(title)}</div>')

            for table_html in section["tables"]:
                # Wrap in backtest-detail
                html_parts.append(f'  <div class="backtest-item"><div class="backtest-detail">{table_html}</div></div>')

            if section["plain_talk"]:
                pt = re.sub(r'\*+', '', section["plain_talk"]).strip()
                html_parts.append(f'  <div class="backtest-item"><div class="backtest-detail">{escape_html(pt)}</div></div>')

            if section["other_text"]:
                other = re.sub(r'\*+', '', section["other_text"]).strip()
                paras = [p.strip() for p in other.split("\n") if p.strip()]
                for p in paras:
                    html_parts.append(f'  <div class="backtest-item"><div class="backtest-detail">{escape_html(p)}</div></div>')

            html_parts.append('</div>')

        elif "综合判断" in title or "信号综合" in title or "一句话总结" in title:
            html_parts.append('<div class="summary-card">')
            html_parts.append(f'  <div class="summary-header">{escape_html(title)}</div>')

            for table_html in section["tables"]:
                html_parts.append(table_html)

            if section["plain_talk"]:
                pt = re.sub(r'\*+', '', section["plain_talk"]).strip()
                html_parts.append(f'<div class="plain-talk"><span class="plain-label">大白话：</span>{escape_html(pt)}</div>')

            if section["other_text"]:
                other = re.sub(r'\*+', '', section["other_text"]).strip()
                paras = [p.strip() for p in other.split("\n") if p.strip()]
                for p in paras:
                    lines_list = p.split("\n")
                    for ll in lines_list:
                        ll = ll.strip()
                        if ll:
                            html_parts.append(f'<div class="plain-talk">{escape_html(ll)}</div>')

            html_parts.append('</div>')

        elif "来源" in title or "数据来源" in title:
            html_parts.append('<div class="source-summary">')
            html_parts.append(f'  <div class="ss-header">{escape_html(title)}</div>')

            for table_html in section["tables"]:
                html_parts.append(table_html)

            if section["other_text"]:
                other = re.sub(r'\*+', '', section["other_text"]).strip()
                paras = [p.strip() for p in other.split("\n") if p.strip()]
                for p in paras:
                    html_parts.append(f'<div style="padding:8px 18px;font-size:12px;color:var(--text-secondary);">{escape_html(p)}</div>')

            html_parts.append('</div>')

        elif "本周关注" in title or "关注清单" in title:
            html_parts.append('<div class="summary-card">')
            html_parts.append(f'  <div class="summary-header">{escape_html(title)}</div>')

            for table_html in section["tables"]:
                html_parts.append(table_html)

            html_parts.append('</div>')

        else:
            # Generic card for any other section
            html_parts.append('<div class="signal-card">')
            html_parts.append(f'  <div class="signal-header"><span class="signal-title">{escape_html(title)}</span></div>')
            html_parts.append('  <div class="signal-body">')

            for table_html in section["tables"]:
                html_parts.append(table_html)

            if section["plain_talk"]:
                pt = re.sub(r'\*+', '', section["plain_talk"]).strip()
                html_parts.append(f'<div class="plain-talk"><span class="plain-label">大白话：</span>{escape_html(pt)}</div>')

            if section["other_text"]:
                other = re.sub(r'\*+', '', section["other_text"]).strip()
                paras = [p.strip() for p in other.split("\n") if p.strip()]
                for p in paras:
                    html_parts.append(f'<div class="plain-talk">{escape_html(p)}</div>')

            html_parts.append('  </div>')
            html_parts.append('</div>')

    return "\n".join(html_parts)


def generate_html(report):
    """Generate a complete HTML file for one report."""
    md_path = os.path.join(DOCS_DIR, report["md_file"])
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    sections = parse_md_content(md_text)
    oneline = extract_oneline_summary(md_text)

    # Build body
    body_parts = []

    # Header
    body_parts.append('<header>')
    body_parts.append(f'  <h1>每日金融信号日报</h1>')
    body_parts.append(f'  <p class="subtitle">{escape_html(report["date_str"])} · 11项快变量信号 · 大白话解读</p>')
    body_parts.append(f'  <div class="report-meta">')
    body_parts.append(f'    <span>{escape_html(report["version"])}</span>')
    body_parts.append(f'    <span>{escape_html(report["subtitle"])}</span>')
    body_parts.append(f'  </div>')
    body_parts.append(f'  <div class="version-badge">旧版日报（v1.0格式）</div>')
    body_parts.append('</header>')

    # Main quote (one-line summary)
    body_parts.append('<div class="main-quote">')
    body_parts.append(f'  <div class="quote-text">{escape_html(oneline)}</div>')
    body_parts.append('</div>')

    # Render all sections
    for section in sections:
        body_parts.append(render_section_html(section))

    # Disclaimer
    body_parts.append('<div class="disclaimer">')
    body_parts.append('  <h3>免责声明</h3>')
    body_parts.append('  <div class="disclaimer-tag">不构成投资建议</div>')
    body_parts.append('  <p>本报告数据均来自公开渠道，经过多源交叉验证。置信度标注：✅已验证=2个及以上独立来源一致或直接来自官方原始发布。</p>')
    body_parts.append('  <p>本报告内容仅供信息参考和学习交流使用，不构成任何投资建议。金融市场有风险，投资需谨慎。</p>')
    body_parts.append(f'  <p>报告版本：{escape_html(report["version"])} · 制作日期 {escape_html(report["date_str"][:5] + report["date_str"][5:])}</p>')
    body_parts.append('</div>')

    # Footer
    body_parts.append(f'<footer>每日金融信号日报 · {escape_html(report["version"])} · 信源可追溯 · 制作日期 {escape_html(report["date_short"])}</footer>')

    # Assemble full HTML
    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>每日金融信号日报 - {report['date_str']}</title>
<style>
{CSS}
</style>
</head>
<body>
<button class="theme-toggle" id="themeToggle" onclick="toggleTheme()" title="切换明暗模式">&#9790;</button>
<button class="back-to-top" id="backToTop" onclick="scrollToTop()" title="回到顶部">&#9650;</button>
<div class="page-layout">
{''.join(body_parts)}
</div>
<script>
{JS}
</script>
</body>
</html>"""

    # Write to archives
    archive_dir = os.path.join(ARCHIVES_DIR, report["archive_dir"])
    os.makedirs(archive_dir, exist_ok=True)
    html_path = os.path.join(archive_dir, report["html_filename"])
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    return html_path


def main():
    print("=" * 60)
    print("旧版日报 MD → HTML 转换工具")
    print("=" * 60)

    for report in REPORTS:
        print(f"\n处理: {report['md_file']} → {report['html_filename']}")
        try:
            html_path = generate_html(report)
            size = os.path.getsize(html_path)
            print(f"  ✓ 已生成: {html_path} ({size:,} bytes)")
        except Exception as e:
            print(f"  ✗ 失败: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print("转换完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
