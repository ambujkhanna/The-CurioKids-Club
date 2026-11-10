"""Post a rendered video to a Facebook Page (Reel or video) and Instagram (Reel) with Meta's Graph API.

Needs env (GitHub secrets): META_PAGE_ID, META_PAGE_TOKEN (long-lived Page token), META_IG_USER_ID.
Nothing happens if they are missing. Errors never fail the run: each function returns a short status string.

    python pipeline/meta_post.py out/video.mp4 episodes/<id>/episode.json [--long]
"""
import json, os, sys, time, urllib.parse, urllib.request, uuid

GRAPH = "https://graph.facebook.com/v21.0"


def _clean(v, kind):
    """Secrets pasted with quotes, spaces, new lines or an 'access_token:' prefix still work."""
    import re
    v = v or ""
    if kind == "token":
        m = re.search(r"EAA[A-Za-z0-9]+", v)
        return m.group(0) if m else "".join(v.split()).strip('",\'')
    return re.sub(r"\D", "", v)  # IDs: digits only


for _k, _kind in (("META_PAGE_ID", "id"), ("META_PAGE_TOKEN", "token"), ("META_IG_USER_ID", "id")):
    if os.environ.get(_k): os.environ[_k] = _clean(os.environ[_k], _kind)


def have_meta():
    return bool(os.environ.get("META_PAGE_ID") and os.environ.get("META_PAGE_TOKEN"))


def have_ig():
    return have_meta() and bool(os.environ.get("META_IG_USER_ID"))


def _req(url, data=None, headers=None, method=None, raw=None, timeout=600):
    body = raw if raw is not None else (urllib.parse.urlencode(data).encode() if data is not None else None)
    rq = urllib.request.Request(url, data=body, headers=headers or {}, method=method or ("POST" if body is not None else "GET"))
    try:
        with urllib.request.urlopen(rq, timeout=timeout) as r:
            return json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        msg = e.read().decode(errors="replace")
        try:
            msg = json.loads(msg).get("error", {}).get("message", msg)
        except Exception:
            pass
        raise RuntimeError(f"HTTP {e.code}: {msg[:300]}")


def caption(ep, brand_line, platform="instagram"):
    """Short social caption: title, first paragraph of the description, brand line, hashtags (no YouTube-only lines).
    Hashtags follow the platform's limit and always include the channel's own tag (pipeline/hashtags.py)."""
    import hashtags
    desc = ep.get("description", "").split("\n\n")[0].strip()
    tags = hashtags.pick(list(ep.get("hashtags", [])) + list(ep.get("social_hashtags", [])), platform)
    head = hashtags.with_brand(ep["title"], 300)
    if hashtags.BRAND.lower() in head.lower():  # channel tag already in the first line: count it once (Instagram max 5)
        tags = [t for t in tags if t.lower() != hashtags.BRAND.lower()]
    out = f"{head}\n\n{desc}\n\n{hashtags.ENGAGE.get(platform, '')}\n{brand_line}\n\n" + " ".join(tags)
    return out[:2100]


def post_facebook(path, ep, cap, long=False):
    page, tok = os.environ["META_PAGE_ID"], os.environ["META_PAGE_TOKEN"]
    size = os.path.getsize(path)
    try:
        if long:  # normal Page video (16:9 long video), resumable upload
            st = _req(f"{GRAPH}/{page}/videos", {"upload_phase": "start", "file_size": size, "access_token": tok})
            sid, vid = st["upload_session_id"], st.get("video_id")
            with open(path, "rb") as fh:
                off = int(st["start_offset"]); end = int(st["end_offset"])
                while off < end:
                    fh.seek(off); chunk = fh.read(end - off)
                    bnd = uuid.uuid4().hex
                    body = (f"--{bnd}\r\nContent-Disposition: form-data; name=\"upload_phase\"\r\n\r\ntransfer\r\n"
                            f"--{bnd}\r\nContent-Disposition: form-data; name=\"upload_session_id\"\r\n\r\n{sid}\r\n"
                            f"--{bnd}\r\nContent-Disposition: form-data; name=\"start_offset\"\r\n\r\n{off}\r\n"
                            f"--{bnd}\r\nContent-Disposition: form-data; name=\"access_token\"\r\n\r\n{tok}\r\n"
                            f"--{bnd}\r\nContent-Disposition: form-data; name=\"video_file_chunk\"; filename=\"c.mp4\"\r\n"
                            f"Content-Type: application/octet-stream\r\n\r\n").encode() + chunk + f"\r\n--{bnd}--\r\n".encode()
                    r = _req(f"https://graph-video.facebook.com/v21.0/{page}/videos", raw=body,
                             headers={"Content-Type": f"multipart/form-data; boundary={bnd}"})
                    off, end = int(r["start_offset"]), int(r["end_offset"])
            _req(f"{GRAPH}/{page}/videos", {"upload_phase": "finish", "upload_session_id": sid, "access_token": tok,
                                             "title": ep["title"][:250], "description": cap})
            return f"posted (video {vid}), " + (fb_cover_when_ready(vid, tok) if vid else "no cover")
        # Reel: start -> upload bytes -> finish (published now)
        st = _req(f"{GRAPH}/{page}/video_reels", {"upload_phase": "start", "access_token": tok})
        vid = st["video_id"]
        with open(path, "rb") as fh:
            _req(f"https://rupload.facebook.com/video-upload/v21.0/{vid}", raw=fh.read(),
                 headers={"Authorization": f"OAuth {tok}", "offset": "0", "file_size": str(size)})
        _req(f"{GRAPH}/{page}/video_reels", {"upload_phase": "finish", "video_id": vid, "video_state": "PUBLISHED",
                                              "description": cap, "access_token": tok})
        LAST["fb_video_id"] = vid
        return f"posted (reel {vid}), " + fb_cover_when_ready(vid, tok)
    except Exception as e:
        return f"failed: {e}"[:300]


