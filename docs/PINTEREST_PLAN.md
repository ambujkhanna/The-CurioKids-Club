# Plan: post our videos to Pinterest automatically

**Status:** PLANNED 2026-11-23 (owner: "Pinterest only" from `docs/PLATFORMS.md`). Same file in both repos.
**Why Pinterest:** parents and teachers search it for "science for kids", "fun facts", activities. Pins keep being found for months (unlike a feed post), and each Pin links back to our YouTube video. Best fit: **The CurioKids Club**; AInation optional later ("AI tips" boards).
**Rules kept:** free API, secrets only in GitHub Secrets, on/off switch, never blocks a YouTube upload.

> Pinterest's API terms, limits and screens change: check developers.pinterest.com while doing the owner steps. Claude will adjust if a screen looks different.

---

## 1. Owner steps (about 30 minutes + Pinterest's review time)

1. **Business account:** pinterest.com → sign up or convert your account to a **Business** account (free) for The CurioKids Club. Profile picture = channel logo, website = the YouTube channel link.
2. **Claim the website** (optional, helps reach): Settings → Claimed accounts → **YouTube** → connect the channel.
3. **Boards:** create 3–5 public boards, e.g. *Science for Kids*, *Animal Facts for Kids*, *Space for Kids*, *Human Body for Kids*, *Fun Facts for Kids*. Each needs a short description with the words parents search for.
4. **Developer app:** developers.pinterest.com → **My apps** → **Connect app** / Create app:
   - Name: *CurioKids Club Publisher*; purpose: "Publishing our own YouTube Shorts as video Pins on our own boards".
   - Redirect URI: `https://localhost/` (only used once to get the login token).
   - Note the **App ID** and **App secret key**.
5. **Access level:** new apps start with **Trial access** (limited; Pins may only be visible to you). Click **Upgrade / Request Standard access**: describe the use (own content, own boards, ~1–2 Pins a day). Approval can take days to weeks.
6. **Tell Claude "Pinterest app created"** → Claude sends a one-time helper (§3) to get the long-lived login token, then you save 4 secrets.

## 2. Secrets and variables (kids repo; later AInation the same way)

| Name | Type | What |
|---|---|---|
| `PINTEREST_APP_ID` | secret | from the developer app |
| `PINTEREST_APP_SECRET` | secret | from the developer app |
| `PINTEREST_REFRESH_TOKEN` | secret | from the one-time login (§3); lasts about a year, renewed by re-doing §3 |
| `PINTEREST_BOARD` | variable | default board name or id, e.g. `Fun Facts for Kids` |
| `PINTEREST` | variable | `on` / `off` (default off until the first test passes) |
| `PINTEREST_LANGS` | variable | which versions to pin: default `en` (English only; `en,es` adds Spanish) |

## 3. One-time login token (Claude builds, owner runs once)

`tools/pinterest_login.py` (runs on your PC, needs only Python):
1. opens the Pinterest consent page for your app (scopes `boards:read, boards:write, pins:read, pins:write, user_accounts:read`);
2. you click **Allow** → the browser lands on `https://localhost/?code=…` (an error page is normal) → copy the address bar into the script;
3. the script exchanges the code and prints the **refresh token** → save it as `PINTEREST_REFRESH_TOKEN` (never in chat).

## 4. Claude's work

**4.1 `pipeline/pinterest_post.py`** (same pattern as `meta_post.py`)
- Refresh token → short-lived access token (`POST /v5/oauth/token`).
- Video upload: `POST /v5/media` (register) → upload the MP4 to the returned upload URL → poll `GET /v5/media/{id}` until *succeeded*.
- Create the Pin: `POST /v5/pins` with `board_id`, `title` (≤ 100), `description` (≤ 500, with 3–5 hashtags from `hashtags.py`), `link` = the YouTube video URL, `media_source` = the uploaded video + cover image (our thumbnail).
- Board choice: by topic words (animals → *Animal Facts for Kids*, space → *Space for Kids* …), else `PINTEREST_BOARD`.
- Returns "posted: <pin link>" or the reason it was skipped; **never fails the run**.

**4.2 Wiring**
- `daily.py`: after the YouTube upload (and Facebook/Instagram), `rec["pinterest"] = pinterest_post.post(...)` when `PINTEREST=on` and the language is in `PINTEREST_LANGS`. The record keeps the Pin link (no double posts).
- Run summary line: "Pinterest: posted / skipped (reason)".
- Workflows: pass the 3 secrets + 3 variables (daily Short, long video).
- Backfill option in Run workflow: **"Post 3 old videos to Pinterest"** (spreads older Shorts, 3 per run).

**4.3 Tests:** unit tests with a fake Pinterest API (token refresh, upload polling, pin body, title/description limits, skip rules); then one real **dry run** that prints the Pin it would create.

**4.4 Docs:** `CONFIGURATION.md`, `docs/PLATFORMS.md` (status), handoffs, `HOW_IT_WORKS.md` (Publish station adds Pinterest).

## 5. Go-live

1. Owner §1 + §3, secrets saved, `PINTEREST` still `off`.
2. Claude bundle → owner pushes.
3. Manual run **"Post 3 old videos to Pinterest"** → check the 3 Pins (visible to you only while on Trial access).
4. After **Standard access** is approved: set `PINTEREST=on` → every new English kids Short is pinned automatically.
5. After 2–3 weeks: compare Pinterest clicks (Pinterest analytics) with YouTube traffic source "Pinterest"; decide on AInation.

## 6. Checklist

- [ ] 1.1 Business account
- [ ] 1.2 YouTube claimed
- [ ] 1.3 3–5 boards
- [ ] 1.4 developer app (App ID + secret)
- [ ] 1.5 Standard access requested
- [ ] 3 refresh token → secrets saved
- [ ] 4 Claude: module, wiring, tests, docs → bundle
- [ ] 5.3 backfill test (3 Pins)
- [ ] 5.4 `PINTEREST=on` after Standard access
