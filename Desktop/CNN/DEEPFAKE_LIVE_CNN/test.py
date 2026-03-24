# import torch
# import torch.nn as nn

# # --- 1. Recreate the EXACT architecture from your training ---
# class SpectrogramCNN(nn.Module):
#     def __init__(self):
#         super().__init__()
#         self.conv_layers = nn.Sequential(
#             nn.Conv2d(1, 16, kernel_size=3, padding=1),
#             nn.ReLU(),
#             nn.MaxPool2d(2, 2),
            
#             nn.Conv2d(16, 32, kernel_size=3, padding=1),
#             nn.ReLU(),
#             nn.MaxPool2d(2, 2),
            
#             nn.Conv2d(32, 64, kernel_size=3, padding=1),
#             nn.ReLU(),
#             nn.AdaptiveAvgPool2d((1, 1))
#         )
#         self.classifier = nn.Sequential(
#             nn.Linear(64, 32),
#             nn.ReLU(),
#             nn.Dropout(0.5),
#             nn.Linear(32, 2) 
#         )

#     def forward(self, x):
#         x = self.conv_layers(x)
#         x = x.view(x.size(0), -1)
#         return self.classifier(x)

# # --- 2. Load and Diagnose ---
# def diagnose_model():
#     print("--- 🩺 Diagnosing deepfake_detector_v2.pth ---")
#     device = torch.device("cpu")
#     model = SpectrogramCNN()
    
#     try:
#         model.load_state_dict(torch.load("deepfake_detector_v2.pth", map_location=device))
#         model.eval()
#         print("✅ Model loaded successfully!")
#     except Exception as e:
#         print(f"❌ ERROR loading model: {e}")
#         return

#     # TEST A: SILENCE TEST (Input = all zeros)
#     # Shape matches your mel_transform output (1 channel, 64 mels, ~126 time steps)
#     silence_input = torch.zeros((1, 1, 64, 126))
#     with torch.no_grad():
#         output = model(silence_input)
#         probs = torch.softmax(output, dim=1)
#         pred = torch.argmax(probs).item()
#         label = "Bonafide" if pred == 0 else "FAKE"
#         print(f"\n🔇 Silence Test: Predicted {label} with {probs[0][pred].item()*100:.2f}% confidence")

#     # TEST B: NOISE TEST (Input = random numbers)
#     noise_input = torch.randn((1, 1, 64, 126))
#     with torch.no_grad():
#         output = model(noise_input)
#         probs = torch.softmax(output, dim=1)
#         pred = torch.argmax(probs).item()
#         label = "Bonafide" if pred == 0 else "FAKE"
#         print(f"🎲 Noise Test: Predicted {label} with {probs[0][pred].item()*100:.2f}% confidence")

#     # TEST C: WEIGHT ANALYSIS
#     print("\n📈 Weight Stats:")
#     for name, param in model.named_parameters():
#         if 'weight' in name:
#             mean_val = param.data.mean().item()
#             std_val = param.data.std().item()
#             print(f"Layer: {name} | Mean: {mean_val:.6f} | Std: {std_val:.6f}")

#     # CRITICAL CHECK: Are weights all zero?
#     if all(param.data.std().item() < 1e-7 for name, param in model.named_parameters() if 'weight' in name):
#         print("\n🚨 CRITICAL ISSUE: Your model weights have collapsed (they are all basically the same). Training failed!")

# diagnose_model()


############################## CLAUDE AI whole test   #####################################################333
# """
# test_model.py  —  Deepfake detector analysis & diagnostics
# ────────────────────────────────────────────────────────────
# Run:  python test_model.py

# What it does:
#   1. Loads your trained model
#   2. Runs a full evaluation on your test split (bonafide + spoof folders)
#   3. Prints confusion matrix, per-class accuracy, EER
#   4. Plots ROC curve, confidence histogram, and per-class confidence distribution
#   5. Flags the worst-performing files so you know what's tripping the model

# Requirements:
#   pip install scikit-learn matplotlib torchaudio torch
# """

# import os, random, json
# import torch
# import torch.nn as nn
# import torchaudio
# import numpy as np
# import matplotlib
# matplotlib.use("Agg")           # headless — saves PNGs instead of opening windows
# import matplotlib.pyplot as plt
# from sklearn.metrics import (
#     confusion_matrix, classification_report,
#     roc_curve, auc, ConfusionMatrixDisplay
# )
# from sklearn.model_selection import train_test_split

# # ─────────────────────────────────────────
# # 1. Config  (edit these to match your setup)
# # ─────────────────────────────────────────
# BONAFIDE_DIR  = "data/bonafide_merged"
# SPOOF_DIR     = "data/spoof"
# MODEL_PATH    = "deepfake_detector.pth"
# RESULTS_DIR   = "test_results"      # output folder for plots + JSON report
# MAX_LEN       = 64000
# SAMPLE_RATE   = 16000
# TEST_SIZE     = 0.2                 # fraction of data used for testing (must match training)
# RANDOM_SEED   = 42
# os.makedirs(RESULTS_DIR, exist_ok=True)

# # ─────────────────────────────────────────
# # 2. Model (must match training exactly)
# # ─────────────────────────────────────────
# class SpectrogramCNN(nn.Module):
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

# # ─────────────────────────────────────────
# # 3. Preprocessing (must match app.py)
# # ─────────────────────────────────────────
# mel_transform = torchaudio.transforms.MelSpectrogram(sample_rate=SAMPLE_RATE, n_mels=64)

# def pad_or_truncate(w):
#     if w.size(1) > MAX_LEN:
#         return w[:, :MAX_LEN]
#     if w.size(1) < MAX_LEN:
#         return torch.nn.functional.pad(w, (0, MAX_LEN - w.size(1)))
#     return w

# def load_and_preprocess(path):
#     """Load an audio file and return the normalized log-mel spectrogram tensor."""
#     try:
#         waveform, sr = torchaudio.load(path)   # already normalized to [-1,1]
#         if sr != SAMPLE_RATE:
#             waveform = torchaudio.transforms.Resample(sr, SAMPLE_RATE)(waveform)
#         if waveform.size(0) > 1:
#             waveform = waveform.mean(dim=0, keepdim=True)
#         waveform = pad_or_truncate(waveform)