LAST = {}
COVER = {}  # {"jpg": designed thumbnail path, "url": public CDN link of it (via a hidden Page photo)}


def _multipart(fields, file_field=None, file_name=None, data=None, ctype="image/jpeg"):
    bnd = uuid.uuid4().hex; body = b""
    for k, v in fields.items():
        body += f"--{bnd}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode()
    if file_field:
        body += (f"--{bnd}\r\nContent-Disposition: form-data; name=\"{file_field}\"; filename=\"{file_name}\"\r\n"
                 f"Content-Type: {ctype}\r\n\r\n").encode() + data + b"\r\n"
    return body + f"--{bnd}--\r\n".encode(), {"Content-Type": f"multipart/form-data; boundary={bnd}"}


def cover_url():
    """Public link to the designed thumbnail (Instagram needs a URL for a Reel cover): uploaded to the Page as an
    UNPUBLISHED photo (never shown on the Page). Returns None if it can't be made."""
    if "url" in COVER or not COVER.get("jpg") or not os.path.exists(COVER["jpg"]): return COVER.get("url")
    page, tok = os.environ["META_PAGE_ID"], os.environ["META_PAGE_TOKEN"]
    try:
        body, hd = _multipart({"published": "false", "access_token": tok}, "source", "cover.jpg", open(COVER["jpg"], "rb").read())
        pid = _req(f"{GRAPH}/{page}/photos", raw=body, headers=hd)["id"]
        imgs = _req(f"{GRAPH}/{pid}?fields=images&access_token={urllib.parse.quote(tok)}").get("images", [])
        COVER["url"] = max(imgs, key=lambda i: i.get("width", 0))["source"] if imgs else None
    except Exception as e:
        print("note: no cover link:", str(e)[:150]); COVER["url"] = None
    return COVER["url"]


def _cover_params():
    u = cover_url()
    return {"cover_url": u} if u else {"thumb_offset": "3000"}  # else a frame after the curtains open


def fb_set_thumbnail(vid, jpg=None):
    """Use the designed thumbnail as the Facebook video/Reel cover (best effort). Returns a short status."""
    jpg = jpg or COVER.get("jpg")
    if not jpg or not os.path.exists(jpg): return "no thumbnail"
    try:
        body, hd = _multipart({"is_preferred": "true", "access_token": os.environ["META_PAGE_TOKEN"]}, "source", "thumb.jpg",
                              open(jpg, "rb").read())
        _req(f"{GRAPH}/{vid}/thumbnails", raw=body, headers=hd)
        return "cover set"
    except Exception as e:
        print("note: Facebook cover not set:", str(e)[:150])
        if "does not exist" in str(e): return "cover not set: video not found on the Page (deleted?)"
        return "cover not set: " + str(e)[:120]


def fb_cover_when_ready(vid, tok, wait=300):
    """Set the designed cover once Facebook has finished processing the video (setting it earlier silently fails)."""
    t0 = time.time()
    while time.time() - t0 < wait:
        try:
            s = _req(f"{GRAPH}/{vid}?fields=status&access_token={urllib.parse.quote(tok)}").get("status", {})
            if s.get("video_status") in ("ready", "published") or s.get("processing_phase", {}).get("status") == "complete": break
            if s.get("video_status") == "error": return "cover not set: Facebook could not process the video"
        except Exception:
            pass
        time.sleep(15)
    res = "no thumbnail"
    for _ in range(3):
        res = fb_set_thumbnail(vid)
        if res in ("cover set", "no thumbnail") or "deleted" in res: break
        time.sleep(20)
    return res


