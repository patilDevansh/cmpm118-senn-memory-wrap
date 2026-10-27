# CMPM 118 – Self-Explainable DNNs (Memory Wrap)

Work for the **AIEA Lab auditor program (UCSC CMPM 118, Fall 2026)** on the *Self-Explainable Deep Neural Networks* project.

Author: Devansh Patil (3rd-year CS, UCSC)

This repo holds my helper scripts, Nautilus job files and written reports. It does **not** contain the Memory Wrap code, the dataset or the model. Those come from the authors' repository: [KRLGroup/memory-wrap](https://github.com/KRLGroup/memory-wrap) (MIT license), which includes the pre-trained model `paper/models/2000.pt`.

## What's here

| Path | What it is |
|---|---|
| `reports/Task1_Nautilus_OnePage.md` | Task 1: onboarding to Nautilus (one page) |
| `reports/Task1_3_Nautilus_Onboarding.md` | Task 3: Nautilus setup, in more detail |
| `reports/Task2_Project_Onboarding.md` | Task 2: running Memory Wrap locally and generating memory images |
| `reports/Task4_Nautilus_Run.md` | Task 4: running the same code headless on Nautilus |
| `reports/Task5_Paper_Summary.md` | Task 5: summary of the Memory Wrap paper |
| `reports/figures/local/`, `reports/figures/nautilus/` | Example memory-image figures from each run |
| `scripts/` | Helper scripts (below) |
| `nautilus/` | Kubernetes Job and PVC used for Task 4 |

## Scripts

- `scripts/parquet_to_mat.py` – SVHN's original download server was unreachable, so this rebuilds `train_32x32.mat` / `test_32x32.mat` (the layout `torchvision.datasets.SVHN` reads) from the Hugging Face mirror [`ufldl-stanford/svhn`](https://huggingface.co/datasets/ufldl-stanford/svhn). Split sizes match the original (73,257 train / 26,032 test).
- `scripts/run_with_local_svhn.py` – launcher that skips torchvision's MD5 check for those rebuilt files, then runs a Memory Wrap script as if called with `python script.py`.
- `scripts/max_images.patch` – adds an optional `--max_images` flag to `paper/scripts/generate_memory_images.py` so it doesn't render all 8,678 figures.

## Reproduce locally

```bash
git clone https://github.com/KRLGroup/memory-wrap.git senn && cd senn
python3 -m venv .venv && source .venv/bin/activate
pip install torch torchvision memorywrap captum absl-py entmax einops pyyaml scipy pyarrow
git apply ../scripts/max_images.patch
cd paper
# download the Hugging Face SVHN parquet files into datasets_raw/ as train.parquet and test.parquet, then:
mkdir -p datasets && python ../../scripts/parquet_to_mat.py datasets_raw datasets
cp ../../scripts/run_with_local_svhn.py .
python run_with_local_svhn.py eval.py --path models/2000.pt                         # test accuracy
cd scripts && python ../run_with_local_svhn.py generate_memory_images.py --path_model ../models/2000.pt --max_images 20
```

## Results

| Run | Test accuracy (pre-trained MobileNet-v2 + Memory Wrap, 2,000 SVHN training samples) | Eval time |
|---|---|---|
| Laptop (CPU) | 80.37% | ~26 min |
| Nautilus (CPU, 4 cores) | 80.37% | ~10 min |

The paper reports 81.44 ± 0.76% for this setting, averaged over 15 runs.

## Nautilus

`nautilus/senn-job.yaml` and `nautilus/senn-pvc.yaml` run the same evaluation as a small CPU-only Kubernetes Job in the lab's `aiea-auditors` namespace. See `reports/Task4_Nautilus_Run.md` for the commands, what went wrong on the first run, and the results.

## Credits

- Memory Wrap: B. La Rosa, R. Capobianco, D. Nardi. *A self-interpretable module for deep image classification on small data.* Applied Intelligence, 2022. [arXiv:2106.01440](https://arxiv.org/abs/2106.01440)
- Project lead: Mattia (Biagio) La Rosa. Course and lab: Prof. Leilani Gilpin, AIEA Lab, UC Santa Cruz.
