"""Voice Lab: try expressive open-source voices on GitHub's computer and save samples to listen to.

    python voicelab/voice_lab.py chatterbox     # Chatterbox (MIT): expressive, keeps Mia/Leo voices (clones mia_ref.wav / leo_ref.wav)
    python voicelab/voice_lab.py hindi          # Hindi accent test: each line as A (today), B (cfg 0), C (Hindi clip), D (Hindi clip, cfg 0.2)
    python voicelab/voice_lab.py turbo          # Chatterbox-Turbo (MIT): real laughs/chuckles with [laugh] [chuckle] tags

Writes MP3s to voicelab/out/. Each model runs separately so one failing does not stop the other.
"""
import os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
MIA, LEO = os.path.join(HERE, "mia_ref.wav"), os.path.join(HERE, "leo_ref.wav")

LINES = [  # (name, speaker, text)
    ("comedy_setup", "MIA", "Okay Leo, here's a good one. Why did the cookie go to the doctor?"),
    ("comedy_punch", "MIA", "Because... it felt CRUMMY!"),
    ("leo_reaction", "LEO", "No way! That is SO silly! Tell me another one!"),
    ("science_wow", "MIA", "Your heart beats about one hundred thousand times every single day. Isn't that amazing?"),
    ("leo_surprised", "LEO", "Whoa! Even when I'm sleeping?"),
    ("quiz_host", "MIA", "Welcome back to the quiz! Here comes question number one. Are you ready?"),
]


def mp3(wav, name):
    dst = os.path.join(OUT, name + ".mp3")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "128k", dst], check=True)
    os.remove(wav); print("saved", dst, flush=True)


def chatterbox():
    import torchaudio as ta
    from chatterbox.tts import ChatterboxTTS
    model = ChatterboxTTS.from_pretrained(device="cpu")
    for ex in (0.5, 0.8):  # exaggeration: 0.5 = natural, 0.8 = very animated
        for name, who, text in LINES:
            t0 = time.time()
            wav = model.generate(text, audio_prompt_path=MIA if who == "MIA" else LEO, exaggeration=ex, cfg_weight=0.35)
            p = os.path.join(OUT, f"chatterbox_ex{int(ex*10)}_{name}.wav"); ta.save(p, wav, model.sr)
            mp3(p, f"chatterbox_ex{int(ex*10)}_{name}"); print(f"  {time.time() - t0:.0f}s", flush=True)


TURBO_LINES = [  # (name, speaker, text) - comedy lines with real laugh tags
    ("leo_laugh_reaction", "LEO", "[laugh] No way! That is SO silly! [laugh] Tell me another one!"),
    ("mia_punchline_chuckle", "MIA", "Because... it felt crummy! [chuckle]"),
    ("leo_giggle_fit", "LEO", "Hee hee... [laugh] okay, okay, I can't stop laughing!"),
    ("mia_joke_champ", "MIA", "[laugh] Ha! Leo, you're the joke champ!"),
    ("leo_teddy_joke", "LEO", "Why did the teddy bear say no to dessert? [chuckle] Because it was already stuffed!"),
    ("mia_reacts", "MIA", "[gasp] Oh my! [laugh] That's the funniest one yet!"),
    ("science_calm", "MIA", "Your heart beats about one hundred thousand times every single day. Isn't that amazing?"),
]


def turbo():
    import torchaudio as ta
    from chatterbox.tts_turbo import ChatterboxTurboTTS
    model = ChatterboxTurboTTS.from_pretrained(device="cpu")
    for name, who, text in TURBO_LINES:
        t0 = time.time()
        wav = model.generate(text, audio_prompt_path=MIA if who == "MIA" else LEO)
        p = os.path.join(OUT, f"turbo_{name}.wav"); ta.save(p, wav, model.sr)
        mp3(p, f"turbo_{name}"); print(f"  {time.time() - t0:.0f}s", flush=True)


