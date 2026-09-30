# Meet Greg

**Try it: https://whistler-arc.github.io/greg-demo/**

A try-before-you-install demo of [Greg](https://github.com/WHISTLER-Arc/Greg),
the Home Assistant integration that gives your coffee table feelings. Mostly
bad ones.

Poke the table, put a mug down, fill the room, and watch him go from resting to
existential. Underneath is his real sidebar panel running against a pretend
Home Assistant, so you can change his settings and write him lines before he
is anywhere near your house. In English he speaks with Piper's Alan voice, the
voice he was written for.

## How it stays honest

Nothing about Greg is copied by hand into this repo. `build.py` reads a
checkout of the Greg repo and embeds his line pools, his mood images and his
panel (`greg-panel.js`, unmodified). His reactions use the same thresholds,
timings and shuffled deck as the integration, ported from `__init__.py`. Two
timers are shortened so a visitor sees them: 20 minutes of silence becomes 20
seconds, and the 42 minute brood is a button.

The site rebuilds from Greg's `main` on every push here, weekly, and on demand
from the Actions tab.

## Building locally

    git clone https://github.com/WHISTLER-Arc/Greg ../Greg
    pip install pillow
    python build.py --greg ../Greg

Then open `index.html`, or serve the folder with `python -m http.server` so the
voice clips load.

Refreshing the voice clips is covered in [tools/README.md](tools/README.md).

---

By WHISTLER & Arc. MIT licensed, like Greg.
