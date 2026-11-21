"""Leakage-aware, local benchmark runner for native LMLM experiments."""
from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

from .config import LMLMConfig
from .evaluate import evaluate_file
from .runtime import LMLMRuntime
from .tokenizer import BPETokenizer, ByteTokenizer
from .training import train_from_text


def split_text(
    text: str,
    *,
    train_ratio: float = 0.8,
    validation_ratio: float = 0.1,
    test_ratio: float = 0.1,
) -> tuple[str, str, str]:
    """Split text into disjoint contiguous character ranges.

    The split is deterministic and preserves every character exactly once.
    Tokenizers must be fitted only on the returned training segment.
    """
    ratios = (train_ratio, validation_ratio, test_ratio)
    if any(value <= 0 or value >= 1 for value in ratios):
        raise ValueError("each split ratio must be between 0 and 1")
    if abs(sum(ratios) - 1.0) > 1e-8:
        raise ValueError("train, validation, and test ratios must sum to 1")
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if len(text) < 3:
        raise ValueError("corpus must contain at least three characters")

    train_end = int(len(text) * train_ratio)
    validation_end = train_end + int(len(text) * validation_ratio)
    if train_end < 1 or validation_end <= train_end or validation_end >= len(text):
        raise ValueError("corpus is too small for three non-empty splits")
    return text[:train_end], text[train_end:validation_end], text[validation_end:]


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def run_benchmark(
    corpus_path: str | Path,
    output_dir: str | Path,
    *,
    tokenizer_types: tuple[str, ...] = ("byte", "bpe"),
    train_ratio: float = 0.8,
    validation_ratio: float = 0.1,
    test_ratio: float = 0.1,
    steps: int = 100,
    batch_size: int = 8,
    learning_rate: float = 3e-4,
    eval_every: int = 25,
    seed: int = 17,
    context_length: int = 128,
    hidden_size: int = 128,
    layers: int = 2,
    heads: int = 4,
    device: str = "auto",
    vocab_size: int = 512,
    min_frequency: int = 2,
) -> dict[str, Any]:
    """Train byte/BPE baselines and evaluate on untouched held-out test text."""
    allowed = {"byte", "bpe"}
    if not tokenizer_types or any(kind not in allowed for kind in tokenizer_types):
        raise ValueError("tokenizer_types must contain 'byte' and/or 'bpe'")
    if len(set(tokenizer_types)) != len(tokenizer_types):
        raise ValueError("tokenizer_types must not contain duplicates")

    source = Path(corpus_path)
    text = source.read_text(encoding="utf-8")
    train_text, validation_text, test_text = split_text(
        text,
        train_ratio=train_ratio,
        validation_ratio=validation_ratio,
        test_ratio=test_ratio,
    )
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    split_manifest = {
        "method": "contiguous_character_ranges",
        "ratios": {
            "train": train_ratio,
            "validation": validation_ratio,
            "test": test_ratio,
        },
        "splits": {
            "train": {"characters": len(train_text), "sha256": _sha256(train_text)},
            "validation": {
                "characters": len(validation_text),
                "sha256": _sha256(validation_text),
            },
            "test": {"characters": len(test_text), "sha256": _sha256(test_text)},
        },
        "tokenizer_fit_scope": "training split only",
        "test_usage": "final evaluation only; never used for training or model selection",
    }
    (destination / "splits.json").write_text(
        json.dumps(split_manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    results: dict[str, Any] = {}
    with tempfile.TemporaryDirectory(prefix="lmlm-benchmark-") as temporary:
        temp = Path(temporary)
        train_file = temp / "train.txt"
        validation_file = temp / "validation.txt"
        test_file = temp / "test.txt"
        train_file.write_text(train_text, encoding="utf-8")
        validation_file.write_text(validation_text, encoding="utf-8")
        test_file.write_text(test_text, encoding="utf-8")

        for kind in tokenizer_types:
            run_dir = destination / kind
            run_dir.mkdir(parents=True, exist_ok=True)
            if kind == "byte":
                tokenizer = ByteTokenizer()
            else:
                tokenizer = BPETokenizer.train(
                    train_text,
                    vocab_size=vocab_size,
                    min_frequency=min_frequency,
                )

            config = LMLMConfig(
                vocab_size=tokenizer.vocab_size,
                context_length=context_length,
                hidden_size=hidden_size,
                num_layers=layers,
                num_heads=heads,
                device=device,
            )
            checkpoint = run_dir / "final.pt"
            history_file = run_dir / "history.jsonl"
            checkpoint_dir = run_dir / "checkpoints"
            train_from_text(
                train_file,
                checkpoint,
                config=config,
                tokenizer=tokenizer,
                steps=steps,
                batch_size=batch_size,
                learning_rate=learning_rate,
                seed=seed,
                validation_path=validation_file,
                history_path=history_file,
                checkpoint_dir=checkpoint_dir,
                eval_every=eval_every,
            )
            runtime = LMLMRuntime.from_checkpoint(checkpoint, device=device)
            validation_metrics = evaluate_file(runtime, validation_file)
            test_metrics = evaluate_file(runtime, test_file)
            results[kind] = {
                "tokenizer": kind,
                "vocab_size": tokenizer.vocab_size,
                "seed": seed,
                "steps": steps,
                "checkpoint": str(checkpoint),
                "history": str(history_file),
                "periodic_checkpoints": len(list(checkpoint_dir.glob("step-*.pt"))),
                "validation": validation_metrics,
                "test": test_metrics,
            }

    report: dict[str, Any] = {
        "format": "lmlm-benchmark-v1",
        "source_name": source.name,
        "source_sha256": _sha256(text),
        "splits": split_manifest,
        "training": {
            "steps": steps,
            "batch_size": batch_size,
            "learning_rate": learning_rate,
            "eval_every": eval_every,
            "seed": seed,
            "context_length": context_length,
            "hidden_size": hidden_size,
            "layers": layers,
            "heads": heads,
            "device_requested": device,
        },
        "runs": results,
        "comparison_note": (
            "Compare perplexity only within the same tokenizer and evaluation "
            "corpus. Byte and BPE token counts/perplexities are not directly "
            "comparable because their token units differ."
        ),
    }
    (destination / "benchmark.json").write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return report
