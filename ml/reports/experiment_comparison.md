# AtmoGraph – Initial ML Experiments

## 1. Dataset

**Dataset:** SynDelay v1  
**Records:** 155,488  
**Task:** Three-class delivery prediction  
**Dataset type:** Synthetic

### Class distribution

| Class | Meaning | Records | Percentage |
|---|---|---:|---:|
| 0 | Early delivery | 36,724 | 23.62% |
| 1 | On-time delivery | 29,055 | 18.69% |
| 2 | Delayed delivery | 89,709 | 57.70% |

Note: The first two class counts differ from those reported in the published paper. This discrepancy requires verification.

## 2. Experiment A – Random Forest with shipping mode

- Accuracy: 0.5673
- Macro F1: 0.4862
- Weighted F1: 0.5584

## 3. Experiment B – Random Forest without shipping mode

- Accuracy: 0.3991
- Macro F1: 0.3336
- Weighted F1: 0.4099

## 4. ZeroRule baseline

- Accuracy: approximately 0.5770
- Macro F1: approximately 0.2439

## 5. Initial findings

1. Shipping mode has a substantial influence on model performance.
2. Removing shipping mode reduces Macro F1 by approximately 15.26 percentage points.
3. Random Forest with shipping mode outperforms ZeroRule on Macro F1.
4. Accuracy alone is insufficient because the dataset is imbalanced.
5. Further investigation is needed to establish whether shipping mode is available at the intended prediction time and how the synthetic labels were generated.

## 6. Limitations

- SynDelay is synthetic, not a collection of real-world delivery outcomes.
- The current experiments use a random stratified split.
- The test set remains reserved.
- The results do not establish real-world predictive performance.
- The relationship between shipping mode and target labels requires further investigation.