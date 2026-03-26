# from flask import Flask, request, jsonify
# import torch
# import torch.nn as nn
# import numpy as np
# import librosa
# import soundfile as sf
# from flask_cors import CORS

# app = Flask(__name__)
# CORS(app)  # enable CORS

# # --- Define CNN model (same as training) ---
# class DeepfakeCNN(nn.Module):
#     def __init__(self):
#         super(DeepfakeCNN, self).__init__()
#         self.conv1 = nn.Conv2d(1, 16, kernel_size=3, stride=1, padding=1)
#         self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1)
#         self.pool = nn.MaxPool2d(2, 2)
#         self.fc1 = nn.Linear(32 * 16 * 100, 128)
#         self.fc2 = nn.Linear(128, 2)

#     def forward(self, x):
#         x = self.pool(torch.relu(self.conv1(x)))
#         x = self.pool(torch.relu(self.conv2(x)))
#         x = x.view(x.size(0), -1)
#         x = torch.relu(self.fc1(x))
#         x = self.fc2(x)
#         return x

# # --- Load trained model ---
# device = torch.device("cpu")
# model = DeepfakeCNN().to(device)
# state_dict = torch.load("deepfake_cnn_balanced.pth", map_location=device)
# model.load_state_dict(state_dict)
# model.eval()

# @app.route("/")
# def home():
#     return "Deepfake CNN API is running. Use /predict with POST to classify audio."

# @app.route("/predict", methods=["POST"])
# def predict():
#     if "file" not in request.files:
#         return jsonify({"error": "No file uploaded"}), 400

#     file = request.files["file"]

#     try:
#         y, sr = librosa.load(file, sr=16000)
#     except Exception:
#         data, sr = sf.read(file)
#         y = librosa.resample(data.astype(float), orig_sr=sr, target_sr=16000)

#     # --- Compute mel spectrogram ---
#     S = librosa.feature.melspectrogram(y=y, sr=16000, n_mels=64, n_fft=2048, hop_length=512)
#     S = librosa.power_to_db(S, ref=np.max)

#     # --- Normalize to training range ---
#     S = np.clip(S, -80, 0)

#     # --- Pad/trim to fixed shape (64, 400) ---
#     target_len = 400
#     if S.shape[1] > target_len:
#         S = S[:, :target_len]
#     else:
#         S = np.pad(S, ((0, 0), (0, target_len - S.shape[1])), mode="constant")

#     print("DEBUG Spectrogram:", S.shape, "min:", S.min(), "max:", S.max())

#     # --- Convert to torch tensor ---
#     X_tensor = torch.tensor(S, dtype=torch.float32).unsqueeze(0).unsqueeze(0).to(device)

#     # --- Run model inference ---
#     with torch.no_grad():
#         outputs = model(X_tensor)
#         probs = torch.softmax(outputs, dim=1)
#         confidence, predicted = torch.max(probs, 1)

#     # ⚠️ Adjust label mapping based on training
#     # If training used 0=FAKE, 1=REAL, then:
#     label = "FAKE" if predicted.item() == 0 else "REAL"

#     print("Raw outputs:", outputs)
#     print("Softmax probs:", probs)

#     return jsonify({"prediction": label, "confidence": float(confidence.item() * 100)})

# if __name__ == "__main__":
#     app.run(port=5000, debug=True)
# ####################################################################################################333
# import os
# import numpy as np
# import librosa
# import torch
# import torch.nn as nn
# import torch.nn.functional as F
# from flask import Flask, request, jsonify
04
# # -----------------------------
# # 1. CNN Model (same as training)
# # -----------------------------
# class DeepfakeCNN(nn.Module):
#     def __init__(self):
#         super(DeepfakeCNN, self).__init__()
#         self.conv1 = nn.Conv2d(1, 16, kernel_size=3, stride=1, padding=1)
#         self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1)
#         self.pool = nn.MaxPool2d(2, 2)
#         self.fc1 = nn.Linear(32 * 16 * 100, 128)
#         self.dropout = nn.Dropout(0.5)
#         self.fc2 = nn.Linear(128, 2)

#     def forward(self, x):
#         x = self.pool(F.relu(self.conv1(x)))
#         x = self.pool(F.relu(self.conv2(x)))
#         x = x.view(x.size(0), -1)
#         x = self.dropout(F.relu(self.fc1(x)))
#         x = self.fc2(x)
#         return x

