"""Small cartoon sound effects made from code (no recordings, no licences). 24 kHz mono float32.

    snore()  - a cartoon snore: raspy inhale + whistling exhale (for "Zzz" in scripts)
"""
import numpy as np

SR = 24000


def _lowpass(x, k):
    """Cheap smoothing filter (moving average of k samples, applied twice)."""
    w = np.ones(k) / k
    return np.convolve(np.convolve(x, w, "same"), w, "same")


def snore(seed=0, cycles=1):
    rng = np.random.default_rng(seed); out = []
    for _ in range(cycles):
        t1 = np.arange(int(0.75 * SR)) / SR  # raspy inhale: filtered noise with a 30-40 Hz flutter
        rasp = _lowpass(rng.normal(0, 1, t1.size), 18) * (0.55 + 0.45 * np.sin(2 * np.pi * rng.uniform(30, 40) * t1))
        rasp += 0.35 * np.sin(2 * np.pi * (85 + 25 * t1) * t1) * (0.5 + 0.5 * np.sin(2 * np.pi * 34 * t1))
        rasp *= np.sin(np.pi * t1 / t1[-1]) ** 1.5 * np.linspace(0.6, 1.0, t1.size)
        t2 = np.arange(int(0.95 * SR)) / SR  # whistling exhale: falling tone with a little wobble + breath
        f = 1500 - 700 * (t2 / t2[-1]) + 25 * np.sin(2 * np.pi * 6 * t2)
        whistle = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.55 + _lowpass(rng.normal(0, 1, t2.size), 6) * 0.12
        whistle *= np.sin(np.pi * t2 / t2[-1]) ** 1.2
        out += [rasp / (np.abs(rasp).max() + 1e-9) * 0.75, np.zeros(int(0.08 * SR)), whistle * 0.7, np.zeros(int(0.15 * SR))]
    return np.concatenate(out).astype(np.float32)


if __name__ == "__main__":
    import soundfile as sf, sys
    sf.write(sys.argv[1] if len(sys.argv) > 1 else "snore.wav", snore(), SR)
