"""One-time (or cached) setup of the free Kokoro voice model files at the repo root.

Creates: kokoro-q8.onnx, voices.bin, kokoro-dur.onnx   (needs: npm, python packages numpy + onnx)
    python pipeline/setup_models.py
Sources (Apache-2.0 model weights, redistributed on npm): kokoro-q8-shards, kokoro-local-runtime.
"""
import glob, hashlib, os, shutil, subprocess, tarfile, tempfile
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONNX, VOICES, DUR = (os.path.join(ROOT, n) for n in ("kokoro-q8.onnx", "voices.bin", "kokoro-dur.onnx"))
SHA_PREFIX = "fbae9257"


HINDI = ("hf_alpha", "hf_beta", "hm_omega", "hm_psi")
V1_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"


def add_hindi_voices():
    """Add Kokoro v1.0's Hindi voices (Apache-2.0) to voices.bin if missing (for the Hindi videos)."""
    have = dict(np.load(VOICES))
    if all(h in have for h in HINDI): return
    import urllib.request
    tmp = tempfile.mkdtemp(); f = os.path.join(tmp, "v1.bin")
    urllib.request.urlretrieve(V1_URL, f)
    v1 = np.load(f)
    for h in HINDI: have[h] = v1[h]
    with open(VOICES, "wb") as fh:
        np.savez(fh, **have)
    shutil.rmtree(tmp, ignore_errors=True)
    print("added Hindi voices:", ", ".join(HINDI))


def main():
    if all(os.path.exists(p) for p in (ONNX, VOICES, DUR)):
        print("models already present")
        try: add_hindi_voices()
        except Exception as e: print("note: could not add Hindi voices:", e)
        return
    tmp = tempfile.mkdtemp()
    subprocess.run(["npm", "pack", "kokoro-q8-shards@1.0.0", "kokoro-local-runtime@0.1.0"], cwd=tmp, check=True,
                   stdout=subprocess.DEVNULL)
    for t in glob.glob(os.path.join(tmp, "*.tgz")):
        d = os.path.join(tmp, os.path.basename(t)[:-4]); os.makedirs(d)
        with tarfile.open(t) as tf:
            tf.extractall(d, filter="data")
    shards = sorted(glob.glob(os.path.join(tmp, "kokoro-q8-shards*", "package", "kokoro-q8.part*.bin")))
    with open(ONNX, "wb") as out:
        for s in shards:
            out.write(open(s, "rb").read())
    sha = hashlib.sha256(open(ONNX, "rb").read()).hexdigest()
    assert sha.startswith(SHA_PREFIX), f"unexpected model checksum {sha}"
    vdir = glob.glob(os.path.join(tmp, "kokoro-local-runtime*", "package", "voices"))[0]
    voices = {os.path.basename(f)[:-4]: np.fromfile(f, dtype=np.float32).reshape(510, 1, 256)
              for f in glob.glob(os.path.join(vdir, "*.bin"))}
    with open(VOICES, "wb") as fh:
        np.savez(fh, **voices)
    import onnx  # expose per-phoneme durations for lip-sync
    m = onnx.load(ONNX)
    cast = [n for n in m.graph.node if n.output[0] == "/encoder/Cast_output_0"][0]
    to = [a.i for a in cast.attribute if a.name == "to"][0]
    m.graph.output.append(onnx.helper.make_tensor_value_info("/encoder/Cast_output_0", to, None))
    onnx.save(m, DUR)
    shutil.rmtree(tmp, ignore_errors=True)
    try: add_hindi_voices()
    except Exception as e: print("note: could not add Hindi voices:", e)
    print("models ready:", ONNX, VOICES, DUR)


if __name__ == "__main__":
    main()
