# """
# compare_models.py
# -----------------
# Tests ALL your .pth model files and ranks them.
# Run:  python compare_models.py

# No dataset needed - uses synthetic signals to check
# whether each model can predict BOTH classes.
# """

# import sys
# import math
# import torch
# import torch.nn as nn
# import torchaudio
# import torchaudio.transforms as T
# import os

# SAMPLE_RATE = 16000
# MAX_LEN     = 64000

# # All your model files - edit this list if you add more
# MODEL_FILES = [
#     "deepfake_detector.pth",
#     "deepfake_detector1.pth",
#     "deepfake_detector2.pth",
#     "deepfake_detector_v2.pth",
#     "deepfake_cnn_asvspoof_best.pth",
# ]

# transform = T.MelSpectrogram(sample_rate=SAMPLE_RATE, n_mels=64)


# # ── Architectures ─────────────────────────────────────────────────────────────
# # Architecture A - what your training script uses
# class SpectrogramCNN_A(nn.Module):
#     def __init__(self):
#         super().__init__()
#         self.conv1   = nn.Conv2d(1, 16, kernel_size=3, stride=1)
#         self.conv2   = nn.Conv2d(16, 32, kernel_size=3, stride=1)
#         self.pool    = nn.MaxPool2d(2, 2)
#         self.gap     = nn.AdaptiveAvgPool2d((15, 399))
#         self.fc1     = nn.Linear(32 * 15 * 399, 64)
#         self.dropout = nn.Dropout(0.5)
#         self.fc2     = nn.Linear(64, 2)

#     def forward(self, x):
#         x = torch.relu(self.conv1(x))
#         x = self.pool(x)
#         x = torch.relu(self.conv2(x))
#         x = self.pool(x)
#         x = self.gap(x)
#         x = x.view(x.size(0), -1)
#         x = torch.relu(self.fc1(x))
#         x = self.dropout(x)
#         return self.fc2(x)


# # Architecture B - older DeepfakeCNN (from your commented-out app.py versions)
# class SpectrogramCNN_B(nn.Module):
#     def __init__(self):
#         super().__init__()
#         self.conv1   = nn.Conv2d(1, 16, kernel_size=3, stride=1, padding=1)
#         self.conv2   = nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1)
#         self.pool    = nn.MaxPool2d(2, 2)
#         self.fc1     = nn.Linear(32 * 16 * 100, 128)
#         self.dropout = nn.Dropout(0.5)
#         self.fc2     = nn.Linear(128, 2)

#     def forward(self, x):
#         x = self.pool(torch.relu(self.conv1(x)))
#         x = self.pool(torch.relu(self.conv2(x)))
#         x = x.view(x.size(0), -1)
#         x = self.dropout(torch.relu(self.fc1(x)))
#         return self.fc2(x)


# # Architecture C - studyfetch 3-layer version
# class SpectrogramCNN_C(nn.Module):
#     def __init__(self):
#         super().__init__()
#         self.conv_layers = nn.Sequential(
#             nn.Conv2d(1, 16, kernel_size=3, padding=1), nn.ReLU(), nn.MaxPool2d(2, 2),
#             nn.Conv2d(16, 32, kernel_size=3, padding=1), nn.ReLU(), nn.MaxPool2d(2, 2),
#             nn.Conv2d(32, 64, kernel_size=3, padding=1), nn.ReLU(), nn.AdaptiveAvgPool2d((1, 1))
#         )
#         self.classifier = nn.Sequential(
#             nn.Linear(64, 32), nn.ReLU(), nn.Dropout(0.5), nn.Linear(32, 2)
#         )

#     def forward(self, x):
#         x = self.conv_layers(x)
#         x = x.view(x.size(0), -1)
#         return self.classifier(x)


# ARCHITECTURES = [SpectrogramCNN_A, SpectrogramCNN_B, SpectrogramCNN_C]
# ARCH_NAMES    = ["SpectrogramCNN_A (gap+64)", "SpectrogramCNN_B (padding+128)", "SpectrogramCNN_C (3layer+64ch)"]