# # -----------------------------
# # 2. Load trained model
# # -----------------------------
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# model = DeepfakeCNN().to(device)
# model.load_state_dict(torch.load("deepfake_cnn_asvspoof_best.pth", map_location=device))
# model.eval()

# # -----------------------------
# # 3. Audio Preprocessing
# # -----------------------------
# def preprocess_audio(file_path):
#     y, sr = librosa.load(file_path, sr=16000)
#     S = librosa.feature.melspectrogram(y=y, sr=16000, n_mels=64, n_fft=2048, hop_length=512)
#     S = librosa.power_to_db(S, ref=np.max)
#     S = np.clip(S, -80, 0)
#     target_len = 400
#     if S.shape[1] > target_len:
#         S = S[:, :target_len]
#     else:
#         S = np.pad(S, ((0,0),(0,target_len-S.shape[1])), mode="constant")
#     tensor = torch.tensor(S, dtype=torch.float32).unsqueeze(0).unsqueeze(0)  # (1,1,64,400)
#     return tensor.to(device)

# # -----------------------------
# # 4. Flask App
# # -----------------------------
# app = Flask(__name__)

# @app.route("/")
# def home():
#     return "Deepfake CNN API is running. Use /predict with POST to classify audio."

# @app.route("/predict", methods=["POST"])
# def predict():
#     if "file" not in request.files:
#         return jsonify({"error": "No file uploaded"}), 400

#     file = request.files["file"]
#     file_path = os.path.join("uploads", file.filename)
#     os.makedirs("uploads", exist_ok=True)
#     file.save(file_path)

#     # Preprocess and predict
#     inputs = preprocess_audio(file_path)
#     with torch.no_grad():
#         outputs = model(inputs)
#         probs = torch.softmax(outputs, dim=1)
#         predicted = torch.argmax(probs, dim=1).item()
#         confidence = probs[0][predicted].item()

#     label = "bonafide" if predicted == 1 else "spoof"
#     return jsonify({
#         "prediction": label,
#         "confidence": round(confidence * 100, 2)
#     })

# if __name__ == "__main__":
#     app.run(debug=True)
# #########################################################################################33

# from flask import Flask, request, jsonify
# import librosa, torch, torch.nn as nn, torch.nn.functional as F
# import numpy as np
# from flask_cors import CORS


# app = Flask(__name__)
# CORS(app)

# # --- CNN model (same as training) ---
# class DeepfakeCNN(nn.Module):
#     def __init__(self):
#         super(DeepfakeCNN, self).__init__()
#         self.conv1 = nn.Conv2d(1, 16, kernel_size=3, stride=1, padding=1)
#         self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1)
#         self.pool = nn.MaxPool2d(2, 2)
#         self.fc1 = nn.Linear(32 * 16 * 100, 128)
#         self.dropout = nn.Dropout(0.5)
#         self.fc2 = nn.Linear(128, 2)

#     def forward(self, x):
#         x = self.pool(F.relu(self.conv1(x)))
#         x = self.pool(F.relu(self.conv2(x)))
#         x = x.view(x.size(0), -1)
#         x = self.dropout(F.relu(self.fc1(x)))
#         x = self.fc2(x)
#         return x

# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# model = DeepfakeCNN().to(device)
# model.load_state_dict(torch.load("deepfake_cnn_asvspoof_best.pth", map_location=device))
# model.eval()

# def preprocess_audio(file_path):
#     # Force mono, 16kHz
#     y, sr = librosa.load(file_path, sr=16000, mono=True)

#     # Trim leading/trailing silence
#     y, _ = librosa.effects.trim(y)

#     # If too short, pad with zeros
#     if len(y) < 16000:  # less than 1 second
#         y = np.pad(y, (0, 16000 - len(y)), mode="constant")

#     # Generate mel spectrogram
#     S = librosa.feature.melspectrogram(y=y, sr=16000, n_mels=64, n_fft=2048, hop_length=512)
#     S = librosa.power_to_db(S, ref=np.max)
#     S = np.clip(S, -80, 0)