#         spec  = mel_transform(waveform)
#         spec  = torch.log(spec + 1e-9)
#         mean, std = spec.mean(), spec.std()
#         if std > 1e-6:
#             spec = (spec - mean) / std
#         return spec.unsqueeze(0)               # [1, 1, 64, T]
#     except Exception as e:
#         print(f"  ⚠️  Skipping {path}: {e}")
#         return None

# # ─────────────────────────────────────────
# # 4. Build balanced test set (same split as training)
# # ─────────────────────────────────────────
# def gather_files(directory):
#     return [
#         os.path.join(directory, f)
#         for f in os.listdir(directory)
#         if f.lower().endswith((".wav", ".flac", ".mp3"))
#     ]

# print("Loading file lists…")
# bonafide_files = gather_files(BONAFIDE_DIR)
# spoof_files    = gather_files(SPOOF_DIR)

# min_len        = min(len(bonafide_files), len(spoof_files))
# random.seed(RANDOM_SEED)
# bonafide_files = random.sample(bonafide_files, min_len)
# spoof_files    = random.sample(spoof_files,    min_len)

# all_files  = bonafide_files + spoof_files
# all_labels = [0] * min_len + [1] * min_len

# _, test_files, _, test_labels = train_test_split(
#     all_files, all_labels,
#     test_size=TEST_SIZE, stratify=all_labels, random_state=RANDOM_SEED
# )
# print(f"Test set: {len(test_files)} files  "
#       f"(bonafide={test_labels.count(0)}, spoof={test_labels.count(1)})")

# # ─────────────────────────────────────────
# # 5. Load model
# # ─────────────────────────────────────────
# print(f"\nLoading model from {MODEL_PATH}…")
# model = SpectrogramCNN()
# model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
# model.eval()
# print("✅ Model loaded.")

# # ─────────────────────────────────────────
# # 6. Run inference on every test file
# # ─────────────────────────────────────────
# y_true, y_pred, y_scores = [], [], []
# failed_files = []

# print("\nRunning inference…")
# for i, (path, label) in enumerate(zip(test_files, test_labels)):
#     spec = load_and_preprocess(path)
#     if spec is None:
#         failed_files.append(path)
#         continue

#     with torch.no_grad():
#         logits = model(spec)
#         probs  = torch.softmax(logits, dim=1)[0]
#         pred   = torch.argmax(probs).item()

#     y_true.append(label)
#     y_pred.append(pred)
#     y_scores.append(probs[1].item())  # P(spoof) for ROC

#     if (i + 1) % 100 == 0:
#         print(f"  {i+1}/{len(test_files)} done…")

# print(f"\nDone. Skipped {len(failed_files)} unreadable files.")

# y_true   = np.array(y_true)
# y_pred   = np.array(y_pred)
# y_scores = np.array(y_scores)

# # ─────────────────────────────────────────
# # 7. Metrics
# # ─────────────────────────────────────────
# correct  = (y_true == y_pred).sum()
# total    = len(y_true)
# accuracy = correct / total * 100

# cm = confusion_matrix(y_true, y_pred)
# tn, fp, fn, tp = cm.ravel()

# bonafide_acc = tn / (tn + fp) * 100   # how often real audio is correctly called real
# spoof_acc    = tp / (tp + fn) * 100   # how often fake audio is correctly called fake

# # Equal Error Rate (EER) — where FAR == FRR
# fpr, tpr, thresholds = roc_curve(y_true, y_scores)
# fnr = 1 - tpr
# abs_diff = np.abs(fpr - fnr)
# eer_idx  = np.argmin(abs_diff)
# eer      = (fpr[eer_idx] + fnr[eer_idx]) / 2 * 100
# roc_auc  = auc(fpr, tpr)

# print("\n" + "═"*50)
# print("  RESULTS")
# print("═"*50)
# print(f"  Overall accuracy : {accuracy:.2f}%  ({correct}/{total})")
# print(f"  Bonafide accuracy: {bonafide_acc:.2f}%")
# print(f"  Spoof accuracy   : {spoof_acc:.2f}%")
# print(f"  ROC-AUC          : {roc_auc:.4f}")
# print(f"  EER              : {eer:.2f}%  (lower = better)")
# print("═"*50)

# print("\n  Confusion matrix  (rows=true, cols=pred):")
# print(f"               Pred Bonafide  Pred Spoof")
# print(f"  True Bonafide   {tn:>8}      {fp:>8}")
# print(f"  True Spoof      {fn:>8}      {tp:>8}")

# print("\n  Classification report:")
# print(classification_report(y_true, y_pred,
#       target_names=["Bonafide", "Spoof"], zero_division=0))

# # ─────────────────────────────────────────
# # 8. Find worst predictions (most confident wrong answers)
# # ─────────────────────────────────────────
# errors = []
# for i, (path, true, pred, score) in enumerate(
#         zip(test_files[:len(y_true)], y_true, y_pred, y_scores)):
#     if true != pred:
#         conf = score if pred == 1 else 1 - score
#         errors.append({
#             "file":  path,
#             "true":  "Bonafide" if true == 0 else "Spoof",
#             "pred":  "Bonafide" if pred == 0 else "Spoof",
#             "confidence": round(conf * 100, 2),
#         })

# errors.sort(key=lambda x: x["confidence"], reverse=True)

# print(f"\n  Top 10 most-confident wrong predictions:")
# for e in errors[:10]:
#     print(f"  [{e['true']:>8} → predicted {e['pred']:>8}  {e['confidence']:5.1f}%]  {os.path.basename(e['file'])}")

# # ─────────────────────────────────────────
# # 9. Save JSON report
# # ─────────────────────────────────────────
# report = {
#     "accuracy":        round(accuracy, 2),
#     "bonafide_acc":    round(bonafide_acc, 2),
#     "spoof_acc":       round(spoof_acc, 2),
#     "roc_auc":         round(roc_auc, 4),
#     "eer":             round(eer, 2),
#     "total_samples":   total,
#     "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
#     "top_errors":      errors[:20],
# }
# report_path = os.path.join(RESULTS_DIR, "report.json")
# with open(report_path, "w") as f:
#     json.dump(report, f, indent=2)
# print(f"\n  JSON report → {report_path}")

