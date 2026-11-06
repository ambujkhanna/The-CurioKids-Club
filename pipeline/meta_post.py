"""Post a rendered video to a Facebook Page (Reel or video) and Instagram (Reel) with Meta's Graph API.

Needs env (GitHub secrets): META_PAGE_ID, META_PAGE_TOKEN (long-lived Page token), META_IG_USER_ID.
Nothing happens if they are missing. Errors never fail the run: each function returns a short status string.

    python pipeline/meta_post.py out/video.mp4 episodes/<id>/episode.json [--long]
"""
import json, os, sys, time, urllib.parse, urllib.request, uuid

GRAPH = "https://graph.facebook.com/v21.0"


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
        return f"posted (reel {vid})"
    except Exception as e:
        return f"failed: {e}"[:300]


def post_instagram(path, cap):
    ig, tok = os.environ["META_IG_USER_ID"], os.environ["META_PAGE_TOKEN"]
    try:
        c = _req(f"{GRAPH}/{ig}/media", {"media_type": "REELS", "upload_type": "resumable", "caption": cap,
                                          "share_to_feed": "true", "access_token": tok})
        cid = c["id"]; uri = c.get("uri") or f"https://rupload.facebook.com/ig-api-upload/v21.0/{cid}"
        with open(path, "rb") as fh:
            _req(uri, raw=fh.read(), headers={"Authorization": f"OAuth {tok}", "offset": "0", "file_size": str(os.path.getsize(path))})
        for _ in range(60):  # wait until Instagram has processed the video (up to ~10 min)
            s = _req(f"{GRAPH}/{cid}?fields=status_code,status&access_token={urllib.parse.quote(tok)}")
            if s.get("status_code") == "FINISHED": break
            if s.get("status_code") in ("ERROR", "EXPIRED"): return f"failed: processing {s.get('status', s)}"[:300]
            time.sleep(10)
        else:
            return "failed: Instagram processing timed out"
        p = _req(f"{GRAPH}/{ig}/media_publish", {"creation_id": cid, "access_token": tok})
        return f"posted (reel {p.get('id')})"
    except Exception as e:
        return f"failed: {e}"[:300]


def post_all(path, ep, brand_line, long=False):
    """Returns {"facebook": status, "instagram": status} (only for configured platforms)."""
    out = {}
    if not have_meta():
        return out
    cap = caption(ep, brand_line)
    out["facebook"] = post_facebook(path, ep, cap, long)
    if have_ig() and not long:  # long 16:9 videos go to Facebook only
        out["instagram"] = post_instagram(path, cap)
    return out


if __name__ == "__main__":
    ep = json.load(open(sys.argv[2], encoding="utf-8"))
    print(post_all(sys.argv[1], ep, "", "--long" in sys.argv))
