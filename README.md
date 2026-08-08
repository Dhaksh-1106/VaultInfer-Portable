# VaultInfer-Portable

A lightweight, self-contained inference tool that classifies a text sentence as **ALERT** or **NORMAL**, using sentence embeddings and a custom-trained logistic regression classifier.

This is the portable, plug-and-run version of the VaultInfer project — no training pipeline, no encryption stack, just clone and run.

---

## How it works

1. **Embedding** — The input sentence is passed through [`all-MiniLM-L6-v2`](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2), a pretrained sentence-transformer model, producing a dense 384-dimensional vector representation of the sentence's meaning.

2. **Classification** — That embedding is fed into a custom-trained logistic regression classifier (`vault_model`), trained from scratch on a labeled ALERT/NORMAL sentence dataset.

3. **Output** — The script prints the predicted probability that the input is an ALERT.

The classifier achieves **99.4% accuracy** (0.007 SD across cross-validation folds).

> This portable build runs plain inference only — no homomorphic encryption. See [Related projects](#related-projects) below for the encrypted version.

---

## Project structure

```
VaultInfer-Portable/
├── run.py                  # Entry point — run this to classify a sentence
├── vault_model              # Custom-trained logistic regression classifier (joblib)
├── vault_weights.npy         # Model weights (reference/legacy artifact)
├── vault_bias.npy            # Model bias (reference/legacy artifact)
├── requirements.txt          # Python dependencies
├── vault_model_cache/        # Auto-generated on first run — not tracked in git
└── .gitignore
```

---

## Setup

**1. Clone the repo**

```bash
git clone https://github.com/Dhaksh-1106/VaultInfer-Portable
cd VaultInfer-Portable
```

**2. Create a virtual environment**

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # macOS/Linux
```

**3. Install dependencies**

```bash
python -m pip install -r requirements.txt
```

---

## Usage

```bash
python run.py
```

You'll be prompted to enter a sentence:

```
Enter your sentence : <your text here>

-------Final Classification------
Probability of alert is : --.-- %
```

### First run

On the first run, the script downloads `all-MiniLM-L6-v2` from Hugging Face Hub (~80–90MB) and caches it locally in `vault_model_cache/`. Every run after that loads from the local cache — no repeated downloads, no internet needed once cached.

---

## Requirements

- Python 3.10+
- Core dependencies (see `requirements.txt` for exact versions):
  - `sentence-transformers` — generates sentence embeddings
  - `scikit-learn` — required to unpickle and run the classifier (used internally by `joblib.load`, even though it's not directly imported in `run.py`)
  - `joblib` — loads the trained model artifact

---

## Use cases

VaultInfer separates genuine threat/anomaly language from routine or administrative text — including tricky cases like negations ("no anomalies detected"), terse log-style phrasing, and jargon-heavy sentences that sound alarming but aren't.

- Triaging logs, alerts, or messages in a monitoring dashboard
- First-pass filter in an incident-response / SOC workflow
- Screening free-text tickets or reports before routing to a human

---

## Related projects

This repo lives alongside two other projects in the same family, both hosted in [VaultInfer](https://github.com/chiragbulbule/VaultInfer):

### 🔐 VaultInfer (full repo)
The complete research pipeline this classifier comes from — same model, but with **privacy-preserving inference** built in. It runs classification directly on **encrypted embeddings** using **TenSEAL (CKKS homomorphic encryption)**, so sentence content is never exposed in plaintext during prediction. To make logistic regression work under encryption, the sigmoid function is approximated with a degree-5 Taylor polynomial. Trained and validated via stratified k-fold cross-validation on a 350-sentence ALERT/NORMAL dataset.

### 🩻 VaultMed
A sibling project applying the same encrypted-inference philosophy to medical imaging instead of text — classifying chest X-rays for pneumonia detection (**CheXNet → clip(p95) → RobustScaler → Logistic Regression**), reaching 91% test accuracy (96% PNEUMONIA recall, 82% NORMAL recall).

### 📦 VaultInfer-Portable (this repo)
The same trained classifier, stripped of the encryption stack, for instant local use — drop in a sentence, get an ALERT/NORMAL probability, no setup beyond `pip install`.

---

## Notes

- `vault_model_cache/` is excluded from version control (`.gitignore`) and regenerates automatically.
- The classifier expects embeddings from `all-MiniLM-L6-v2` specifically (384-dim); swapping the embedding model without retraining will break predictions.
