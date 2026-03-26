import os
import shutil

# Paths
original_folder = "data/bonafide"
augmented_folder = "data/bonafide_augmented"
merged_folder = "data/bonafide_merged"

# Create merged folder
os.makedirs(merged_folder, exist_ok=True)

# Copy original files
for file in os.listdir(original_folder):
    if file.endswith(".wav") or file.endswith(".flac"):
        shutil.copy(os.path.join(original_folder, file),
                    os.path.join(merged_folder, file))

# Copy augmented files
for file in os.listdir(augmented_folder):
    if file.endswith(".wav") or file.endswith(".flac"):
        shutil.copy(os.path.join(augmented_folder, file),
                    os.path.join(merged_folder, file))

print("✅ Merge complete! All bonafide files (original + augmented) are now in:", merged_folder)