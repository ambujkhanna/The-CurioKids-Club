"""Upload one rendered episode to YouTube (Data API v3), scheduled with publishAt.

Needs env: YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN (OAuth for The CurioKids Club channel,
scope https://www.googleapis.com/auth/youtube - needed to add videos to the playlist; an older token with only
youtube.upload still uploads, it just can't add to the playlist). Never commit these; store them as GitHub secrets.
Optional repo variables: MADE_FOR_KIDS ("true"/"false", default "false") and YT_PLAYLIST (playlist title or id;
empty = off, videos are added to playlists by hand).
Note: videos uploaded by an unaudited API project are locked to PRIVATE until Google approves the
project audit. Until then the video is uploaded privately and you flip it to public in YouTube Studio.
"""
import os, sys, time
import hashtags

SCOPES = None  # use whatever scopes the refresh token was granted (youtube, or the older youtube.upload)


def made_for_kids():
    return os.environ.get("MADE_FOR_KIDS", "false").strip().lower() in ("1", "true", "yes")


def have_credentials():
    return all(os.environ.get(k) for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"))


def _service():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    creds = Credentials(None, refresh_token=os.environ["YT_REFRESH_TOKEN"], token_uri="https://oauth2.googleapis.com/token",
                        client_id=os.environ["YT_CLIENT_ID"], client_secret=os.environ["YT_CLIENT_SECRET"], scopes=SCOPES)
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def upload(path, ep, publish_at_utc_iso):
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload
    import images  # credits required by CC BY illustrations
    cred = images.credits(ep)
    desc = ep["description"].rstrip() + ("\n\n" + cred if cred else "") + "\n\n" + " ".join(hashtags.pick(ep.get("hashtags", []), "youtube"))
    body = {
        "snippet": {"title": ep["title"][:100], "description": desc[:4900], "tags": ep.get("tags", [])[:15],
                    "categoryId": "27", "defaultLanguage": ep.get("lang", "en"), "defaultAudioLanguage": ep.get("lang", "en")},
        "status": {"privacyStatus": "private", "publishAt": publish_at_utc_iso, "selfDeclaredMadeForKids": made_for_kids(),
                   "containsSyntheticMedia": True},
    }
    if not publish_at_utc_iso:  # publish immediately
        body["status"].pop("publishAt"); body["status"]["privacyStatus"] = "public"
    yt = _service()
    for attempt in range(2):
        try:
            req = yt.videos().insert(part="snippet,status", body=body,
                                     media_body=MediaFileUpload(path, mimetype="video/mp4", chunksize=8 * 1024 * 1024, resumable=True))
            resp = None
            while resp is None:
                _, resp = req.next_chunk()
            return resp["id"]
        except HttpError as e:
            # older API surfaces may reject the synthetic-media flag: retry once without it
            if attempt == 0 and "containsSyntheticMedia" in str(e):
                body["status"].pop("containsSyntheticMedia", None); continue
            raise


def set_thumbnail(video_id, path):
    """Upload the designed thumbnail. Never fails the run: returns 'set' or the reason it was skipped."""
    try:
        from googleapiclient.http import MediaFileUpload
        _service().thumbnails().set(videoId=video_id, media_body=MediaFileUpload(path, mimetype="image/jpeg")).execute()
        return "set"
    except Exception as e:  # e.g. channel not phone-verified for custom thumbnails
        msg = str(e)
        if "404" in msg or "cannot be found" in msg.lower() or "trying to insert a thumbnail image for cannot" in msg:
            print("thumbnail not set: video not found"); return "not set: video not found on YouTube (deleted?)"
        if "forbidden" in msg.lower() or "403" in msg:
            msg = "not allowed yet - verify the channel (youtube.com/verify) to enable custom thumbnails; " + msg[:160]
        print("thumbnail not set:", msg)
        return "not set: " + msg[:220]


def _why(e):
    m = str(e)
    if "insufficient" in m.lower() or "403" in m:
        return ("the YouTube token can only upload: make a new refresh token with scope "
                "https://www.googleapis.com/auth/youtube (docs/SETUP.md) - " + m[:120])
    return m[:200]


_PL = {}


def playlist_id(yt=None):
    """Find the playlist named YT_PLAYLIST (case-insensitive) on the channel; an id (PL...) also works."""
    want = (os.environ.get("YT_PLAYLIST") or "").strip()
    if want in _PL: return _PL[want]
    if want.startswith("PL") and len(want) > 16:
        _PL[want] = want; return want
    yt = yt or _service(); tok = None
    norm = lambda s: "".join(s.lower().split())
    while True:
        r = yt.playlists().list(part="snippet", mine=True, maxResults=50, pageToken=tok).execute()
        for it in r.get("items", []):
            if norm(it["snippet"]["title"]) == norm(want):
                _PL[want] = it["id"]; return it["id"]
        tok = r.get("nextPageToken")
        if not tok: break
    raise RuntimeError(f"no playlist called '{want}' on this channel (create it in YouTube Studio, or set the YT_PLAYLIST variable)")


def add_to_playlist(video_id, existing=None):
    """Add the video to the playlist. Never fails the run: returns 'added ...' or the reason it was skipped."""
    if not (os.environ.get("YT_PLAYLIST") or "").strip():
        return "off (added by hand)"
    try:
        yt = _service(); pid = playlist_id(yt)
        if existing is not None and video_id in existing:
            return "already in playlist"
        yt.playlistItems().insert(part="snippet", body={"snippet": {"playlistId": pid,
                                  "resourceId": {"kind": "youtube#video", "videoId": video_id}}}).execute()
        return f"added ({os.environ['YT_PLAYLIST']})"
    except Exception as e:
        print("playlist:", e); return "not added: " + _why(e)


def playlist_videos():
    """Video ids already in the playlist (to avoid duplicates)."""
    yt = _service(); pid = playlist_id(yt); out, tok = set(), None
    while True:
        r = yt.playlistItems().list(part="contentDetails", playlistId=pid, maxResults=50, pageToken=tok).execute()
        out |= {it["contentDetails"]["videoId"] for it in r.get("items", [])}
        tok = r.get("nextPageToken")
        if not tok: return out


def set_made_for_kids(video_id):
    """Apply the MADE_FOR_KIDS setting to an already-uploaded video (keeps its privacy and schedule)."""
    try:
        yt = _service()
        r = yt.videos().list(part="status", id=video_id).execute()
        if not r.get("items"): return "video not found"
        st = r["items"][0]["status"]; want = made_for_kids()
        if st.get("selfDeclaredMadeForKids") == want and st.get("madeForKids") == want:
            return "made for kids: " + ("yes" if want else "no") + " (unchanged)"
        body = {"privacyStatus": st["privacyStatus"], "selfDeclaredMadeForKids": want}
        for k in ("publishAt", "license", "embeddable", "publicStatsViewable", "containsSyntheticMedia"):
            if k in st: body[k] = st[k]
        yt.videos().update(part="status", body={"id": video_id, "status": body}).execute()
        chk = yt.videos().list(part="status", id=video_id).execute()["items"][0]["status"]
        if chk.get("madeForKids") != want:
            return ("made for kids: still YES - YouTube Studio's channel setting overrides it (Settings > Channel > "
                    "Advanced settings > Audience)")
        return "made for kids: " + ("yes" if want else "no")
    except Exception as e:
        print("made-for-kids:", e); return "not changed: " + _why(e)


if __name__ == "__main__":
    import json
    ep = json.load(open(sys.argv[2]))
    print(upload(sys.argv[1], ep, sys.argv[3]))