# # ── Helpers ───────────────────────────────────────────────────────────────────
# def pad_or_truncate(w):
#     n = w.size(1)
#     if n > MAX_LEN:  return w[:, :MAX_LEN]
#     if n < MAX_LEN:  return torch.nn.functional.pad(w, (0, MAX_LEN - n))
#     return w


# def make_spec(waveform):
#     w = pad_or_truncate(waveform)
#     s = transform(w)
#     return s.unsqueeze(0)


# def make_sine(freq=440, seconds=3):
#     t = torch.linspace(0, seconds, int(SAMPLE_RATE * seconds))
#     return (0.5 * torch.sin(2 * math.pi * freq * t)).unsqueeze(0)


# def make_noise(seconds=3):
#     return (torch.rand(1, int(SAMPLE_RATE * seconds)) * 2 - 1) * 0.5


# # 20 varied test signals - frequencies, amplitudes, noise levels
# TEST_SIGNALS = (
#     [make_sine(freq=f, seconds=3) for f in [100, 200, 300, 440, 800, 1200, 2000, 3000, 4000]] +
#     [make_noise(seconds=s) for s in [1, 2, 3, 4]] +
#     [make_sine(freq=440, seconds=s) for s in [1, 2, 4, 5]] +
#     [(torch.rand(1, MAX_LEN) * 2 - 1) * amp for amp in [0.1, 0.3, 0.7, 1.0]]
# )


# def try_load(model_path, arch_class):
#     """Try loading model_path with a given architecture. Returns model or None."""
#     try:
#         m = arch_class()
#         state = torch.load(model_path, map_location="cpu")
#         m.load_state_dict(state)
#         m.eval()
#         return m
#     except Exception:
#         return None


# def evaluate_model(model):
#     """
#     Run all test signals through the model.
#     Returns dict with: bonafide_count, spoof_count, avg_bonafide_prob,
#     avg_spoof_prob, both_classes, avg_max_confidence
#     """
#     preds       = []
#     b_probs     = []
#     s_probs     = []
#     max_confs   = []

#     with torch.no_grad():
#         for sig in TEST_SIGNALS:
#             try:
#                 spec   = make_spec(sig)
#                 logits = model(spec)
#                 probs  = torch.softmax(logits, dim=1)[0]
#                 pred   = int(torch.argmax(probs).item())
#                 preds.append(pred)
#                 b_probs.append(float(probs[0].item()))
#                 s_probs.append(float(probs[1].item()))
#                 max_confs.append(float(probs[pred].item()))
#             except Exception:
#                 pass

#     bonafide_count = preds.count(0)
#     spoof_count    = preds.count(1)
#     both_classes   = bonafide_count > 0 and spoof_count > 0
#     avg_b          = sum(b_probs) / len(b_probs) if b_probs else 0
#     avg_s          = sum(s_probs) / len(s_probs) if s_probs else 0
#     avg_conf       = sum(max_confs) / len(max_confs) if max_confs else 0

#     return {
#         "bonafide_count": bonafide_count,
#         "spoof_count":    spoof_count,
#         "both_classes":   both_classes,
#         "avg_bonafide":   round(avg_b * 100, 1),
#         "avg_spoof":      round(avg_s * 100, 1),
#         "avg_confidence": round(avg_conf * 100, 1),
#         "total_signals":  len(preds),
#     }


# # ── Main ──────────────────────────────────────────────────────────────────────
# print("\n" + "=" * 65)
# print("  COMPARING ALL MODEL FILES")
# print("=" * 65)

# results = []

# for model_path in MODEL_FILES:
#     if not os.path.exists(model_path):
#         print("\n[SKIP] {} -- file not found".format(model_path))
#         continue

#     size_mb = os.path.getsize(model_path) / (1024 * 1024)
#     print("\nTesting: {}  ({:.1f} MB)".format(model_path, size_mb))

#     loaded_model = None
#     loaded_arch  = None

#     for arch_class, arch_name in zip(ARCHITECTURES, ARCH_NAMES):
#         m = try_load(model_path, arch_class)
#         if m is not None:
#             loaded_model = m
#             loaded_arch  = arch_name
#             print("  Architecture: {}".format(arch_name))
#             break

