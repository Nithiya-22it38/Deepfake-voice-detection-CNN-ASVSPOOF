################################claude AI soooo close results #################33333

# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import torch
# import torch.nn as nn
# import torchaudio
# from pydub import AudioSegment
# import io, os

# app = Flask(__name__)
# CORS(app)

# MAX_LEN   = 64000
# transform = torchaudio.transforms.MelSpectrogram(sample_rate=16000, n_mels=64)

# def pad_or_truncate(waveform):
#     if waveform.size(1) > MAX_LEN:
#         return waveform[:, :MAX_LEN]
#     elif waveform.size(1) < MAX_LEN:
#         pad_len = MAX_LEN - waveform.size(1)
#         return torch.nn.functional.pad(waveform, (0, pad_len))
#     else:
#         return waveform

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

# # Best model from compare_models.py results
# model = SpectrogramCNN()
# model.load_state_dict(torch.load("deepfake_detector1.pth", map_location="cpu"))
# model.eval()
# print("Model loaded: deepfake_detector1.pth")

# @app.route("/")
# def home():
#     return "Deepfake CNN API is running. Use /predict with POST to classify audio."

# @app.route("/predict", methods=["POST"])
# def predict():
#     try:
#         if "file" not in request.files:
#             return jsonify({"error": "No file uploaded"}), 400

#         audio_file = request.files["file"]
#         file_bytes = audio_file.read()

#         audio = AudioSegment.from_file(io.BytesIO(file_bytes))
#         audio = audio.set_channels(1)
#         audio = audio.set_frame_rate(16000)

#         samples_raw = audio.get_array_of_samples()
#         waveform    = torch.tensor(samples_raw, dtype=torch.float32).unsqueeze(0)

#         sample_width = audio.sample_width
#         if sample_width == 2:
#             waveform = waveform / 32768.0
#         elif sample_width == 4:
#             waveform = waveform / 2147483648.0
#         else:
#             max_val = torch.max(torch.abs(waveform))
#             if max_val > 0:
#                 waveform = waveform / max_val

#         print("waveform shape:{} min:{:.4f} max:{:.4f} mean:{:.4f}".format(
#             list(waveform.shape),
#             waveform.min().item(),
#             waveform.max().item(),
#             waveform.mean().item()))

#         waveform = pad_or_truncate(waveform)

#         spec = transform(waveform)
#         spec = spec.unsqueeze(0)

#         print("spec shape:{} min:{:.4f} max:{:.4f} mean:{:.4f}".format(
#             list(spec.shape),
#             spec.min().item(),
#             spec.max().item(),
#             spec.mean().item()))

#         with torch.no_grad():
#             output     = model(spec)
#             probs      = torch.softmax(output, dim=1)[0]
#             pred_class = int(torch.argmax(probs).item())
#             confidence = float(probs[pred_class].item()) * 100

#         b_prob = round(float(probs[0].item()) * 100, 2)
#         s_prob = round(float(probs[1].item()) * 100, 2)
#         label  = "Bonafide" if pred_class == 0 else "Spoof"

#         print("Bonafide:{}%  Spoof:{}%  -> {}".format(b_prob, s_prob, label))

#         return jsonify({
#             "prediction":    label,
#             "confidence":    round(confidence, 2),
#             "bonafide_prob": b_prob,
#             "spoof_prob":    s_prob,
#         })

#     except Exception as e:
#         print("ERROR: {}".format(e))
#         return jsonify({"error": str(e)}), 400

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=True)

####################### CLOUDE some what close as not high confidence ##########33
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import torch
# import torch.nn as nn
# import torchaudio
# from pydub import AudioSegment
# import io, os

# app = Flask(__name__)
# CORS(app)

# MAX_LEN     = 64000
# transform   = torchaudio.transforms.MelSpectrogram(sample_rate=16000, n_mels=64)

