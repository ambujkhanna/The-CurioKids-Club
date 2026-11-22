"""Phone alerts (roadmap R6, 2026-11-22). Same file in both channels. Does nothing until a secret is set:
  * Telegram: TELEGRAM_BOT_TOKEN (from @BotFather) + TELEGRAM_CHAT_ID (your chat with the bot)
  * Discord:  DISCORD_WEBHOOK_URL (channel settings -> Integrations -> Webhooks)
  * WhatsApp: WHATSAPP_PHONE (your number with country code, e.g. +9198XXXXXXXX) + WHATSAPP_APIKEY, via the free
              CallMeBot service (callmebot.com: message their number once from your WhatsApp to get the key;
              personal use, messages only go to your own number). Added 2026-11-22 (owner prefers WhatsApp).
Never raises: an alert problem must never break a run.

    python pipeline/notify.py "text"        # used by the workflows' failure step
"""
import json, os, sys, urllib.parse, urllib.request


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
    phone, key = os.environ.get("WHATSAPP_PHONE", "").strip(), os.environ.get("WHATSAPP_APIKEY", "").strip()
    if phone and key:
        try:
            q = urllib.parse.urlencode({"phone": phone, "text": text[:900], "apikey": key})
            req = urllib.request.Request("https://api.callmebot.com/whatsapp.php?" + q, headers={"User-Agent": "studio-video-pipeline/1.0"})
            body = urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "replace")
            if "error" in body.lower() and "queued" not in body.lower() and "sent" not in body.lower():
                print("note: WhatsApp alert answer:", body[:120].replace(key, "***"))
            else:
                sent.append("whatsapp")
        except Exception as e:
            print("note: WhatsApp alert failed:", str(e)[:80].replace(key, "***"))
    return sent


if __name__ == "__main__":
    print("alert sent via:", send(" ".join(sys.argv[1:]) or "test alert") or "nothing (no alert secrets set)")
