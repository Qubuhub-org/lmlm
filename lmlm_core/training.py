"""Small-corpus training loop for the native LMLM model."""
from __future__ import annotations

import json
from pathlib import Path

from .config import LMLMConfig
from .model import LMLMModel
from .runtime import LMLMRuntime, Tokenizer, resolve_device
from .tokenizer import ByteTokenizer


def train_from_text(
    corpus_path: str | Path,
    output_path: str | Path,
    *,
    config: LMLMConfig | None = None,
    tokenizer: Tokenizer | None = None,
    steps: int = 100,
    batch_size: int = 8,
    learning_rate: float = 3e-4,
    seed: int = 17,
    validation_path: str | Path | None = None,
    history_path: str | Path | None = None,
    checkpoint_dir: str | Path | None = None,
    eval_every: int = 25,
) -> Path:
    """Train locally and optionally record validation metrics/checkpoints.

    When validation_path is supplied, evaluation occurs every eval_every steps
    and at the final step. Checkpoints and JSONL history are written locally.
    """
    try:
        import torch
    except ImportError as exc:
        raise RuntimeError(
            "Training requires PyTorch. Install it with: pip install 'lmlm-core[runtime]'"
        ) from exc

    if steps <= 0 or batch_size <= 0 or learning_rate <= 0:
        raise ValueError("steps, batch_size, and learning_rate must be positive")
    if eval_every <= 0:
        raise ValueError("eval_every must be positive")

    text = Path(corpus_path).read_text(encoding="utf-8")
    validation_text = (
        Path(validation_path).read_text(encoding="utf-8")
        if validation_path is not None else None
    )
    if validation_text is not None and not validation_text:
        raise ValueError("validation corpus must not be empty")

    selected_tokenizer = tokenizer or ByteTokenizer()
    tokens = selected_tokenizer.encode(text)
    selected = config or LMLMConfig(vocab_size=selected_tokenizer.vocab_size)
    if selected.vocab_size != selected_tokenizer.vocab_size:
        raise ValueError("model vocab_size must match the active tokenizer vocabulary")
    length = selected.context_length
    if len(tokens) < length + 1:
        raise ValueError(
            f"Corpus needs at least {length + 1} tokens; received {len(tokens)}"
        )

    torch.manual_seed(seed)
    device = resolve_device(selected.device)
    model = LMLMModel(selected).to(device)
    model.train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
    token_tensor = torch.tensor(tokens, dtype=torch.long, device=device)
    last_start = len(tokens) - length - 1
    history: list[dict[str, float | int]] = []
    interval_losses: list[float] = []
    destination = Path(output_path)

    def record(step: int) -> None:
        runtime = LMLMRuntime(model, selected, device, selected_tokenizer)
        row: dict[str, float | int] = {
            "step": step,
            "train_loss": sum(interval_losses) / len(interval_losses),
        }
        if validation_text is not None:
            from .evaluate import evaluate_text
            metrics = evaluate_text(runtime, validation_text)
            row.update({
                "validation_loss": metrics["loss"],
                "validation_perplexity": metrics["perplexity"],
                "validation_tokens": metrics["token_count"],
            })
        history.append(row)
        interval_losses.clear()
        if checkpoint_dir is not None:
            runtime.save_checkpoint(Path(checkpoint_dir) / f"step-{step:06d}.pt")

    for step in range(1, steps + 1):
        starts = torch.randint(0, last_start + 1, (batch_size,), device=device)
        offsets = starts.tolist()
        inputs = torch.stack([token_tensor[i:i + length] for i in offsets])
        targets = torch.stack([token_tensor[i + 1:i + length + 1] for i in offsets])
        _, loss = model(inputs, targets)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        interval_losses.append(float(loss.detach().item()))

        if validation_text is not None and (step % eval_every == 0 or step == steps):
            record(step)

    model.eval()
    runtime = LMLMRuntime(model, selected, device, selected_tokenizer)
    runtime.save_checkpoint(destination)

    if history_path is not None:
        history_file = Path(history_path)
        history_file.parent.mkdir(parents=True, exist_ok=True)
        history_file.write_text(
            "".join(json.dumps(row, sort_keys=True) + "\\n" for row in history),
            encoding="utf-8",
        )
    return destination