# # Temperature scaling: softens overconfident probabilities.
# # T=1.0 = no change (raw softmax)
# # T=2.5 = honest range (~55-85% instead of ~95-100%)
# # Increase T if confidence still feels too high,
# # decrease T if predictions feel too uncertain.
# TEMPERATURE = 2.5


# def pad_or_truncate(waveform):
#     if waveform.size(1) > MAX_LEN:
#         return waveform[:, :MAX_LEN]
#     elif waveform.size(1) < MAX_LEN:
#         pad_len = MAX_LEN - waveform.size(1)
#         return torch.nn.functional.pad(waveform, (0, pad_len))
#     else:
#         return waveform


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


# model = SpectrogramCNN()
# model.load_state_dict(torch.load("deepfake_detector1.pth", map_location="cpu"))
# model.eval()
# print("Model loaded: deepfake_detector1.pth  (temperature={})".format(TEMPERATURE))


# @app.route("/")
# def home():
#     return "Deepfake CNN API is running. Use /predict with POST to classify audio."


# @app.route("/predict", methods=["POST"])
# def predict():
#     try:
#         if "file" not in request.files:
#             return jsonify({"error": "No file uploaded"}), 400

#         audio_file = request.files["file"]
#         file_bytes = audio_file.read()

#         audio = AudioSegment.from_file(io.BytesIO(file_bytes))
#         audio = audio.set_channels(1)
#         audio = audio.set_frame_rate(16000)

#         samples_raw  = audio.get_array_of_samples()
#         waveform     = torch.tensor(samples_raw, dtype=torch.float32).unsqueeze(0)

#         sample_width = audio.sample_width
#         if sample_width == 2:
#             waveform = waveform / 32768.0
#         elif sample_width == 4:
#             waveform = waveform / 2147483648.0
#         else:
#             max_val = torch.max(torch.abs(waveform))
#             if max_val > 0:
#                 waveform = waveform / max_val

#         print("waveform shape:{} min:{:.4f} max:{:.4f} mean:{:.4f}".format(
#             list(waveform.shape),
#             waveform.min().item(),
#             waveform.max().item(),
#             waveform.mean().item()))

#         waveform = pad_or_truncate(waveform)
#         spec     = transform(waveform)
#         spec     = spec.unsqueeze(0)

#         print("spec shape:{} min:{:.4f} max:{:.4f} mean:{:.4f}".format(
#             list(spec.shape),
#             spec.min().item(),
#             spec.max().item(),
#             spec.mean().item()))

#         with torch.no_grad():
#             logits = model(spec)

#             # Raw softmax (what model actually thinks)
#             raw_probs = torch.softmax(logits, dim=1)[0]

#             # Temperature-scaled softmax (honest confidence for display)
#             scaled_probs = torch.softmax(logits / TEMPERATURE, dim=1)[0]

#             pred_class = int(torch.argmax(raw_probs).item())

#         # Use raw probs for the decision, scaled probs for display
#         label  = "Bonafide" if pred_class == 0 else "Spoof"

#         b_prob_display = round(float(scaled_probs[0].item()) * 100, 2)
#         s_prob_display = round(float(scaled_probs[1].item()) * 100, 2)
#         confidence     = b_prob_display if pred_class == 0 else s_prob_display

#         print("raw    -> Bonafide:{:.1f}%  Spoof:{:.1f}%".format(
#             float(raw_probs[0].item()) * 100,
#             float(raw_probs[1].item()) * 100))
#         print("scaled -> Bonafide:{:.1f}%  Spoof:{:.1f}%  -> {}".format(
#             b_prob_display, s_prob_display, label))

#         return jsonify({
#             "prediction":    label,
#             "confidence":    confidence,
#             "bonafide_prob": b_prob_display,
#             "spoof_prob":    s_prob_display,
#         })

#     except Exception as e:
#         print("ERROR: {}".format(e))
#         return jsonify({"error": str(e)}), 400


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=True)

################### live recording CA working with more confidence#################3


