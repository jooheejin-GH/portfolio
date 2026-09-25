"""Capture cover screenshots from the mock-data demos for jobs that have no real screenshot.

Usage: python3 scripts/shoot_demos.py [--force] [slug ...]
Writes docs/shots/<slug>.jpg (1440x900). Skips slugs that already have a shot unless --force.
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
DEMO = ROOT / "docs/demo"
SHOTS = ROOT / "docs/shots"

args = [a for a in sys.argv[1:] if not a.startswith("--")]
force = "--force" in sys.argv
slugs = args or sorted(p.name for p in DEMO.iterdir() if (p / "index.html").exists())

with sync_playwright() as p:
    browser = p.chromium.launch()
    for slug in slugs:
        out = SHOTS / f"{slug}.jpg"
        if out.exists() and not force:
            print(f"skip {slug} (has shot)")
            continue
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto((DEMO / slug / "index.html").as_uri())
        page.wait_for_timeout(1200)
        page.screenshot(path=str(out), type="jpeg", quality=80)
        page.close()
        print(f"shot {slug}")
    browser.close()