def _fb_source(vid, tok, wait=600):
    """Public CDN link of the Facebook copy (used as a fallback source for Instagram)."""
    t0 = time.time()
    while time.time() - t0 < wait:
        try:
            r = _req(f"{GRAPH}/{vid}?fields=source,status&access_token={urllib.parse.quote(tok)}")
            if r.get("source") and (r.get("status", {}).get("video_status") in (None, "ready")):
                return r["source"]
        except Exception:
            pass
        time.sleep(15)
    return None


def _ig_wait_publish(ig, cid, tok):
    for _ in range(60):  # wait until Instagram has processed the video (up to ~10 min)
        s = _req(f"{GRAPH}/{cid}?fields=status_code,status&access_token={urllib.parse.quote(tok)}")
        if s.get("status_code") == "FINISHED": break
        if s.get("status_code") in ("ERROR", "EXPIRED"): raise RuntimeError(f"processing {s.get('status', s)}")
        time.sleep(10)
    else:
        raise RuntimeError("Instagram processing timed out")
    p = _req(f"{GRAPH}/{ig}/media_publish", {"creation_id": cid, "access_token": tok})
    return p.get("id")


def ig_check(path, cap="check"):
    """Upload a video to Instagram as an UNPUBLISHED Reel container and wait for processing.
    Nothing is posted (unpublished containers expire after 24 h). Returns 'accepted' or the error."""
    ig, tok = os.environ["META_IG_USER_ID"], os.environ["META_PAGE_TOKEN"]
    try:
        c = _req(f"{GRAPH}/{ig}/media", {"media_type": "REELS", "upload_type": "resumable", "caption": cap,
                                          "share_to_feed": "true", "access_token": tok, **_cover_params()})
        cid = c["id"]; uri = c.get("uri") or f"https://rupload.facebook.com/ig-api-upload/v21.0/{cid}"
        data = open(path, "rb").read()
        _req(uri, raw=data, headers={"Authorization": f"OAuth {tok}", "offset": "0", "file_size": str(len(data)),
                                     "Content-Type": "application/octet-stream"})
        for _ in range(60):
            s = _req(f"{GRAPH}/{cid}?fields=status_code,status&access_token={urllib.parse.quote(tok)}")
            if s.get("status_code") == "FINISHED": return "accepted"
            if s.get("status_code") in ("ERROR", "EXPIRED"): return f"rejected: {s.get('status', s)}"[:200]
            time.sleep(10)
        return "timed out"
    except Exception as e:
        return f"rejected: {e}"[:200]


def ig_safe(path, target_mb=26, kb=None, tag="ig"):
    """Instagram copy: 720x1280 H.264 High, 30 fps, AAC 44.1 kHz, sized under ~target_mb.
    (Tested 2026-11-07: this account's API rejected files over ~30 MB with ProcessingFailedError,
    and accepted 19-28 MB files.)"""
    import subprocess
    out = path[:-4] + f"_{tag}.mp4"
    try:
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                                   capture_output=True, text=True, check=True).stdout.strip())
    except Exception:
        dur = 90.0
    kb = kb or int(max(900, min(3000, target_mb * 8192 / max(dur, 1) - 160)))  # video kbit/s within the size budget
    vf = "scale=1280:720" if long_video(path) else "scale=720:1280"
    # exactly the plain recipe Instagram accepted in the 2026-11-07 test (no profile/level/GOP/colour flags)
    # 2026-11-08 test: files with a bitrate cap (-maxrate/-bufsize) were always rejected; this exact plain recipe was accepted
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", path, "-vf", vf, "-b:v", f"{kb}k",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-ar", "44100", "-ac", "2",
           "-movflags", "+faststart", out]
    try:
        subprocess.run(cmd, check=True)
        print(f"Instagram copy: {os.path.getsize(out) / 1e6:.1f} MB at {kb} kbit/s")
        return out
    except Exception as e:
        print("note: could not make Instagram copy:", e)
        return path


def long_video(path):
    try:
        import subprocess
        r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                            "-of", "csv=p=0", path], capture_output=True, text=True, check=True).stdout.strip().split(",")
        return int(r[0]) > int(r[1])
    except Exception:
        return False


def _ig_direct(ig, tok, path, cap):
    c = _req(f"{GRAPH}/{ig}/media", {"media_type": "REELS", "upload_type": "resumable", "caption": cap,
                                      "share_to_feed": "true", "access_token": tok, **_cover_params()})
    cid = c["id"]; uri = c.get("uri") or f"https://rupload.facebook.com/ig-api-upload/v21.0/{cid}"
    with open(path, "rb") as fh:
        data = fh.read()
    _req(uri, raw=data, headers={"Authorization": f"OAuth {tok}", "offset": "0", "file_size": str(len(data)),
                                 "Content-Type": "application/octet-stream"})
    return _ig_wait_publish(ig, cid, tok)


