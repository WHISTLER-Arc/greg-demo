#!/usr/bin/env python3
"""Build index.html for the Greg demo from a checkout of the Greg repo.

    python build.py --greg ../Greg

Everything Greg-specific comes from that checkout, so the demo never drifts
from the real thing: his line pools (all languages), the sidebar panel
(greg-panel.js, embedded unmodified), the four mood images and the version.

The only thing it cannot regenerate is Alan's voice. English lines are matched
to clips by their exact text through clips/manifest.json. A line with no clip
still works, it just speaks in the visitor's browser voice until the next clip
run (see tools/README.md). The build prints how many lines that is.
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MOODS = ("resting", "annoyed", "judging", "existential")


def load_lines(greg: Path) -> dict:
    comp = greg / "custom_components" / "greg"
    sys.path.insert(0, str(comp))
    try:
        import lines  # Greg's own package, so pools come out exactly as he sees them
    finally:
        sys.path.pop(0)
    return {
        code: {"name": mod.LANGUAGE_NAME, "openers": list(mod.OPENERS),
               "pools": {k: list(v) for k, v in mod.POOLS.items()}}
        for code, mod in lines.LANGUAGES.items()
    }


def load_version(greg: Path) -> str:
    const = (greg / "custom_components" / "greg" / "const.py").read_text(encoding="utf-8")
    m = re.search(r'^VERSION_DISPLAY = "([^"]+)"', const, re.M)
    return m.group(1) if m else "v?"


def load_images(greg: Path) -> dict:
    from PIL import Image  # pip install pillow
    out = {}
    for mood in MOODS:
        im = Image.open(greg / "www" / "greg" / f"greg_{mood}.png").convert("RGB")
        im.thumbnail((560, 560))
        buf = io.BytesIO()
        im.save(buf, "WEBP", quality=80)
        out[mood] = "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()
    return out


def write_social_images(greg: Path) -> None:
    """og.png for link previews (forum, chat apps) and a small favicon."""
    from PIL import Image
    src = Image.open(greg / "www" / "greg" / "greg_judging.png").convert("RGB")
    face = src.copy()
    face.thumbnail((630, 630))
    # Stretch the outermost pixel columns sideways so the square art blends
    # into a wide card without a visible seam.
    x0 = (1200 - face.width) // 2
    card = Image.new("RGB", (1200, 630))
    card.paste(face.crop((0, 0, 1, face.height)).resize((x0, face.height)), (0, 0))
    card.paste(face.crop((face.width - 1, 0, face.width, face.height)).resize((1200 - x0 - face.width, face.height)), (x0 + face.width, 0))
    card.paste(face, (x0, 0))
    card.save(HERE / "og.png", optimize=True)
    icon = src.copy()
    icon.thumbnail((128, 128))
    icon.save(HERE / "icon.png", optimize=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--greg", required=True, type=Path, help="path to a Greg repo checkout")
    args = ap.parse_args()
    greg = args.greg.resolve()

    lines = load_lines(greg)
    manifest = json.loads((HERE / "clips" / "manifest.json").read_text(encoding="utf-8"))
    en = lines["en"]
    spoken = [l for p in en["pools"].values() for l in p] + en["openers"]
    clips = {t: p for t, p in manifest.get("en", {}).items()
             if t in set(spoken) and (HERE / p).exists()}
    missing = [t for t in spoken if t not in clips]

    panel = (greg / "custom_components" / "greg" / "panel" / "greg-panel.js").read_text(encoding="utf-8")
    version = load_version(greg)

    page = (HERE / "template.html").read_text(encoding="utf-8")
    compact = dict(ensure_ascii=False, separators=(",", ":"))
    page = (page
            .replace("%%BUILT_NOTE%%", f"<!-- Built by build.py from template.html against Greg {version}. Edit the template, not this file. -->")
            .replace("%%LINES%%", json.dumps(lines, **compact))
            .replace("%%IMGS%%", json.dumps(load_images(greg), **compact))
            .replace("%%CLIPS%%", json.dumps(clips, **compact))
            .replace("%%VERSION%%", version)
            .replace("%%PANEL_JS%%", panel))
    if "%%" in page.replace("%%'", ""):
        leftover = re.findall(r"%%[A-Z_]+%%", page)
        if leftover:
            print("unfilled placeholders:", leftover, file=sys.stderr)
            return 1
    (HERE / "index.html").write_text(page, encoding="utf-8")
    write_social_images(greg)

    unused = len(manifest.get("en", {})) - len(clips)
    print(f"Greg {version}: {sum(len(p) for l in lines.values() for p in l['pools'].values())} lines in {len(lines)} languages")
    print(f"Alan clips: {len(clips)} of {len(spoken)} English lines and openers")
    if missing:
        print(f"{len(missing)} English line(s) have no clip yet and will use the browser voice:")
        for t in missing[:10]:
            print("  -", t[:90])
    if unused:
        print(f"{unused} clip(s) belong to lines that no longer exist. Harmless; remove them on the next clip run.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
