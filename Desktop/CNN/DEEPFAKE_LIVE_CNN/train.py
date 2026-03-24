import os, random, numpy as np
import torch, torch.nn as nn, torch.optim as optim
import torchaudio, torchaudio.transforms as T
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import train_test_split

# ── Config ────────────────────────────────────────────────────────────────────
BONAFIDE_DIR = "data/bonafide_merged"
SPOOF_DIR    = "data/spoof"
SAVE_PATH    = "deepfake_detector_fixed.pth"
SAMPLE_RATE  = 16000
MAX_LEN      = 64000
N_MELS       = 64
BATCH_SIZE   = 16
EPOCHS       = 40
LR           = 0.0003
PATIENCE     = 8
SEED         = 42

random.seed(SEED)
torch.manual_seed(SEED)

# ── Feature extraction ────────────────────────────────────────────────────────
mel       = T.MelSpectrogram(sample_rate=SAMPLE_RATE, n_fft=1024,
                              hop_length=512, n_mels=N_MELS, f_min=0, f_max=8000)
time_mask = T.TimeMasking(time_mask_param=20)
freq_mask = T.FrequencyMasking(freq_mask_param=8)


def pad_or_truncate(w):
    n = w.size(1)
    if n > MAX_LEN: return w[:, :MAX_LEN]
    if n < MAX_LEN: return torch.nn.functional.pad(w, (0, MAX_LEN - n))
    return w


def instance_norm(spec):
    mean, std = spec.mean(), spec.std()
    return (spec - mean) / std if std > 1e-6 else spec


def make_spec(waveform, augment=False):
    """
    Returns shape [1, N_MELS, T]  — NO unsqueeze(0) here.
    DataLoader adds the batch dim automatically → [B, 1, N_MELS, T].
    app.py adds unsqueeze(0) itself since it runs single samples.
    """
    spec = mel(waveform)                        # [1, N_MELS, T]
    spec = torch.log(spec + 1e-6)
    if augment:
        if random.random() < 0.5: spec = time_mask(spec)
        if random.random() < 0.5: spec = freq_mask(spec)
    return instance_norm(spec)                  # [1, N_MELS, T]  ← no unsqueeze


def augment_wave(w):
    if random.random() < 0.8:
        w = torch.clamp(w * random.uniform(0.25, 4.0), -1.0, 1.0)
    if random.random() < 0.4:
        w = torch.clamp(w + torch.randn_like(w) * random.uniform(0.001, 0.015), -1.0, 1.0)
    if random.random() < 0.3:
        w = torch.roll(w, random.randint(-8000, 8000), dims=1)
    return w


# ── Dataset ───────────────────────────────────────────────────────────────────
class AudioDataset(Dataset):
    def __init__(self, files, labels, augment=False):
        self.files, self.labels, self.augment = files, labels, augment

    def __len__(self): return len(self.files)

    def __getitem__(self, idx):
        try:
            w, sr = torchaudio.load(self.files[idx])
            if sr != SAMPLE_RATE:
                w = T.Resample(sr, SAMPLE_RATE)(w)
            if w.size(0) > 1:
                w = w.mean(dim=0, keepdim=True)
            w = pad_or_truncate(w)
            if self.augment:
                w = augment_wave(w)
            # make_spec returns [1, N_MELS, T]
            # DataLoader stacks B of these → [B, 1, N_MELS, T] ✓
            return make_spec(w, augment=self.augment), self.labels[idx]
        except Exception as e:
            print("  Skip {}: {}".format(os.path.basename(self.files[idx]), e))
            return torch.zeros(1, N_MELS, 126), self.labels[idx]


# ── Model ─────────────────────────────────────────────────────────────────────
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
        # x: [B, 1, N_MELS, T]  — 4D ✓
        x = self.pool(torch.relu(self.bn1(self.conv1(x))))
        x = self.pool(torch.relu(self.bn2(self.conv2(x))))
        x = self.pool(torch.relu(self.bn3(self.conv3(x))))
        x = self.gap(x).view(x.size(0), -1)
        return self.fc2(self.dropout(torch.relu(self.fc1(x))))