#     # Pad/truncate to fixed length
#     target_len = 400
#     if S.shape[1] > target_len:
#         S = S[:, :target_len]
#     else:
#         S = np.pad(S, ((0,0),(0,target_len-S.shape[1])), mode="constant")

#     tensor = torch.tensor(S, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
#     return tensor.to(device)



# @app.route("/")
# def home():
#     return "Deepfake CNN API is running. Use /predict with POST to classify audio."

# @app.route("/predict", methods=["POST"])
# def predict():
#     file = request.files["file"]
#     if file.content_length == 0:
#         return jsonify({"prediction": "error", "confidence": 0, "error": "Empty audio file"}), 400

#     file.save("live.wav")

#     inputs = preprocess_audio("live.wav")
#     if inputs is None:
#         return jsonify({"prediction": "error", "confidence": 0, "error": "Invalid audio"}), 400

#     with torch.no_grad():
#         outputs = model(inputs)

#         # ✅ Debugging: print raw probabilities
#         probs = torch.softmax(outputs, dim=1)[0].cpu().numpy()
#         print("Probabilities:", probs)   # e.g. [0.95, 0.05]

#         predicted = int(np.argmax(probs))
#         confidence = float(probs[predicted])

#     label = "spoof" if predicted == 0 else "bonafide"
#     return jsonify({"prediction": label, "confidence": confidence})



# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)



######################3working of 30 epoches training

# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import torch
# import torch.nn as nn
# import torch.nn.functional as F
# import librosa
# import numpy as np
# import io
# from pydub import AudioSegment

# app = Flask(__name__)
# CORS(app)

# # ---------------------------
# # Model (same as training)
# # ---------------------------
# class DeepfakeCNN(nn.Module):
#     def __init__(self):
#         super(DeepfakeCNN, self).__init__()
#         self.conv1 = nn.Conv2d(1, 16, kernel_size=3, stride=1, padding=1)
#         self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1)
#         self.pool = nn.MaxPool2d(2, 2)
#         self.fc1 = nn.Linear(32 * 16 * 100, 128)
#         self.dropout = nn.Dropout(0.5)
#         self.fc2 = nn.Linear(128, 2)

#     def forward(self, x):
#         x = self.pool(F.relu(self.conv1(x)))
#         x = self.pool(F.relu(self.conv2(x)))
#         x = x.view(x.size(0), -1)
#         x = self.dropout(F.relu(self.fc1(x)))
#         x = self.fc2(x)
#         return x

# # ---------------------------
# # Load trained weights
# # ---------------------------
# model = DeepfakeCNN()
# model.load_state_dict(torch.load("deepfake_cnn_asvspoof_best.pth", map_location="cpu"))
# model.eval()

# # ---------------------------
# # Preprocessing (same as training)
# # ---------------------------


# def preprocess_audio(file_bytes):
#     # Decode with pydub (handles webm/opus/wav/mp3)
#     audio = AudioSegment.from_file(io.BytesIO(file_bytes))
#     y = np.array(audio.get_array_of_samples(), dtype=np.float32)
#     sr = audio.frame_rate

#     # Normalize to [-1,1]
#     y = y / np.max(np.abs(y))

#     # Librosa spectrogram pipeline
#     S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=64, n_fft=2048, hop_length=512)
#     S = librosa.power_to_db(S, ref=np.max)
#     S = np.clip(S, -80, 0)

#     # Pad/truncate to 400 frames
#     target_len = 400
#     if S.shape[1] > target_len:
#         S = S[:, :target_len]
#     else:
#         S = np.pad(S, ((0,0),(0,target_len-S.shape[1])), mode="constant")

#     tensor = torch.tensor(S, dtype=torch.float32).unsqueeze(0).unsqueeze(0)  # (1,1,64,400)
#     return tensor


# # ---------------------------
# # Routes
# # ---------------------------
# @app.route("/")
# def home():
#     return "Deepfake CNN API is running. Use /predict with POST to classify audio."

# @app.route("/predict", methods=["POST"])
# def predict():
#     try:
#         audio_file = request.files["file"]
#         tensor = preprocess_audio(audio_file.read())

#         with torch.no_grad():
#             output = model(tensor)
#             probs = torch.softmax(output, dim=1)[0]
#             pred_class = torch.argmax(probs).item()
#             confidence = probs[pred_class].item() * 100

