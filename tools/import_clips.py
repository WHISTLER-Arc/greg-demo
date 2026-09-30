#!/usr/bin/env python3
"""Replace the English clips with a fresh greg-alan-clips.zip from render-clips.js.

    python tools/import_clips.py ~/Downloads/greg-alan-clips.zip

Re-encodes each clip to 32 kbps mono (plenty for speech, about 7.7 MB for the
full set instead of 18) and rewrites clips/manifest.json. Needs ffmpeg.
"""
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    with tempfile.TemporaryDirectory() as tmp, zipfile.ZipFile(sys.argv[1]) as z:
        z.extractall(tmp)
        manifest = json.loads((Path(tmp) / "manifest.json").read_text(encoding="utf-8"))
        shutil.rmtree(HERE / "en", ignore_errors=True)
        for text, rel in manifest.items():
            out = HERE / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(Path(tmp) / rel),
                            "-ac", "1", "-ar", "22050", "-b:a", "32k", str(out)], check=True)
    (HERE / "clips" / "manifest.json").write_text(
        json.dumps({"en": manifest}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Imported {len(manifest)} clips. Commit en/ and clips/manifest.json.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