# ── Data ──────────────────────────────────────────────────────────────────────
def gather(d):
    return [os.path.join(d, f) for f in os.listdir(d)
            if f.lower().endswith((".wav", ".flac", ".mp3"))]

print("Loading files...")
b_files = gather(BONAFIDE_DIR)
s_files = gather(SPOOF_DIR)
n       = min(len(b_files), len(s_files))
files   = random.sample(b_files, n) + random.sample(s_files, n)
labels  = [0] * n + [1] * n
print("  {} bonafide + {} spoof".format(n, n))

tr_f, te_f, tr_l, te_l = train_test_split(
    files, labels, test_size=0.2, stratify=labels, random_state=SEED)

counts  = [tr_l.count(0), tr_l.count(1)]
weights = [1.0 / counts[lb] for lb in tr_l]
sampler = WeightedRandomSampler(weights, len(tr_l), replacement=True)

tr_loader = DataLoader(AudioDataset(tr_f, tr_l, augment=True),
                       batch_size=BATCH_SIZE, sampler=sampler, num_workers=0)
te_loader = DataLoader(AudioDataset(te_f, te_l, augment=False),
                       batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

# ── Verify tensor shape before training ───────────────────────────────────────
sample_spec, sample_label = AudioDataset(tr_f[:1], tr_l[:1])[0]
print("  Single sample spec shape : {}  (should be [1, {}, ~126])".format(
    list(sample_spec.shape), N_MELS))
assert sample_spec.dim() == 3, \
    "ERROR: spec should be 3D [1, N_MELS, T] but got {}D".format(sample_spec.dim())
print("  Shape check PASSED")

# ── Training ──────────────────────────────────────────────────────────────────
device    = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model     = SpectrogramCNN().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.AdamW(model.parameters(), lr=LR, weight_decay=1e-4)
scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)

best_acc, patience_count = 0.0, 0
print("\nTraining on {} ...".format(device))

for epoch in range(EPOCHS):
    model.train()
    loss_sum, correct, total = 0.0, 0, 0

    for specs, lbls in tr_loader:
        # specs: [B, 1, N_MELS, T]  — 4D ✓
        specs, lbls = specs.to(device), lbls.to(device)
        optimizer.zero_grad()
        out  = model(specs)
        loss = criterion(out, lbls)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        loss_sum += loss.item()
        correct  += (out.argmax(1) == lbls).sum().item()
        total    += lbls.size(0)

    scheduler.step()

    model.eval()
    vc, vt = 0, 0
    with torch.no_grad():
        for specs, lbls in te_loader:
            specs, lbls = specs.to(device), lbls.to(device)
            vc += (model(specs).argmax(1) == lbls).sum().item()
            vt += lbls.size(0)

    tr_acc = 100 * correct / total
    va_acc = 100 * vc / vt
    mark   = ""
    if va_acc > best_acc:
        best_acc, patience_count = va_acc, 0
        torch.save(model.state_dict(), SAVE_PATH)
        mark = " <- saved"
    else:
        patience_count += 1

    print("Epoch {:02d}/{} | train {:.1f}% | val {:.1f}% | loss {:.4f}{}".format(
        epoch+1, EPOCHS, tr_acc, va_acc, loss_sum/len(tr_loader), mark))

    if patience_count >= PATIENCE:
        print("Early stop at epoch {}.".format(epoch+1))
        break

print("\nBest val: {:.2f}%  ->  {}".format(best_acc, SAVE_PATH))

# ── Evaluation ────────────────────────────────────────────────────────────────
model.load_state_dict(torch.load(SAVE_PATH, map_location=device))
model.eval()
y_true, y_pred = [], []
with torch.no_grad():
    for specs, lbls in te_loader:
        y_pred.extend(model(specs.to(device)).argmax(1).cpu().numpy())
        y_true.extend(lbls.numpy())

print("\nConfusion matrix:")
print(confusion_matrix(y_true, y_pred))
print(classification_report(y_true, y_pred,
      target_names=["Bonafide","Spoof"], zero_division=0))
