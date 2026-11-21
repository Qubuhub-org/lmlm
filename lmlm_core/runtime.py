"""Checkpoint management and local autoregressive generation."""
from __future__ import annotations

from pathlib import Path

from .config import LMLMConfig
from .model import LMLMModel
from .tokenizer import (
    BOS_TOKEN_ID,
    EOS_TOKEN_ID,
    BPETokenizer,
    ByteTokenizer,
    tokenizer_from_dict,
)

try:
    import torch
except ImportError:
    torch = None

Tokenizer = ByteTokenizer | BPETokenizer


def _require_torch():
    if torch is None:
        raise RuntimeError(
            "The LMLM neural runtime requires PyTorch. "
            "Install it with: pip install 'lmlm-core[runtime]'"
        )
    return torch


def resolve_device(requested: str = "auto") -> str:
    """Resolve auto to CUDA, Apple MPS, or CPU."""
    backend = _require_torch()
    if requested != "auto":
        if requested.startswith("cuda") and not backend.cuda.is_available():
            raise RuntimeError("CUDA was requested but is not available")
        if requested == "mps" and not (
            hasattr(backend.backends, "mps") and backend.backends.mps.is_available()
        ):
            raise RuntimeError("MPS was requested but is not available")
        return requested
    if backend.cuda.is_available():
        return "cuda"
    if hasattr(backend.backends, "mps") and backend.backends.mps.is_available():
        return "mps"
    return "cpu"


class LMLMRuntime:
    """Owns an in-process LMLM model, tokenizer, and local generation loop."""
    def __init__(
        self,
        model: LMLMModel,
        config: LMLMConfig,
        device: str,
        tokenizer: Tokenizer | None = None,
    ) -> None:
        self.model = model
        self.config = config
        self.device = device
        self.tokenizer = tokenizer or ByteTokenizer()
        if self.config.vocab_size != self.tokenizer.vocab_size:
            raise ValueError(
                "model vocab_size must match the active tokenizer vocabulary"
            )
        self.model.to(device)
        self.model.eval()

    @classmethod
    def create_untrained(
        cls,
        config: LMLMConfig | None = None,
        tokenizer: Tokenizer | None = None,
    ) -> "LMLMRuntime":
        """Create random weights for architecture smoke tests, not useful answers."""
        _require_torch()
        selected_tokenizer = tokenizer or ByteTokenizer()
        selected = config or LMLMConfig(vocab_size=selected_tokenizer.vocab_size)
        device = resolve_device(selected.device)
        return cls(LMLMModel(selected), selected, device, selected_tokenizer)

    @classmethod
    def from_checkpoint(cls, path: str | Path, device: str = "auto") -> "LMLMRuntime":
        backend = _require_torch()
        resolved = resolve_device(device)
        checkpoint = backend.load(Path(path), map_location=resolved, weights_only=True)
        if not isinstance(checkpoint, dict):
            raise ValueError("Unsupported or invalid LMLM checkpoint format")
        checkpoint_format = checkpoint.get("format")
        if checkpoint_format == "lmlm-core-v1":
            tokenizer = ByteTokenizer()
        elif checkpoint_format == "lmlm-core-v2":
            tokenizer = tokenizer_from_dict(checkpoint.get("tokenizer", {}))
        else:
            raise ValueError("Unsupported or invalid LMLM checkpoint format")
        config = LMLMConfig.from_dict(checkpoint["config"])
        if config.vocab_size != tokenizer.vocab_size:
            raise ValueError("checkpoint model and tokenizer vocabularies do not match")
        model = LMLMModel(config)
        model.load_state_dict(checkpoint["model_state"], strict=True)
        return cls(model, config, resolved, tokenizer)

    def save_checkpoint(self, path: str | Path) -> None:
        backend = _require_torch()
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        backend.save(
            {
                "format": "lmlm-core-v2",
                "config": self.config.to_dict(),
                "tokenizer": self.tokenizer.to_dict(),
                "model_state": self.model.state_dict(),
            },
            destination,
        )

    def generate(
        self,
        prompt: str,
        *,
        max_new_tokens: int = 80,
        temperature: float = 0.8,
        top_k: int | None = 40,
    ) -> str:
        backend = _require_torch()
        if max_new_tokens < 0:
            raise ValueError("max_new_tokens must be non-negative")
        if temperature <= 0:
            raise ValueError("temperature must be greater than zero")
        if top_k is not None and top_k <= 0:
            raise ValueError("top_k must be greater than zero")

        token_ids = self.tokenizer.encode(prompt, add_bos=True)
        if not token_ids:
            token_ids = [BOS_TOKEN_ID]
        generated = backend.tensor([token_ids], dtype=backend.long, device=self.device)

        with backend.inference_mode():
            for _ in range(max_new_tokens):
                context = generated[:, -self.config.context_length:]
                logits, _ = self.model(context)
                next_logits = logits[:, -1, :] / temperature
                if top_k is not None:
                    count = min(top_k, next_logits.shape[-1])
                    cutoff = backend.topk(next_logits, count).values[:, -1, None]
                    next_logits = next_logits.masked_fill(
                        next_logits < cutoff, float("-inf")
                    )
                probabilities = backend.softmax(next_logits, dim=-1)
                next_token = backend.multinomial(probabilities, num_samples=1)
                generated = backend.cat((generated, next_token), dim=1)
                if int(next_token.item()) == EOS_TOKEN_ID:
                    break
        return self.tokenizer.decode(generated[0].tolist())
