import os
import shutil

# Adjust these paths to your ASVspoof 2019 LA dataset
base_dir = r"C:\Users\library\Downloads\DEEPFAKE_LIVE_CNN-main\DEEPFAKE_LIVE_CNN-main\ASVspoof2019\LA\ASVspoof2019_LA_train"   # training audio folder
protocol_file = r"C:\Users\library\Downloads\DEEPFAKE_LIVE_CNN-main\DEEPFAKE_LIVE_CNN-main\ASVspoof2019\LA\ASVspoof2019_LA_cm_protocols\ASVspoof2019.LA.cm.train.trn.txt"

target_bonafide = "data/bonafide"
target_spoof = "data/spoof"

os.makedirs(target_bonafide, exist_ok=True)
os.makedirs(target_spoof, exist_ok=True)

with open(protocol_file, "r") as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) < 4:
            continue
        file_id = parts[1]   # filename without extension
        label = parts[-1]    # "bonafide" or "spoof"

        src_file = os.path.join(base_dir, "flac", file_id + ".flac")
        if not os.path.exists(src_file):
            continue

        if label == "bonafide":
            dst_file = os.path.join(target_bonafide, file_id + ".flac")
        else:
            dst_file = os.path.join(target_spoof, file_id + ".flac")

        shutil.copy(src_file, dst_file)

print("✅ ASVspoof 2019 train set prepared!")
print(f"Bonafide samples in: {target_bonafide}")
print(f"Spoof samples in: {target_spoof}")
