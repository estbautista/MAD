# MAD

This repository contains an adaptation of [MAD: Multi-Scale Anomaly Detection in Link Streams](https://gitlab.imt-atlantique.fr/publications1/mad), by Esteban Bautista, Laurent Brisson, Cécile Bothorel, and Grégory Smits ([WSDM 2024](https://doi.org/10.1145/3616855.3635834)). It applies MAD's graph-level anomaly detection method to **graph snapshots formed by aggregating temporal interactions within consecutive time windows**.

It addresses the following research question: **Can window-level anomalies still be detected after collapsing the interactions within each window into a single graph?** This adaptation was used as a baseline in the experimental evaluation of **MuTGN**.

For details on the changes, see [MODIFICATIONS.md](MODIFICATIONS.md). The original repository documentation is preserved in [UPSTREAM_README.md](UPSTREAM_README.md).

## Adaptation

The code includes a preprocessing step that aggregates temporal interactions within each time window into a single binary graph. Window size and shift are configurable, and overlapping windows are supported.

Each resulting graph is scored using MAD's original graph-level anomaly detection method, with the preceding `context_length` windows serving as historical context. The training/test split determines the first evaluation window, and anomaly scores are exported for external evaluation.

For details of the original MAD algorithm, refer to the [upstream repository](https://gitlab.imt-atlantique.fr/publications1/mad) and the [WSDM 2024 paper](https://doi.org/10.1145/3616855.3635834).

## Input and output

The input is a **headerless, comma-separated** temporal edge stream with three columns:

```text
source,destination,timestamp
```

For example (without the header line):

```text
0,1,0
1,2,60
0,2,120
```

Source and destination identifiers are read as strings; timestamps are read as integers. The test.py script writes a pickle file containing a **list of anomaly scores**, ordered by evaluation window.



## Configuration

Input/output paths and experiment parameters are specified in a YAML configuration file. It is passed using `--config`. An example is provided in [`config.example.yaml`](config.example.yaml):

```yaml
model:
  context_length: 30

splitting:
  train_test_ratio: 0.7
  window_size: 600
  window_shift: 600

paths:
  dataset: /data/example.csv
  score_file: /output/scores.pkl
```

The `window_size` and `window_shift` parameters control the temporal aggregation, while `context_length` specifies the number of preceding aggregated windows used by MADto fit its internal probabilistic model. The `train_test_ratio` determines the start of the test period.

## Reproducible environment

A validated environment uses **Python 3.15.2** with the dependencies pinned in [`requirements-reconstructed.txt`](requirements-reconstructed.txt): NumPy 2.5.5, PyWavelets 1.10.0, and PyYAML 6.0.3.

From the repository root, build the container image using [Podman](https://podman.io/) (Docker can also be used):

```bash
podman build --no-cache -t madagg:locked .
```

Verify that the MAD implementation imports successfully:

```bash
podman run --rm madagg:locked \
  python -c "import MAD.MAD, MAD.model, pywt; print('MAD imports OK')"
```

## Running window-level anomaly detection

The main entry point is `test.py`, which accepts the YAML configuration file through `--config`.

From the repository root, with `config.yaml` configured and the input dataset placed in `data/`:

```bash
mkdir -p outputs

podman run --rm \
  -v "$PWD/config.yaml:/config.yaml:ro,z" \
  -v "$PWD/data:/data:ro,z" \
  -v "$PWD/outputs:/output:Z" \
  madagg:locked \
  python /app/test.py --config /config.yaml
```

With the example configuration, anomaly scores are written to `outputs/scores.pkl`. The MuTGN repository documents the experiment-specific configurations and downstream evaluation.

## License and provenance

MAD and the bundled `lsmanip` code are distributed under **EUPL 1.2**. The license texts are retained in [`LICENSE.txt`](LICENSE.txt), [`MAD/lsmanip/LICENSE.txt`](MAD/lsmanip/LICENSE.txt), and [`lsmanip/LICENSE.txt`](lsmanip/LICENSE.txt). Both copies of `lsmanip` are retained to preserve the original MAD import structure and the separate window-aggregation runner.

## Citation

If you use the MAD method, please cite the original paper:

```bibtex
@inproceedings{bautista:hal-04361052,
  TITLE = {{MAD: Multi-Scale Anomaly Detection in Link Streams}},
  AUTHOR = {Bautista, Esteban and Brisson, Laurent and Bothorel, C{\'e}cile and Smits, Gr{\'e}gory},
  URL = {https://hal.science/hal-04361052},
  BOOKTITLE = {{The 17th ACM International Conference on Web Search and Data Mining}},
  ADDRESS = {M{\'e}rida (Yucatan), Mexico},
  YEAR = {2024},
  MONTH = Mar,
  DOI = {10.1145/3616855.3635834},
  PDF = {https://hal.science/hal-04361052v1/file/MAD_Paper.pdf},
  HAL_ID = {hal-04361052}
}
```
