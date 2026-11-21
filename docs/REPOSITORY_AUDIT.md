# LMLM repository audit

Audit scope: current repository tree and the two existing runtime-related
branches inspected during the November 2026 reconstruction. This is an
engineering inventory, not a license opinion or a claim that every artifact
has been inspected.

## Core and current behavior

| Path | Observed purpose | Disposition |
|---|---|---|
| `lmlm_core/` | New native text-model baseline: byte tokenizer, causal decoder, runtime, trainer | Active reconstruction core |
| `server.js` | Node API with health route and explicitly mocked chat route | Retain; not neural inference |
| `Lmlm/runlmlm.py` | Legacy Hugging Face masked-language-model fine-tuning example | Retain as legacy experiment; not the native core |
| `Model/config.yaml` | Qwen 2.5 Coder model name and localhost inference endpoint | Treat as an optional local-model adapter configuration, not LMLM's model definition |
| `Lmlm/Index.js` | Cloudflare Workers AI example invoking a hosted model identifier | Legacy adapter/demo; not core inference |
| `@google/generative-ai/Aura.js`, `Lmlm.java` | Gemini SDK integrations | Optional/legacy adapters; not core inference |

## Confirmed cleanup in this branch

- Removed the tracked root `.env`. Its contents were a malformed CORS setting
  followed by a shell command, not a provider credential.
- Replaced `docs/index.html`, which was a Discord.py Jinja template, with a
  static LMLM landing page.
- Removed `docs/indexcontent.md`, which was a Python documentation Jinja
  template.
- Removed the hard-coded Google AI key from `@google/generative-ai/Aura.js`.
  The adapter now reads `GEMINI_API_KEY` from the process environment.

## Security actions still required

- Revoke/rotate the Google AI key that was present in the current `main`
  source and review provider usage. This branch cleanup does not invalidate it.
- Assess Git history cleanup with collaborators. A current-file fix does not
  erase historical copies, forks, caches, or existing clones.
- Review public artifacts and database backups before keeping or redistributing
  them. No binary backup has been opened or declared safe in this audit.
- Enable or verify GitHub secret scanning and push protection.

## Workflow cleanup

- Removed `.github/workflows/django.yml`: it targeted an absent Django
  `manage.py` project and Python 3.7–3.9 rather than the new Python 3.10+
  core.
- Removed `.github/workflows/Lmlm-ci.yml`: it duplicated the maintained CI,
  installed the legacy root requirements, used an invalid setup-python input,
  and searched for `*_test.py` while the repository test file is
  `test_core.py`.
- Removed `.github/workflows/lmlm.yml`: it only printed a Hello World
  placeholder and did not validate or build LMLM.
- Retained `.github/workflows/ci.yml`, `.github/workflows/build-doc.yml`,
  and the GitHub Pages deployment workflow.

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
  repository-wide license. The repository metadata currently reports no
  recognized SPDX license. No project license has been inferred or assigned.
- `VisualStudioSetup.exe`, `p2multitool-1.3.0.tar`, database backup files,
  notebooks, datasets, PDFs, model binaries, coverage dumps, and large
  documentation snapshots. Their contents and rights require separate review.
- Other provider SDK folders and documentation snapshots. These may be useful
  adapters or research notes, but they are not part of the native LMLM core.

## Branch coordination

- This reconstruction is based on `main` and is maintained in its own branch.
- The historical PR that proposes merging `main` into `Runtime` remains
  separate and is not merged by this work.
- User changes added to `main` during this work must be preserved when the
  reconstruction branch is synchronized.

## Next engineering gates

1. Reconcile this branch with the latest `main` before further changes.
2. Run a PyTorch-enabled CPU smoke test for forward, training, checkpoint save,
   checkpoint reload, and generation.
3. Define the native multimodal interfaces and data contracts before adding
   image/audio/video/spatial modules.
4. Resolve repository-wide licensing and artifact provenance.
5. Decide which legacy adapters remain supported and which experiments can be
   archived or removed.
