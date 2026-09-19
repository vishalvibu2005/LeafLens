"""Train the LeafLens leaf instance-segmentation model.

Expected dataset:
    backend/datasets/leaf_detection/data.yaml

The YAML must be a YOLO segmentation dataset with ONE class representing a leaf.
The trained checkpoint is copied to:
    backend/models/leaf_detector/best.pt

Example:
    python training/train_detector.py --data datasets/leaf_detection/data.yaml
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--device", default="0", help="0 for NVIDIA GPU, cpu for CPU")
    args = parser.parse_args()

    if not args.data.exists():
        raise SystemExit(f"Dataset YAML not found: {args.data}")

    from ultralytics import YOLO

    model = YOLO("yolo11n-seg.pt")
    model.train(
        data=str(args.data.resolve()),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        project="models/leaf_detector_training",
        name="yolo11n_seg",
        exist_ok=True,
        patience=10,
        workers=0,
        pretrained=True,
    )

    best = Path("models/leaf_detector_training/yolo11n_seg/weights/best.pt")
    target = Path("models/leaf_detector/best.pt")
    if not best.exists():
        raise SystemExit(f"Training finished but best checkpoint was not found: {best}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(best, target)
    print(f"Saved LeafLens detector to: {target.resolve()}")


if __name__ == "__main__":
    main()
