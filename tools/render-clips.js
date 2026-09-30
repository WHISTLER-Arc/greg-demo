// Renders every English line and opener in Piper's en_GB Alan voice and saves
// them as greg-alan-clips.zip. Run it in your browser, on your own Home
// Assistant, while logged in: open any HA page, press F12, go to Console,
// paste this whole file and press Enter. Takes about five minutes.
//
// Nothing is sent anywhere except your own HA. Lines are read from the Greg
// repo on GitHub so the clips always match what Greg actually says.
(async () => {
  const ENGINE = "tts.piper", LANG = "en_GB", VOICE = "en_GB-alan-medium";
  const ha = document.querySelector("home-assistant");
  if (!ha || !ha.hass) return console.error("Open a Home Assistant page and log in first.");
  const hass = ha.hass;
  const src = await (await fetch("https://raw.githubusercontent.com/WHISTLER-Arc/Greg/main/custom_components/greg/lines/en.py")).text();
  const grab = n => { const m = src.match(new RegExp(n + "\\s*=\\s*\\[([\\s\\S]*?)\\n\\]")); return [...m[1].matchAll(/"((?:[^"\\]|\\.)*)"/g)].map(x => JSON.parse('"' + x[1] + '"')); };
  const POOLS = { soft: "LINES_SOFT", medium: "LINES_MEDIUM", chaos: "LINES_CHAOS", existential: "LINES_EXISTENTIAL", silence: "LINES_SILENCE", openers: "OPENERS" };
  const items = [];
  for (const [k, n] of Object.entries(POOLS)) grab(n).forEach((t, i) => items.push({ p: `en/${k}/${String(i).padStart(2, "0")}.mp3`, t }));

  const files = {}, manifest = {}, errors = [];
  let idx = 0, done = 0;
  const worker = async () => {
    while (idx < items.length) {
      const it = items[idx++];
      try {
        const q = new URLSearchParams({ message: it.t, language: LANG, voice: VOICE });
        const r = await hass.callWS({ type: "media_source/resolve_media", media_content_id: `media-source://tts/${ENGINE}?${q}` });
        const res = await fetch(r.url, { credentials: "same-origin" });
        if (!res.ok) throw new Error("HTTP " + res.status);
        files[it.p] = new Uint8Array(await res.arrayBuffer()); manifest[it.t] = it.p;
      } catch (e) { errors.push(`${it.p}: ${e && e.message || e}`); }
      if (++done % 25 === 0) console.log(`${done} of ${items.length}`);
    }
  };
  await Promise.all([worker(), worker()]);
  if (errors.length) console.warn(errors);

  // Minimal stored zip. MP3 is already compressed.
  const crcT = new Uint32Array(256).map((_, n) => { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1; return c >>> 0; });
  const crc = b => { let c = 0xFFFFFFFF; for (let i = 0; i < b.length; i++) c = crcT[(c ^ b[i]) & 255] ^ (c >>> 8); return (c ^ 0xFFFFFFFF) >>> 0; };
  const enc = new TextEncoder();
  const list = Object.entries(files).sort();
  list.push(["manifest.json", enc.encode(JSON.stringify(manifest, null, 1))]);
  const parts = [], central = []; let off = 0;
  for (const [name, data] of list) {
    const nb = enc.encode(name), c = crc(data);
    const h = new DataView(new ArrayBuffer(30));
    h.setUint32(0, 0x04034b50, true); h.setUint16(4, 20, true); h.setUint16(6, 0x0800, true);
    h.setUint32(14, c, true); h.setUint32(18, data.length, true); h.setUint32(22, data.length, true); h.setUint16(26, nb.length, true);
    parts.push(new Uint8Array(h.buffer), nb, data);
    const cd = new DataView(new ArrayBuffer(46));
    cd.setUint32(0, 0x02014b50, true); cd.setUint16(4, 20, true); cd.setUint16(6, 20, true); cd.setUint16(8, 0x0800, true);
    cd.setUint32(16, c, true); cd.setUint32(20, data.length, true); cd.setUint32(24, data.length, true); cd.setUint16(28, nb.length, true); cd.setUint32(42, off, true);
    central.push(new Uint8Array(cd.buffer), nb);
    off += 30 + nb.length + data.length;
  }
  const size = central.reduce((a, b) => a + b.length, 0);
  const e = new DataView(new ArrayBuffer(22));
  e.setUint32(0, 0x06054b50, true); e.setUint16(8, list.length, true); e.setUint16(10, list.length, true); e.setUint32(12, size, true); e.setUint32(16, off, true);
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([...parts, ...central, new Uint8Array(e.buffer)], { type: "application/zip" }));
  a.download = "greg-alan-clips.zip"; document.body.appendChild(a); a.click(); a.remove();
  console.log(`Done: ${Object.keys(files).length} clips, ${errors.length} errors. Saved greg-alan-clips.zip`);
})();