print("Done. Load in app.py: torch.load('{}')".format(SAVE_PATH))

import os, random
import torch
import torch.nn as nn
import torch.optim as optim
import torchaudio
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import train_test_split

# ---------------------------
# Step 1: Dataset with Spectrograms
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

class AudioDataset(Dataset):
    def _init_(self, files, labels):
        self.files = files
        self.labels = labels

    def _len_(self): return len(self.files)

    def _getitem_(self, idx):
        waveform, sr = torchaudio.load(self.files[idx])
        waveform = pad_or_truncate(waveform)
        spec = transform(waveform)
        spec = spec.unsqueeze(0)   # ✅ add channel dimension
        return spec, self.labels[idx]

# ---------------------------
# Step 2: CNN Model for Spectrograms
# ---------------------------
class SpectrogramCNN(nn.Module):
    def _init_(self):
        super()._init_()
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, stride=1)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=1)
        self.pool = nn.MaxPool2d(2,2)
        self.gap = nn.AdaptiveAvgPool2d((15, 399))  # adaptive pooling
        self.fc1 = nn.Linear(32*15*399, 64)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(64, 2)

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

# ---------------------------
# Step 3: Prepare Balanced Dataset
# ---------------------------
bonafide_dir, spoof_dir = "data/bonafide_merged", "data/spoof"
bonafide_files = [os.path.join(bonafide_dir,f) for f in os.listdir(bonafide_dir) if f.endswith((".wav",".flac"))]
spoof_files = [os.path.join(spoof_dir,f) for f in os.listdir(spoof_dir) if f.endswith((".wav",".flac"))]

min_len = min(len(bonafide_files), len(spoof_files))
bonafide_files = random.sample(bonafide_files, min_len)
spoof_files = random.sample(spoof_files, min_len)

files = bonafide_files + spoof_files
labels = [0]*len(bonafide_files) + [1]*len(spoof_files)

print("Balanced dataset size:", len(files))
print("Bonafide:", labels.count(0), "Spoof:", labels.count(1))

train_files, test_files, train_labels, test_labels = train_test_split(
    files, labels, test_size=0.2, stratify=labels, random_state=42
)

train_dataset = AudioDataset(train_files, train_labels)
test_dataset = AudioDataset(test_files, test_labels)

train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False)

# ---------------------------
# Step 4: Training Loop (20 epochs)
# ---------------------------
model = SpectrogramCNN()
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.0005, weight_decay=1e-5)  # ✅ lower LR
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.5)

EPOCHS = 20
for epoch in range(EPOCHS):
    running_loss, correct, total = 0.0, 0, 0
    model.train()
    for i,(specs,labels) in enumerate(train_loader):
        outputs = model(specs)
        loss = criterion(outputs, labels)
        optimizer.zero_grad(); loss.backward(); optimizer.step()

        running_loss += loss.item()
        _,predicted = torch.max(outputs,1)
        total += labels.size(0)
        correct += (predicted==labels).sum().item()

        if i%20==0:
            print(f"  Epoch {epoch+1}, Batch {i}, Loss {loss.item():.4f}")

    scheduler.step()
    print(f"Epoch {epoch+1}/{EPOCHS}, Loss {running_loss/len(train_loader):.4f}, Acc {100*correct/total:.2f}%")

torch.save(model.state_dict(),"deepfake_detector.pth")
print("✅ Training complete, model saved.")

# ---------------------------
# Step 5: Evaluation
# ---------------------------
model.eval()
y_true,y_pred=[],[]
with torch.no_grad():
    for specs,labels in test_loader:
        outputs = model(specs)
        _,predicted = torch.max(outputs,1)
        y_true.extend(labels.cpu().numpy())
        y_pred.extend(predicted.cpu().numpy())

print("\n🔹 Confusion Matrix:")
print(confusion_matrix(y_true,y_pred,labels=[0,1]))

print("\n🔹 Classification Report:")
print(classification_report(y_true,y_pred,labels=[0,1],target_names=["Bonafide","Spoof"],zero_division=0))