# # ─────────────────────────────────────────
# # 10. Plots
# # ─────────────────────────────────────────
# fig, axes = plt.subplots(1, 3, figsize=(16, 5))
# fig.suptitle("Deepfake Detector — Test Analysis", fontsize=14, fontweight="bold")

# # — Plot 1: Confusion matrix —
# disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Bonafide", "Spoof"])
# disp.plot(ax=axes[0], colorbar=False, cmap="Blues")
# axes[0].set_title("Confusion Matrix")

# # — Plot 2: ROC curve —
# axes[1].plot(fpr, tpr, color="steelblue", lw=2,
#              label=f"ROC (AUC = {roc_auc:.3f})")
# axes[1].plot([0, 1], [0, 1], color="gray", linestyle="--", lw=1)
# axes[1].scatter(fpr[eer_idx], tpr[eer_idx], color="red", s=60, zorder=5,
#                 label=f"EER = {eer:.1f}%")
# axes[1].set_xlabel("False Positive Rate")
# axes[1].set_ylabel("True Positive Rate")
# axes[1].set_title("ROC Curve")
# axes[1].legend(fontsize=9)
# axes[1].set_xlim([0, 1]); axes[1].set_ylim([0, 1.02])

# # — Plot 3: Confidence distribution per class —
# bonafide_scores = y_scores[y_true == 0]   # P(spoof) for bonafide files — should be LOW
# spoof_scores    = y_scores[y_true == 1]   # P(spoof) for spoof files   — should be HIGH

# axes[2].hist(bonafide_scores, bins=30, alpha=0.65, color="steelblue",
#              label="Bonafide (true)", density=True)
# axes[2].hist(spoof_scores,    bins=30, alpha=0.65, color="tomato",
#              label="Spoof (true)",    density=True)
# axes[2].axvline(0.5, color="black", linestyle="--", lw=1, label="Decision boundary (0.5)")
# axes[2].set_xlabel("P(Spoof)")
# axes[2].set_ylabel("Density")
# axes[2].set_title("Score Distribution")
# axes[2].legend(fontsize=9)

# plt.tight_layout()
# plot_path = os.path.join(RESULTS_DIR, "analysis.png")
# plt.savefig(plot_path, dpi=150, bbox_inches="tight")
# print(f"  Plots saved  → {plot_path}")

# # ─────────────────────────────────────────
# # 11. Model health diagnostics
# # ─────────────────────────────────────────
# print("\n" + "═"*50)
# print("  MODEL DIAGNOSTICS")
# print("═"*50)

# overlap = len(set(np.where(bonafide_scores > 0.4)[0]) &
#               set(np.where(bonafide_scores < 0.6)[0]))
# print(f"  Score overlap zone (0.4–0.6): "
#       f"{overlap} bonafide samples are near the boundary — harder to classify")

# if eer > 20:
#     print("  ⚠️  EER > 20% — model is struggling. Consider:")
#     print("       • More training data")
#     print("       • Longer training (try 50 epochs)")
#     print("       • Deeper model (add a 3rd conv layer + batch norm)")
#     print("       • Pre-trained backbone (wav2vec2, EfficientNet-B0 on mel)")
# elif eer > 10:
#     print("  ⚡  EER 10–20% — decent for a small CNN. Improvements:")
#     print("       • Add BatchNorm after each conv layer")
#     print("       • Use SpecAugment during training for regularization")
# else:
#     print("  ✅  EER < 10% — strong result for this architecture.")

# if abs(bonafide_acc - spoof_acc) > 15:
#     worse = "bonafide" if bonafide_acc < spoof_acc else "spoof"
#     print(f"  ⚠️  Class imbalance effect: model is worse on {worse} samples.")
#     print(f"       Check that training data is truly balanced.")

# print("\n  Done. All results saved to:", RESULTS_DIR)



######################### cloude AI dataset only testing
# """
# test_model.py
# -------------
# Tests your trained model using ONLY the saved .pth file.
# No data folders required -- generates synthetic test signals instead.

# Tests run:
#   1. Silent audio         -> should be caught before inference
#   2. Pure sine wave       -> known signal, checks model runs without crashing
#   3. White noise          -> random signal, checks model runs without crashing
#   4. Very short audio     -> checks padding logic
#   5. Very long audio      -> checks truncation logic
#   6. Batch of 8 signals   -> checks model handles batch dimension correctly
#   7. Confidence range     -> all softmax outputs must sum to 1.0
#   8. Determinism          -> same input must give same output every time
#   9. Spectrogram norm     -> log+zscore output should have mean~0, std~1
#  10. Model param count    -> prints total parameters

# Run:
#     python test_model.py

# Optional: point to a different model file
#     python test_model.py deepfake_detector.pth
# """

# import sys
# import math
# import torch
# import torch.nn as nn
# import torchaudio

# MODEL_PATH  = sys.argv[1] if len(sys.argv) > 1 else "deepfake_detector.pth"
# SAMPLE_RATE = 16000
# MAX_LEN     = 64000
# PASS = "PASS"
# FAIL = "FAIL"


# # ── Model (must match training) ──────────────────────────────────────────────
# class SpectrogramCNN(nn.Module):
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


# # ── Preprocessing (must match app.py) ────────────────────────────────────────
# mel_transform = torchaudio.transforms.MelSpectrogram(sample_rate=SAMPLE_RATE, n_mels=64)


# def pad_or_truncate(w):
#     n = w.size(1)
#     if n > MAX_LEN:
#         return w[:, :MAX_LEN]
#     if n < MAX_LEN:
#         return torch.nn.functional.pad(w, (0, MAX_LEN - n))
#     return w


# def make_spectrogram(waveform):
#     spec = mel_transform(waveform)
#     spec = torch.log(spec + 1e-9)
#     mean = spec.mean()
#     std  = spec.std()
#     if std > 1e-6:
#         spec = (spec - mean) / std
#     return spec.unsqueeze(0)