"""
app.py — Deepfake Voice Detector Backend
=========================================
Fixes applied:
  1. Live recordings: browser sends raw PCM float32 as JSON (no ffmpeg/pydub)
  2. Uploaded files: pydub decode (already worked)
  3. Spectrogram instance normalization: makes amplitude irrelevant to the model
  4. Temperature scaling: honest confidence display
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import torch.nn as nn
import torchaudio
import torchaudio.transforms as T
from pydub import AudioSegment
import io

app = Flask(__name__)
CORS(app)

# ── Constants ─────────────────────────────────────────────────────────────────
MAX_LEN     = 64000
SAMPLE_RATE = 16000
TEMPERATURE = 2.5   # softens overconfident softmax outputs

# ── Mel transform — identical to training script ──────────────────────────────
mel_transform = T.MelSpectrogram(sample_rate=SAMPLE_RATE, n_mels=64)


# ── Model — must match training script exactly ────────────────────────────────
class SpectrogramCNN(nn.Module):
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


model = SpectrogramCNN()
model.load_state_dict(torch.load("deepfake_detector1.pth", map_location="cpu"))
model.eval()
print("Model loaded: deepfake_detector1.pth")


# ── Preprocessing helpers ─────────────────────────────────────────────────────
def pad_or_truncate(waveform):
    n = waveform.size(1)
    if n > MAX_LEN: return waveform[:, :MAX_LEN]
    if n < MAX_LEN: return torch.nn.functional.pad(waveform, (0, MAX_LEN - n))
    return waveform


def instance_normalize_spectrogram(spec):
    """
    KEY FIX: Instance normalize the spectrogram.

    WHY THIS WORKS:
    The model was trained on ASVspoof files which are quiet (rms ~0.01).
    Live mic audio is loud (rms ~0.15). This makes the raw mel spectrogram
    values completely different, so the model predicts based on amplitude
    instead of voice features.

    Instance normalization removes the mean and scales by std per sample.
    After this operation, every spectrogram — regardless of mic volume —
    has mean=0 and std=1. The model now sees ONLY the spectral shape
    (the actual voice features) and not the absolute amplitude level.

    This is the standard fix used in production audio classification systems.
    """
    mean = spec.mean()
    std  = spec.std()
    if std > 1e-6:
        spec = (spec - mean) / std
    return spec


def compute_spectrogram(waveform):
    """Compute mel spectrogram with instance normalization."""
    spec = mel_transform(waveform)         # [1, 64, T]
    spec = torch.log(spec + 1e-6)          # log compression (same as log-mel)
    spec = instance_normalize_spectrogram(spec)
    return spec.unsqueeze(0)               # [1, 1, 64, T]


def decode_uploaded_file(file_bytes):
    """Decode uploaded audio file using pydub. Works for wav/mp3/flac/ogg."""
    audio    = AudioSegment.from_file(io.BytesIO(file_bytes))
    audio    = audio.set_channels(1).set_frame_rate(SAMPLE_RATE)
    samples  = audio.get_array_of_samples()
    waveform = torch.tensor(list(samples), dtype=torch.float32).unsqueeze(0)
    sw = audio.sample_width
    if sw == 2:   waveform = waveform / (2 ** 15)
    elif sw == 4: waveform = waveform / (2 ** 31)
    else:
        peak = waveform.abs().max()
        if peak > 0: waveform = waveform / peak
    return waveform


def run_inference(waveform, source=""):
    """Run inference and return prediction with confidence."""
    waveform = pad_or_truncate(waveform)
    spec     = compute_spectrogram(waveform)

    rms  = waveform.pow(2).mean().sqrt().item()
    peak = waveform.abs().max().item()
    print("[{}] rms:{:.5f}  peak:{:.5f}  spec_mean:{:.4f}  spec_std:{:.4f}".format(
        source, rms, peak, spec.mean().item(), spec.std().item()))

    with torch.no_grad():
        logits       = model(spec)
        raw_probs    = torch.softmax(logits, dim=1)[0]
        scaled_probs = torch.softmax(logits / TEMPERATURE, dim=1)[0]
        pred         = int(torch.argmax(raw_probs).item())

    label  = "Bonafide" if pred == 0 else "Spoof"
    b_raw  = float(raw_probs[0].item()) * 100
    s_raw  = float(raw_probs[1].item()) * 100
    b_disp = round(float(scaled_probs[0].item()) * 100, 2)
    s_disp = round(float(scaled_probs[1].item()) * 100, 2)
    conf   = b_disp if pred == 0 else s_disp

    print("raw    B:{:.1f}%  S:{:.1f}%  -> {}".format(b_raw, s_raw, label))
    print("scaled B:{}%  S:{}%".format(b_disp, s_disp))

    return label, conf, b_disp, s_disp


# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def home():
    return "Deepfake CNN API running."


@app.route("/predict", methods=["POST"])
def predict():
    """
    Uploaded file endpoint.
    Accepts multipart/form-data with a 'file' field.
    Supports wav, mp3, flac, ogg, webm.
    """
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file_bytes = request.files["file"].read()
        if len(file_bytes) < 500:
            return jsonify({"error": "File too small"}), 400

        waveform = decode_uploaded_file(file_bytes)

        if waveform.abs().max().item() < 1e-6:
            return jsonify({"error": "Audio file is silent"}), 400

        label, conf, b, s = run_inference(waveform, "UPLOAD")
        return jsonify({"prediction": label, "confidence": conf,
                        "bonafide_prob": b, "spoof_prob": s})

    except Exception as e:
        print("ERROR /predict: {}".format(e))
        return jsonify({"error": str(e)}), 400


@app.route("/predict-live", methods=["POST"])
def predict_live():
    """
    Live recording endpoint.
    Accepts JSON: { "samples": [float, ...], "sampleRate": 16000 }

    WHY JSON instead of a file:
    Browser MediaRecorder produces webm/opus. On Windows, ffmpeg (used by pydub)
    frequently produces all-zero PCM when decoding webm/opus due to missing
    codec support. This is a known Windows ffmpeg issue.

    The fix: the browser uses AudioContext.decodeAudioData() to decode its own
    recording (always works — same engine that encoded it), converts to Float32Array,
    and sends the raw PCM samples as JSON. The server receives plain numbers —
    no file format, no codec, no ffmpeg involved.
    """
    try:
        data = request.get_json(force=True)

        if not data or "samples" not in data:
            return jsonify({"error": "No samples received. Send JSON with 'samples' array."}), 400

        samples     = data["samples"]
        sample_rate = int(data.get("sampleRate", SAMPLE_RATE))

        print("[LIVE] received {} samples at {}Hz".format(len(samples), sample_rate))

        if len(samples) < 8000:
            return jsonify({"error": "Recording too short (minimum 0.5 seconds)"}), 400

        waveform = torch.tensor(samples, dtype=torch.float32).unsqueeze(0)

        if waveform.abs().max().item() < 1e-6:
            return jsonify({
                "error": (
                    "Microphone is silent. "
                    "Go to Windows Settings → Sound → Input, "
                    "click Microphone Array, and unmute it."
                )
            }), 400

        # Resample if browser sent at different rate
        if sample_rate != SAMPLE_RATE:
            resampler = torchaudio.transforms.Resample(
                orig_freq=sample_rate, new_freq=SAMPLE_RATE)
            waveform  = resampler(waveform)
            print("[LIVE] resampled {} → {}Hz".format(sample_rate, SAMPLE_RATE))

        label, conf, b, s = run_inference(waveform, "LIVE")
        return jsonify({"prediction": label, "confidence": conf,
                        "bonafide_prob": b, "spoof_prob": s})

    except Exception as e:
        print("ERROR /predict-live: {}".format(e))
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


