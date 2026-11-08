"""Voice Lab: try expressive open-source voices on GitHub's computer and save samples to listen to.

    python voicelab/voice_lab.py chatterbox     # Chatterbox (MIT): expressive, keeps Mia/Leo voices (clones mia_ref.wav / leo_ref.wav)
    python voicelab/voice_lab.py hindi          # Hindi: Mia, Leo and Dad in Hindi (multilingual Chatterbox, same cloned voices)
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
HINDI_LINES = [
    ("mia_explains", "MIA", "घुरघुराहट बिल्ली की हल्की-सी गुनगुनाहट है। साइंटिस्ट मानते हैं कि उसके गले की छोटी-छोटी मसल्स थरथराती हैं।"),
    ("leo_asks", "LEO", "मिया दीदी, बिल्लियाँ घुरघुराती क्यों हैं?"),
    ("leo_excited", "LEO", "अरे वाह! ये तो कमाल है! एक और बताओ ना!"),
    ("mia_joke", "MIA", "सोते हुए डायनासोर को क्या कहते हैं? डायनो-खर्राटा!"),
    ("dad_calm", "DAD", "जब बिजली चमके, तो घर के अंदर आ जाओ। तूफ़ान को खिड़की से देखना सबसे सेफ़ है।"),
    ("mia_subscribe", "MIA", "और मज़ेदार बातों के लिए किसी बड़े से द क्यूरियो किड्स क्लब को सब्सक्राइब करने को कहो!"),
]


def hindi():
    import torchaudio as ta
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    model = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
    refs = {"MIA": MIA, "LEO": LEO, "DAD": DAD}
    for ex in (0.5, 0.7):
        for name, who, text in HINDI_LINES:
            t0 = time.time()
            wav = model.generate(text, language_id="hi", audio_prompt_path=refs[who], exaggeration=ex, cfg_weight=0.35)
            p = os.path.join(OUT, f"hindi_ex{int(ex * 10)}_{name}.wav"); ta.save(p, wav, model.sr)
            mp3(p, f"hindi_ex{int(ex * 10)}_{name}"); print(f"  {time.time() - t0:.0f}s", flush=True)


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
