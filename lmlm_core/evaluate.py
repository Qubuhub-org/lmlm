"""Deterministic next-token evaluation for local LMLM checkpoints."""
from __future__ import annotations

import math
from pathlib import Path
from typing import TypedDict

from .runtime import LMLMRuntime


class EvaluationResult(TypedDict):
    loss: float
    perplexity: float
    token_count: int
    sequence_count: int


def evaluate_text(runtime: LMLMRuntime, text: str) -> EvaluationResult:
    """Measure mean next-token cross-entropy and perplexity over local text.

    Every target token is scored exactly once. The first token is context only.
    Evaluation uses fixed contiguous windows and no random sampling.
    """
    try:
        import torch
    except ImportError as exc:
        raise RuntimeError(
            "Evaluation requires PyTorch. Install it with: pip install 'lmlm-core[runtime]'"
        ) from exc

    if not isinstance(text, str):
        raise TypeError("text must be a string")
    token_ids = runtime.tokenizer.encode(text)
    if len(token_ids) < 2:
        raise ValueError("Evaluation text must contain at least two tokens")

    context_length = runtime.config.context_length
    weighted_loss = 0.0
    token_count = 0
    sequence_count = 0
    model = runtime.model
    was_training = model.training
    model.eval()

    try:
        with torch.inference_mode():
            for start in range(0, len(token_ids) - 1, context_length):
                end = min(start + context_length, len(token_ids) - 1)
                inputs_list = token_ids[start:end]
                targets_list = token_ids[start + 1:end + 1]
                inputs = torch.tensor(
                    [inputs_list], dtype=torch.long, device=runtime.device
                )
                targets = torch.tensor(
                    [targets_list], dtype=torch.long, device=runtime.device
                )
                _, loss = model(inputs, targets)
                count = len(targets_list)
                weighted_loss += float(loss.item()) * count
                token_count += count
                sequence_count += 1
    finally:
        model.train(was_training)

    mean_loss = weighted_loss / token_count
    perplexity = math.exp(mean_loss) if mean_loss < 709 else math.inf
    return {
        "loss": mean_loss,
        "perplexity": perplexity,
        "token_count": token_count,
        "sequence_count": sequence_count,
    }


def evaluate_file(runtime: LMLMRuntime, path: str | Path) -> EvaluationResult:
    """Evaluate a UTF-8 text file without uploading it or calling a remote API."""
    text = Path(path).read_text(encoding="utf-8")
    return evaluate_text(runtime, text)