#     if loaded_model is None:
#         print("  FAILED to load with any known architecture -- skipping")
#         continue

#     r = evaluate_model(loaded_model)
#     r["model"]     = model_path
#     r["arch"]      = loaded_arch
#     r["size_mb"]   = round(size_mb, 1)
#     results.append(r)

#     status = "BOTH CLASSES" if r["both_classes"] else "BIASED (only Spoof)" if r["spoof_count"] == r["total_signals"] else "BIASED (only Bonafide)"
#     print("  Bonafide predictions: {}/{}".format(r["bonafide_count"], r["total_signals"]))
#     print("  Spoof    predictions: {}/{}".format(r["spoof_count"],    r["total_signals"]))
#     print("  Avg bonafide prob   : {}%".format(r["avg_bonafide"]))
#     print("  Avg spoof    prob   : {}%".format(r["avg_spoof"]))
#     print("  Avg confidence      : {}%".format(r["avg_confidence"]))
#     print("  Status              : {}".format(status))


# # ── Rankings ─────────────────────────────────────────────────────────────────
# print("\n" + "=" * 65)
# print("  RANKING  (best model at top)")
# print("=" * 65)

# if not results:
#     print("  No models could be loaded.")
#     sys.exit(1)

# # Score: both_classes=10pts, lower avg_confidence=less biased (closer to 50=5pts)
# def score(r):
#     pts = 0
#     if r["both_classes"]:
#         pts += 10
#     # reward balance: if avg_spoof is close to 50%, model is less biased
#     balance = abs(r["avg_spoof"] - 50)
#     pts += max(0, 5 - int(balance / 10))
#     return pts

# results.sort(key=score, reverse=True)

# for i, r in enumerate(results):
#     tag = "RECOMMENDED" if i == 0 and r["both_classes"] else ("biased" if not r["both_classes"] else "ok")
#     print("\n  #{} [{}]  {}".format(i + 1, tag, r["model"]))
#     print("     Architecture : {}".format(r["arch"]))
#     print("     Both classes : {}".format(r["both_classes"]))
#     print("     Bonafide/Spoof predictions: {}/{}  out of {}".format(
#         r["bonafide_count"], r["spoof_count"], r["total_signals"]))
#     print("     Avg prob  ->  Bonafide: {}%  Spoof: {}%".format(r["avg_bonafide"], r["avg_spoof"]))

# best = results[0]
# print("\n" + "=" * 65)
# if best["both_classes"]:
#     print("  USE THIS MODEL:  {}".format(best["model"]))
#     print("  In app.py change the load line to:")
#     print('  model.load_state_dict(torch.load("{}", map_location="cpu"))'.format(best["model"]))
# else:
#     print("  WARNING: None of your models predict both classes reliably.")
#     print("  All models are biased toward Spoof.")
#     print("  Best option available: {}".format(best["model"]))
#     print("  Recommendation: retrain with a balanced dataset.")
# print("=" * 65)
# print()




##########################3 live recording CAI ########
"""
compare_models.py
-----------------
Sweeps TARGET_RMS values to find which gives the most balanced
predictions for live recording. Run:

    python compare_models.py

At the end it prints the exact TARGET_RMS and model to use in app.py.
"""

import sys, math, os
import torch
import torch.nn as nn
import torchaudio.transforms as T

SAMPLE_RATE = 16000
MAX_LEN     = 64000

MODEL_FILES = [
    "deepfake_detector.pth",
    "deepfake_detector1.pth",
    "deepfake_detector2.pth",
    "deepfake_detector_v2.pth",
    "deepfake_cnn_asvspoof_best.pth",
]

# Sweep these RMS values to find the sweet spot
RMS_VALUES = [0.01, 0.02, 0.035, 0.05, 0.07, 0.10, 0.15, 0.20, 0.30]

transform = T.MelSpectrogram(sample_rate=SAMPLE_RATE, n_mels=64)


