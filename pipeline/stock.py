"""Real photos and video clips on the boards (roadmap R1, 2026-11-21). Same file in both channels.

Board types in episode.json:
    {"type": "photo", "query": "saturn rings", "caption": "Saturn's rings", "cue": "rings", "icon": "🪐"}
    {"type": "clip",  "query": "earth from space station", "caption": "Our planet", "cue": "planet", "icon": "🌍"}
"art": "<name>" (optional) = our own realistic 3D picture (assets/art/<name>_landscape.jpg); used FIRST when it
exists, the photo search / pin is only the fallback (owner's preference, 2026-11-22).
Optional keys: "source": "nasa" | "openverse" | "auto" (default: NASA first for space words, else Openverse only),
"pick": N (use the N-th good result, 0 = first; change it if the first one isn't right), "clip_start": seconds into
the NASA video (default 3), "icon" (used by the fallback board), "pin": {url, title, source, creator, licence, landing,
credit} = a reviewed photo stored in the episode (used as-is: no search, so it can't drift or hit a rate limit).

Sources (no API keys needed):
  * NASA Image and Video Library (images-api.nasa.gov): photos + videos, generally not copyrighted. Credit "NASA".
    Never suggest NASA endorses us; no NASA logo use.
  * Openverse (api.openverse.org): openly licensed photos. Only licences that allow commercial use AND changes,
    and no share-alike (we crop and animate the photo inside a video): CC0, Public Domain Mark, CC BY.
    The credit (title, creator, licence, link) goes into the video description automatically (credits()).
Channels (owner, 2026-11-22): AInation uses real photos (STOCK on, STOCK_STYLE plain); The CurioKids Club does NOT
(real photos looked pasted-in next to the cartoon world): its workflows default STOCK=off, so any photo/clip board
there becomes an icon board. Kids realism comes from our own clay-style pictures and house icons instead.
Downloads are cached in assets/stock/<id>/ (not committed). If anything fails or STOCK=off, the board falls back to
a big icon board with the caption, so a video never breaks. Pexels / Pixabay can be added later as more sources.
"""
import hashlib, json, math, os, re, subprocess, urllib.error, urllib.parse, urllib.request
import skia

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
CACHE = os.path.join(ROOT, "assets", "stock")
ON = os.environ.get("STOCK", "on").strip().lower() not in ("off", "0", "no", "false")
UA = {"User-Agent": "studio-video-pipeline/1.0 (educational videos)"}
SPACE = set("space planet planets moon mars saturn jupiter venus mercury neptune uranus galaxy nebula star stars sun solar "
            "astronaut rocket orbit earth comet asteroid eclipse iss telescope".split())
OK_LICENCES = {"cc0", "pdm", "by"}   # Openverse licence codes we accept (no NC, no ND, no SA)
CLIP_FPS = 12
STYLE = os.environ.get("STOCK_STYLE", "plain").strip().lower()  # plain (photo fills the card) | polaroid (tilted snapshot + REAL! sticker)
TIMEOUT = 40
_MEMO = {}


def _get(url, binary=False, limit=80 * 2**20, timeout=TIMEOUT):
    for attempt in (1, 2):  # one retry (Openverse sometimes answers 502/504)
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = r.read(limit + 1)
            break
        except urllib.error.HTTPError as e:
            if attempt == 2 or e.code not in (429, 500, 502, 503, 504): raise
            import time; time.sleep(4)
        except (TimeoutError, urllib.error.URLError) as e:  # slow answers / dropped connections: try once more
            if attempt == 2: raise
            import time; time.sleep(4)
    if len(data) > limit: raise ValueError("file too large")
    return data if binary else json.loads(data.decode("utf-8"))


def _size(url):
    try:
        req = urllib.request.Request(url, headers=UA, method="HEAD")
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return int(r.headers.get("Content-Length") or 0)
    except Exception:
        return 0


def _key(sc):
    s = json.dumps([sc.get("type"), sc.get("query"), sc.get("source", "auto"), sc.get("pick", 0), sc.get("clip_start", 3),
                    (sc.get("pin") or {}).get("url")], ensure_ascii=False)
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:14]


def _order(sc):
    src = (sc.get("source") or "auto").lower()
    if sc.get("type") == "clip": return ["nasa"]  # videos: NASA only (for now)
    if src in ("nasa", "openverse"): return [src]
    words = set(re.findall(r"[a-z]+", (sc.get("query") or "").lower()))
    return ["nasa", "openverse"] if words & SPACE else ["openverse"]  # NASA only for space topics (else off-topic photos)


