# Refreshing Alan's voice

Greg's English lines are pre-rendered in Piper's `en_GB-alan-medium` voice,
because that is the voice he was written for and browsers cannot produce it.
When English lines are added or reworded in the Greg repo, the demo keeps
working: those lines play in the visitor's browser voice until the clips are
refreshed. `build.py` lists which lines are missing a clip.

To refresh:

1. Open your Home Assistant in a browser and log in. It needs the Piper
   add-on with the Alan voice, which Greg's README already recommends.
2. Press F12, open **Console**, paste all of `render-clips.js`, press Enter.
   About five minutes later `greg-alan-clips.zip` lands in your downloads.
3. `python tools/import_clips.py path/to/greg-alan-clips.zip`
4. Commit `en/` and `clips/manifest.json`. The site rebuilds on push.
