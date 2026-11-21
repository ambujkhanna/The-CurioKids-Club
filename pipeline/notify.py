"""Phone alerts (roadmap R6, 2026-11-22). Same file in both channels. Does nothing until a secret is set:
  * Telegram: TELEGRAM_BOT_TOKEN (from @BotFather) + TELEGRAM_CHAT_ID (your chat with the bot)
  * Discord:  DISCORD_WEBHOOK_URL (channel settings -> Integrations -> Webhooks)
Never raises: an alert problem must never break a run.

    python pipeline/notify.py "text"        # used by the workflows' failure step
"""
import json, os, sys, urllib.request


def send(text):
    sent = []
    tok, chat = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if tok and chat:
        try:
            req = urllib.request.Request(f"https://api.telegram.org/bot{tok}/sendMessage", method="POST",
                                         data=json.dumps({"chat_id": chat, "text": text[:3900], "disable_web_page_preview": False}).encode(),
                                         headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=15).read(); sent.append("telegram")
        except Exception as e:
            print("note: Telegram alert failed:", str(e)[:80])
    hook = os.environ.get("DISCORD_WEBHOOK_URL")
    if hook:
        try:
            req = urllib.request.Request(hook, method="POST", data=json.dumps({"content": text[:1900]}).encode(),
                                         headers={"Content-Type": "application/json", "User-Agent": "studio-video-pipeline/1.0"})
            urllib.request.urlopen(req, timeout=15).read(); sent.append("discord")
        except Exception as e:
            print("note: Discord alert failed:", str(e)[:80])
    return sent


if __name__ == "__main__":
    print("alert sent via:", send(" ".join(sys.argv[1:]) or "test alert") or "nothing (no alert secrets set)")