# ------------------------------------------------------------------ NASA
def _nasa_assets(item):
    try: return [h for h in _get(item["href"]) if isinstance(h, str)]
    except Exception: return []


def _nasa_photo(q, pick):
    d = _get("https://images-api.nasa.gov/search?" + urllib.parse.urlencode({"q": q, "media_type": "image", "page_size": 25}))
    n = 0
    for it in d["collection"]["items"]:
        meta = (it.get("data") or [{}])[0]
        assets = _nasa_assets(it)
        jpg = next((a for a in assets for size in ("~large.jpg", "~medium.jpg", "~orig.jpg") if a.endswith(size)), None)
        if not jpg: continue
        if n < pick: n += 1; continue
        return {"url": jpg.replace("http://", "https://"), "title": meta.get("title", ""), "source": "NASA",
                "creator": meta.get("photographer") or meta.get("secondary_creator") or meta.get("center") or "NASA",
                "licence": "NASA media (generally not copyrighted)", "landing": f"https://images.nasa.gov/details/{urllib.parse.quote(meta.get('nasa_id', ''))}",
                "credit": "NASA" + (f" / {meta.get('center')}" if meta.get("center") else "")}
    return None


def _nasa_clip(q, pick):
    d = _get("https://images-api.nasa.gov/search?" + urllib.parse.urlencode({"q": q, "media_type": "video", "page_size": 25}))
    n = 0
    for it in d["collection"]["items"]:
        meta = (it.get("data") or [{}])[0]
        assets = _nasa_assets(it)
        vids = [a.replace("http://", "https://").replace(" ", "%20") for a in assets
                if a.endswith(("~mobile.mp4", "~preview.mp4", "~small.mp4", "~medium.mp4"))]
        sized = sorted((sz, v) for v in vids for sz in [_size(v)] if 2**20 < sz <= 150 * 2**20)  # smallest usable file
        if not sized: continue
        mp4 = sized[0][1]
        if n < pick: n += 1; continue
        return {"url": mp4.replace("http://", "https://").replace(" ", "%20"), "title": meta.get("title", ""), "source": "NASA",
                "creator": meta.get("center") or "NASA", "licence": "NASA media (generally not copyrighted)",
                "landing": f"https://images.nasa.gov/details/{urllib.parse.quote(meta.get('nasa_id', ''))}",
                "credit": "NASA" + (f" / {meta.get('center')}" if meta.get("center") else "")}
    return None


# ------------------------------------------------------------------ Openverse
def _openverse_photo(q, pick):
    d = _get("https://api.openverse.org/v1/images/?" + urllib.parse.urlencode(
        {"q": q, "license_type": "commercial,modification", "mature": "false", "page_size": 20}))  # anonymous limit is 20 per page
    n = 0
    for r in d.get("results", []):
        lic = (r.get("license") or "").lower()
        w, h = r.get("width") or 0, r.get("height") or 0
        if lic not in OK_LICENCES or (w and w < 900) or (w and h and not 0.55 <= w / h <= 2.1): continue
        if n < pick: n += 1; continue
        ltxt = {"cc0": "CC0", "pdm": "Public Domain Mark"}.get(lic, f"CC BY {r.get('license_version', '')}".strip())
        who = r.get("creator") or "unknown"
        return {"url": r["url"], "title": r.get("title") or "", "source": r.get("source") or "Openverse", "creator": who,
                "licence": ltxt, "landing": r.get("foreign_landing_url") or "",
                "credit": who if lic == "by" else ("Public domain" if lic != "by" else who)}
    return None