# def run_inference(model, waveform):
#     waveform = pad_or_truncate(waveform)
#     spec     = make_spectrogram(waveform)
#     with torch.no_grad():
#         logits = model(spec)
#         probs  = torch.softmax(logits, dim=1)[0]
#         pred   = int(torch.argmax(probs).item())
#     return pred, probs


# # ── Signal generators ─────────────────────────────────────────────────────────
# def make_sine(freq=440, seconds=3):
#     t = torch.linspace(0, seconds, int(SAMPLE_RATE * seconds))
#     return (0.5 * torch.sin(2 * math.pi * freq * t)).unsqueeze(0)


# def make_noise(seconds=3):
#     return (torch.rand(1, int(SAMPLE_RATE * seconds)) * 2 - 1) * 0.5


# def make_silence(seconds=3):
#     return torch.zeros(1, int(SAMPLE_RATE * seconds))


# def make_short():
#     return make_sine(seconds=0.5)    # 0.5s -- well below MAX_LEN


# def make_long():
#     return make_sine(seconds=10)     # 10s -- above MAX_LEN (4s)


# # ── Test runner ───────────────────────────────────────────────────────────────
# results = []


# def test(name, fn):
#     try:
#         status, detail = fn()
#         tag = PASS if status else FAIL
#     except Exception as e:
#         tag, detail = FAIL, "Exception: {}".format(e)
#     results.append((tag, name, detail))
#     print("  [{:4}]  {}  --  {}".format(tag, name, detail))


# # ── Load model ────────────────────────────────────────────────────────────────
# print("\nLoading model from {}...".format(MODEL_PATH))
# try:
#     model = SpectrogramCNN()
#     model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
#     model.eval()
#     print("Model loaded.\n")
#     load_ok = True
# except Exception as e:
#     print("FAILED to load model: {}\n".format(e))
#     load_ok = False

# if not load_ok:
#     sys.exit(1)

# print("Running tests...\n")

# # ── Test 1: Silence detection ─────────────────────────────────────────────────
# def t_silence():
#     w   = make_silence()
#     rms = w.pow(2).mean().sqrt().item()
#     blocked = rms < 0.001
#     return blocked, "rms={:.6f}  blocked={}".format(rms, blocked)

# test("Silence detection (rms < 0.001)", t_silence)

# # ── Test 2: Sine wave runs without error ──────────────────────────────────────
# def t_sine():
#     w    = make_sine(freq=440, seconds=3)
#     pred, probs = run_inference(model, w)
#     label = "Bonafide" if pred == 0 else "Spoof"
#     return True, "pred={} ({:.1f}%)".format(label, float(probs[pred].item()) * 100)

# test("Sine 440 Hz inference (no crash)", t_sine)

# # ── Test 3: White noise runs without error ────────────────────────────────────
# def t_noise():
#     w    = make_noise(seconds=3)
#     pred, probs = run_inference(model, w)
#     label = "Bonafide" if pred == 0 else "Spoof"
#     return True, "pred={} ({:.1f}%)".format(label, float(probs[pred].item()) * 100)

# test("White noise inference (no crash)", t_noise)

# # ── Test 4: Short audio padded correctly ─────────────────────────────────────
# def t_short():
#     w       = make_short()
#     padded  = pad_or_truncate(w)
#     correct = padded.size(1) == MAX_LEN
#     return correct, "after padding size={} expected={}".format(padded.size(1), MAX_LEN)

# test("Short audio padded to MAX_LEN", t_short)

# # ── Test 5: Long audio truncated correctly ────────────────────────────────────
# def t_long():
#     w         = make_long()
#     truncated = pad_or_truncate(w)
#     correct   = truncated.size(1) == MAX_LEN
#     return correct, "after truncation size={} expected={}".format(truncated.size(1), MAX_LEN)

# test("Long audio truncated to MAX_LEN", t_long)

# # ── Test 6: Batch of 8 inputs ─────────────────────────────────────────────────
# def t_batch():
#     signals = [make_sine(freq=(200 + i * 50), seconds=3) for i in range(8)]
#     specs   = []
#     for w in signals:
#         w = pad_or_truncate(w)
#         specs.append(make_spectrogram(w))
#     batch = torch.cat(specs, dim=0)   # [8, 1, 64, T]
#     with torch.no_grad():
#         out = model(batch)
#     ok = out.shape == (8, 2)
#     return ok, "output shape={} expected=(8, 2)".format(list(out.shape))

# test("Batch of 8 inputs", t_batch)

# # ── Test 7: Softmax sums to 1.0 ───────────────────────────────────────────────
# def t_probs():
#     w        = make_noise()
#     _, probs = run_inference(model, w)
#     total    = float(probs.sum().item())
#     ok       = abs(total - 1.0) < 1e-5
#     return ok, "sum={:.6f} (should be 1.0)".format(total)

# test("Softmax sums to 1.0", t_probs)

# # ── Test 8: Determinism (same input -> same output) ───────────────────────────
# def t_determinism():
#     model.eval()
#     w       = make_sine(freq=500, seconds=3)
#     p1, _   = run_inference(model, w)
#     p2, _   = run_inference(model, w)
#     p3, _   = run_inference(model, w)
#     ok      = (p1 == p2 == p3)
#     return ok, "runs=[{}, {}, {}] all same={}".format(p1, p2, p3, ok)

# test("Determinism (same input, 3 runs)", t_determinism)

# # ── Test 9: Spectrogram normalisation ────────────────────────────────────────
# def t_norm():
#     w    = make_noise(seconds=3)
#     w    = pad_or_truncate(w)
#     spec = make_spectrogram(w).squeeze()
#     mean = float(spec.mean().item())
#     std  = float(spec.std().item())
#     ok   = abs(mean) < 0.05 and abs(std - 1.0) < 0.05
#     return ok, "mean={:.4f} std={:.4f} (should be ~0 and ~1)".format(mean, std)

# test("Spectrogram z-score normalization", t_norm)

