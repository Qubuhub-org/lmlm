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
- A deterministic byte-pair (BPE) tokenizer that learns merges from a local
  text corpus without downloading a vocabulary.
- A validated decoder-model configuration with tokenizer-sized vocabularies.
- A causal decoder-only transformer implemented inside the LMLM package.
- Local checkpoint save/load, including tokenizer metadata.
- A small-corpus training loop and command-line interface.
- CPU execution, with optional CUDA and Apple MPS acceleration through PyTorch.

**Status:** this is an experimental text-only baseline. It is not yet a complete
multimodal model, and no production-trained checkpoint is included. The
existing Node `/api/chat` endpoint remains a mock and is not connected to this
neural runtime.

## Requirements

- Python 3.10 or newer.
- PyTorch 2.2 or newer for model training and inference.
- CPU is sufficient for architecture experiments; a supported GPU is optional.

Install the core in editable mode:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[runtime]"
```

On Windows, activate the environment with `.venv\\Scripts\\activate`.

## Quick start

Create a small local corpus (at least 129 UTF-8 bytes for the default context):

```bash
mkdir -p data
printf 'LMLM is a local model. It learns from the text supplied to its trainer.\n' > data/sample.txt
```

Train with the byte tokenizer:

```bash
lmlm train data/sample.txt --output artifacts/lmlm-byte.pt --steps 100
```

Train a learned BPE vocabulary from the same local corpus:

```bash
lmlm train data/sample.txt --output artifacts/lmlm-bpe.pt --steps 100 \
  --tokenizer bpe --vocab-size 512 --min-frequency 2
```

Generate from either checkpoint. The checkpoint contains the tokenizer
metadata needed to encode prompts and decode generated tokens:

```bash
lmlm generate artifacts/lmlm-bpe.pt "LMLM is"
```

The sample corpus is only for a smoke test. Useful language generation
requires a substantially larger, curated corpus, evaluation, and a training
plan. A randomly initialized model does not produce useful assistant output.
The current BPE trainer is a simple deterministic implementation intended
for small local corpora, not a high-throughput production tokenizer trainer.

## Python API

```python
from lmlm_core import BPETokenizer, LMLMConfig
from lmlm_core.runtime import LMLMRuntime

corpus = "LMLM learns from local text. " * 100
tokenizer = BPETokenizer.train(corpus, vocab_size=512, min_frequency=2)
config = LMLMConfig(
    vocab_size=tokenizer.vocab_size,
    context_length=128,
    hidden_size=128,
    num_layers=2,
    num_heads=4,
)
runtime = LMLMRuntime.create_untrained(config, tokenizer)
runtime.save_checkpoint("artifacts/untrained-bpe.pt")
```

An untrained model produces random output. Train it before using it for a task.

## Tests

Run dependency-free tokenizer and configuration tests:

```bash
python -m unittest discover -s tests -v
```

GitHub Actions also installs CPU PyTorch and smoke-tests model forward,
byte-tokenized training, BPE-tokenized training, checkpoint reload, and
generation.

Run the existing Node API checks separately:

```bash
npm install
npm run check
npm test
```

The new Python core and legacy Python experiments have separate dependency
sets. Do not install the root legacy `requirements.txt` into the core
environment; many of its pins come from older Python ecosystems.

## Environment variables

The optional legacy Gemini adapter reads `GEMINI_API_KEY` from the process
environment. Set it in the shell or an approved secret manager before running
that adapter. The core model does not require this key or call Gemini.
`.env.example` documents the variable name; it is not an automatic dotenv
loader.

Never commit populated environment files or credentials. See
[SECURITY.md](SECURITY.md).

## Repository map

- `lmlm_core/` — native tokenizers, configuration, model, runtime, and trainer.
- `tests/` — tests for the new core.
- `docs/RECONSTRUCTION_STATUS.md` — findings, scope, and outstanding audit work.
- `docs/REPOSITORY_AUDIT.md` — legacy component and provenance inventory.
- `Lmlm/`, `Lmlm-protocol/`, `Notebooklmlm/`, `Notebookmarks/` — legacy
  experiments retained pending provenance and integration review.
- `server.js` — existing Node API; its chat route is explicitly a mock.

## Ownership and legacy assets

The repository contains historical assets and mixed license notices. Their
presence is not proof of ownership or redistribution rights. Review provenance
and licensing before packaging or redistributing them. Legacy research files
are being inventoried before deletion.

## Roadmap

1. Stabilize the native text core, training/evaluation loop, and checkpoint format.
2. Benchmark and optimize the learned tokenizer on a representative corpus.
3. Add memory and multimodal interfaces without delegating the core model to
   external providers.
4. Add resource-aware CPU/GPU backends and device profiling.
5. Integrate the runtime with the existing API only after inference contracts,
   limits, and tests are defined.
6. Complete file provenance, licensing, and historical secret audits.
