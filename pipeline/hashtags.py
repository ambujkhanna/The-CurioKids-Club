"""Hashtags per platform, always including the channel's own tag.

    YouTube   : max 15 (with more, YouTube ignores them all); the channel tag is in the first 3 (shown above the title)
    Instagram : max 5 (Instagram's limit per post)
    Facebook  : max 10
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KIDS = os.path.exists(os.path.join(ROOT, "library")) or "curio" in ROOT.lower()
BRAND = os.environ.get("BRAND_HASHTAG") or ("#TheCurioKidsClub" if KIDS else "#AInationstudio")
LIMITS = {"youtube": 15, "instagram": 5, "facebook": 10}
NAME = "The CurioKids Club" if KIDS else "AInation Studio"
# one line asking for saves + shares (they count more than likes for reach)
ENGAGE = {
    "instagram": "📌 Save this for later & share it with a curious kid you know! 💛" if KIDS
                 else "📌 Save this & share it with a friend who's curious about AI!",
    "facebook": "💬 Share this with a curious kid (or parent) you know! 💛" if KIDS
                else "💬 Share this with a friend who's curious about AI!",
    "youtube": "👍 Share this with a curious kid you know - and ask a grown-up to subscribe!" if KIDS
               else "👍 Share this with a friend who's curious about AI - and subscribe for more!",
}


def with_brand(title, limit=100):
    """Title + the channel hashtag (visible in the Shorts player / Reel feed, where the description is hidden).
    Left unchanged when it is already there or would not fit."""
    t = (title or "").strip()
    if BRAND.lower() in t.lower() or len(t) + 1 + len(BRAND) > limit: return t
    return f"{t} {BRAND}"


def pick(tags, platform):
    """tags: the episode's hashtags (+ extras). Returns the list for this platform: clean, no duplicates,
    the channel tag second (after the topic tag), '#Shorts' only on YouTube, and within the platform's limit."""
    clean = []
    for t in tags or []:
        t = t.strip()
        if not t: continue
        t = t if t.startswith("#") else "#" + t
        t = "#" + "".join(t[1:].split())  # no spaces inside a hashtag
        if t.lower() == "#shorts" and platform != "youtube": continue
        if t.lower() == BRAND.lower(): continue
        if t.lower() not in [c.lower() for c in clean]: clean.append(t)
    shorts = [t for t in clean if t.lower() == "#shorts"]
    topic = [t for t in clean if t.lower() != "#shorts"]
    out = topic[:1] + [BRAND] + topic[1:] + shorts
    n = LIMITS[platform]
    if len(out) > n:
        out = out[:n - len(shorts)] + shorts if platform == "youtube" else out[:n]
    return out