# ── Architectures ─────────────────────────────────────────────────────────────
class SpectrogramCNN_A(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1   = nn.Conv2d(1, 16, kernel_size=3, stride=1)
        self.conv2   = nn.Conv2d(16, 32, kernel_size=3, stride=1)
        self.pool    = nn.MaxPool2d(2, 2)
        self.gap     = nn.AdaptiveAvgPool2d((15, 399))
        self.fc1     = nn.Linear(32 * 15 * 399, 64)
        self.dropout = nn.Dropout(0.5)
        self.fc2     = nn.Linear(64, 2)

    def forward(self, x):
        x = torch.relu(self.conv1(x))
        x = self.pool(x)
        x = torch.relu(self.conv2(x))
        x = self.pool(x)
        x = self.gap(x)
        x = x.view(x.size(0), -1)
        x = torch.relu(self.fc1(x))
        x = self.dropout(x)
        return self.fc2(x)


class SpectrogramCNN_B(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1   = nn.Conv2d(1, 16, kernel_size=3, stride=1, padding=1)
        self.conv2   = nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1)
        self.pool    = nn.MaxPool2d(2, 2)
        self.fc1     = nn.Linear(32 * 16 * 100, 128)
        self.dropout = nn.Dropout(0.5)
        self.fc2     = nn.Linear(128, 2)

    def forward(self, x):
        x = self.pool(torch.relu(self.conv1(x)))
        x = self.pool(torch.relu(self.conv2(x)))
        x = x.view(x.size(0), -1)
        x = self.dropout(torch.relu(self.fc1(x)))
        return self.fc2(x)


class SpectrogramCNN_C(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv_layers = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, padding=1), nn.ReLU(), nn.MaxPool2d(2, 2),
            nn.Conv2d(16, 32, kernel_size=3, padding=1), nn.ReLU(), nn.MaxPool2d(2, 2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1), nn.ReLU(), nn.AdaptiveAvgPool2d((1, 1))
        )
        self.classifier = nn.Sequential(
            nn.Linear(64, 32), nn.ReLU(), nn.Dropout(0.5), nn.Linear(32, 2)
        )

    def forward(self, x):
        x = self.conv_layers(x)
        x = x.view(x.size(0), -1)
        return self.classifier(x)


ARCHITECTURES = [SpectrogramCNN_A, SpectrogramCNN_B, SpectrogramCNN_C]
ARCH_NAMES    = ["A(gap+64)", "B(padding+128)", "C(3layer)"]


# ── Preprocessing ─────────────────────────────────────────────────────────────
def pad_or_truncate(w):
    n = w.size(1)
    if n > MAX_LEN: return w[:, :MAX_LEN]
    if n < MAX_LEN: return torch.nn.functional.pad(w, (0, MAX_LEN - n))
    return w


def normalize_rms(waveform, target):
    rms = waveform.pow(2).mean().sqrt()
    if rms > 1e-6:
        waveform = waveform * (target / rms)
    return torch.clamp(waveform, -1.0, 1.0)


def make_spec(waveform):
    w = pad_or_truncate(waveform)
    return transform(w).unsqueeze(0)


# ── Signals at raw mic level (loud, before normalization) ─────────────────────
def make_sine(freq, seconds=3):
    t = torch.linspace(0, seconds, int(SAMPLE_RATE * seconds))
    return (0.3 * torch.sin(2 * math.pi * freq * t)).unsqueeze(0)

def make_voice(seconds=3):
    t   = torch.linspace(0, seconds, int(SAMPLE_RATE * seconds))
    sig = torch.zeros_like(t)
    for h, a in [(150, 0.5), (300, 0.3), (600, 0.15), (1200, 0.05)]:
        sig = sig + a * torch.sin(2 * math.pi * h * t)
    return (sig / sig.abs().max() * 0.3).unsqueeze(0)

def make_noise(seconds=3):
    return (torch.rand(1, int(SAMPLE_RATE * seconds)) * 2 - 1) * 0.3