#         return jsonify({
#             "prediction": "Bonafide" if pred_class == 1 else "FAKE",
#             "confidence": confidence
#         })
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400

# if __name__ == "__main__":
#     app.run(host="127.0.0.1", port=5000, debug=True)

##############20epoches 
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import torch
# import torch.nn as nn
# import torchaudio
# from pydub import AudioSegment
# import numpy as np
# import io

# app = Flask(__name__)
# CORS(app)  # allow React frontend requests

# # ---------------------------
# # Preprocessing (same as training)
# # ---------------------------
# MAX_LEN = 64000
# transform = torchaudio.transforms.MelSpectrogram(sample_rate=16000, n_mels=64)

# def pad_or_truncate(waveform):
#     if waveform.size(1) > MAX_LEN:
#         return waveform[:, :MAX_LEN]
#     elif waveform.size(1) < MAX_LEN:
#         pad_len = MAX_LEN - waveform.size(1)
#         return torch.nn.functional.pad(waveform, (0, pad_len))
#     else:
#         return waveform

# # ---------------------------
# # Model (same as training)
# # ---------------------------
# class SpectrogramCNN(nn.Module):
#     def __init__(self):
#         super().__init__()
#         self.conv1 = nn.Conv2d(1, 16, kernel_size=3, stride=1)
#         self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=1)
#         self.pool = nn.MaxPool2d(2,2)
#         self.gap = nn.AdaptiveAvgPool2d((15, 399))  # adaptive pooling
#         self.fc1 = nn.Linear(32*15*399, 64)
#         self.dropout = nn.Dropout(0.5)              # regularization
#         self.fc2 = nn.Linear(64, 2)

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

# # ---------------------------
# # Load trained weights
# # ---------------------------
# model = SpectrogramCNN()
# model.load_state_dict(torch.load("deepfake_detector2.pth", map_location="cpu"))
# model.eval()

# # ---------------------------
# # Helper: decode audio with pydub (FFmpeg)
# # ---------------------------
# def decode_audio(file_bytes):
#     # pydub uses FFmpeg under the hood
#     audio = AudioSegment.from_file(io.BytesIO(file_bytes))
#     samples = np.array(audio.get_array_of_samples(), dtype=np.float32)

#     # Normalize to [-1,1]
#     if np.max(np.abs(samples)) > 0:
#         samples = samples / np.max(np.abs(samples))

#     waveform = torch.tensor(samples).unsqueeze(0)  # [1, samples]
#     return waveform, audio.frame_rate

# # ---------------------------
# # Routes
# # ---------------------------
# @app.route("/")
# def home():
#     return "Deepfake CNN API is running. Use /predict with POST to classify audio."

# @app.route("/predict", methods=["POST"])
# def predict():
#     try:
#         audio_file = request.files["file"]
#         waveform, sample_rate = decode_audio(audio_file.read())

#         # Resample if needed
#         if sample_rate != 16000:
#             resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
#             waveform = resampler(waveform)

#         # Preprocess
#         waveform = pad_or_truncate(waveform)
#         spec = transform(waveform)   # [1, n_mels, time]
#         spec = spec.unsqueeze(0)     # add batch dim

#         with torch.no_grad():
#             output = model(spec)
#             probs = torch.softmax(output, dim=1)[0]
#             pred_class = torch.argmax(probs).item()
#             confidence = probs[pred_class].item() * 100

#         return jsonify({
#             "prediction": "Bonafide" if pred_class == 0 else "Spoof",
#             "confidence": confidence
#         })
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400

# if __name__ == "__main__":
#     app.run(host="127.0.0.1", port=5000, debug=True)




#####################studyfetch dataset
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import torch
# import torch.nn as nn
# import torchaudio
# import torchaudio.transforms as T
# from pydub import AudioSegment
# import io

# app = Flask(__name__)
# CORS(app)

# # --- Configuration (Must match training script) ---
# MAX_LEN = 64000
# SAMPLE_RATE = 16000
# mel_transform = T.MelSpectrogram(sample_rate=SAMPLE_RATE, n_mels=64, n_fft=1024, hop_length=512)

# # Architecture matched to the training script
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

