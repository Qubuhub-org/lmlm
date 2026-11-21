# LMLM repository audit

Audit scope: current repository tree and the runtime-related branches inspected
during the November 2026 reconstruction. This is an engineering inventory, not
a license opinion or a claim that every artifact has been inspected.

## Core and current behavior

| Path | Observed purpose | Disposition |
|---|---|---|
| `lmlm_core/` | Native text-model baseline: byte tokenizer, learned BPE tokenizer, causal decoder, runtime, trainer | Active reconstruction core |
| `server.js` | Node API with health route and explicitly mocked chat route | Retain; not neural inference |
| `Lmlm/runlmlm.py` | Legacy Hugging Face masked-language-model fine-tuning example | Retain as legacy experiment; not the native core |
| `Model/config.yaml` | Qwen 2.5 Coder model name and localhost inference endpoint | Treat as an optional local-model adapter configuration, not LMLM's model definition |
| `Lmlm/Index.js` | Cloudflare Workers AI example invoking a hosted model identifier | Legacy adapter/demo; not core inference |
| `@google/generative-ai/Aura.js`, `Lmlm.java` | Gemini SDK integrations | Optional/legacy adapters; not core inference |

## Confirmed cleanup

- Removed the tracked root `.env`. Its contents were a malformed CORS setting
  followed by a shell command, not a provider credential.
- Replaced `docs/index.html`, which was a Discord.py Jinja template, with a
  static LMLM landing page.
- Removed `docs/indexcontent.md`, which was a Python documentation Jinja
  template.
- Removed `REPRODUCE.md`, an incomplete generic Kaggle competition guide,
  and `predict_code/calibrate_model.py`, an empty unused script.
- Removed the standalone `rsc.io/quote.go` archive and its empty placeholder;
  repository search found no LMLM references or Go module manifest using it.
- Removed the unrelated Django workflow, obsolete duplicate LMLM CI workflow,
  and Hello World placeholder workflow.
- Removed a hard-coded Google AI key from `@google/generative-ai/Aura.js`.
  The adapter now requires `GEMINI_API_KEY` from the process environment.

## Security actions still required

- Revoke/rotate the Google AI key that was present in the original `main`
  source and review provider usage. A current-file fix does not invalidate it.
- Assess Git history cleanup with collaborators. A current-file fix does not
  erase historical copies, forks, caches, or existing clones.
- Review public artifacts and database backups before keeping or redistributing
  them. No binary backup has been opened or declared safe in this audit.
- Enable or verify GitHub secret scanning and push protection.

## Workflow inventory

- `.github/workflows/ci.yml` validates the Python core, CPU PyTorch training
  and inference smoke tests, Node API, and Docker build.
- `.github/workflows/build-doc.yml` validates the static LMLM documentation.
- `.github/workflows/build.yml` deploys the reviewed `docs/` directory to
  GitHub Pages.
- Obsolete Django, duplicate LMLM, and placeholder workflows were removed.

## Legacy or unclear assets retained

These paths were not deleted because their purpose, dependencies, provenance,
or redistribution rights have not been fully established:

- `app/app.py`: visibly uses a MeshAnything mesh-generation pipeline. It may
  be a separate 3D experiment; integration with LMLM has not been established.
- `docs/website/Index.md`: large legacy documentation page containing older
  LMLM descriptions and Ollama-oriented material. It is not linked from the
  new documentation landing page.
- `cs/lmlm/README.md`: legacy project notes with old naming and mixed provider
  references. Retained because it contains LMLM-specific material that may be
  worth reconciling rather than deleting wholesale.
- `LICENSE.txt`: contains React copyright/license snippets, not a clear
  repository-wide license. The repository metadata reports no recognized SPDX
  license. No project license has been inferred or assigned.
- `VisualStudioSetup.exe`, `p2multitool-1.3.0.tar`, database backup files,
  notebooks, datasets, PDFs, model binaries, coverage dumps, and large
  documentation snapshots. Their contents and rights require separate review.
- Other provider SDK folders and documentation snapshots. These may be useful
  adapters or research notes, but they are not part of the native LMLM core.

## Branch coordination

- The native text core and verified cleanup have been merged to `main`.
- The historical PR that proposed merging `main` into `Runtime` remains
  separate and was not merged by this reconstruction.
- User changes added to `main` during this work were preserved.

## Next engineering gates

1. Benchmark the BPE tokenizer on a representative, owner-approved corpus and
   improve training efficiency before large-corpus use.
2. Add validation loss/perplexity and reproducible model evaluation.
3. Design memory and multimodal data contracts before adding image, audio,
   video, spatial, or action modules.
4. Add resource-aware CPU/GPU profiling and checkpoint compatibility tests.
5. Resolve repository-wide licensing and artifact provenance before
   redistributing legacy binaries, notebooks, datasets, or imported code.
