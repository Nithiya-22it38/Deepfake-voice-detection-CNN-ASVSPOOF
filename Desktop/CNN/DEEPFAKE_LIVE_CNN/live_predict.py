import sounddevice as sd
import soundfile as sf
import librosa
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

# -----------------------------
# CNN Model (same as training)
# -----------------------------
class DeepfakeCNN(nn.Module):
    def __init__(self):
        super(DeepfakeCNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(32 * 16 * 100, 128)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(128, 2)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(x.size(0), -1)
        x = self.dropout(F.relu(self.fc1(x)))
        x = self.fc2(x)
        return x

# -----------------------------
# Load trained model
# -----------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = DeepfakeCNN().to(device)
model.load_state_dict(torch.load("deepfake_cnn_asvspoof_best.pth", map_location=device))
model.eval()

# -----------------------------
# Preprocessing
# -----------------------------
def preprocess_audio(file_path):
    y, sr = librosa.load(file_path, sr=16000, mono=True)
    S = librosa.feature.melspectrogram(y=y, sr=16000, n_mels=64, n_fft=2048, hop_length=512)
    S = librosa.power_to_db(S, ref=np.max)
    S = np.clip(S, -80, 0)
    target_len = 400
    if S.shape[1] > target_len:
        S = S[:, :target_len]
    else:
        S = np.pad(S, ((0,0),(0,target_len-S.shape[1])), mode="constant")
    tensor = torch.tensor(S, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
    return tensor.to(device)

# -----------------------------
# Live Recording + Prediction
# -----------------------------
def record_and_predict(duration=5, sr=16000):
    print("Recording...")
    audio = sd.rec(int(duration * sr), samplerate=sr, channels=1)
    sd.wait()
    sf.write("live.wav", audio, sr)
    print("Saved live.wav")

    inputs = preprocess_audio("live.wav")
    with torch.no_grad():
        outputs = model(inputs)
        probs = torch.softmax(outputs, dim=1)
        predicted = torch.argmax(probs, dim=1).item()
        confidence = probs[0][predicted].item()

    label = "bonafide (real)" if predicted == 1 else "spoof (fake)"
    print(f"Prediction: {label}")
    print(f"Confidence: {confidence*100:.2f}%")

if __name__ == "__main__":
    record_and_predict(duration=5)  # record 5 seconds