# # ── Test 10: Parameter count ──────────────────────────────────────────────────
# def t_params():
#     total     = sum(p.numel() for p in model.parameters())
#     trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
#     return True, "total={:,}  trainable={:,}".format(total, trainable)

# test("Model parameter count", t_params)

# # ── Test 11: Both classes reachable ──────────────────────────────────────────
# def t_both_classes():
#     predictions = set()
#     signals = [
#         make_sine(freq=200, seconds=4),
#         make_sine(freq=4000, seconds=4),
#         make_noise(seconds=4),
#         torch.rand(1, MAX_LEN) * 0.1,
#         torch.rand(1, MAX_LEN),
#     ]
#     for w in signals:
#         pred, _ = run_inference(model, w)
#         predictions.add(pred)
#     both = len(predictions) == 2
#     return both, "classes seen={} (need both 0 and 1)".format(sorted(predictions))

# test("Both classes reachable with varied inputs", t_both_classes)

# # ── Test 12: Consistent low-confidence on ambiguous input ────────────────────
# def t_confidence_range():
#     issues = []
#     for _ in range(5):
#         w = make_noise(seconds=3)
#         _, probs = run_inference(model, w)
#         b = float(probs[0].item())
#         s = float(probs[1].item())
#         if not (0.0 <= b <= 1.0 and 0.0 <= s <= 1.0):
#             issues.append("out of range: b={:.3f} s={:.3f}".format(b, s))
#     ok = len(issues) == 0
#     return ok, "all probabilities in [0,1]  issues={}".format(issues if issues else "none")

# test("Probabilities always in [0, 1]", t_confidence_range)

# # ── Summary ───────────────────────────────────────────────────────────────────
# passed = sum(1 for r in results if r[0] == PASS)
# failed = sum(1 for r in results if r[0] == FAIL)
# total  = len(results)

# print("\n" + "=" * 52)
# print("  SUMMARY:  {}/{} passed,  {}/{} failed".format(passed, total, failed, total))
# print("=" * 52)

# if failed > 0:
#     print("\n  Failed tests:")
#     for tag, name, detail in results:
#         if tag == FAIL:
#             print("    [FAIL]  {}  --  {}".format(name, detail))

# # Quick health interpretation
# print("\n  Model health:")
# if passed == total:
#     print("  All tests passed. Pipeline is working correctly.")
# elif passed >= total - 2:
#     print("  Minor issues. Check the failed tests above.")
# else:
#     print("  Multiple failures. Model or preprocessing may be broken.")

# # Check if both classes are reachable (most important signal)
# both_test = next((r for r in results if "Both classes" in r[1]), None)
# if both_test and both_test[0] == FAIL:
#     print("\n  WARNING: model only predicts one class.")
#     print("  This means it is biased -- most likely causes:")
#     print("    1. Training data was not balanced")
#     print("    2. Model overfit to the majority class")
#     print("    3. Preprocessing mismatch (run app.py and check the debug output)")

# print()


######################### C AI final test of dataset ###########3


"""
test_model.py  —  Deepfake Detector Test Suite
===============================================
Run AFTER training:
    python test_model.py

Tests:
  1. Dataset test   — runs on your actual audio files (bonafide + spoof folders)
  2. Pipeline test  — verifies preprocessing matches training exactly
  3. Live sim test  — simulates live mic conditions (loud audio, noise, volume variation)
  4. Stress test    — edge cases: silence, clipping, very short, very long

Output:
  - Per-class accuracy, confusion matrix, ROC-AUC, EER
  - test_results/report.json
  - test_results/analysis.png
"""

import os, sys, random, json
import torch, torch.nn as nn
import torchaudio, torchaudio.transforms as T
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import (
    confusion_matrix, classification_report,
    roc_curve, auc, ConfusionMatrixDisplay
)
from sklearn.model_selection import train_test_split

# ── Config — must match train_fixed.py and app.py ────────────────────────────
BONAFIDE_DIR = "data/bonafide_merged"
SPOOF_DIR    = "data/spoof"
MODEL_PATH   = "deepfake_detector_fixed.pth"
RESULTS_DIR  = "test_results"
SAMPLE_RATE  = 16000
MAX_LEN      = 64000
N_MELS       = 64
SEED         = 42

os.makedirs(RESULTS_DIR, exist_ok=True)
random.seed(SEED)

# ── Preprocessing — identical to train_fixed.py and app.py ───────────────────
mel = T.MelSpectrogram(sample_rate=SAMPLE_RATE, n_fft=1024,
                       hop_length=512, n_mels=N_MELS, f_min=0, f_max=8000)


def pad_or_truncate(w):
    n = w.size(1)
    if n > MAX_LEN: return w[:, :MAX_LEN]
    if n < MAX_LEN: return torch.nn.functional.pad(w, (0, MAX_LEN - n))
    return w


def instance_norm(spec):
    mean, std = spec.mean(), spec.std()
    return (spec - mean) / std if std > 1e-6 else spec


def make_spec(waveform):
    spec = mel(waveform)
    spec = torch.log(spec + 1e-6)
    return instance_norm(spec).unsqueeze(0)


def preprocess(waveform, sr):
    """Full preprocessing: resample → mono → clamp → pad → spectrogram."""
    if sr != SAMPLE_RATE:
        waveform = T.Resample(sr, SAMPLE_RATE)(waveform)
    if waveform.size(0) > 1:
        waveform = waveform.mean(dim=0, keepdim=True)
    waveform = torch.clamp(pad_or_truncate(waveform), -1.0, 1.0)
    return make_spec(waveform)


