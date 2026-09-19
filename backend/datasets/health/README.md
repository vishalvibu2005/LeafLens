# Health dataset

For the binary classifier, organise source images as:

```text
health/
├── Healthy/
└── Diseased/
```

`training/train_health.py` creates stratified train/validation/test splits.
Keep near-duplicate photos of the same physical leaf in the same split to
avoid leakage. Include different lighting, backgrounds, cameras, viewing
angles, severities, and plant species only where that coverage is intended.

For later species-aware work, keep coverage explicit, for example
`mango/healthy`, `mango/diseased`, `neem/healthy`, and `neem/diseased`. A
model must not be presented as diagnosing a species or condition that was not
included in its training and evaluation data.
