"""Upload one rendered episode to YouTube (Data API v3), scheduled with publishAt.

Needs env: YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN (OAuth for the Curio Kids Club channel,
scope https://www.googleapis.com/auth/youtube.upload). Never commit these; store them as GitHub secrets.
Note: videos uploaded by an unaudited API project are locked to PRIVATE until Google approves the
project audit. Until then the video is uploaded privately and you flip it to public in YouTube Studio.
"""
import os, sys, time

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


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
    desc = ep["description"].rstrip() + "\n\n" + " ".join(ep.get("hashtags", []))
    body = {
        "snippet": {"title": ep["title"][:100], "description": desc[:4900], "tags": ep.get("tags", [])[:15],
                    "categoryId": "27", "defaultLanguage": "en", "defaultAudioLanguage": "en"},
        "status": {"privacyStatus": "private", "publishAt": publish_at_utc_iso, "selfDeclaredMadeForKids": True,
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


if __name__ == "__main__":
    import json
    ep = json.load(open(sys.argv[2]))
    print(upload(sys.argv[1], ep, sys.argv[3]))