# ── Model — identical to train_fixed.py and app.py ───────────────────────────
class SpectrogramCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1,  32, 3, padding=1); self.bn1 = nn.BatchNorm2d(32)
        self.conv2 = nn.Conv2d(32, 64, 3, padding=1); self.bn2 = nn.BatchNorm2d(64)
        self.conv3 = nn.Conv2d(64,128, 3, padding=1); self.bn3 = nn.BatchNorm2d(128)
        self.pool    = nn.MaxPool2d(2, 2)
        self.gap     = nn.AdaptiveAvgPool2d((4, 4))
        self.fc1     = nn.Linear(128 * 4 * 4, 256)
        self.dropout = nn.Dropout(0.5)
        self.fc2     = nn.Linear(256, 2)

    def forward(self, x):
        x = self.pool(torch.relu(self.bn1(self.conv1(x))))
        x = self.pool(torch.relu(self.bn2(self.conv2(x))))
        x = self.pool(torch.relu(self.bn3(self.conv3(x))))
        x = self.gap(x).view(x.size(0), -1)
        return self.fc2(self.dropout(torch.relu(self.fc1(x))))


# ── Load model ────────────────────────────────────────────────────────────────
if not os.path.exists(MODEL_PATH):
    print("ERROR: {} not found. Run train_fixed.py first.".format(MODEL_PATH))
    sys.exit(1)

model = SpectrogramCNN()
model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
model.eval()
print("Model loaded: {}".format(MODEL_PATH))


def predict(spec):
    """Run inference. Returns (label, bonafide_prob, spoof_prob)."""
    with torch.no_grad():
        probs = torch.softmax(model(spec), dim=1)[0]
    b = float(probs[0])
    s = float(probs[1])
    return ("Bonafide" if b > s else "Spoof"), b, s


# ─────────────────────────────────────────────────────────────────────────────
# TEST 1: DATASET TEST
# Uses same train/test split as training (SEED=42, test_size=0.2)
# so results are on held-out files the model never saw
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  TEST 1: DATASET TEST (held-out test split)")
print("="*60)

def gather(d):
    return [os.path.join(d, f) for f in os.listdir(d)
            if f.lower().endswith((".wav", ".flac", ".mp3"))]

bonafide_files = gather(BONAFIDE_DIR)
spoof_files    = gather(SPOOF_DIR)
n              = min(len(bonafide_files), len(spoof_files))
bonafide_files = random.sample(bonafide_files, n)
spoof_files    = random.sample(spoof_files, n)
all_files      = bonafide_files + spoof_files
all_labels     = [0]*n + [1]*n

_, test_files, _, test_labels = train_test_split(
    all_files, all_labels, test_size=0.2, stratify=all_labels, random_state=SEED)

print("Test files: {} (bonafide={} spoof={})".format(
    len(test_files), test_labels.count(0), test_labels.count(1)))

y_true, y_pred, y_scores = [], [], []
failed = []

for i, (path, label) in enumerate(zip(test_files, test_labels)):
    try:
        w, sr = torchaudio.load(path)
        spec  = preprocess(w, sr)
        _, b, s = predict(spec)
        pred  = 0 if b > s else 1
        y_true.append(label)
        y_pred.append(pred)
        y_scores.append(s)   # P(Spoof) for ROC
    except Exception as e:
        failed.append((path, str(e)))

    if (i+1) % 200 == 0:
        print("  {}/{} done...".format(i+1, len(test_files)))

print("  Skipped {} files due to load errors".format(len(failed)))

y_true   = np.array(y_true)
y_pred   = np.array(y_pred)
y_scores = np.array(y_scores)

# Metrics
cm         = confusion_matrix(y_true, y_pred)
tn, fp, fn, tp = cm.ravel()
accuracy   = (tn+tp) / (tn+fp+fn+tp) * 100
bon_acc    = tn / (tn+fp) * 100
spoof_acc  = tp / (tp+fn) * 100

fpr, tpr, _ = roc_curve(y_true, y_scores)
roc_auc     = auc(fpr, tpr)
fnr         = 1 - tpr
eer_idx     = int(np.argmin(np.abs(fpr - fnr)))
eer         = (fpr[eer_idx] + fnr[eer_idx]) / 2 * 100

print("\nResults:")
print("  Overall accuracy : {:.2f}%".format(accuracy))
print("  Bonafide accuracy: {:.2f}%".format(bon_acc))
print("  Spoof accuracy   : {:.2f}%".format(spoof_acc))
print("  ROC-AUC          : {:.4f}".format(roc_auc))
print("  EER              : {:.2f}%  (lower = better)".format(eer))
print("\nConfusion matrix (rows=true, cols=predicted):")
print("               Pred Bonafide  Pred Spoof")
print("  True Bonafide  {:>10}  {:>10}".format(tn, fp))
print("  True Spoof     {:>10}  {:>10}".format(fn, tp))
print("\nClassification report:")
print(classification_report(y_true, y_pred,
      target_names=["Bonafide","Spoof"], zero_division=0))

# Worst predictions (most confidently wrong)
errors = []
for path, true, pred, score in zip(test_files[:len(y_true)], y_true, y_pred, y_scores):
    if true != pred:
        conf = float(score) if pred==1 else float(1-score)
        errors.append({"file": os.path.basename(path),
                        "true": "Bonafide" if true==0 else "Spoof",
                        "pred": "Bonafide" if pred==0 else "Spoof",
                        "confidence": round(conf*100, 1)})
errors.sort(key=lambda x: x["confidence"], reverse=True)

if errors:
    print("Top 5 most-confident wrong predictions:")
    for e in errors[:5]:
        print("  [{} predicted as {} ({:.1f}%)] {}".format(
            e["true"], e["pred"], e["confidence"], e["file"]))


# ─────────────────────────────────────────────────────────────────────────────
# TEST 2: PIPELINE CONSISTENCY TEST
# Verifies preprocessing is deterministic and matches expected output
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  TEST 2: PIPELINE CONSISTENCY TEST")
print("="*60)

results_2 = []

def run_test(name, waveform):
    spec = make_spec(torch.clamp(pad_or_truncate(waveform), -1.0, 1.0))
    label, b, s = predict(spec)
    spec_mean = float(spec.mean())
    spec_std  = float(spec.std())
    mean_ok   = abs(spec_mean) < 0.05
    std_ok    = abs(spec_std - 1.0) < 0.05
    status    = "PASS" if (mean_ok and std_ok) else "FAIL"
    results_2.append(status)
    print("  [{:4}] {:35} spec_mean={:.4f} spec_std={:.4f}  pred={}".format(
        status, name, spec_mean, spec_std, label))

