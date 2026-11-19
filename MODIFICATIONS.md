# Modifications and provenance

This repository adapts the graph-anomaly code from [MAD](https://gitlab.imt-atlantique.fr/publications1/mad), by **Esteban Bautista, Laurent Brisson, Cécile Bothorel, and Grégory Smits** (*MAD: Multi-Scale Anomaly Detection in Link Streams*, 17th ACM International Conference on Web Search and Data Mining (WSDM 2024), DOI [10.1145/3616855.3635834](https://doi.org/10.1145/3616855.3635834), [HAL hal-04361052](https://hal.science/hal-04361052)). The adaptation was used in the MuTGN experimental evaluation.

The comparison uses [MAD](https://gitlab.imt-atlantique.fr/publications1/mad), under `Proposed/graph_anomaly/`, as the upstream reference. 

## Main graph-level experiment

**File:** `test.py` (adapted from upstream `main.py`)

- Replaced command-line dataset, window-size, and initial-time arguments with YAML-based configuration of input/output paths, MAD context length, window size/shift, and training/test ratio.
- Added temporal window aggregation using the top-level `lsmanip` package. Each input interaction is assigned to every matching window; repeated edges in one window are collapsed to binary presence using a set.
- Restricted the loaded stream to the evaluation period and the preceding context needed by MAD. The first evaluated window is derived from the train/test ratio.
- Constructed graph queries and historical context on window indices. `context_length` therefore counts aggregated window-index steps rather than raw timestamp units.
- Anomaly scores are saved into a pickle file for external evaluation.

## Added code 

- `config.py`: YAML configuration loading and output-directory creation. 
- `scores_train_data.py`: utility for examining anomaly-score behavior on the training/validation split. 

## Dependencies and distribution scope

This distribution focuses on the graph-anomaly implementation used in MuTGN and does not include the original MAD node- or edge-anomaly experiment branches. Original MAD documentation is retained in `UPSTREAM_README.md`.

The MAD EUPL 1.2 license text is provided in `LICENSE.txt`. The `lsmanip` EUPL 1.2 license text is provided in both `MAD/lsmanip/LICENSE.txt` and `lsmanip/LICENSE.txt`.
