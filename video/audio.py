"""Nappe d'ambiance synthétisée + houle + impulsions aux changements de scène."""
import numpy as np, wave
import os, importlib
SCENES = importlib.import_module(os.environ.get('SCN','scenes')).SCENES

SR = 44100
D = sum(d for d, _ in SCENES)
N = int(D * SR)
t = np.arange(N) / SR
out = np.zeros(N)

def midi(m):
    return 440 * 2 ** ((m - 69) / 12)

# progression : Dm9 · Bbmaj7 · Fmaj7 · C(add9), 9 s par accord
CHORDS = [[50, 57, 60, 64, 65], [46, 53, 57, 60, 62], [41, 53, 57, 60, 64], [48, 55, 59, 62, 67]]
CH = 9.0
rng = np.random.default_rng(7)
k = 0
start = 0.0
while start < D:
    notes = CHORDS[k % 4]
    s0, s1 = int(start * SR), min(N, int((start + CH + 4) * SR))
    tt = t[s0:s1] - start
    env = np.minimum(1, tt / 2.5) * np.clip((CH + 4 - tt) / 4, 0, 1)
    for m in notes:
        f = midi(m)
        for det in (-0.12, 0.0, 0.12):
            ph = rng.uniform(0, 2 * np.pi)
            out[s0:s1] += env * (np.sin(2 * np.pi * f * (1 + det / 100) * tt + ph)
                                 + 0.18 * np.sin(4 * np.pi * f * tt + ph)) * 0.035
    # basse
    fb = midi(notes[0] - 12)
    out[s0:s1] += env * np.sin(2 * np.pi * fb * tt) * 0.09
    start += CH
    k += 1

# houle : bruit filtré, modulé lentement
noise = rng.standard_normal(N)
for _ in range(3):
    noise = np.convolve(noise, np.ones(60) / 60, mode='same')
swell = 0.5 + 0.5 * np.sin(2 * np.pi * t / 11.0)
out += noise * swell * 0.55

# impulsion grave à chaque changement de scène
acc = 0
for d, _ in SCENES[:-1]:
    acc += d
    s0 = int((acc - 0.05) * SR)
    L = int(1.2 * SR)
    tt = np.arange(L) / SR
    f = 55 * np.exp(-tt * 3) + 38
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 4.5) * 0.22
    out[s0:s0 + L] += boom[:max(0, min(L, N - s0))]

# fondu d'entrée / sortie, normalisation
fade = np.ones(N)
fi, fo = int(1.5 * SR), int(3.0 * SR)
fade[:fi] = np.linspace(0, 1, fi)
fade[-fo:] = np.linspace(1, 0, fo)
out *= fade
out = out / np.max(np.abs(out)) * 0.6
stereo = np.stack([out, np.roll(out, 220)], axis=1)
pcm = (stereo * 32767).astype(np.int16)
_out = os.environ.get('OUTDIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out'))
os.makedirs(_out, exist_ok=True)
with wave.open(os.path.join(_out, 'music.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print('audio', D, 's')
