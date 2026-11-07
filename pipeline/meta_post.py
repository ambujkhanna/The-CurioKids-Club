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


def caption(ep, brand_line):
    """Short social caption: title, first paragraph of the description, brand line, hashtags (no YouTube-only lines)."""
    desc = ep.get("description", "").split("\n\n")[0].strip()
    tags = [h if h.startswith("#") else "#" + h for h in ep.get("hashtags", []) if h.lower() != "#shorts"]
    extra = ep.get("social_hashtags", [])
    out = f"{ep['title']}\n\n{desc}\n\n{brand_line}\n\n" + " ".join(dict.fromkeys(tags + extra))
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
            return f"posted (video {vid})"
        # Reel: start -> upload bytes -> finish (published now)
        st = _req(f"{GRAPH}/{page}/video_reels", {"upload_phase": "start", "access_token": tok})
        vid = st["video_id"]
        with open(path, "rb") as fh:
            _req(f"https://rupload.facebook.com/video-upload/v21.0/{vid}", raw=fh.read(),
                 headers={"Authorization": f"OAuth {tok}", "offset": "0", "file_size": str(size)})
        _req(f"{GRAPH}/{page}/video_reels", {"upload_phase": "finish", "video_id": vid, "video_state": "PUBLISHED",
                                              "description": cap, "access_token": tok})
        LAST["fb_video_id"] = vid
        return f"posted (reel {vid})"
    except Exception as e:
        return f"failed: {e}"[:300]


LAST = {}


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


def ig_check(path):
    """Upload a video to Instagram as an UNPUBLISHED Reel container and wait for processing.
    Nothing is posted (unpublished containers expire after 24 h). Returns 'accepted' or the error."""
    ig, tok = os.environ["META_IG_USER_ID"], os.environ["META_PAGE_TOKEN"]
    try:
        c = _req(f"{GRAPH}/{ig}/media", {"media_type": "REELS", "upload_type": "resumable", "caption": "check",
                                          "share_to_feed": "true", "access_token": tok})
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


def ig_safe(path):
    """Instagram-friendly copy: H.264 High@4.1, 30 fps, keyframe every 2 s, steady bitrate, AAC 44.1 kHz stereo."""
    import subprocess
    out = path[:-4] + "_ig.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", path,
           "-c:v", "libx264", "-profile:v", "high", "-level:v", "4.1", "-pix_fmt", "yuv420p", "-r", "30",
           "-g", "60", "-keyint_min", "60", "-sc_threshold", "0", "-b:v", "6M", "-maxrate", "8M", "-bufsize", "12M",
           "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
           "-c:a", "aac", "-ar", "44100", "-ac", "2", "-b:a", "128k", "-movflags", "+faststart", out]
    try:
        subprocess.run(cmd, check=True)
        return out
    except Exception as e:
        print("note: could not make Instagram copy:", e)
        return path


def post_instagram(path, cap):
    ig, tok = os.environ["META_IG_USER_ID"], os.environ["META_PAGE_TOKEN"]
    path = ig_safe(path)
    err = ""
    # 1) direct (resumable) upload of the file
    try:
        c = _req(f"{GRAPH}/{ig}/media", {"media_type": "REELS", "upload_type": "resumable", "caption": cap,
                                          "share_to_feed": "true", "access_token": tok})
        cid = c["id"]; uri = c.get("uri") or f"https://rupload.facebook.com/ig-api-upload/v21.0/{cid}"
        with open(path, "rb") as fh:
            data = fh.read()
        _req(uri, raw=data, headers={"Authorization": f"OAuth {tok}", "offset": "0", "file_size": str(len(data)),
                                     "Content-Type": "application/octet-stream"})
        return f"posted (reel {_ig_wait_publish(ig, cid, tok)})"
    except Exception as e:
        err = str(e)[:160]
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
            c = _req(f"{GRAPH}/{ig}/media", {"media_type": "REELS", "video_url": src, "caption": cap, "share_to_feed": "true", "access_token": tok})
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
                                          "share_to_feed": "true", "access_token": tok})
        return f"posted via Facebook copy (reel {_ig_wait_publish(ig, c['id'], tok)})"
    except Exception as e:
        return f"failed: 1) direct: {err} | 2) hidden copy: {err2} | 3) FB reel copy: {e}"[:600]


def post_all(path, ep, brand_line, long=False, done=None):
    """Returns {"facebook": status, "instagram": status} (only for configured platforms).
    done: the episode's saved record - platforms that already say "posted" are skipped (no duplicates on re-runs)."""
    import re
    out, done = {}, (done or {})
    if not have_meta():
        return out
    cap = caption(ep, brand_line)
    fb_prev = str(done.get("facebook", ""))
    if fb_prev.startswith("posted"):
        m = re.search(r"(\d{6,})", fb_prev)
        if m: LAST["fb_video_id"] = m.group(1)
        out["facebook"] = fb_prev + " (kept, not re-posted)"
    else:
        out["facebook"] = post_facebook(path, ep, cap, long)
    if have_ig() and not long:  # long 16:9 videos go to Facebook only
        ig_prev = str(done.get("instagram", ""))
        out["instagram"] = ig_prev + " (kept, not re-posted)" if ig_prev.startswith("posted") else post_instagram(path, cap)
    return out


if __name__ == "__main__":
    ep = json.load(open(sys.argv[2], encoding="utf-8"))
    print(post_all(sys.argv[1], ep, "", "--long" in sys.argv))
