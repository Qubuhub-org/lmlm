"""Native decoder-only transformer. PyTorch is an optional runtime dependency."""
from __future__ import annotations

from .config import LMLMConfig

try:
    import torch
    from torch import nn
except ImportError:  # Package configuration/tokenizer remain usable without PyTorch.
    torch = None
    nn = None


if nn is not None:
    class LMLMModel(nn.Module):
        """Compact causal language model implemented inside the LMLM package."""
        def __init__(self, config: LMLMConfig) -> None:
            super().__init__()
            self.config = config
            self.token_embeddings = nn.Embedding(config.vocab_size, config.hidden_size)
            self.position_embeddings = nn.Embedding(config.context_length, config.hidden_size)
            layer = nn.TransformerEncoderLayer(
                d_model=config.hidden_size,
                nhead=config.num_heads,
                dim_feedforward=config.hidden_size * 4,
                dropout=config.dropout,
                activation="gelu",
                batch_first=True,
                norm_first=True,
            )
            self.blocks = nn.TransformerEncoder(layer, num_layers=config.num_layers)
            self.final_norm = nn.LayerNorm(config.hidden_size)
            self.output = nn.Linear(config.hidden_size, config.vocab_size, bias=False)
            self.output.weight = self.token_embeddings.weight

        def forward(self, input_ids, targets=None):
            if input_ids.ndim != 2:
                raise ValueError("input_ids must have shape [batch, sequence]")
            batch_size, sequence_length = input_ids.shape
            if sequence_length > self.config.context_length:
                raise ValueError("sequence exceeds configured context_length")
            positions = torch.arange(sequence_length, device=input_ids.device).unsqueeze(0)
            hidden = self.token_embeddings(input_ids) + self.position_embeddings(positions)
            causal_mask = torch.triu(
                torch.ones(sequence_length, sequence_length, dtype=torch.bool, device=input_ids.device),
                diagonal=1,
            )
            hidden = self.blocks(hidden, mask=causal_mask)
            logits = self.output(self.final_norm(hidden))
            loss = None
            if targets is not None:
                loss = nn.functional.cross_entropy(
                    logits.reshape(batch_size * sequence_length, -1),
                    targets.reshape(batch_size * sequence_length),
                )
            return logits, loss
else:
    class LMLMModel:  # type: ignore[no-redef]
        """Helpful error when the optional tensor backend is missing."""
        def __init__(self, *_args, **_kwargs) -> None:
            raise RuntimeError(
                "The LMLM neural runtime requires PyTorch. "
                "Install it with: pip install 'lmlm-core[runtime]'"
            )
