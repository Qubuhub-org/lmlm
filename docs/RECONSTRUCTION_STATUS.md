# LMLM reconstruction status

## Scope

This document records the native core reconstruction. The objective is to make
the in-built model core explicit and independently testable without deleting
historical research files whose purpose or redistribution rights have not been
established.

LMLM is treated as the model itself: a local-first, in-built multimodal model
family and runtime. The current implementation is a text-only decoder baseline;
it is not a complete multimodal implementation and does not claim a trained
production model exists.

## Findings

- The root Node service exposes a health endpoint and a mock chat response.
  The mock endpoint does not perform neural inference.
- `Lmlm/runlmlm.py` is a legacy Hugging Face masked-language-model
  fine-tuning example, not the native LMLM architecture.
- The root `requirements.txt` pins many old scientific Python packages. It
  remains separate from the new package to avoid breaking legacy experiments.
- The tracked root `.env` was malformed configuration, not a provider
  credential; it has been removed from the current tree.
- `@google/generative-ai/Aura.js` contained a hard-coded Google AI API key.
  The current source now requires `GEMINI_API_KEY`. The credential must still
  be revoked/rotated because source cleanup does not invalidate historical
  copies.
- The Discord.py and Python documentation templates, generic Kaggle
  reproduction stub, empty predictor, unrelated Go quote sample, and obsolete
  CI workflows have been removed.
- Other legacy research assets and provider adapters remain under review.

## Native core

- Dependency-light Python package `lmlm-core`.
- UTF-8 byte tokenizer with reserved control tokens.
- Deterministic BPE tokenizer trained from a local corpus; tokenizer metadata is
  serialized with the model checkpoint.
- Validated model configuration supports vocabulary sizes matching the active
  tokenizer.
- Causal decoder transformer implemented with optional PyTorch.
- Local checkpoint save/load supports the original byte-tokenizer checkpoint
  format and the newer tokenizer-aware format.
- Small-corpus trainer and CLI support both byte and BPE tokenizers.
- Deterministic validation evaluator reports next-token cross-entropy, perplexity, target-token count, and evaluation-window count. It scores each target once using contiguous context windows.
- Training accepts an explicit random seed (default 17); exact cross-device bitwise reproducibility is not promised.
- Leakage-aware benchmark runner creates deterministic contiguous train/validation/test splits and fits BPE only on training text.
- Periodic checkpoints and JSONL training/validation history are written at configured evaluation intervals.
- Benchmark reports include validation/test loss, perplexity, token counts, and bits-per-byte normalized by scored UTF-8 bytes.
- CPU execution, with CUDA and Apple MPS selected when available.

## Validation

GitHub Actions runs:
- Python compile checks and dependency-free tokenizer/configuration tests.
- CPU PyTorch forward-pass tests.
- Evaluation tests for token coverage, finite metrics, short-input rejection, and restoration of model train/eval mode.
- Benchmark tests for deterministic non-overlapping splits, invalid split ratios, byte accounting, and byte/BPE end-to-end held-out evaluation.
- Tiny-corpus byte-tokenized training, checkpoint reload, and generation.
- Tiny-corpus BPE-tokenized training, checkpoint reload, and generation.
- Existing Node API tests, syntax checks, and Docker image build.
- Static documentation validation and Pages deployment.

## Deliberate limitations

- The BPE implementation is deterministic but intentionally simple. It is
  suitable for small-corpus experiments, not yet optimized for large-scale
  vocabulary training.
- The initial architecture is text-only. Image, audio, video, spatial, and
  action modalities need separately designed encoders/decoders and data
  contracts.
- The model must be trained on a suitable corpus before its output is useful.
- Perplexity comparisons are meaningful only when tokenizer and evaluation corpus are held constant; bits-per-byte is the normalized cross-tokenizer comparison metric.
- Default benchmark splits are contiguous character ranges. Multi-document corpora should be split by document/group before benchmarking to avoid related documents crossing boundaries.
- No production-trained checkpoint is included.
- The existing Node `/api/chat` endpoint remains a mock and is not connected
  to this neural runtime.
- The new core does not call remote providers or depend on external model
  registries. Legacy provider adapters remain separate from the core.

## Remaining audit work

No binary, notebook, dataset, or imported source tree has been deleted. The
confirmed unrelated text templates, empty files, generic Kaggle stub,
unreferenced Go quote sample, and obsolete workflows were removed. Remaining
binary, archive, notebook, dataset, and legacy experiment files still need
provenance, license, purpose, and dependency checks before removal.
