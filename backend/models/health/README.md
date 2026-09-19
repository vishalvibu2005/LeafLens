# Health checkpoint format

Place a real, evaluated health-model checkpoint at `best.pt` and its companion
metadata at `metadata.json`. `app.models.health_classifier.HealthClassifier`
supports either a serialized PyTorch `nn.Module`, or the state-dictionary
checkpoint produced by `training/train_health.py`.

The metadata must describe the actual evaluation run, for example:

```json
{
  "model_version": "1.0.0",
  "architecture": "mobilenet_v3_small",
  "classes": ["Healthy", "Diseased"],
  "input_size": 224,
  "confidence_threshold": 0.6,
  "trained_at": "2026-09-18T00:00:00+00:00",
  "dataset": "datasets/health",
  "metrics": {"accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1": 0.0}
}
```

The values above are illustrative structure only, not valid model metrics. Do
not copy them into a production metadata file; the training script writes real
test-set metrics. Until a compatible checkpoint is installed, the API returns
no health prediction and the UI says that the model is unavailable.
