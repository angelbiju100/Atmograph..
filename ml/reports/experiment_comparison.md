# AtmoGraph – Initial ML Experiments

## 1\. Dataset

**Dataset:** SynDelay v1  
**Records:** 155,488  
**Task:** Three-class delivery prediction  
**Dataset type:** Synthetic

### Class distribution

|Class|Meaning|Records|Percentage|
|-|-|-:|-:|
|0|Early delivery|36,724|23.62%|
|1|On-time delivery|29,055|18.69%|
|2|Delayed delivery|89,709|57.70%|

Note: The first two class counts differ from those reported in the published paper. This discrepancy requires verification.

## 2\. Experiment A – Random Forest with shipping mode

* Accuracy: 0.5673
* Macro F1: 0.4862
* Weighted F1: 0.5584

## 3\. Experiment B – Random Forest without shipping mode

* Accuracy: 0.3991
* Macro F1: 0.3336
* Weighted F1: 0.4099

## 4\. ZeroRule baseline

* Accuracy: approximately 0.5770
* Macro F1: approximately 0.2439

## 5\. Initial findings

1. Shipping mode has a substantial influence on model performance.
2. Removing shipping mode reduces Macro F1 by approximately 15.26 percentage points.
3. Random Forest with shipping mode outperforms ZeroRule on Macro F1.
4. Accuracy alone is insufficient because the dataset is imbalanced.
5. Further investigation is needed to establish whether shipping mode is available at the intended prediction time and how the synthetic labels were generated.

## 6\. Limitations

* SynDelay is synthetic, not a collection of real-world delivery outcomes.
* The current experiments use a random stratified split.
* The test set remains reserved.
* The results do not establish real-world predictive performance.
* The relationship between shipping mode and target labels requires further investigation.





\## 6. GraphSAGE Feature Ablation Experiment

### Objective

A controlled feature ablation experiment was conducted to investigate the contribution of network degree features to GraphSAGE link-prediction performance.

The original node feature matrix contained:

- 106 location features
- 512 product TF-IDF features
- 2 network degree features (log in-degree and log out-degree)

For the ablation experiment, the two degree features were removed, reducing the input feature dimension from 620 to 618.

### Experimental Consistency

Both GraphSAGE experiments used:

- The same training, validation and test edge splits.
- The same validation and test negative-edge files.
- The same random seed (42).
- The same training negative-sampling algorithm and configuration.
- The same two-layer GraphSAGE architecture with mean aggregation.
- The same hidden dimension (128) and embedding dimension (64).
- The same dropout rate (0.3).
- The same Adam optimizer and learning rate (0.001).
- The same weight decay (0.0001).
- The same maximum epochs (100) and early-stopping patience (15).

The only intended input-feature difference was the removal of the two degree features. The models were therefore compared under matching data splits and training configurations. Their training trajectories and best epochs were allowed to differ.

### Results

| Model | Test ROC-AUC | Test Average Precision |
|---|---:|---:|
| GraphSAGE with degree features | 0.9345 | 0.9302 |
| GraphSAGE without degree features | 0.9345 | 0.9259 |
| Degree-based heuristic | 0.9405 | 0.9382 |

### Observations

1. Removing degree features did not change test ROC-AUC at four decimal places.
2. Average Precision decreased from 0.9302 to 0.9259 after removing degree features.
3. GraphSAGE without degree features retained strong link-prediction performance, suggesting that location, product and graph-neighbour information provide useful predictive signal.
4. The degree-based heuristic achieved the highest ROC-AUC and Average Precision among the evaluated methods.
5. GraphSAGE did not demonstrate a measurable performance advantage over the simpler degree-based baseline.

### Interpretation and Limitations

The ablation suggests that GraphSAGE can retain strong link-prediction performance without explicitly receiving degree features. However, the results do not establish that location and product attributes independently improve predictive performance.

The difference between the two GraphSAGE models is small and has not been tested for statistical significance. Although their data splits, negative-sampling procedures and key training configurations were matched, the generated training negative-edge arrays have not yet been directly compared element by element.

The task is static directed link prediction on AnonNet, not real-world disruption prediction. Random edge splitting and randomly sampled non-edges may also make the task easier than predicting future network connections.

### Saved Outputs

- `ml/models/graphsage_without_degree.pt`
- `ml/reports/graphsage_without_degree_results.json`
- `ml/reports/graphsage_without_degree_history.csv`
