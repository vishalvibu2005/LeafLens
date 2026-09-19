"""Train an evaluated LeafLens health model from an ImageFolder dataset.

Usage: python training/train_health.py --data datasets/health
The script deliberately has no invented metrics: metadata is written only
after evaluation on a held-out test split.
"""
from __future__ import annotations

import argparse
import json
import random
from datetime import datetime, timezone
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True, help="ImageFolder directory, e.g. datasets/health")
    parser.add_argument("--output", type=Path, default=Path("models/health"))
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--patience", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def metrics_from_predictions(targets, predictions, classes):
    import numpy as np
    class_count = len(classes)
    matrix = np.zeros((class_count, class_count), dtype=int)
    for actual, predicted in zip(targets, predictions): matrix[actual, predicted] += 1
    precision, recall, f1 = [], [], []
    for index in range(class_count):
        tp = matrix[index, index]; fp = matrix[:, index].sum() - tp; fn = matrix[index, :].sum() - tp
        p = tp / (tp + fp) if tp + fp else 0.0; r = tp / (tp + fn) if tp + fn else 0.0
        precision.append(p); recall.append(r); f1.append(2 * p * r / (p + r) if p + r else 0.0)
    report = {
        name: {"precision": float(precision[index]), "recall": float(recall[index]), "f1": float(f1[index]), "support": int(matrix[index, :].sum())}
        for index, name in enumerate(classes)
    }
    summary = {"accuracy": float(matrix.trace() / matrix.sum()) if matrix.sum() else 0.0, "precision": float(np.mean(precision)), "recall": float(np.mean(recall)), "f1": float(np.mean(f1))}
    return matrix, summary, report


def main():
    args = parse_args()
    import numpy as np
    import torch
    from torch import nn
    from torch.utils.data import DataLoader, Subset
    from torchvision import datasets, models, transforms

    random.seed(args.seed); np.random.seed(args.seed); torch.manual_seed(args.seed)
    if not args.data.is_dir(): raise SystemExit(f"Dataset directory does not exist: {args.data}")
    base = datasets.ImageFolder(args.data)
    if len(base.classes) < 2: raise SystemExit("At least two class folders are required.")
    if len(base) < 20: raise SystemExit("At least 20 images are required for stratified train/validation/test splits.")
    labels = [label for _, label in base.samples]
    groups = {label: [] for label in range(len(base.classes))}
    for index, label in enumerate(labels): groups[label].append(index)
    train_idx, val_idx, test_idx = [], [], []
    for indices in groups.values():
        random.shuffle(indices); count = len(indices); test_end = max(1, round(count * .15)); val_end = test_end + max(1, round(count * .15))
        test_idx += indices[:test_end]; val_idx += indices[test_end:val_end]; train_idx += indices[val_end:]
    if not train_idx or not val_idx or not test_idx: raise SystemExit("Each class needs enough images for all three splits.")
    normalize = transforms.Normalize([.485, .456, .406], [.229, .224, .225])
    train_transform = transforms.Compose([transforms.Resize((224, 224)), transforms.RandomHorizontalFlip(), transforms.RandomRotation(12), transforms.ColorJitter(.15, .15, .1, .03), transforms.ToTensor(), normalize])
    eval_transform = transforms.Compose([transforms.Resize((224, 224)), transforms.ToTensor(), normalize])
    train_data = datasets.ImageFolder(args.data, transform=train_transform); eval_data = datasets.ImageFolder(args.data, transform=eval_transform)
    train_loader = DataLoader(Subset(train_data, train_idx), batch_size=args.batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(Subset(eval_data, val_idx), batch_size=args.batch_size, num_workers=0)
    test_loader = DataLoader(Subset(eval_data, test_idx), batch_size=args.batch_size, num_workers=0)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.DEFAULT)
    model.classifier[3] = nn.Linear(model.classifier[3].in_features, len(base.classes)); model.to(device)
    counts = np.bincount([labels[index] for index in train_idx], minlength=len(base.classes))
    criterion = nn.CrossEntropyLoss(weight=torch.tensor(len(train_idx) / (len(base.classes) * counts), dtype=torch.float32, device=device))
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    best_accuracy, stale, best_state = -1.0, 0, None
    for epoch in range(args.epochs):
        model.train()
        for images, targets in train_loader:
            optimizer.zero_grad(); loss = criterion(model(images.to(device)), targets.to(device)); loss.backward(); optimizer.step()
        model.eval(); hits = total = 0
        with torch.no_grad():
            for images, targets in val_loader:
                predicted = model(images.to(device)).argmax(1).cpu(); hits += int((predicted == targets).sum()); total += len(targets)
        accuracy = hits / total
        print(f"epoch {epoch + 1}: validation accuracy={accuracy:.4f}")
        if accuracy > best_accuracy:
            best_accuracy, stale = accuracy, 0; best_state = {key: value.cpu() for key, value in model.state_dict().items()}
        else:
            stale += 1
            if stale >= args.patience: break
    model.load_state_dict(best_state); model.eval(); predictions, targets_all = [], []
    with torch.no_grad():
        for images, targets in test_loader:
            predictions.extend(model(images.to(device)).argmax(1).cpu().tolist()); targets_all.extend(targets.tolist())
    matrix, metric_values, report = metrics_from_predictions(targets_all, predictions, base.classes)
    args.output.mkdir(parents=True, exist_ok=True)
    torch.save({"architecture": "mobilenet_v3_small", "model_state_dict": best_state}, args.output / "best.pt")
    metadata = {"model_version": "1.0.0", "architecture": "mobilenet_v3_small", "classes": base.classes, "input_size": 224, "confidence_threshold": .60, "trained_at": datetime.now(timezone.utc).isoformat(), "dataset": str(args.data), "split": {"train": len(train_idx), "validation": len(val_idx), "test": len(test_idx)}, "metrics": metric_values, "confusion_matrix": matrix.tolist(), "classification_report": report}
    (args.output / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__": main()
