# Plan: keep the code private, keep the runs free (option 2)

**Status:** PLANNED 2026-11-23 (owner chose option 2; to be executed later). Same file in both repos.
**Goal:** nobody outside can read or copy the code, scripts, episodes and analytics, while the daily runs keep working **for free** and keep reading the same secrets and variables.

---

## 1. Why this design

| | Today | After |
|---|---|---|
| Code, episodes, scripts, docs | public repo (anyone can read) | **private "core" repo** |
| Workflows (the timetable) | public repo | stay in the **public "runner" repo** (only `.github/workflows/`, README, LICENSE) |
| Secrets and variables | public repo (never visible to anyone) | **unchanged**: stay in the public runner repo, nothing to re-enter |
| GitHub Actions minutes | free (public repo) | **still free**: the runs still happen in the public runner repo |
| Run logs, summaries, Artifacts | public | still public, so we **print less** and **encrypt** Artifacts (§5) |

Each run first downloads the private code with a token (`CORE_TOKEN`), then works exactly as today. State updates (`state.json`) and new pictures are pushed to the **private** repo.

**Honest limits**
- What has already been public cannot be un-published: anyone may have cloned it before. This protects everything **from now on**. Check the repo page's **Forks** count: forks keep their copy.
- Workflow files, run names/times and the published videos stay visible. The "factory" (code, prompts, scripts, analytics) does not.
- Even today the code is not free to reuse: `LICENSE` (added 2026-11-23) says *All rights reserved*.

---

## 2. Names used below

| Thing | Kids | AInation |
|---|---|---|
| Public runner repo (existing) | `ambujkhanna/The-CurioKids-Club` | `ambujkhanna/youtube-studio-automation` |
| New private core repo | `ambujkhanna/curiokids-core` | `ambujkhanna/aination-core` |
| Local folder for the core repo | `C:\Users\Ambuj\Documents\GitHub\curiokids-core` | `C:\Users\Ambuj\Documents\GitHub\aination-core` |
| Token secret (in the public repo) | `CORE_TOKEN` | `CORE_TOKEN` |

(Any names work; keep these unless there is a reason to change them.)

---

## 3. Owner steps (about 20 minutes, both channels)

**3.1 Create the two private repos (empty)**
github.com → **New repository** → name `curiokids-core` → **Private** → do **not** add a README/licence → Create. Same for `aination-core`.

