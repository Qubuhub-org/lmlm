# LMLM — Large Multimodal Local Model

LMLM is an in-built model family designed to run inside the user's own device,
environment, or local playground. The model and its runtime are the product;
external model registries are not the core architecture.

This repository contains historical experiments and multiple language stacks.
The `lmlm-core` package establishes a native, local-first foundation without
depending on a hosted model provider.

## Current implementation

The native core currently provides:

- A reversible UTF-8 byte tokenizer.
- A deterministic byte-pair (BPE) tokenizer trained from local text.
- A validated decoder-only transformer with tokenizer-sized vocabularies.
- Local checkpoint save/load, including tokenizer metadata.
- Small-corpus training and a command-line interface.
- Deterministic next-token evaluation with cross-entropy and perplexity.
- CPU execution, with optional CUDA and Apple MPS acceleration through PyTorch.

**Status:** experimental text-only baseline. This is not yet a complete
multimodal model, and no production-trained checkpoint is included. The
existing Node `/api/chat` endpoint remains a mock and is not connected to this
neural runtime.

## Requirements and installation

- Python 3.10 or newer.
- PyTorch 2.2 or newer for training, inference, and evaluation.

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[runtime]"
```

## Quick start

Create a local UTF-8 corpus with enough content for the configured context:

```bash
mkdir -p data
printf 'LMLM is a local model. It learns from local text.\n' > data/sample.txt
```

Train a byte-tokenized model:

```bash
lmlm train data/sample.txt --output artifacts/lmlm-byte.pt --steps 100
```

Or train a BPE vocabulary from the same local corpus:

```bash
lmlm train data/sample.txt --output artifacts/lmlm-bpe.pt --steps 100 \
  --tokenizer bpe --vocab-size 512 --min-frequency 2
```

Generate locally:

```bash
lmlm generate artifacts/lmlm-bpe.pt "LMLM is"
```

Evaluate on a held-out UTF-8 text file:

```bash
lmlm evaluate artifacts/lmlm-bpe.pt data/validation.txt
```

Evaluation reports mean next-token cross-entropy loss, perplexity, the number
of scored target tokens, and the number of evaluation windows. The evaluator
uses fixed contiguous windows, scores every next-token target exactly once,
and does not shuffle or upload the corpus. Use a validation corpus that was
not used for training; otherwise the result is not a meaningful generalization
estimate. Perplexity is only comparable across models evaluated on the same
tokenization and dataset.

## Reproducibility

Training uses a configurable random seed (default `17`):

```bash
lmlm train data/train.txt --output artifacts/model.pt --seed 17
```

This seeds PyTorch's random generator. Exact bit-for-bit reproducibility across
different devices, PyTorch versions, and accelerator kernels is not guaranteed.

## Python API

```python
from lmlm_core.evaluate import evaluate_file
from lmlm_core.runtime import LMLMRuntime

runtime = LMLMRuntime.from_checkpoint("artifacts/model.pt", device="cpu")
metrics = evaluate_file(runtime, "data/validation.txt")
print(metrics)
```

An untrained model produces random output. Train it before using it for a task.
The current BPE trainer is a simple deterministic implementation intended for
small local corpora, not a high-throughput production tokenizer trainer.

## Tests

```bash
python -m unittest discover -s tests -v
```

GitHub Actions also runs CPU PyTorch training, checkpoint, generation, and
evaluation tests, plus the existing Node API checks and Docker build.

The new Python core and legacy Python experiments have separate dependency
sets. Do not install the root legacy `requirements.txt` into the core
environment; many pins are from older Python ecosystems.

## Security and repository map

The core model does not require a hosted provider key. Legacy provider
adapters remain separate. Never commit populated environment files or
credentials; see [SECURITY.md](SECURITY.md).

- `lmlm_core/` — native tokenizer, model, runtime, trainer, and evaluator.
- `tests/` — core tests.
- `docs/RECONSTRUCTION_STATUS.md` — reconstruction status and limitations.
- `docs/REPOSITORY_AUDIT.md` — legacy asset and provenance inventory.
- `server.js` — existing Node API; its chat route is a mock.

Historical assets remain pending provenance and licensing review.