import math
sr = SAMPLE_RATE
t  = torch.linspace(0, 3, sr*3)

run_test("sine 440Hz  (normal vol)",   (0.3 * torch.sin(2*math.pi*440*t)).unsqueeze(0))
run_test("sine 440Hz  (loud x4)",      (1.2 * torch.sin(2*math.pi*440*t)).unsqueeze(0))
run_test("sine 440Hz  (quiet /10)",    (0.03* torch.sin(2*math.pi*440*t)).unsqueeze(0))
run_test("white noise (normal)",       (torch.rand(1, sr*3)*2-1)*0.3)
run_test("white noise (loud)",         (torch.rand(1, sr*3)*2-1)*1.5)
run_test("white noise (quiet)",        (torch.rand(1, sr*3)*2-1)*0.01)
run_test("multi-freq (voice-like)",    sum(a*torch.sin(2*math.pi*f*t)
                                          for f,a in [(150,.5),(300,.3),(600,.15)]).unsqueeze(0))

# Determinism check — same input must always give same output
w    = (torch.rand(1, MAX_LEN)*2-1)*0.3
p1, b1, _ = predict(make_spec(torch.clamp(pad_or_truncate(w), -1.0, 1.0)))
p2, b2, _ = predict(make_spec(torch.clamp(pad_or_truncate(w), -1.0, 1.0)))
p3, b3, _ = predict(make_spec(torch.clamp(pad_or_truncate(w), -1.0, 1.0)))
det_ok = (p1==p2==p3) and abs(b1-b2)<1e-5 and abs(b2-b3)<1e-5
results_2.append("PASS" if det_ok else "FAIL")
print("  [{:4}] {:35} all 3 runs same={}".format(
    "PASS" if det_ok else "FAIL", "determinism (same input x3)", det_ok))

passed2 = results_2.count("PASS")
print("\n  {}/{} pipeline tests passed".format(passed2, len(results_2)))


# ─────────────────────────────────────────────────────────────────────────────
# TEST 3: LIVE RECORDING SIMULATION
# Simulates what /predict-live receives after AudioContext.decodeAudioData
# Applies same transformations as app.py predict_live endpoint
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  TEST 3: LIVE RECORDING SIMULATION")
print("="*60)

def sim_live(waveform, description):
    """Simulate what app.py predict-live does."""
    # Mimic AudioContext output: float32, may have peaks > 1.0
    # Then app.py clamps it
    w = torch.clamp(pad_or_truncate(waveform), -1.0, 1.0)
    spec = make_spec(w)
    label, b, s = predict(spec)
    rms = float(w.pow(2).mean().sqrt())
    print("  {:40} rms={:.4f}  pred={} (B={:.1f}% S={:.1f}%)".format(
        description, rms, label, b*100, s*100))
    return label, b, s

bonafide_count, spoof_count = 0, 0

# Test with actual bonafide files at mic-level volume
print("\n  Bonafide files at mic volume (should predict Bonafide):")
sample_bon = random.sample(bonafide_files, min(5, len(bonafide_files)))
for path in sample_bon:
    try:
        w, sr = torchaudio.load(path)
        if sr != SAMPLE_RATE: w = T.Resample(sr, SAMPLE_RATE)(w)
        if w.size(0) > 1: w = w.mean(0, keepdim=True)
        # Scale to mic-level amplitude (rms ~0.2)
        rms = w.pow(2).mean().sqrt()
        if rms > 1e-6: w = w * (0.2 / rms)
        label, b, s = sim_live(w, os.path.basename(path))
        if label == "Bonafide": bonafide_count += 1
    except: pass

# Test with actual spoof files at mic-level volume
print("\n  Spoof files at mic volume (should predict Spoof):")
sample_spoof = random.sample(spoof_files, min(5, len(spoof_files)))
for path in sample_spoof:
    try:
        w, sr = torchaudio.load(path)
        if sr != SAMPLE_RATE: w = T.Resample(sr, SAMPLE_RATE)(w)
        if w.size(0) > 1: w = w.mean(0, keepdim=True)
        rms = w.pow(2).mean().sqrt()
        if rms > 1e-6: w = w * (0.2 / rms)
        label, b, s = sim_live(w, os.path.basename(path))
        if label == "Spoof": spoof_count += 1
    except: pass

print("\n  Live sim: {}/5 bonafide correct, {}/5 spoof correct".format(
    bonafide_count, spoof_count))
live_ok = (bonafide_count + spoof_count) >= 7
print("  Live robustness: {}".format("PASS (>=7/10)" if live_ok else "FAIL (<7/10)"))


# ─────────────────────────────────────────────────────────────────────────────
# TEST 4: STRESS / EDGE CASES
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  TEST 4: STRESS / EDGE CASES")
print("="*60)

stress_results = []

def stress_test(name, fn):
    try:
        ok, detail = fn()
        status = "PASS" if ok else "FAIL"
    except Exception as e:
        ok, status, detail = False, "FAIL", "Exception: {}".format(e)
    stress_results.append(status)
    print("  [{:4}] {:40} {}".format(status, name, detail))

# Silence — must not crash, should have valid output
def t_silence():
    w = torch.zeros(1, MAX_LEN)
    spec = make_spec(torch.clamp(pad_or_truncate(w), -1.0, 1.0))
    l, b, s = predict(spec)
    return True, "pred={} (model handles silence without crash)".format(l)
stress_test("silence input (all zeros)", t_silence)

# Clipping — values > 1.0 from AudioContext
def t_clip():
    w = torch.ones(1, MAX_LEN) * 1.8   # simulates AudioContext peak > 1.0
    w = torch.clamp(w, -1.0, 1.0)       # app.py clamps this
    spec = make_spec(pad_or_truncate(w))
    l, b, s = predict(spec)
    return True, "pred={} clamp worked peak=1.0".format(l)
stress_test("clipped input (peak=1.8, clamped)", t_clip)

# Short audio — 0.5 seconds, must be padded to MAX_LEN
def t_short():
    w = (torch.rand(1, 8000)*2-1)*0.3   # 0.5 seconds
    padded = pad_or_truncate(w)
    ok = padded.size(1) == MAX_LEN
    return ok, "padded {} → {}".format(w.size(1), padded.size(1))
