# LMLM — Large Multimodal Local Model

LMLM is an in-built model family designed to run inside the user's own device,
environment, or local playground. The model and its runtime are the product;
external model registries are not the core architecture.

This repository contains historical experiments and multiple language stacks.
The new `lmlm-core` package establishes a native, local-first foundation
without depending on a hosted model provider.

## Current implementation

The first native core increment provides:

- A deterministic UTF-8 byte tokenizer with reserved control tokens.
- A validated decoder-model configuration.
- A causal decoder-only transformer implemented inside the LMLM package.
- Local checkpoint save/load and autoregressive text generation.
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

Initialize a configuration:

```bash
lmlm init-config configs/small.json --context-length 128 --hidden-size 128
```

Train a local checkpoint:

```bash
lmlm train data/sample.txt --output artifacts/lmlm.pt --steps 100
```

Generate from the checkpoint:

```bash
lmlm generate artifacts/lmlm.pt "LMLM is"
```

The sample corpus is only for a smoke test. Useful language generation
requires a substantially larger, curated corpus, evaluation, and a training
plan. A randomly initialized model does not produce useful assistant output.

## Python API

```python
from lmlm_core import ByteTokenizer, LMLMConfig
from lmlm_core.runtime import LMLMRuntime

tokenizer = ByteTokenizer()
print(tokenizer.decode(tokenizer.encode("Hello, LMLM")))

config = LMLMConfig(context_length=128, hidden_size=128, num_layers=2, num_heads=4)
runtime = LMLMRuntime.create_untrained(config)
runtime.save_checkpoint("artifacts/untrained.pt")
```

## Tests

Run dependency-free core tests:

```bash
python -m unittest discover -s tests -v
```

Run the existing Node API checks separately:

```bash
npm install
npm run check
npm test
```

The new Python core and legacy Python experiments have separate dependency
sets. Do not install the root legacy `requirements.txt` into the core
environment; many of its pins come from older Python ecosystems.

## Repository map

- `lmlm_core/` — native tokenizer, configuration, model, runtime, and trainer.
- `tests/` — tests for the new core.
- `docs/RECONSTRUCTION_STATUS.md` — findings, scope, and outstanding audit work.
- `Lmlm/`, `Lmlm-protocol/`, `Notebooklmlm/`, `Notebookmarks/` — legacy
  experiments retained pending provenance and integration review.
- `server.js` — existing Node API; its chat route is explicitly a mock.

## Security and ownership

Never commit populated environment files or credentials. Use environment
variables or a secret manager for runtime configuration. See [SECURITY.md](SECURITY.md).

The repository contains historical assets and mixed license notices. Their
presence is not proof of ownership or redistribution rights. Review provenance
and licensing before packaging or redistributing them.

## Roadmap

1. Stabilize the native text core, training/evaluation loop, and checkpoint format.
2. Design LMLM's own tokenizer and vocabulary-training pipeline.
3. Add memory and multimodal interfaces without delegating the core model to
   external providers.
4. Add resource-aware CPU/GPU backends and device profiling.
5. Integrate the runtime with the existing API only after inference contracts,
   limits, and tests are defined.
6. Complete file provenance, licensing, dependency, and historical secret audits.
