from sklearn.metrics import confusion_matrix, classification_report
import numpy as np

# Validation
model.eval()
vc, vt = 0, 0
all_true, all_pred, all_spoof_prob = [], [], []

with torch.no_grad():
    for specs, lbls in te_loader:
        specs, lbls = specs.to(device), lbls.to(device)
        out = model(specs)
        probs = torch.softmax(out, dim=1)[:, 1]   # spoof prob
        preds = out.argmax(1)

        vc += (preds == lbls).sum().item()
        vt += lbls.size(0)

        all_true.extend(lbls.cpu().numpy().tolist())
        all_pred.extend(preds.cpu().numpy().tolist())
        all_spoof_prob.extend(probs.cpu().numpy().tolist())

val_acc = 100 * vc / vt
print(f"Validation Acc: {val_acc:.2f}%")
print("Confusion Matrix:")
print(confusion_matrix(all_true, all_pred))
print(classification_report(all_true, all_pred, target_names=["bonafide", "spoof"], digits=4))

bonafide_scores = [p for y, p in zip(all_true, all_spoof_prob) if y == 0]
spoof_scores    = [p for y, p in zip(all_true, all_spoof_prob) if y == 1]
print(f"Mean spoof prob on bonafide: {np.mean(bonafide_scores):.4f}")
print(f"Mean spoof prob on spoof:    {np.mean(spoof_scores):.4f}")