# ------------------------------------------------------------------ fetch + cache
def fetch(sc):
    """Download (once) the photo / clip for a board. Returns its cache folder with meta.json, or None."""
    if not ON or not sc.get("query"): return None
    k = _key(sc); d = os.path.join(CACHE, k); mf = os.path.join(d, "meta.json")
    if os.path.exists(mf): return d
    kind = sc.get("type"); pick = int(sc.get("pick", 0) or 0)
    pin = sc.get("pin")
    if isinstance(pin, dict) and pin.get("url") and kind == "photo":  # a reviewed photo, stored in the episode: no search
        try:
            data = _get(pin["url"], binary=True, limit=25 * 2**20)
            if skia.Image.MakeFromEncoded(skia.Data.MakeWithCopy(data)) is None: raise ValueError("unreadable")
            os.makedirs(d, exist_ok=True); open(os.path.join(d, "photo.jpg"), "wb").write(data)
            m = {k: pin.get(k, "") for k in ("url", "title", "source", "creator", "licence", "landing", "credit")}
            m.update({"query": sc["query"], "kind": kind, "pinned": True})
            json.dump(m, open(mf, "w"), indent=1, ensure_ascii=False)
            print(f"stock: photo '{sc['query']}' <- pinned {m['source']}: {m['title'][:60]}"); return d
        except Exception as e:
            print(f"note: pinned photo for '{sc.get('query')}' failed ({str(e)[:80]}); searching instead")
            import shutil; shutil.rmtree(d, ignore_errors=True)
    for src in _order(sc):
        try:
            if kind == "clip": m = _nasa_clip(sc["query"], pick)
            else: m = (_nasa_photo if src == "nasa" else _openverse_photo)(sc["query"], pick)
            if not m: continue
            os.makedirs(d, exist_ok=True)
            if kind == "clip":
                # smallest NASA version (<= 150 MB), downloaded once; 14 s are cut into frames, then the file is deleted
                mp4 = os.path.join(d, "clip.mp4"); open(mp4, "wb").write(_get(m["url"], binary=True, limit=150 * 2**20, timeout=180))
                fr = os.path.join(d, "frames"); os.makedirs(fr, exist_ok=True)
                start = float(sc.get("clip_start", 3))
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(start), "-i", mp4, "-t", "14", "-an", "-vf",
                                f"fps={CLIP_FPS},scale=960:-2", "-q:v", "4", os.path.join(fr, "f%04d.jpg")], check=True, timeout=240)
                os.remove(mp4)
                m["frames"] = len([f for f in os.listdir(fr) if f.endswith(".jpg")])
                if m["frames"] < CLIP_FPS: raise ValueError("clip too short")
            else:
                data = _get(m["url"], binary=True, limit=25 * 2**20)
                img = skia.Image.MakeFromEncoded(skia.Data.MakeWithCopy(data))
                if img is None or img.width() < 600: raise ValueError("unreadable or too small")
                open(os.path.join(d, "photo.jpg"), "wb").write(data)
            m.update({"query": sc["query"], "kind": kind})
            json.dump(m, open(mf, "w"), indent=1, ensure_ascii=False)
            print(f"stock: {kind} '{sc['query']}' <- {m['source']}: {m['title'][:60]}")
            return d
        except Exception as e:
            print(f"note: stock {kind} '{sc.get('query')}' from {src} failed: {str(e)[:100]}")
            import shutil; shutil.rmtree(d, ignore_errors=True)
    return None


def boards(ep):
    out = []
    for l in ep.get("lines", []):
        b = l.get("board") or {}
        if b.get("type") in ("photo", "clip"): out.append(b)
    return out


def prefetch(ep):
    """Download everything an episode needs (the daily run calls this before rendering). Returns the number found."""
    return sum(1 for b in boards(ep) if art_path(b) or fetch(b))


def credits(ep):
    """Description lines for the photos / clips this episode uses (CC BY needs title, creator, licence and link)."""
    lines = []
    for b in boards(ep):
        if art_path(b): continue  # our own picture: no third-party credit needed
        mf = os.path.join(CACHE, _key(b), "meta.json")
        if not os.path.exists(mf): continue
        m = json.load(open(mf, encoding="utf-8"))
        if m["source"] == "NASA":
            lines.append(f"\"{m['title'][:80]}\" courtesy of NASA ({m['landing']})")
        else:
            lines.append(f"\"{m['title'][:80] or 'Photo'}\" by {m['creator']} ({m['licence']}) {m['landing']}".strip())
    return ("Photos and footage: " + "; ".join(dict.fromkeys(lines))) if lines else ""


# ------------------------------------------------------------------ drawing
_IMG = {}
_SAMP = skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear)


def _img(path):
    if path not in _IMG:
        if len(_IMG) > 40: _IMG.clear()
        _IMG[path] = skia.Image.MakeFromEncoded(skia.Data.MakeWithCopy(open(path, "rb").read()))
    return _IMG[path]


def _cover(c, img, x, y, w, h, zoom=1.0):
    s = max(w / img.width(), h / img.height()) * zoom
    iw, ih = img.width() * s, img.height() * s
    c.drawImageRect(img, skia.Rect.MakeXYWH(x + (w - iw) / 2, y + (h - ih) * 0.45, iw, ih), _SAMP, skia.Paint(AntiAlias=True))


def _col(h, a=1.0):
    h = h.lstrip("#"); return skia.Color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(255 * a))


def art_path(sc):
    """Our own realistic 3D picture for this board, if it exists (owner, 2026-11-22: 3D art first, raw photo only as
    the fallback). "art": "<name>" -> assets/art/<name>_landscape.jpg|png (made on Kaggle, see tools/kaggle/)."""
    name = sc.get("art")
    if not isinstance(name, str) or not name: return None
    for o in ("landscape", "portrait"):
        for ext in ("jpg", "png", "webp"):
            p = os.path.join(ROOT, "assets", "art", f"{os.path.basename(name)}_{o}.{ext}")
            if os.path.exists(p): return p
    return None