**3.2 Copy everything, with full history (all branches and tags), into them** (Git Bash; a plain bare copy, because a "mirror" copy would also try to push GitHub's hidden pull-request refs and fail):
```bash
cd /c/Users/Ambuj/Documents/GitHub && git clone --bare https://github.com/ambujkhanna/The-CurioKids-Club.git kids-copy.git && cd kids-copy.git && git push --all https://github.com/ambujkhanna/curiokids-core.git && git push --tags https://github.com/ambujkhanna/curiokids-core.git && cd .. && rm -rf kids-copy.git
```
```bash
cd /c/Users/Ambuj/Documents/GitHub && git clone --bare https://github.com/ambujkhanna/youtube-studio-automation.git ain-copy.git && cd ain-copy.git && git push --all https://github.com/ambujkhanna/aination-core.git && git push --tags https://github.com/ambujkhanna/aination-core.git && cd .. && rm -rf ain-copy.git
```
Then clone the core repos for daily use:
```bash
cd /c/Users/Ambuj/Documents/GitHub && git clone https://github.com/ambujkhanna/curiokids-core.git && git clone https://github.com/ambujkhanna/aination-core.git
```

**3.3 Create one access token** (fine-grained, never paste it in chat)
GitHub → your picture → **Settings** → **Developer settings** → **Personal access tokens** → **Fine-grained tokens** → **Generate new token**:
- Name: `core-access`; Expiration: **1 year** (set a calendar reminder to renew it).
- Repository access: **Only select repositories** → `curiokids-core`, `aination-core`.
- Permissions → Repository: **Contents: Read and write**, **Issues: Read and write**, Metadata: Read (automatic).
- Generate → copy it once.

**3.4 Save the token in both public runner repos**
Each public repo → Settings → Secrets and variables → Actions → New repository secret → `CORE_TOKEN` = the token.
Also add a repository **variable** `CORE_REPO` = `ambujkhanna/curiokids-core` (kids) / `ambujkhanna/aination-core` (AInation).
And one more secret `ARTIFACT_PASSWORD` = a long password you keep in your password manager (used to lock Artifacts, §5).

**3.5 Tell Claude "steps 3.1-3.4 done"** → Claude prepares the bundles for §4.

---

## 4. Claude's work (one bundle per repo)

**4.1 Workflows (public runner repos):** in every workflow (`*-short.yml`, `*-long.yml`, `topic-radar.yml`, `youtube-analytics.yml`, `weekly-art.yml`, `voice-lab.yml`, `growth-tests.yml`), the checkout step becomes:
```yaml
- uses: actions/checkout@v4
  with:
    repository: ${{ vars.CORE_REPO }}
    token: ${{ secrets.CORE_TOKEN }}
```
Everything after it runs unchanged on the private code. A first step fails clearly if `CORE_TOKEN`/`CORE_REPO` are missing.

**4.2 Things that pointed at the public repo**
| Today | After |
|---|---|
| `save_state.py` pushes `state.json` to the checked-out repo | unchanged: it now pushes to the **private** repo (the checkout token has write access) |
| weekly art run commits new pictures | unchanged: commits to the private repo |
| Topic radar / trend alerts open issues in `GITHUB_REPOSITORY` (public!) | open them in `CORE_REPO` with `CORE_TOKEN` (issues become private; GitHub still emails you) |
| Daily runs download the analytics Artifact from the public repo (performance data downloadable by anyone signed in) | the analytics run **commits** the latest report to the private repo (`data/analytics/`, last 8 weeks only); daily runs read it from the checkout. No analytics Artifact. |
| Kaggle names use the public repo name | unchanged (works either way) |

**4.3 Less in public logs and summaries** (new variable `PRIVATE_LOGS`, default `on` after the move)
- Run summaries show only: episode id, title, YouTube link, status, problems. No full scripts, no trend script text, no growth brief tables (they go into a private issue or `data/` instead).
- Trend Short: the script is saved in the private repo (`custom/scripts/…`), not printed.
- The Run-workflow **script** box (pasted scripts) is shown in the public run log: after the move, use script **files** in the private `scripts/` folder instead (the README will say so).

**4.4 Locked Artifacts**
Videos, thumbnails and pictures are put in a 7-Zip archive locked with `ARTIFACT_PASSWORD` (AES-256, file names hidden) and kept **3 days**. To open: download from the run → open with 7-Zip → enter the password.

**4.5 Public runner repos are emptied** (after the new set-up has passed a dry run)
Everything except `.github/workflows/`, `README.md` (short public description + notice) and `LICENSE` is deleted from the public repos' `main`. Old **workflow runs** with detailed logs are deleted (a small script with your permission). Old commits stay in history; see §1 limits.

**4.6 Docs:** `HOW_IT_WORKS.md`, `CONFIGURATION.md` (`CORE_REPO`, `CORE_TOKEN`, `ARTIFACT_PASSWORD`, `PRIVATE_LOGS`), handoffs and the push commands (from now on bundles go to the **core** folders) are updated.

---

## 5. Go-live order (no missed uploads)

1. Owner §3 (any time; nothing changes yet).
2. Claude bundle A (**core repos**): `PRIVATE_LOGS`, analytics into `data/`, issues to `CORE_REPO`. Owner pushes it to the core repos.
3. Claude bundle B (**public runner repos**): new workflows. Owner pushes.
4. Test: run **Dry run** (daily Short), **Trend Short dry run**, **Topic radar**, **YouTube analytics** by hand in each runner repo. All must pass.
5. Owner pushes bundle C (**public runner repos**): removes the code from the public `main`.
6. Watch one full day of scheduled runs.

**Rollback** at any point before step 5: revert the workflow bundle (the old public code is still there). After step 5: push the old workflows back and point them at the public history (`git revert`).

---

## 6. Day-to-day after the move

- Bundles from Claude go to the **core** folders (`curiokids-core`, `aination-core`) with the same kind of one-line push command.
- Only workflow changes go to the public runner repos.
- Secrets and variables: still set in the **public runner** repos (that is where the runs happen).
- Renew `CORE_TOKEN` once a year (GitHub emails a week before it expires).

## 7. Checklist

- [ ] 3.1 private repos created
- [ ] 3.2 history copied, core repos cloned locally
- [ ] 3.3 fine-grained token created (1 year)
- [ ] 3.4 `CORE_TOKEN`, `CORE_REPO`, `ARTIFACT_PASSWORD` saved in both public repos
- [ ] 4 Claude: bundles A (core) and B (runner)
- [ ] 5.4 manual test runs pass in both runner repos
- [ ] 5.5 public repos emptied, old run logs deleted
- [ ] 5.6 one full day of scheduled runs OK
