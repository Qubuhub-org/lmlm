"""Small-corpus training loop for the native LMLM model."""
from __future__ import annotations

from pathlib import Path

from .config import LMLMConfig
from .model import LMLMModel
from .runtime import LMLMRuntime, resolve_device
from .tokenizer import ByteTokenizer


def train_from_text(
    corpus_path: str | Path,
    output_path: str | Path,
    *,
    config: LMLMConfig | None = None,
    steps: int = 100,
    batch_size: int = 8,
    learning_rate: float = 3e-4,
    seed: int = 17,
) -> Path:
    """Train on a local UTF-8 text file and save an LMLM checkpoint."""
    try:
        import torch
    except ImportError as exc:
        raise RuntimeError(
            "Training requires PyTorch. Install it with: pip install 'lmlm-core[runtime]'"
        ) from exc

    if steps <= 0 or batch_size <= 0 or learning_rate <= 0:
        raise ValueError("steps, batch_size, and learning_rate must be positive")

    text = Path(corpus_path).read_text(encoding="utf-8")
    tokens = ByteTokenizer().encode(text)
    selected = config or LMLMConfig()
    length = selected.context_length
    if len(tokens) < length + 1:
        raise ValueError(
            f"Corpus needs at least {length + 1} UTF-8 bytes; received {len(tokens)}"
        )

    torch.manual_seed(seed)
    device = resolve_device(selected.device)
    model = LMLMModel(selected).to(device)
    model.train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
    token_tensor = torch.tensor(tokens, dtype=torch.long, device=device)
    last_start = len(tokens) - length - 1

    for _ in range(steps):
        starts = torch.randint(0, last_start + 1, (batch_size,), device=device)
        offsets = starts.tolist()
        inputs = torch.stack([token_tensor[i:i + length] for i in offsets])
        targets = torch.stack([token_tensor[i + 1:i + length + 1] for i in offsets])
        _, loss = model(inputs, targets)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

    model.eval()
    runtime = LMLMRuntime(model, selected, device)
    runtime.save_checkpoint(output_path)
    return Path(output_path)