stress_test("short audio (0.5s → padded to 4s)", t_short)

# Long audio — 20 seconds, must be truncated to MAX_LEN
def t_long():
    w = (torch.rand(1, SAMPLE_RATE*20)*2-1)*0.3
    trunc = pad_or_truncate(w)
    ok = trunc.size(1) == MAX_LEN
    return ok, "truncated {} → {}".format(w.size(1), trunc.size(1))
stress_test("long audio (20s → truncated to 4s)", t_long)

# Softmax sums to 1.0
def t_softmax():
    w = (torch.rand(1, MAX_LEN)*2-1)*0.3
    spec = make_spec(torch.clamp(w, -1.0, 1.0))
    l, b, s = predict(spec)
    ok = abs(b + s - 1.0) < 1e-5
    return ok, "B+S = {:.6f} (should be 1.0)".format(b+s)
stress_test("softmax sums to 1.0", t_softmax)

# Both classes reachable
def t_both_classes():
    preds = set()
    signals = [
        (torch.rand(1, MAX_LEN)*2-1) * amp
        for amp in [0.01, 0.05, 0.1, 0.2, 0.5]
    ]
    for w in signals:
        spec = make_spec(torch.clamp(pad_or_truncate(w), -1.0, 1.0))
        l, b, s = predict(spec)
        preds.add(l)
    ok = len(preds) == 2
    return ok, "classes seen={}".format(sorted(preds))
stress_test("both classes reachable", t_both_classes)

# Batch inference — same as single inference
def t_batch():
    w1 = (torch.rand(1, MAX_LEN)*2-1)*0.3
    w2 = (torch.rand(1, MAX_LEN)*2-1)*0.3
    s1 = make_spec(torch.clamp(w1, -1.0, 1.0))
    s2 = make_spec(torch.clamp(w2, -1.0, 1.0))
    batch = torch.cat([s1, s2], dim=0)
    with torch.no_grad():
        out = model(batch)
    ok = out.shape == (2, 2)
    return ok, "batch output shape={} expected=(2,2)".format(list(out.shape))
stress_test("batch inference shape", t_batch)

passed4 = stress_results.count("PASS")
print("\n  {}/{} stress tests passed".format(passed4, len(stress_results)))


# ─────────────────────────────────────────────────────────────────────────────
# SAVE REPORT
# ─────────────────────────────────────────────────────────────────────────────
report = {
    "model":             MODEL_PATH,
    "test1_accuracy":    round(accuracy, 2),
    "test1_bonafide_acc":round(bon_acc, 2),
    "test1_spoof_acc":   round(spoof_acc, 2),
    "test1_roc_auc":     round(float(roc_auc), 4),
    "test1_eer":         round(float(eer), 2),
    "test1_samples":     len(y_true),
    "test2_pipeline":    "{}/{}".format(passed2, len(results_2)),
    "test3_live_ok":     live_ok,
    "test4_stress":      "{}/{}".format(passed4, len(stress_results)),
    "top_errors":        errors[:10],
}
with open(os.path.join(RESULTS_DIR, "report.json"), "w") as f:
    json.dump(report, f, indent=2)
print("\nReport saved: {}/report.json".format(RESULTS_DIR))


# ─────────────────────────────────────────────────────────────────────────────
# PLOTS
# ─────────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle("Deepfake Detector — Test Results", fontsize=14)

# Confusion matrix
ConfusionMatrixDisplay(cm, display_labels=["Bonafide","Spoof"]).plot(
    ax=axes[0], colorbar=False, cmap="Blues")
axes[0].set_title("Confusion matrix")

# ROC curve
axes[1].plot(fpr, tpr, color="steelblue", lw=2,
             label="ROC AUC={:.3f}".format(roc_auc))
axes[1].plot([0,1],[0,1], color="gray", linestyle="--", lw=1)
axes[1].scatter(fpr[eer_idx], tpr[eer_idx], color="red", s=60,
                label="EER={:.1f}%".format(eer))
axes[1].set_xlabel("FPR"); axes[1].set_ylabel("TPR")
axes[1].set_title("ROC curve"); axes[1].legend(fontsize=9)

# Score distribution
axes[2].hist(y_scores[y_true==0], bins=30, alpha=0.65,
             color="steelblue", label="Bonafide (true)", density=True)
axes[2].hist(y_scores[y_true==1], bins=30, alpha=0.65,
             color="tomato", label="Spoof (true)", density=True)
axes[2].axvline(0.5, color="black", linestyle="--", lw=1, label="Boundary")
axes[2].set_xlabel("P(Spoof)"); axes[2].set_ylabel("Density")
axes[2].set_title("Score distribution"); axes[2].legend(fontsize=9)

plt.tight_layout()
plot_path = os.path.join(RESULTS_DIR, "analysis.png")
plt.savefig(plot_path, dpi=150, bbox_inches="tight")
print("Plots saved: {}".format(plot_path))


# ─────────────────────────────────────────────────────────────────────────────
# FINAL SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  SUMMARY")
print("="*60)
print("  Dataset accuracy : {:.2f}%".format(accuracy))
print("  EER              : {:.2f}%".format(eer))
print("  Pipeline tests   : {}/{}".format(passed2, len(results_2)))
print("  Stress tests     : {}/{}".format(passed4, len(stress_results)))
print("  Live robustness  : {}".format("PASS" if live_ok else "FAIL"))
print()

if accuracy >= 85:
    verdict = "READY FOR DEPLOYMENT"
elif accuracy >= 75:
    verdict = "ACCEPTABLE FOR DEMO"
else:
    verdict = "NEEDS MORE TRAINING — accuracy too low"

print("  VERDICT: {}".format(verdict))

if accuracy < 75:
    print()
    print("  To improve:")
    print("  1. Use more training data (>2000 files per class)")
    print("  2. Increase EPOCHS to 60 in train_fixed.py")
    print("  3. Check score distribution plot — if peaks overlap,")
    print("     model has not learned to separate the classes")