DAD = os.path.join(os.path.dirname(HERE), "assets", "voices", "dad.wav")
HI_REFS = os.path.join(HERE, "hi_refs")  # native Hindi reference clips (made with Kokoro's Hindi voices, Apache-2.0)
HINDI_LINES = [  # varnamala-style lines (single letters are the hardest) + everyday dialogue
    ("var_ka", "MIA", "ये है क! क से कबूतर, क से केला!"),
    ("var_kha", "MIA", "अब है ख, हवा के साथ! ख से खरगोश, ख से खीरा!"),
    ("var_all", "LEO", "मैं सब बोलूँ! क, ख, ग, घ, ङ!"),
    ("var_swar", "MIA", "अ से अनार, आ से आम, इ से इमली, ई से ईख!"),
    ("leo_asks", "LEO", "मिया दीदी, बिल्लियाँ घुरघुराती क्यों हैं?"),
    ("dad_calm", "DAD", "जब बिजली चमके, तो घर के अंदर आ जाओ। तूफ़ान को खिड़की से देखना सबसे सेफ़ है।"),
]
# A = today (English clip, cfg 0.35) · B = English clip, cfg 0 (Chatterbox's tip against accent transfer)
# C = Hindi clip, cfg 0.35 · D = Hindi clip, cfg 0.2
HINDI_VARIANTS = [("A_today", "en", 0.35), ("B_en_cfg0", "en", 0.0), ("C_hiclip", "hi", 0.35), ("D_hiclip_cfg02", "hi", 0.2)]


def hindi():
    import torch, torchaudio as ta
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    model = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
    en = {"MIA": MIA, "LEO": LEO, "DAD": DAD}
    hi = {n: os.path.join(HI_REFS, n.lower() + ".wav") for n in en}
    for name, who, text in HINDI_LINES:
        for tag, src, cfg in HINDI_VARIANTS:
            t0 = time.time(); torch.manual_seed(7)
            ref = (hi if src == "hi" else en)[who]
            wav = model.generate(text, language_id="hi", audio_prompt_path=ref, exaggeration=0.5, cfg_weight=cfg)
            p = os.path.join(OUT, f"hindi_{name}_{tag}.wav"); ta.save(p, wav, model.sr)
            mp3(p, f"hindi_{name}_{tag}"); print(f"  {time.time() - t0:.0f}s", flush=True)


def bark():
    import numpy as np
    from scipy.io import wavfile
    os.environ.setdefault("SUNO_USE_SMALL_MODELS", "False")
    from bark import SAMPLE_RATE, generate_audio, preload_models
    preload_models()
    bark_lines = [
        ("bark_leo_laugh", "v2/en_speaker_9", "[laughs] Ha! That is SO silly! [laughs] Tell me another one!"),
        ("bark_mia_punch", "v2/en_speaker_9", "Because... it felt crummy! [laughs]"),
        ("bark_giggle", "v2/en_speaker_9", "[giggles] Hee hee! Okay, okay, one more joke!"),
        ("bark_excited", "v2/en_speaker_9", "Whoa! Your heart beats about one hundred thousand times a day! Amazing!"),
        ("bark_singsong", "v2/en_speaker_9", "♪ Twinkle twinkle shining bright, little star of gentle light ♪"),
    ]
    for name, spk, text in bark_lines:
        t0 = time.time()
        audio = generate_audio(text, history_prompt=spk)
        p = os.path.join(OUT, name + ".wav"); wavfile.write(p, SAMPLE_RATE, (audio * 32767).astype(np.int16))
        mp3(p, name); print(f"  {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "chatterbox"
    try:
        {"chatterbox": chatterbox, "turbo": turbo, "hindi": hindi, "bark": bark}[which]()
    except Exception as e:
        import traceback; traceback.print_exc()
        open(os.path.join(OUT, f"{which}_FAILED.txt"), "w").write(str(e))
        print(f"{which} failed: {e}")