def _build(E, i, t0, t1, sc, kind):
    ap = art_path(sc)
    if ap:  # our 3D art: same card look as a photo, no credit label (it's our own picture)
        tin = t0 + 0.2; tcap = max(tin + 0.6, E.cue_t(i, sc, tin + 0.6))
        x, y, w, h = E.BX + 26, E.BY + 26, E.BW - 52, E.BH - 52; cap = sc.get("caption")

        def draw_art(c, t, e):
            k = min(1.0, max(0.0, (t - tin) / max(0.5, t1 - tin)))
            rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), 30, 30)
            sh = skia.Paint(AntiAlias=True, Color=_col("#000000", 0.18)); sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 16))
            c.save(); c.translate(0, 10); c.drawRRect(rr, sh); c.restore()
            c.save(); c.clipRRect(rr, doAntiAlias=True); _cover(c, _img(ap), x, y, w, h, 1.0 + 0.10 * k); c.restore()
            st = skia.Paint(AntiAlias=True, Color=_col("#FFFFFF")); st.setStyle(skia.Paint.kStroke_Style); st.setStrokeWidth(8); c.drawRRect(rr, st)
        E.el(tin, t1, draw_art, None, (E.BCX, E.BCY))
        if cap: E.el(tcap, t1, lambda c, t, e: E.pill(c, E.BCX, y + 56, cap, sc.get("color", "#0A84FF"), 44), pivot=(E.BCX, y + 56))
        return
    d = fetch(sc)
    if not d:  # fallback: big icon board with the caption
        return E.BUILD_BIG(i, t0, t1, {"type": "big", "icon": sc.get("icon", "bulb"), "text": sc.get("caption", ""), "cue": sc.get("cue")})
    m = json.load(open(os.path.join(d, "meta.json"), encoding="utf-8"))
    tin = t0 + 0.2                      # the photo / clip shows as the line starts ...
    tcap = max(tin + 0.6, E.cue_t(i, sc, tin + 0.6))  # ... and the caption pops on the cue word
    x, y, w, h = E.BX + 26, E.BY + 26, E.BW - 52, E.BH - 52
    cap = sc.get("caption"); credit = ("Photo: " if kind == "photo" else "Video: ") + m.get("credit", m["source"])
    nframes = m.get("frames", 0)

    if STYLE == "polaroid":  # a real snapshot shown on purpose: white border, slight tilt, tape, a "REAL!" sticker
        def draw(c, t, e):
            k = min(1.0, max(0.0, (t - tin) / max(0.5, t1 - tin)))
            pw, ph = w * 0.86, h * 0.94; px, py = E.BCX - pw / 2, y + (h - ph) / 2 + 6
            c.save(); c.rotate(-2.5, E.BCX, py + ph / 2)
            fr = skia.Rect.MakeXYWH(px, py, pw, ph)
            sh = skia.Paint(AntiAlias=True, Color=_col("#000000", 0.25)); sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 18))
            c.save(); c.translate(8, 14); c.drawRect(fr, sh); c.restore()
            c.drawRect(fr, skia.Paint(AntiAlias=True, Color=_col("#FFFEF8")))
            m_ = pw * 0.045; inner = skia.Rect.MakeXYWH(px + m_, py + m_, pw - 2 * m_, ph - m_ - ph * 0.17)
            c.save(); c.clipRect(inner, True)
            try:
                if kind == "clip":
                    f = int(max(0.0, t - tin) * CLIP_FPS) % max(1, nframes) + 1
                    _cover(c, _img(os.path.join(d, "frames", f"f{f:04d}.jpg")), inner.x(), inner.y(), inner.width(), inner.height(), 1.0 + 0.04 * k)
                else:
                    _cover(c, _img(os.path.join(d, "photo.jpg")), inner.x(), inner.y(), inner.width(), inner.height(), 1.0 + 0.08 * k)
            except Exception as ex:
                print("note: stock frame skipped:", str(ex)[:80])
            c.restore()
            f = skia.Font(E.K.FONT_B if hasattr(E.K, "FONT_B") else None, 22)
            tw = f.measureText(credit[:44]); c.drawString(credit[:44], px + pw - m_ - tw, py + ph - ph * 0.06, f, skia.Paint(AntiAlias=True, Color=_col("#8A8A99")))
            for tx_, rot in ((px + pw * 0.18, -12), (px + pw * 0.82, 10)):  # two strips of tape
                c.save(); c.rotate(rot, tx_, py); c.drawRect(skia.Rect.MakeXYWH(tx_ - 55, py - 20, 110, 40), skia.Paint(AntiAlias=True, Color=_col("#FFF3B0", 0.85))); c.restore()
            c.restore()
            # "REAL!" / "REAL VIDEO!" sticker, top right
            sx, sy, r = px + pw - 30, py + 26, 62
            path = skia.Path()
            for j in range(24):
                rr_ = r if j % 2 == 0 else r * 0.8; a_ = j * math.pi / 12 - math.pi / 2
                pt = (sx + math.cos(a_) * rr_, sy + math.sin(a_) * rr_)
                path.moveTo(*pt) if j == 0 else path.lineTo(*pt)
            path.close()
            c.save(); c.rotate(12, sx, sy)
            c.drawPath(path, skia.Paint(AntiAlias=True, Color=_col("#FF4D6D")))
            st_ = skia.Paint(AntiAlias=True, Color=_col("#FFFFFF")); st_.setStyle(skia.Paint.kStroke_Style); st_.setStrokeWidth(5); c.drawPath(path, st_)
            fb = skia.Font(E.K.FONT_XB if hasattr(E.K, "FONT_XB") else None, 30 if kind == "photo" else 24)
            lab = "REAL!" if kind == "photo" else "REAL\nVIDEO!"
            ls = lab.split("\n")
            for j, part in enumerate(ls):
                tw2 = fb.measureText(part); c.drawString(part, sx - tw2 / 2, sy + 11 + (j - (len(ls) - 1) / 2) * 28, fb, skia.Paint(AntiAlias=True, Color=_col("#FFFFFF")))
            c.restore()
        E.el(tin, t1, draw, None, (E.BCX, E.BCY))
        if cap:
            E.el(tcap, t1, lambda c, t, e: E.pill(c, E.BCX, y + 40, cap, sc.get("color", "#0A84FF"), 44), pivot=(E.BCX, y + 40))
        return

    def draw(c, t, e):
        k = min(1.0, max(0.0, (t - tin) / max(0.5, t1 - tin)))
        rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), 30, 30)
        sh = skia.Paint(AntiAlias=True, Color=_col("#000000", 0.18)); sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 16))
        c.save(); c.translate(0, 10); c.drawRRect(rr, sh); c.restore()
        c.save(); c.clipRRect(rr, doAntiAlias=True)
        try:
            if kind == "clip":
                f = int(max(0.0, t - tin) * CLIP_FPS) % max(1, nframes) + 1
                _cover(c, _img(os.path.join(d, "frames", f"f{f:04d}.jpg")), x, y, w, h, 1.0 + 0.04 * k)
            else:
                _cover(c, _img(os.path.join(d, "photo.jpg")), x, y, w, h, 1.0 + 0.10 * k)
        except Exception as ex:
            print("note: stock frame skipped:", str(ex)[:80])
        # small credit label, bottom right
        f = skia.Font(E.K.FONT_B if hasattr(E.K, "FONT_B") else None, 20)
        tw = f.measureText(credit[:40])
        c.drawRoundRect(skia.Rect.MakeXYWH(x + w - tw - 34, y + h - 44, tw + 22, 32), 16, 16, skia.Paint(AntiAlias=True, Color=_col("#000000", 0.45)))
        c.drawString(credit[:40], x + w - tw - 23, y + h - 21, f, skia.Paint(AntiAlias=True, Color=_col("#FFFFFF", 0.95)))
        c.restore()
        st = skia.Paint(AntiAlias=True, Color=_col("#FFFFFF")); st.setStyle(skia.Paint.kStroke_Style); st.setStrokeWidth(8)
        c.drawRRect(rr, st)
    E.el(tin, t1, draw, None, (E.BCX, E.BCY))
    if cap:
        E.el(tcap, t1, lambda c, t, e: E.pill(c, E.BCX, y + 56, cap, sc.get("color", "#0A84FF"), 44), pivot=(E.BCX, y + 56))


def build_photo(E, i, t0, t1, sc): return _build(E, i, t0, t1, sc, "photo")
def build_clip(E, i, t0, t1, sc): return _build(E, i, t0, t1, sc, "clip")
BUILDERS = {"photo": build_photo, "clip": build_clip}


if __name__ == "__main__":  # python pipeline/stock.py episodes/*/episode.json  -> fetch everything, print credits
    import sys
    for f in sys.argv[1:]:
        ep = json.load(open(f, encoding="utf-8")); n = prefetch(ep)
        if boards(ep): print(f, n, "of", len(boards(ep)), "found |", credits(ep))
