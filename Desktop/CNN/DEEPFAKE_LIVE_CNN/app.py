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

################### live recording CA   #################3

from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import torch.nn as nn
import torchaudio
from pydub import AudioSegment
import io

app = Flask(__name__)
CORS(app)

MAX_LEN     = 64000
transform   = torchaudio.transforms.MelSpectrogram(sample_rate=16000, n_mels=64)
TEMPERATURE = 2.5

# RMS target only applied to LIVE recordings
# Uploaded files are already at the right level so skip normalization for them
TARGET_RMS  = 0.035


def pad_or_truncate(waveform):
    if waveform.size(1) > MAX_LEN:
        return waveform[:, :MAX_LEN]
    elif waveform.size(1) < MAX_LEN:
        pad_len = MAX_LEN - waveform.size(1)
        return torch.nn.functional.pad(waveform, (0, pad_len))
    return waveform


def decode_pydub(file_bytes):
    """Decode any audio format to float32 waveform in [-1, 1] at 16kHz mono."""
    audio = AudioSegment.from_file(io.BytesIO(file_bytes))
    audio = audio.set_channels(1)
    audio = audio.set_frame_rate(16000)
    samples  = audio.get_array_of_samples()
    waveform = torch.tensor(list(samples), dtype=torch.float32).unsqueeze(0)
    sw = audio.sample_width
    if sw == 2:
        waveform = waveform / (2 ** 15)
    elif sw == 4:
        waveform = waveform / (2 ** 31)
    else:
        peak = torch.max(torch.abs(waveform))
        if peak > 0:
            waveform = waveform / peak
    return waveform


def normalize_rms(waveform, target_rms):
    """Scale waveform so its RMS matches target_rms."""
    rms = waveform.pow(2).mean().sqrt()
    if rms > 1e-6:
        waveform = waveform * (target_rms / rms)
    return torch.clamp(waveform, -1.0, 1.0)


def run_inference(waveform):
    waveform = pad_or_truncate(waveform)
    spec     = transform(waveform)
    spec     = spec.unsqueeze(0)

    print("spec -> min:{:.4f}  max:{:.4f}  mean:{:.4f}".format(
        spec.min().item(), spec.max().item(), spec.mean().item()))

    with torch.no_grad():
        logits       = model(spec)
        raw_probs    = torch.softmax(logits, dim=1)[0]
        scaled_probs = torch.softmax(logits / TEMPERATURE, dim=1)[0]
        pred_class   = int(torch.argmax(raw_probs).item())

    label      = "Bonafide" if pred_class == 0 else "Spoof"
    b_display  = round(float(scaled_probs[0].item()) * 100, 2)
    s_display  = round(float(scaled_probs[1].item()) * 100, 2)
    confidence = b_display if pred_class == 0 else s_display

    print("raw    -> Bonafide:{:.1f}%  Spoof:{:.1f}%".format(
        float(raw_probs[0].item()) * 100,
        float(raw_probs[1].item()) * 100))
    print("scaled -> Bonafide:{}%  Spoof:{}%  -> {}".format(
        b_display, s_display, label))

    return label, confidence, b_display, s_display


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


@app.route("/")
def home():
    return "Deepfake CNN API is running. Use /predict or /predict-live."


# ── Uploaded file endpoint (no RMS normalization — was working fine) ──────────
@app.route("/predict", methods=["POST"])
def predict():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file_bytes = request.files["file"].read()
        waveform   = decode_pydub(file_bytes)

        rms = waveform.pow(2).mean().sqrt().item()
        print("[UPLOAD] rms:{:.5f}  peak:{:.5f}  shape:{}".format(
            rms, waveform.abs().max().item(), list(waveform.shape)))

        # No amplitude normalization for uploaded files
        label, confidence, b_display, s_display = run_inference(waveform)

        return jsonify({
            "prediction":    label,
            "confidence":    confidence,
            "bonafide_prob": b_display,
            "spoof_prob":    s_display,
        })

    except Exception as e:
        print("ERROR: {}".format(e))
        return jsonify({"error": str(e)}), 400


# ── Live recording endpoint (with RMS normalization) ──────────────────────────
@app.route("/predict-live", methods=["POST"])
def predict_live():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file_bytes = request.files["file"].read()
        waveform   = decode_pydub(file_bytes)

        rms_before = waveform.pow(2).mean().sqrt().item()
        print("[LIVE] before norm -> rms:{:.5f}  peak:{:.5f}  shape:{}".format(
            rms_before, waveform.abs().max().item(), list(waveform.shape)))

        # Normalize amplitude to match training data loudness
        waveform = normalize_rms(waveform, TARGET_RMS)

        rms_after = waveform.pow(2).mean().sqrt().item()
        print("[LIVE] after  norm -> rms:{:.5f}  peak:{:.5f}".format(
            rms_after, waveform.abs().max().item()))

        label, confidence, b_display, s_display = run_inference(waveform)

        return jsonify({
            "prediction":    label,
            "confidence":    confidence,
            "bonafide_prob": b_display,
            "spoof_prob":    s_display,
        })

    except Exception as e:
        print("ERROR: {}".format(e))
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)