"""Build site/index.html from data/jobs.public.json + data/profile.json + site/shots/.

Screenshots: put files in site/shots/ named <slug>.png|jpg|webp (cover) and
<slug>-2.png, <slug>-3.png ... for extra images.
"""
import json, re, html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
jobs = json.loads((ROOT / "data/jobs.public.json").read_text())
prof = json.loads((ROOT / "data/profile.json").read_text())
shots_dir = ROOT / "site/shots"

LEAK = re.compile(r"https?://|seacon\.ai|seacon-dev|192\.168|192\.132|\(ผู้ใช้:")

def shots_for(slug):
    files = [p for p in shots_dir.glob(f"{slug}*") if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")
             and re.fullmatch(rf"{re.escape(slug)}(-\d+)?", p.stem)]
    files.sort(key=lambda p: int(p.stem.rsplit("-", 1)[1]) if p.stem != slug else 0)
    return [f"shots/{p.name}" for p in files]

for j in jobs:
    j["shots"] = shots_for(j["slug"])
    blob = json.dumps(j, ensure_ascii=False)
    if LEAK.search(blob):
        raise SystemExit(f"leak check failed in {j['slug']}: {LEAK.search(blob).group(0)}")

years = sorted({j["year"] for j in jobs})
out = (ROOT / "template.html").read_text()
for k, v in {
    "__NAME__": prof["name"], "__ROLE__": prof["role"], "__HEADLINE__": prof["headline"],
    "__LEAD__": prof["lead"], "__FOOTER__": prof["footer"], "__COUNT__": str(len(jobs)),
    "__SPAN__": f"{years[0]}–{years[-1]}" if len(years) > 1 else str(years[0]),
}.items():
    out = out.replace(k, html.escape(v))
out = out.replace("__JOBS__", json.dumps(jobs, ensure_ascii=False).replace("</", "<\\/"))
(ROOT / "site/index.html").write_text(out)
print(f"built site/index.html · {len(jobs)} jobs · {sum(bool(j['shots']) for j in jobs)} with screenshots")