RAW_SIGNALS = (
    [make_sine(f) for f in [100, 200, 300, 440, 800, 1200, 2000, 3000]] +
    [make_voice(s) for s in [2, 3, 4]] +
    [make_noise(s) for s in [2, 3, 4]] +
    [(torch.rand(1, MAX_LEN) * 2 - 1) * 0.3 for _ in range(4)]
)


# ── Load helpers ──────────────────────────────────────────────────────────────
def try_load(path, arch_class):
    try:
        m = arch_class()
        m.load_state_dict(torch.load(path, map_location="cpu"))
        m.eval()
        return m
    except Exception:
        return None


def run_signals(model, signals):
    b, s = 0, 0
    with torch.no_grad():
        for sig in signals:
            try:
                spec  = make_spec(sig)
                probs = torch.softmax(model(spec), dim=1)[0]
                pred  = int(torch.argmax(probs).item())
                if pred == 0: b += 1
                else:         s += 1
            except Exception:
                pass
    return b, s


# ── Main ──────────────────────────────────────────────────────────────────────
print("\nLoading models...")
loaded_models = {}
for path in MODEL_FILES:
    if not os.path.exists(path):
        continue
    for cls, name in zip(ARCHITECTURES, ARCH_NAMES):
        m = try_load(path, cls)
        if m is not None:
            loaded_models[path] = (m, name)
            print("  Loaded {} ({})".format(path, name))
            break

if not loaded_models:
    print("No models found.")
    sys.exit(1)

print("\n" + "=" * 75)
print("  RMS SWEEP  — finding the best TARGET_RMS for live recording")
print("  Goal: closest to 50% Bonafide / 50% Spoof split")
print("=" * 75)
print("{:<10} ".format("RMS"), end="")
for path in loaded_models:
    short = path.replace("deepfake_", "").replace(".pth", "")
    print("{:<22}".format(short), end="")
print()
print("-" * 75)

# Track best result per model
best_per_model = {}   # path -> (best_rms, best_balance, b, s)

for rms_val in RMS_VALUES:
    normalized = [normalize_rms(sig, rms_val) for sig in RAW_SIGNALS]
    n = len(normalized)

    print("{:<10.3f} ".format(rms_val), end="")
    for path, (model, arch) in loaded_models.items():
        b, s = run_signals(model, normalized)
        balance = abs(b - s)
        marker = " <--" if balance == 0 else ""

        # Track the most balanced result for this model
        if path not in best_per_model or balance < best_per_model[path][1]:
            best_per_model[path] = (rms_val, balance, b, s)

        col = "B{}% S{}%{}".format(
            round(b / n * 100), round(s / n * 100), marker)
        print("{:<22}".format(col), end="")
    print()

# ── Final recommendation ──────────────────────────────────────────────────────
print("\n" + "=" * 75)
print("  BEST SETTINGS PER MODEL")
print("=" * 75)

candidates = []
for path, (best_rms, best_balance, b, s) in best_per_model.items():
    n = len(RAW_SIGNALS)
    arch = loaded_models[path][1]
    print("\n  {}  ({})".format(path, arch))
    print("    Best TARGET_RMS : {}".format(best_rms))
    print("    Split at that RMS: Bonafide {}/{}  Spoof {}/{}".format(b, n, s, n))
    print("    Balance score   : {} (0=perfect)".format(best_balance))
    candidates.append((best_balance, best_rms, path, arch, b, s))

# Sort by balance (lowest = most balanced)
candidates.sort(key=lambda x: x[0])
best_balance, best_rms, best_path, best_arch, best_b, best_s = candidates[0]

n = len(RAW_SIGNALS)
print("\n" + "=" * 75)
print("  RECOMMENDATION")
print("=" * 75)
print("  Model      : {}".format(best_path))
print("  Architecture: {}".format(best_arch))
print("  TARGET_RMS : {}".format(best_rms))
print("  Split      : Bonafide {}/{}  Spoof {}/{}".format(best_b, n, best_s, n))
print()
print("  In app.py set:")
print("    TEMPERATURE = 2.5")
print("    TARGET_RMS  = {}".format(best_rms))
print('    model.load_state_dict(torch.load("{}", map_location="cpu"))'.format(best_path))
print("=" * 75)
print()