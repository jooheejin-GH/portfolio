"""Render mock cover images for LINE-bot and automation jobs.

Reads data/mock_line.json and data/mock_sheet.json, renders each entry as HTML
and screenshots it to docs/shots/<slug>.jpg (1440x800). Existing real/demo
shots are kept unless --force.

Usage: python3 scripts/mock_render.py [--force] [slug ...]
"""
import html
import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "docs/shots"
W, H = 1440, 800
esc = lambda s: html.escape(str(s))

BASE_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Anuphan:wght@400;500;600;700&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
body{width:1440px;height:800px;overflow:hidden;font-family:Anuphan,sans-serif;color:#16181d}
"""

IMG_ICONS = {
    "slip": ("สลิปโอนเงิน", '<rect x="14" y="6" width="36" height="52" rx="4"/><path d="M22 18h20M22 26h20M22 34h12"/><circle cx="40" cy="46" r="5"/>'),
    "receipt": ("ใบเสร็จ", '<path d="M16 6h32v52l-5-4-5 4-6-4-6 4-5-4-5 4z"/><path d="M24 18h16M24 26h16M24 34h10"/>'),
    "parcel": ("รูปพัสดุ", '<path d="M8 20l24-12 24 12v26L32 58 8 46z"/><path d="M8 20l24 12 24-12M32 32v26"/>'),
    "cheque": ("รูปเช็ค", '<rect x="4" y="16" width="56" height="32" rx="3"/><path d="M12 26h24M12 34h14M42 38h12"/>'),
    "photo": ("รูปภาพ", '<rect x="6" y="12" width="52" height="40" rx="4"/><circle cx="22" cy="26" r="5"/><path d="M6 46l16-14 12 10 8-6 16 12"/>'),
    "qr": ("QR Code", '<rect x="8" y="8" width="18" height="18"/><rect x="38" y="8" width="18" height="18"/><rect x="8" y="38" width="18" height="18"/><path d="M38 38h6v6h-6zM50 38h6M38 50h6v6M50 50h6v6"/>'),
}
ACCENT = {"green": "#06c755", "blue": "#1f5eff", "orange": "#f97316", "red": "#e5484d", "purple": "#7c5cff"}


def line_html(slug, d):
    msgs = []
    for m in d["messages"]:
        side = "me" if m["from"] == "user" else "bot"
        if "text" in m:
            inner = f'<div class="bub">{esc(m["text"])}</div>'
        elif "image" in m:
            label, svg = IMG_ICONS.get(m["image"], IMG_ICONS["photo"])
            inner = f'<div class="img"><svg viewBox="0 0 64 64" fill="none" stroke="#7a8595" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round">{svg}</svg><span>{label}</span></div>'
        else:
            c = m["card"]
            acc = ACCENT.get(c.get("accent", "green"), "#06c755")
            rows = "".join(f'<div class="r"><span>{esc(a)}</span><b>{esc(b)}</b></div>' for a, b in c.get("rows", []))
            btn = f'<div class="btn" style="color:{acc}">{esc(c["button"])}</div>' if c.get("button") else ""
            sub = f'<div class="sub">{esc(c["subtitle"])}</div>' if c.get("subtitle") else ""
            inner = f'<div class="card"><div class="ch" style="background:{acc}"><div class="t">{esc(c["title"])}</div>{sub}</div><div class="cb">{rows}</div>{btn}</div>'
        av = '<div class="av"></div>' if side == "bot" else ""
        msgs.append(f'<div class="m {side}">{av}{inner}</div>')
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}
body{{background:radial-gradient(1200px 700px at 20% 10%,#e7f8ee,#cfeedd 45%,#a9dfc2)}}
.blob{{position:absolute;border-radius:50%;filter:blur(2px);opacity:.55}}
.phone{{position:absolute;left:50%;top:48px;transform:translateX(-50%);width:470px;height:900px;border-radius:56px;background:#0e1116;padding:14px;box-shadow:0 40px 80px rgba(10,40,25,.35)}}
.scr{{width:100%;height:100%;border-radius:44px;overflow:hidden;background:#8ca8d4;display:flex;flex-direction:column}}
.top{{background:#2b3645;color:#fff;padding:40px 22px 14px;display:flex;align-items:center;gap:12px;font-weight:600;font-size:19px}}
.top .ic{{width:34px;height:34px;border-radius:50%;background:#06c755;display:grid;place-items:center;font-size:13px;font-weight:700}}
.chat{{padding:16px 14px;display:flex;flex-direction:column;gap:12px}}
.m{{display:flex;align-items:flex-end;gap:8px}}
.m.me{{justify-content:flex-end}}
.av{{width:34px;height:34px;border-radius:50%;background:#06c755;flex:none;border:2px solid #fff}}
.bub{{max-width:300px;padding:10px 14px;border-radius:20px;font-size:17px;line-height:1.45;background:#fff}}
.me .bub{{background:#8de055}}
.img{{width:180px;height:150px;border-radius:16px;background:#eef1f5;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;color:#5d6775;font-size:14px}}
.img svg{{width:64px;height:64px}}
.card{{width:318px;border-radius:18px;background:#fff;overflow:hidden;box-shadow:0 2px 6px rgba(0,0,0,.08)}}
.ch{{padding:12px 16px;color:#fff}} .ch .t{{font-weight:700;font-size:18px}} .ch .sub{{font-size:14px;opacity:.9}}
.cb{{padding:10px 16px}} .r{{display:flex;justify-content:space-between;gap:10px;font-size:15px;padding:5px 0;border-bottom:1px solid #eef0f3}}
.r:last-child{{border:0}} .r span{{color:#6b7280}} .r b{{font-weight:600;text-align:right}}
.btn{{border-top:1px solid #eef0f3;text-align:center;padding:10px;font-weight:600;font-size:16px}}
</style></head><body>
<div class="blob" style="width:380px;height:380px;left:120px;top:380px;background:#8fdcb2"></div>
<div class="blob" style="width:300px;height:300px;right:160px;top:60px;background:#bff0d3"></div>
<div class="phone"><div class="scr"><div class="top"><div class="ic">LINE</div>{esc(d["bot"])}</div><div class="chat">{"".join(msgs)}</div></div></div>
</body></html>"""


CHIP = {"green": ("#dcfce7", "#166534"), "orange": ("#ffedd5", "#9a3412"), "red": ("#fee2e2", "#991b1b"),
        "blue": ("#dbeafe", "#1e40af"), "gray": ("#f1f5f9", "#475569")}


def sheet_html(slug, d):
    cols = d["columns"]
    align = d.get("align") or ["l"] * len(cols)
    sc = d.get("status_col")
    colors = d.get("status_colors", {})
    letters = "ABCDEFGHIJ"
    head = '<tr><th class="rn"></th>' + "".join(f'<th class="cl">{letters[i]}</th>' for i in range(len(cols))) + "</tr>"
    hdr = '<tr class="hd"><td class="rn">1</td>' + "".join(f'<td class="{a}">{esc(c)}</td>' for c, a in zip(cols, align)) + "</tr>"
    body = ""
    for i, row in enumerate(d["rows"][:10]):
        cells = ""
        for j, (v, a) in enumerate(zip(row, align)):
            if j == sc:
                bg, fg = CHIP.get(colors.get(v, "gray"), CHIP["gray"])
                v = f'<span class="chip" style="background:{bg};color:{fg}">{esc(v)}</span>'
            else:
                v = esc(v)
            cells += f'<td class="{a}">{v}</td>'
        body += f'<tr><td class="rn">{i + 2}</td>{cells}</tr>'
    tabs = "".join(f'<span class="tab{" on" if k == 0 else ""}">{esc(t)}</span>' for k, t in enumerate(d["tabs"]))
    flow = '<span class="arr">→</span>'.join(f'<span class="fc">{esc(f)}</span>' for f in d["flow"])
    summ = "".join(f'<span class="kp"><small>{esc(a)}</small><b>{esc(b)}</b></span>' for a, b in d.get("summary", []))
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}
body{{background:radial-gradient(1200px 700px at 80% 0%,#fff4e0,#fde2b8 50%,#f6c98a)}}
.wrap{{position:absolute;left:90px;right:90px;top:40px}}
.bar{{display:flex;align-items:center;gap:10px;margin-bottom:18px;flex-wrap:wrap}}
.fc{{background:#fff;border:1px solid rgba(0,0,0,.08);border-radius:999px;padding:7px 16px;font-weight:600;font-size:17px;box-shadow:0 2px 6px rgba(120,70,0,.08)}}
.arr{{color:#b45309;font-weight:700;font-size:20px}}
.kps{{margin-left:auto;display:flex;gap:10px}}
.kp{{background:#16181d;color:#fff;border-radius:12px;padding:6px 14px;display:flex;flex-direction:column;line-height:1.25}}
.kp small{{font-size:12px;opacity:.7}} .kp b{{font-size:18px}}
.win{{background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 30px 70px rgba(120,70,0,.25)}}
.tb{{display:flex;align-items:center;gap:12px;padding:12px 18px;border-bottom:1px solid #e5e7eb}}
.ico{{width:26px;height:32px;border-radius:4px;background:#0f9d58;position:relative}}
.ico:after{{content:"";position:absolute;inset:9px 6px;border:2px solid #fff;border-radius:1px}}
.fn{{font-size:18px;font-weight:600}}
.menu{{display:flex;gap:18px;padding:4px 18px 10px 56px;font-size:14px;color:#4b5563;border-bottom:1px solid #e5e7eb}}
table{{border-collapse:collapse;width:100%;font-size:15px;table-layout:fixed}}
th.cl{{background:#f8f9fa;color:#6b7280;font-weight:500;font-size:12px;height:24px;border:1px solid #e5e7eb}}
.rn{{width:44px;background:#f8f9fa;color:#6b7280;text-align:center;font-size:12px;border:1px solid #e5e7eb}}
td{{border:1px solid #edf0f2;padding:0 10px;height:38px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
tr.hd td{{background:#fef3c7;font-weight:700}}
td.r{{text-align:right;font-variant-numeric:tabular-nums}} td.c{{text-align:center}}
.chip{{border-radius:999px;padding:2px 10px;font-size:13px;font-weight:600}}
.tabs{{display:flex;gap:4px;padding:8px 12px;background:#f8f9fa;border-top:1px solid #e5e7eb}}
.tab{{padding:5px 14px;border-radius:6px;font-size:14px;color:#4b5563}} .tab.on{{background:#e6f4ea;color:#137333;font-weight:600}}
</style></head><body><div class="wrap">
<div class="bar">{flow}<div class="kps">{summ}</div></div>
<div class="win"><div class="tb"><div class="ico"></div><div class="fn">{esc(d["file"])}</div></div>
<div class="menu"><span>ไฟล์</span><span>แก้ไข</span><span>ดู</span><span>แทรก</span><span>รูปแบบ</span><span>ข้อมูล</span><span>ส่วนขยาย</span></div>
<table>{head}{hdr}{body}</table><div class="tabs">{tabs}</div></div>
</div></body></html>"""


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    force = "--force" in sys.argv
    jobs = []
    for fname, fn in (("mock_line.json", line_html), ("mock_sheet.json", sheet_html)):
        p = ROOT / "data" / fname
        if p.exists():
            jobs += [(slug, d, fn) for slug, d in json.loads(p.read_text()).items()]
    real = {p.stem.rsplit("-", 1)[0] if p.stem[-2:-1] == "-" and p.stem[-1].isdigit() else p.stem
            for p in SHOTS.glob("*.jpg")}
    marker = ROOT / "data/mock_shots.json"
    mocked = set(json.loads(marker.read_text())) if marker.exists() else set()
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H})
        for slug, d, fn in jobs:
            if args and slug not in args:
                continue
            if slug in real and slug not in mocked and not force:
                continue  # keep real/demo screenshots
            pg.set_content(fn(slug, d))
            pg.wait_for_timeout(250)
            pg.evaluate("document.fonts.ready")
            pg.screenshot(path=str(SHOTS / f"{slug}.jpg"), type="jpeg", quality=82)
            mocked.add(slug)
            print("mock", slug)
        b.close()
    marker.write_text(json.dumps(sorted(mocked), indent=0))


if __name__ == "__main__":
    main()