# # Load the model
# device = torch.device("cpu")
# model = SpectrogramCNN()
# # Using the model file generated by your training script
# model.load_state_dict(torch.load("deepfake_detector_v2.pth", map_location=device))
# model.eval()

# @app.route("/")
# def home():
#     return "Deepfake CNN API is running. Use /predict with POST to classify audio."

# @app.route("/predict", methods=["POST"])
# def predict():
#     try:
#         audio_file = request.files["file"]
#         file_bytes = audio_file.read()

#         # 1. Load with pydub and convert to Float32
#         audio = AudioSegment.from_file(io.BytesIO(file_bytes))
#         samples = audio.get_array_of_samples()
#         waveform = torch.tensor(samples, dtype=torch.float32)

#         # --- FIX 1: Bit-Depth Scaling ---
#         # Some mics record in 16-bit, some in 32-bit. We force it to -1.0 to 1.0 range.
#         if audio.sample_width == 2: # 16-bit
#             waveform = waveform / 32768.0
#         elif audio.sample_width == 4: # 32-bit
#             waveform = waveform / 2147483648.0
        
#         waveform = waveform.unsqueeze(0)

#         # --- FIX 2: Lower Silence Threshold for Live Mic ---
#         max_amplitude = torch.max(torch.abs(waveform)).item()
#         if max_amplitude < 0.001: # Much more sensitive for live mic!
#             return jsonify({"prediction": "No Voice Detected", "confidence": 0.0})

#         # --- FIX 3: Dynamic Range Compression ---
#         # This makes quiet recordings look just like your training files!
#         waveform = waveform / (max_amplitude + 1e-8)

#         # 2. Resample and Mono
#         if audio.frame_rate != 16000:
#             resampler = T.Resample(audio.frame_rate, 16000)
#             waveform = resampler(waveform)
#         if waveform.size(0) > 1:
#             waveform = waveform.mean(dim=0, keepdim=True)

#         # 3. Pad/Truncate
#         if waveform.size(1) > 64000:
#             waveform = waveform[:, :64000]
#         else:
#             waveform = torch.nn.functional.pad(waveform, (0, 64000 - waveform.size(1)))

#         # 4. Generate Log-Mel-Spectrogram (The core feature)
#         spec = mel_transform(waveform)
#         spec = (spec + 1e-9).log()
        
#         # --- CRITICAL FIX 4: Spectrogram Normalization ---
#         # This centers the "Log" values around zero, which prevents 100% Fake bias.
#         spec = (spec - spec.mean()) / (spec.std() + 1e-8)
        
#         spec = spec.unsqueeze(0) if spec.dim() == 3 else spec

#         # 5. Prediction
#         model.eval()
#         with torch.no_grad():
#             output = model(spec)
#             probs = torch.softmax(output, dim=1)[0]
#             pred_class = torch.argmax(probs).item()
            
#             print(f"DEBUG - Final Max: {max_amplitude:.4f} | Raw Output: {output.tolist()}")

#         return jsonify({
#             "prediction": "Bonafide" if pred_class == 0 else "FAKE",
#             "confidence": round(probs[pred_class].item() * 100, 2)
#         })

#     except Exception as e:
#         print(f"Error: {e}")
#         return jsonify({"error": str(e)}), 400

# if __name__ == "__main__":
#     app.run(host="127.0.0.1", port=5000, debug=True)


############ working of 2nd dataset

# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import torch
# import torch.nn as nn
# import torchaudio
# from pydub import AudioSegment
# import io

# app = Flask(__name__)
# CORS(app)

# MAX_LEN = 64000
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
#         self.conv1 = nn.Conv2d(1, 16, kernel_size=3, stride=1)
#         self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=1)
#         self.pool = nn.MaxPool2d(2,2)
#         self.gap = nn.AdaptiveAvgPool2d((15, 399))
#         self.fc1 = nn.Linear(32*15*399, 64)
#         self.fc2 = nn.Linear(64, 2)

#     def forward(self, x):
#         x = torch.relu(self.conv1(x))
#         x = self.pool(x)
#         x = torch.relu(self.conv2(x))
#         x = self.pool(x)
#         x = self.gap(x)
#         x = x.view(x.size(0), -1)
#         x = torch.relu(self.fc1(x))
#         return self.fc2(x)

