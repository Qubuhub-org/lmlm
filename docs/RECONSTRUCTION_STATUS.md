# LMLM reconstruction status

## Scope

This document records the first reconstruction pass. The objective is to make
the in-built model core explicit and independently testable without deleting
historical research files whose purpose or redistribution rights have not
been established.

LMLM is treated as the model itself: a local-first, in-built multimodal model
family and runtime. This first code increment is a text-only decoder baseline;
it is not a complete multimodal implementation and does not claim a trained
production model exists.

## Findings from the current main branch

- The root Node service exposes a health endpoint and a mock chat response.
  The mock endpoint does not perform neural inference.
- `Lmlm/runlmlm.py` is a legacy Hugging Face masked-language-model
  fine-tuning example, not the native LMLM architecture.
- The root `requirements.txt` pins many old scientific Python packages. It
  remains separate from the new package to avoid breaking legacy experiments.
- The tracked root `.env` contains a malformed CORS setting followed by a
  shell command. It is not an API credential, but should not be tracked.
- `@google/generative-ai/Aura.js` contained a hard-coded Google AI API key.
  The reconstruction branch removes the literal and requires
  `GEMINI_API_KEY`. The credential must still be revoked/rotated because
  source cleanup does not invalidate historical copies.
- The Discord.py documentation template and Python documentation landing
  template were confirmed unrelated to LMLM and replaced/removed in this
  branch. Other legacy research assets remain under provenance and dependency
  review. The large legacy `docs/website/Index.md` file is retained but is not
  linked from the current documentation landing page.
- An older pull request proposes merging `main` into `Runtime`. This
  reconstruction branch is based on `main` and does not alter that PR or the
  `Runtime` branch.

## Added in this increment

- A dependency-light Python package named `lmlm-core`.
- A deterministic UTF-8 byte tokenizer with reserved control tokens.
- A validated native model configuration whose vocabulary size is locked to
  the active byte tokenizer.
- A causal decoder transformer implemented with optional PyTorch.
- Local checkpoint save/load and autoregressive generation.
- A small-corpus training loop and CLI.
- Unit tests for configuration and tokenizer behavior, plus an optional
  PyTorch model forward-pass test.
- Python core compilation and unit tests in GitHub Actions.
- Environment-based credential handling for the existing Gemini adapter.

## Deliberate limitations

- The tokenizer is byte-level. It is reproducible and requires no downloaded
  vocabulary, but is less efficient than a learned subword tokenizer.
- The initial architecture is text-only. Image, audio, video, spatial, and
  action modalities need separately designed encoders/decoders and data
  contracts.
- The model must be trained on a suitable corpus before its output is useful.
- PyTorch is optional for package installation but required for model training
  and inference. CPU is supported; CUDA and Apple MPS are selected when present.
- This new core does not call remote providers or depend on external model
  registries. The legacy Gemini adapter is separate from the core.
- No production-trained checkpoint is included. The PyTorch forward-pass test
  is skipped when PyTorch is not installed.

## Not removed in this increment

No binary, archive, notebook, dataset, imported source tree, or legacy
experiment has been deleted. Those items need provenance, license, purpose,
and dependency checks before removal.
