

\# ATMOGRAPH – MACHINE LEARNING HANDOVER

\*\*Project:\*\* AtmoGraph  

\*\*Module:\*\* Machine Learning and Network Intelligence  

\*\*Status:\*\* Core ML experiments completed; backend integration pending



\---



\## 1. Project Overview



AtmoGraph is a supply-chain network intelligence platform designed to explore network structure, identify structurally important nodes, simulate hypothetical disruption propagation and investigate network connectivity.



The current ML implementation uses two separate datasets:



1\. \*\*AnonNet:\*\* An anonymised directed supply network dataset used for graph analysis, link prediction and propagation simulations.

2\. \*\*SynDelay:\*\* A synthetic delivery dataset used for delivery-outcome classification experiments.



These datasets are separate and do not have a verified common identifier. They must not be artificially joined.



\---



\## 2. Dataset Information



\### AnonNet



\- Nodes: 7,245

\- Directed edges: 43,926

\- Self-loops: 4 in the original graph

\- Weakly connected components: 1

\- Average in-degree: 6.06

\- Average out-degree: 6.06



The graph uses the original source-to-target edge direction. The business meaning of edge direction has not yet been independently established.



\### SynDelay



\- Records: 155,488

\- Features: 41

\- Target classes:

&#x20; - 0: Early

&#x20; - 1: On-time

&#x20; - 2: Delayed



SynDelay is synthetic. Its classification results should not be presented as validated real-world delivery predictions.



\---



\## 3. Machine Learning Experiments



\### 3.1 Random Forest – Delivery Classification



Three experiments were conducted.



| Experiment | Accuracy | Macro F1 |

|---|---:|---:|

| Full feature model | 0.5673 | 0.4862 |

| Without shipping mode | 0.3991 | 0.3336 |

| Shipping mode only | 0.5711 | 0.4825 |



The shipping-mode-only model performed almost as well as the full model. This indicates a strong association between shipping mode and the synthetic delivery label.



The intended prediction time and label-generation process need further investigation before treating the model as suitable for prospective delivery prediction.



Model files:



\- `ml/models/random\_forest\_baseline.joblib`

\- `ml/models/random\_forest\_without\_shipping\_mode.joblib`



\### 3.2 GraphSAGE – Directed Link Prediction



A two-layer GraphSAGE architecture was trained using:



\- Location one-hot features

\- Product TF-IDF features

\- Log in-degree and out-degree features

\- 128 hidden channels

\- 64-dimensional node embeddings

\- Mean aggregation

\- Dropout: 0.3

\- Adam optimiser

\- Learning rate: 0.001

\- Weight decay: 0.0001



The graph was divided into:

\- Training: 80%

\- Validation: 10%

\- Testing: 10%



Four self-loops were excluded from this experiment.



Results:



| Metric | Result |

|---|---:|

| Best epoch | 30 |

| Validation ROC-AUC | 0.9398 |

| Test ROC-AUC | 0.9345 |

| Test Average Precision | 0.9302 |



Model files:



\- `ml/models/graphsage\_link\_prediction.pt`

\- `ml/models/graphsage\_node\_embeddings.npy`



\### 3.3 Link Prediction Baseline Comparison



All methods were evaluated on the same held-out test positive and negative edge sets.



| Method | ROC-AUC | Average Precision |

|---|---:|---:|

| Degree-based heuristic | 0.9405 | 0.9382 |

| GraphSAGE | 0.9345 | 0.9302 |

| Directed common neighbours | 0.7007 | 0.6991 |

| Random | 0.5030 | 0.5052 |



The degree-based heuristic slightly outperformed GraphSAGE. Therefore, GraphSAGE should not be described as the best-performing method.



\### 3.4 GraphSAGE Feature Ablation



The two degree features were removed, leaving 618 location and product features.



| Model | Test ROC-AUC | Test AP |

|---|---:|---:|

| GraphSAGE with degree | 0.9345 | 0.9302 |

| GraphSAGE without degree | 0.9345 | 0.9259 |



The model retained strong performance without explicit degree features.



The difference is small and has not been tested for statistical significance. Training negative samples should be verified as identical before treating this as a strictly controlled ablation.



Model file:



\- `ml/models/graphsage\_without\_degree.pt`



\---



\## 4. Network Analysis



The network analysis includes:



\- In-degree and out-degree

\- Total degree

\- Betweenness centrality

\- PageRank

\- Node-removal disruption simulation



Important findings:



\- Node n4859 has the highest total degree: 516.

\- Node n5063 has the highest betweenness: 0.035472.

\- Node n5063 also has the highest PageRank: 0.006615.



Node-removal simulation:



| Removed node | Components after removal | Nodes outside largest component |

|---|---:|---:|

| n4859 | 25 | 24 |

| n5063 | 4 | 3 |

| n6211 | 8 | 7 |



