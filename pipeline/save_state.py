"""Save this run's state.json changes to the repo, even if other runs pushed in the meantime.

    python pipeline/save_state.py "Daily run: update episode state"

GitHub checks out the commit a run was TRIGGERED on, so a queued run does not see what earlier runs saved.
This keeps only the episodes this run changed, lays them over the latest state from GitHub, and pushes
(retrying a few times). Episodes changed by other runs are kept.
"""
import glob, json, os, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MSG = sys.argv[1] if len(sys.argv) > 1 else "Run: update state"


def git(*a, check=True):
    return subprocess.run(["git", *a], cwd=ROOT, check=check, capture_output=True, text=True)


def show(ref, path):
    r = git("show", f"{ref}:{path}", check=False)
    try:
        return json.loads(r.stdout) if r.returncode == 0 else {"episodes": {}}
    except Exception:
        return {"episodes": {}}


files = sorted({os.path.relpath(p, ROOT) for p in
                glob.glob(os.path.join(ROOT, "episodes", "state.json")) + glob.glob(os.path.join(ROOT, "long", "state.json")) +
                glob.glob(os.path.join(ROOT, "library", "*", "state.json"))})
changes = {}
for f in files:
    mine = json.load(open(os.path.join(ROOT, f))).get("episodes", {})
    base = show("HEAD", f).get("episodes", {})
    ch = {k: v for k, v in mine.items() if base.get(k) != v}
    if ch: changes[f] = ch
if not changes:
    print("state: nothing changed"); sys.exit(0)
git("config", "user.name", os.environ.get("STATE_BOT", "curio-kids-bot")); git("config", "user.email", "actions@users.noreply.github.com")
branch = os.environ.get("GITHUB_REF_NAME") or "main"
for attempt in range(6):
    git("fetch", "origin", branch)
    git("reset", "-q", "--hard", f"origin/{branch}")
    for f, ch in changes.items():
        st = show("HEAD", f); st.setdefault("episodes", {}).update(ch)
        os.makedirs(os.path.dirname(os.path.join(ROOT, f)), exist_ok=True)
        json.dump(st, open(os.path.join(ROOT, f), "w"), indent=2)
        git("add", f)
    if git("diff", "--cached", "--quiet", check=False).returncode == 0:
        print("state: already up to date"); sys.exit(0)
    git("commit", "-q", "-m", MSG)
    r = git("push", "origin", f"HEAD:{branch}", check=False)
    if r.returncode == 0:
        print("state saved:", ", ".join(f"{f} ({', '.join(sorted(c))})" for f, c in changes.items())); sys.exit(0)
    print("push refused (another run saved first) - merging and retrying:", r.stderr.strip()[:200])
    time.sleep(3 + attempt * 3)
print("state: could not push after retries"); sys.exit(1)