def post_instagram(path, cap):
    ig, tok = os.environ["META_IG_USER_ID"], os.environ["META_PAGE_TOKEN"]
    src = path
    path = ig_safe(src)
    err = ""
    # 1) direct (resumable) upload; Instagram sometimes rejects one encoding and accepts another
    #    (2026-11-08: two of four episodes were rejected with the same recipe), so try a ladder of encodings
    tries = [("size-budget", path), ("3 Mbps", None), ("2 Mbps", None), ("1.5 Mbps", None)]
    for k, (name, p) in enumerate(tries):
        try:
            if p is None:
                p = ig_safe(src, kb={"3 Mbps": 3000, "2 Mbps": 2000, "1.5 Mbps": 1500}[name], tag=f"ig{k}")
            vid = _ig_direct(ig, tok, p, cap)
            return f"posted (reel {vid})" + (f" with the {name} copy" if k else "")
        except Exception as e:
            err = f"{err} [{name}] {str(e)[:90]}"
            time.sleep(20)
    err = err.strip()[:300]
    # 2) upload the Instagram-format copy to the Page as a hidden (unpublished) video, then let Instagram fetch it
    err2 = ""
    try:
        page = os.environ["META_PAGE_ID"]
        bnd = uuid.uuid4().hex
        with open(path, "rb") as fh:
            data = fh.read()
        body = (f"--{bnd}\r\nContent-Disposition: form-data; name=\"published\"\r\n\r\nfalse\r\n"
                f"--{bnd}\r\nContent-Disposition: form-data; name=\"access_token\"\r\n\r\n{tok}\r\n"
                f"--{bnd}\r\nContent-Disposition: form-data; name=\"source\"; filename=\"ig.mp4\"\r\nContent-Type: video/mp4\r\n\r\n").encode() \
               + data + f"\r\n--{bnd}--\r\n".encode()
        r = _req(f"https://graph-video.facebook.com/v21.0/{page}/videos", raw=body, headers={"Content-Type": f"multipart/form-data; boundary={bnd}"}, timeout=900)
        hid = r.get("id")
        src = _fb_source(hid, tok) if hid else None
        if src:
            c = _req(f"{GRAPH}/{ig}/media", {"media_type": "REELS", "video_url": src, "caption": cap, "share_to_feed": "true", "access_token": tok, **_cover_params()})
            return f"posted via hidden copy (reel {_ig_wait_publish(ig, c['id'], tok)})"
        err2 = "hidden copy not ready"
    except Exception as e:
        err2 = str(e)[:140]
    # 3) last fallback: let Instagram fetch the Reel that was just posted to the Facebook Page
    vid = LAST.get("fb_video_id")
    if not vid:
        return f"failed: {err} (no Facebook copy to fall back on)"[:300]
    try:
        src = _fb_source(vid, tok)
        if not src:
            return f"failed: {err}; Facebook copy not ready for fallback"[:300]
        c = _req(f"{GRAPH}/{ig}/media", {"media_type": "REELS", "video_url": src, "caption": cap,
                                          "share_to_feed": "true", "access_token": tok, **_cover_params()})
        return f"posted via Facebook copy (reel {_ig_wait_publish(ig, c['id'], tok)})"
    except Exception as e:
        return f"failed: 1) direct: {err} | 2) hidden copy: {err2} | 3) FB reel copy: {e}"[:600]


def post_all(path, ep, brand_line, long=False, done=None, thumb=None):
    """Returns {"facebook": status, "instagram": status} (only for configured platforms).
    done: the episode's saved record - platforms that already say "posted" are skipped (no duplicates on re-runs)."""
    import re
    out, done = {}, (done or {})
    if not have_meta():
        return out
    cap = caption(ep, brand_line, "instagram"); cap_fb = caption(ep, brand_line, "facebook")
    COVER.clear(); COVER["jpg"] = thumb or (path[:-4] + "_thumbnail.jpg")  # the designed thumbnail, if rendered
    fb_prev = str(done.get("facebook", ""))
    if fb_prev.startswith("posted"):
        m = re.search(r"(\d{6,})", fb_prev)
        if m: LAST["fb_video_id"] = m.group(1)
        out["facebook"] = fb_prev + " (kept, not re-posted)"
    else:
        out["facebook"] = post_facebook(path, ep, cap_fb, long)
    if have_ig() and not long:  # long 16:9 videos go to Facebook only
        ig_prev = str(done.get("instagram", ""))
        out["instagram"] = ig_prev + " (kept, not re-posted)" if ig_prev.startswith("posted") else post_instagram(path, cap)
        if not ig_prev.startswith("posted") and str(out["instagram"]).startswith("posted"):
            out["instagram"] += ", designed cover" if COVER.get("url") else ", cover: video frame (designed cover link failed)"
    return out


if __name__ == "__main__":
    ep = json.load(open(sys.argv[2], encoding="utf-8"))
    print(post_all(sys.argv[1], ep, "", "--long" in sys.argv))