# model = SpectrogramCNN()
# model.load_state_dict(torch.load("deepfake_detector.pth", map_location="cpu"))
# model.eval()

# @app.route("/")
# def home():
#     return "Deepfake CNN API is running. Use /predict with POST to classify audio."

# @app.route("/predict", methods=["POST"])
# def predict():
#     try:
#         audio_file = request.files["file"]
#         file_bytes = audio_file.read()

#         # Decode with pydub (handles webm/opus/wav/mp3)
#         audio = AudioSegment.from_file(io.BytesIO(file_bytes))
#         samples = audio.get_array_of_samples()
#         waveform = torch.tensor(samples, dtype=torch.float32).unsqueeze(0)
#         sample_rate = audio.frame_rate

#         # Resample if needed
#         if sample_rate != 16000:
#             resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
#             waveform = resampler(waveform)

#         waveform = pad_or_truncate(waveform)
#         spec = transform(waveform)
#         spec = spec.unsqueeze(0)

#         with torch.no_grad():
#             output = model(spec)
#             probs = torch.softmax(output, dim=1)[0]
#             pred_class = torch.argmax(probs).item()
#             confidence = probs[pred_class].item() * 100

#         return jsonify({
#             "prediction": "Real" if pred_class == 0 else "FAKE",
#             "confidence": confidence
#         })
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400

# if __name__ == "__main__":
#     app.run(host="127.0.0.1", port=5000, debug=True)

##########################################     MC            ###########################################################
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import torch
# import torch.nn as nn
# import torchaudio
# from pydub import AudioSegment
# import io, os

# app = Flask(__name__)
# CORS(app)  # enable CORS for all routes

# MAX_LEN = 64000
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
#         self.conv1 = nn.Conv2d(1, 16, kernel_size=3, stride=1)
#         self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=1)
#         self.pool = nn.MaxPool2d(2,2)
#         self.gap = nn.AdaptiveAvgPool2d((15, 399))
#         self.fc1 = nn.Linear(32*15*399, 64)
#         self.fc2 = nn.Linear(64, 2)

#     def forward(self, x):
#         x = torch.relu(self.conv1(x))
#         x = self.pool(x)
#         x = torch.relu(self.conv2(x))
#         x = self.pool(x)
#         x = self.gap(x)
#         x = x.view(x.size(0), -1)
#         x = torch.relu(self.fc1(x))
#         return self.fc2(x)

# model = SpectrogramCNN()
# model.load_state_dict(torch.load("deepfake_detector.pth", map_location="cpu"))
# model.eval()

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

#         # Decode with pydub (handles webm/opus/wav/mp3)
#         audio = AudioSegment.from_file(io.BytesIO(file_bytes))
#         samples = audio.get_array_of_samples()
#         waveform = torch.tensor(samples, dtype=torch.float32).unsqueeze(0)
#         sample_rate = audio.frame_rate

#         # Resample if needed
#         if sample_rate != 16000:
#             resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
#             waveform = resampler(waveform)

#         waveform = pad_or_truncate(waveform)
#         spec = transform(waveform)
#         spec = spec.unsqueeze(0)

#         with torch.no_grad():
#             output = model(spec)
#             probs = torch.softmax(output, dim=1)[0]
#             pred_class = torch.argmax(probs).item()
#             confidence = probs[pred_class].item() * 100

#         return jsonify({
#             "prediction": "Bonafide" if pred_class == 0 else "Spoof",
#             "confidence": confidence
#         })
        

#     except Exception as e:
#         return jsonify({"error": str(e)}), 400
    
  


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=True)


####################### CLAUDE AI 111############################
from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import torch.nn as nn
import torchaudio
from pydub import AudioSegment
import io, os

app = Flask(__name__)
CORS(app)

# ---------------------------
# Preprocessing (MUST match training)
# ---------------------------
MAX_LEN = 64000
transform = torchaudio.transforms.MelSpectrogram(sample_rate=16000, n_mels=64)

def pad_or_truncate(waveform):
    if waveform.size(1) > MAX_LEN:
        return waveform[:, :MAX_LEN]
    elif waveform.size(1) < MAX_LEN:
        pad_len = MAX_LEN - waveform.size(1)
        return torch.nn.functional.pad(waveform, (0, pad_len))
    else:
        return waveform

