# More platforms for the same videos (roadmap R8): options and advice

**Written 2026-11-23 for the owner's decision. Nothing here is built yet. Same file in both repos.**
Today every Short already goes to **YouTube + Facebook Page + Instagram Reels** automatically (`meta_post.py`).
Each new platform would be one small module like `meta_post.py`, with its own on/off variable, posting the same MP4 with captions from `hashtags.py`. Terms and limits below are as known in Nov 2026: check each platform's current developer terms before switching one on.

## The options

| Platform | Best for | Who is there | Posting by API | Approval needed? | Effort | Advice |
|---|---|---|---|---|---|---|
| **Threads** (Meta) | AInation (and parents for kids) | adults, tech and creators | free; video posts supported | uses your existing Meta app; app review only for other people's accounts | **small** (same Meta login as Instagram) | ✅ **first pick**: almost free to add |
| **Pinterest** | **Kids** | parents and teachers searching for activities and "facts for kids" | free API v5; video Pins | yes: "Standard access" app review (a few days to weeks) | medium | ✅ good long-term traffic: Pins keep getting found for months |
| **LinkedIn** | **AInation** | professionals, "AI at work" | free; video posts on your profile or a Company Page | yes for Company Pages (Community Management API); personal profile posting is easier | medium | ✅ strong fit for practical AI tips |
| **Bluesky** | AInation | tech-savvy, growing | free, open API; video up to ~3 min | no (app password) | **small** | 👍 easy, smaller audience |
| **TikTok** | AInation (kids content is risky: TikTok is 13+) | young adults | Content Posting API | yes: app audit; until approved, posts are **private only** | medium-large | ⏸ later, after the audit |
| **Telegram channel** | both | your own followers | free Bot API | no | small | 👎 no discovery: only helps if you already have followers |
| **X (Twitter)** | AInation | news, tech | posting API is paid (free tier is tiny) | – | – | ❌ against the free-only rule |
| **Snapchat Spotlight, Moj, Josh** | – | – | no public posting API | – | – | ❌ by hand only |

## Things to know before adding any

- **Kids channel:** most social platforms are 13+. Post kids videos where **parents and teachers** are (Pinterest, Facebook, Threads), not as content aimed at children on TikTok or Snapchat.
- **Same video everywhere is fine,** but each platform likes its own caption style (already handled per platform by `hashtags.py`).
- **No YouTube watermark issue:** we upload our own MP4 file, not a re-download from YouTube.
- **Measure:** each module would save its post link in the run record, like Facebook/Instagram today, so we can compare.

## Suggested order

1. **Threads**: AInation first (needs: tick the Threads permission on your existing Meta app; ~1 hour of work for me).
2. **Pinterest** for kids (needs: a Pinterest **business** account + developer app; apply for Standard access).
3. **LinkedIn** for AInation (needs: a Company Page for AInation Studio or your profile + developer app).
4. Bluesky (needs: an account + app password) whenever convenient.
