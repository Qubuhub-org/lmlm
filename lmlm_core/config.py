"""Validated configuration for the native LMLM decoder model."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

BYTE_TOKENIZER_VOCAB_SIZE = 260


@dataclass(frozen=True, slots=True)
class LMLMConfig:
    """Configuration for a compact decoder-only transformer.

    Defaults are intended for CPU experimentation, not production deployment.
    """
    vocab_size: int = BYTE_TOKENIZER_VOCAB_SIZE
    context_length: int = 128
    hidden_size: int = 128
    num_layers: int = 2
    num_heads: int = 4
    dropout: float = 0.1
    device: str = "auto"

    def __post_init__(self) -> None:
        if self.vocab_size != BYTE_TOKENIZER_VOCAB_SIZE:
            raise ValueError(
                f"vocab_size must be {BYTE_TOKENIZER_VOCAB_SIZE} while ByteTokenizer is active"
            )
        for name in ("context_length", "hidden_size", "num_layers", "num_heads"):
            if getattr(self, name) <= 0:
                raise ValueError(f"{name} must be greater than zero")
        if self.hidden_size % self.num_heads:
            raise ValueError("hidden_size must be divisible by num_heads")
        if not 0.0 <= self.dropout < 1.0:
            raise ValueError("dropout must be in the range [0, 1)")
        if not isinstance(self.device, str) or not self.device.strip():
            raise ValueError("device must be a non-empty string")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, values: Mapping[str, Any]) -> "LMLMConfig":
        allowed = set(cls.__dataclass_fields__)
        unknown = set(values) - allowed
        if unknown:
            raise ValueError(
                "Unknown LMLM configuration field(s): " + ", ".join(sorted(unknown))
            )
        return cls(**dict(values))