# ---------------------------
# Model (MUST exactly match training script)
# ---------------------------
class SpectrogramCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, stride=1)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.gap = nn.AdaptiveAvgPool2d((15, 399))   # ✅ matches training
        self.fc1 = nn.Linear(32 * 15 * 399, 64)
        self.dropout = nn.Dropout(0.5)               # ✅ was missing in your old app.py!
        self.fc2 = nn.Linear(64, 2)

    def forward(self, x):
        x = torch.relu(self.conv1(x))
        x = self.pool(x)
        x = torch.relu(self.conv2(x))
        x = self.pool(x)
        x = self.gap(x)
        x = x.view(x.size(0), -1)
        x = torch.relu(self.fc1(x))
        x = self.dropout(x)                          # ✅ was missing in your old app.py!
        return self.fc2(x)

# ---------------------------
# Load model
# ---------------------------
model = SpectrogramCNN()
model.load_state_dict(torch.load("deepfake_detector.pth", map_location="cpu"))
model.eval()
print("✅ Model loaded successfully.")

@app.route("/")
def home():
    return "Deepfake CNN API is running. Use /predict with POST to classify audio."

@app.route("/predict", methods=["POST"])
def predict():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        audio_file = request.files["file"]
        file_bytes = audio_file.read()

        # ── Step 1: Decode with pydub (handles webm/opus/wav/mp3) ──
        audio = AudioSegment.from_file(io.BytesIO(file_bytes))

        # ── Step 2: Convert to mono (live mic may be stereo) ──
        audio = audio.set_channels(1)

        # ── Step 3: Resample to 16kHz ──
        audio = audio.set_frame_rate(16000)

        # ── Step 4: Get raw samples ──
        samples_raw = audio.get_array_of_samples()
        waveform = torch.tensor(samples_raw, dtype=torch.float32).unsqueeze(0)  # [1, N]

        # ── Step 5: NORMALIZE to [-1, 1] ──
        # THIS IS THE CRITICAL FIX:
        # torchaudio.load() normalizes automatically, but pydub does NOT.
        # Your training data was normalized; live audio must be too.
        sample_width = audio.sample_width  # bytes per sample: 2 = 16-bit, 4 = 32-bit
        if sample_width == 2:
            waveform = waveform / 32768.0
        elif sample_width == 4:
            waveform = waveform / 2147483648.0
        else:
            # Fallback: normalize by actual max
            max_val = torch.max(torch.abs(waveform))
            if max_val > 0:
                waveform = waveform / max_val

        # ── Debug: log waveform stats ──
        print(f"DEBUG waveform | shape: {waveform.shape} | min: {waveform.min():.4f} | max: {waveform.max():.4f} | mean: {waveform.mean():.4f}")

        # ── Step 6: Pad or truncate to MAX_LEN ──
        waveform = pad_or_truncate(waveform)

        # ── Step 7: Compute Mel Spectrogram (same transform as training) ──
        spec = transform(waveform)   # [1, n_mels, time]
        spec = spec.unsqueeze(0)     # [1, 1, n_mels, time]  → batch dim

        # ── Debug: log spectrogram stats ──
        print(f"DEBUG spectrogram | shape: {spec.shape} | min: {spec.min():.4f} | max: {spec.max():.4f} | mean: {spec.mean():.4f}")

        # ── Step 8: Inference ──
        with torch.no_grad():
            output = model(spec)
            probs = torch.softmax(output, dim=1)[0]
            pred_class = torch.argmax(probs).item()
            confidence = probs[pred_class].item() * 100

        # ── Debug: log raw logits and probabilities ──
        print(f"DEBUG logits: {output.tolist()}")
        print(f"DEBUG probs → Bonafide: {probs[0].item()*100:.2f}% | Spoof: {probs[1].item()*100:.2f}%")
        print(f"DEBUG prediction: {'Bonafide' if pred_class == 0 else 'Spoof'} ({confidence:.2f}%)")

        return jsonify({
            "prediction": "Bonafide" if pred_class == 0 else "Spoof",
            "confidence": round(confidence, 2),
            "bonafide_prob": round(probs[0].item() * 100, 2),
            "spoof_prob": round(probs[1].item() * 100, 2),
        })

    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)