These are structural stress tests, not estimates of actual financial or operational losses.



\---



\## 5. Propagation Simulation



An Independent Cascade-style simulation was implemented.



Configuration:



\- Initial node: n5063

\- Maximum propagation steps: 50

\- Transmission probabilities: 0.05, 0.10, 0.20 and 0.30

\- 100 simulations per probability

\- 400 simulations in total



Mean affected nodes:



| Probability | Mean affected nodes | Mean percentage affected |

|---|---:|---:|

| 0.05 | 28.91 | 0.3990% |

| 0.10 | 877.52 | 12.1121% |

| 0.20 | 2,822.65 | 38.9600% |

| 0.30 | 3,858.12 | 53.2522% |



All 400 simulations naturally terminated before reaching the step limit.



Statistical analysis includes bootstrap confidence intervals based on 5,000 resamples per probability.



These transmission probabilities are hypothetical and have not been calibrated against observed disruptions.



\---



\## 6. Important ML Files



\### Source scripts



`ml/src/`



\- `inspect\_datasets.py`

\- `analyze\_network.py`

\- `network\_analysis.py`

\- `prepare\_graph\_features.py`

\- `prepare\_graph\_splits.py`

\- `inspect\_graph\_features.py`

\- `train\_baseline.py`

\- `test\_shipping\_mode\_only.py`

\- `train\_graphsage.py`

\- `train\_graphsage\_no\_degree.py`

\- `evaluate\_link\_prediction\_baselines.py`

\- `propagation\_simulation.py`

\- `analyze\_propagation\_statistics.py`



\### Processed graph data



`ml/data/processed/`



\- `node\_features.npy`

\- `node\_feature\_ids.csv`

\- `node\_feature\_names.csv`

\- `train\_edges.npy`

\- `val\_edges.npy`

\- `test\_edges.npy`

\- `val\_negative\_edges.npy`

\- `test\_negative\_edges.npy`

\- `message\_passing\_edges.npy`



\### Reports



`ml/reports/`



Contains dataset inspection, model results, training histories, link prediction comparisons, network centrality analysis, propagation simulations and statistical analysis.



\---



\## 7. Backend Integration Requirements



The backend team should:



1\. Preserve the existing FastAPI endpoints where possible.

2\. Implement model-loading services for the required ML models.

3\. Load and validate processed graph features and node ID mappings.

4\. Integrate network centrality and node investigation services.

5\. Integrate propagation simulation results and configuration.

6\. Add database persistence for simulation runs and relevant results.

7\. Handle missing nodes, invalid requests and model-loading errors.

8\. Ensure predictions and simulations are clearly labelled according to their actual methodology.



Existing prototype endpoints:



\- `GET /health`

\- `GET /api/network/summary`

\- `GET /api/network/top-nodes`

\- `GET /api/network/nodes/{node\_id}`

\- `POST /api/network/simulate/{node\_id}`

\- `GET /api/network/nodes/{node\_id}/neighbors`



The current backend reads CSV data into memory. Database integration remains part of backend engineering.



\---



\## 8. Technical Limitations



The following limitations must be retained in project documentation:



1\. AnonNet edge semantics have not been independently verified.

2\. AnonNet does not contain observed disruption labels.

3\. Propagation probabilities are hypothetical.

4\. SynDelay is synthetic and separate from AnonNet.

5\. GraphSAGE performs static link prediction, not disruption prediction.

6\. Random edge splitting does not evaluate future network evolution.

7\. Randomly sampled non-edges may be easier to classify than realistic candidate links.

8\. The degree heuristic slightly outperforms GraphSAGE in the current evaluation.

9\. The Random Forest results show strong dependence on shipping mode.

10\. The models require further validation before real-world operational use.



\---



\## 9. Division of Responsibilities



\### Machine Learning and Research



Completed:

\- Dataset inspection

\- Random Forest experiments

\- Graph feature engineering

\- GraphSAGE link prediction

\- Baseline comparisons

\- Network centrality analysis

\- Node-removal simulations

\- Monte Carlo propagation analysis

\- Statistical analysis

\- Experiment documentation



Remaining:

\- Verify identical training negative samples for the GraphSAGE ablation.

\- Support backend model integration.

\- Validate the integrated application with the backend team.



\### Backend Engineering and Infrastructure



Partner responsibility:

\- Database design and implementation

\- Data ingestion and validation

\- Backend architecture

\- Model-loading API services

\- Database integration

\- API testing

\- Frontend/backend integration

\- Deployment preparation



\---



\## 10. Final Project Status



The core ML experimentation and analysis phase is complete.



The next phase is integration: connecting the ML assets and network intelligence functionality to the backend and database, followed by end-to-end application testing.



\*\*AtmoGraph should be presented as a network intelligence and hypothetical disruption-simulation prototype, not as a validated real-world disruption forecasting system.\*\*



