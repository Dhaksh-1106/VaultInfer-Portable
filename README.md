# VaultInfer-Portable

A lightweight, self-contained inference tool that classifies a text sentence as **ALERT** or **NORMAL**, using sentence embeddings and a logistic regression classifier. This is the portable, plug-and-run version of the VaultInfer project — no training pipeline, no heavy setup, just clone and run.

## How it works

1. **Embedding** — The input sentence is passed through [`all-MiniLM-L6-v2`](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2), a pretrained sentence-transformer model, producing a dense 384-dimensional vector representation of the sentence's meaning.
2. **Classification** — That embedding is fed into a custom-trained logistic regression classifier (`vault_model`), which outputs a probability of the sentence belonging to the **ALERT** class.
3. **Output** — The script prints the predicted probability (%) that the input is an ALERT.

The classifier was trained on a labeled dataset of ALERT/NORMAL sentences as part of the original VaultInfer project, achieving **99.4% accuracy** (0.007 SD across cross-validation folds).

> Note: this portable build runs plain inference only. It does not include the homomorphic-encryption (TenSEAL/CKKS) forward pass used in the full VaultInfer research pipeline — this version is meant for fast, local, unencrypted classification.

## Project structure

```
VaultInfer-Portable/
├── run.py                  # Entry point — run this to classify a sentence
├── vault_model              # Pretrained logistic regression classifier (joblib)
├── vault_weights.npy         # Model weights (reference/legacy artifact)
├── vault_bias.npy            # Model bias (reference/legacy artifact)
├── requirements.txt          # Python dependencies
├── vault_model_cache/        # Auto-generated on first run — not tracked in git
└── .gitignore
```

## Setup

**1. Clone the repo**

```bash
git clone <https://github.com/Dhaksh-1106/VaultInfer-Portable>
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

On the first run, the script downloads `all-MiniLM-L6-v2` from Hugging Face Hub (~80–90MB) and caches it locally in `vault_model_cache/`. Every subsequent run loads the model from this local cache — no repeated downloads, no internet connection required after the first launch.

## Requirements

- Python 3.10+
- See `requirements.txt` for exact package versions. Core dependencies:
  - `sentence-transformers` — for generating sentence embeddings
  - `scikit-learn` — required to unpickle and run the classifier (used internally by `joblib.load`, even though it's not directly imported in `run.py`)
  - `joblib` — for loading the pretrained model artifact

## Use cases

VaultInfer is trained to distinguish genuine alert-worthy language from routine, technical, or administrative text — the kind of judgment call a monitoring system, log pipeline, or incident-response tool has to make when deciding what deserves a human's attention. The training data spans a broad mix of categories, including:

- **Cyber and network threats** — intrusion attempts, suspicious traffic, security incidents
- **Physical and subtle threats** — understated or indirect warning language, not just overt danger phrasing
- **Industrial and critical-systems language** — equipment failures, safety-critical conditions
- **High-intensity vs. subtle alerts** — both loud, urgent phrasing and quieter, easy-to-miss warning signs
- **Terse, clipped alert phrasing** — short-form language typical of logs, radio chatter, or system messages
- **Linguistic negations** — sentences that use alert-sounding vocabulary but actually negate the threat (e.g. "no anomalies detected"), which the model needs to correctly classify as NORMAL despite surface-level similarity to ALERT phrasing
- **Administrative, casual, and routine technical text** — everyday operational language that should not be flagged
- **Technical vocabulary in normal contexts** — domain-specific jargon that sounds serious but describes routine operation, not a threat

This breadth is intentional — the goal isn't just keyword-matching on "alarming" words, but recognizing genuine semantic intent behind a sentence, including cases designed to fool a naive classifier (negations, jargon-heavy routine text, terse phrasing).

**Practical use cases:**

- Triaging incoming logs, alerts, or messages in a monitoring dashboard, surfacing the ones that actually warrant attention
- A lightweight first-pass filter in an incident-response or SOC (security operations center) style workflow
- Screening free-text fields (tickets, reports, chat messages) for genuine threat/anomaly language before routing to a human
- **VaultInfer (full repo)** extends this into a privacy-preserving setting — e.g. classifying sensitive operational or security text without ever decrypting it, useful where the content of alerts itself is confidential (defense, critical infrastructure, healthcare-adjacent ops)
- **VaultInfer-Portable (this repo)** is the same classifier stripped down for quick, local, unencrypted use — dropping a sentence in and getting an instant ALERT/NORMAL probability, without needing the encryption stack set up

## Related project

This portable build is a stripped-down, plain-inference version of the full **VaultInfer** project: **[VaultInfer](https://github.com/chiragbulbule/VaultInfer)**.

The full repo contains the complete research pipeline behind this classifier, including:

- Dataset engineering and training on a labeled 350-sentence ALERT/NORMAL corpus
- A degree-5 Taylor polynomial approximation of the sigmoid function, needed to make logistic regression compatible with homomorphic encryption
- A **TenSEAL (CKKS scheme)** encrypted forward pass — the classifier runs inference directly on encrypted embeddings, so the input sentence's content is never exposed in plaintext during prediction
- Stratified k-fold cross-validation used to arrive at the 99.4% accuracy figure

This portable repo exists purely for fast, local, unencrypted classification using the same trained model — it's meant for quick usage/demos, not for privacy-preserving inference. For the encrypted pipeline and the reasoning behind the model design, refer to the main repo above.

The same repo also contains **VaultMed**, a sibling project in the same encrypted-inference family, applied to medical imaging instead of text. It classifies chest X-rays for pneumonia detection using a **CheXNet → clip(p95) → RobustScaler → Logistic Regression** pipeline, achieving 91% test accuracy (96% PNEUMONIA recall, 82% NORMAL recall), with the same privacy-preserving philosophy of running inference on encrypted data rather than plaintext.

## Notes

- `vault_model_cache/` is excluded from version control (`.gitignore`) and regenerates automatically — no need to manually manage or clear it unless you want to force a re-download.
- The classifier expects embeddings from `all-MiniLM-L6-v2` specifically (384-dim); swapping the embedding model without retraining the classifier will break predictions.
