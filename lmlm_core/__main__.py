"""Command-line interface for the LMLM core."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import LMLMConfig
from .evaluate import evaluate_file
from .runtime import LMLMRuntime
from .tokenizer import BPETokenizer, ByteTokenizer
from .training import train_from_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lmlm", description="Train and run the in-built LMLM model locally."
    )
    commands = parser.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init-config", help="write a starter model config")
    init.add_argument("path", type=Path)
    init.add_argument("--context-length", type=int, default=128)
    init.add_argument("--hidden-size", type=int, default=128)
    init.add_argument("--layers", type=int, default=2)
    init.add_argument("--heads", type=int, default=4)

    tokenize = commands.add_parser("tokenize", help="encode text as UTF-8 byte tokens")
    tokenize.add_argument("text")

    train = commands.add_parser("train", help="train from a local UTF-8 corpus")
    train.add_argument("corpus", type=Path)
    train.add_argument("--output", type=Path, default=Path("artifacts/lmlm.pt"))
    train.add_argument("--steps", type=int, default=100)
    train.add_argument("--batch-size", type=int, default=8)
    train.add_argument("--learning-rate", type=float, default=3e-4)
    train.add_argument("--context-length", type=int, default=128)
    train.add_argument("--hidden-size", type=int, default=128)
    train.add_argument("--layers", type=int, default=2)
    train.add_argument("--heads", type=int, default=4)
    train.add_argument("--device", default="auto")
    train.add_argument("--seed", type=int, default=17)
    train.add_argument("--tokenizer", choices=("byte", "bpe"), default="byte")
    train.add_argument("--vocab-size", type=int, default=512)
    train.add_argument("--min-frequency", type=int, default=2)

    generate = commands.add_parser("generate", help="generate from a local checkpoint")
    generate.add_argument("checkpoint", type=Path)
    generate.add_argument("prompt")
    generate.add_argument("--max-new-tokens", type=int, default=80)
    generate.add_argument("--temperature", type=float, default=0.8)
    generate.add_argument("--top-k", type=int, default=40)
    generate.add_argument("--device", default="auto")

    evaluate = commands.add_parser(
        "evaluate", help="measure next-token loss and perplexity on local text"
    )
    evaluate.add_argument("checkpoint", type=Path)
    evaluate.add_argument("corpus", type=Path)
    evaluate.add_argument("--device", default="auto")

    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "init-config":
        config = LMLMConfig(
            context_length=args.context_length,
            hidden_size=args.hidden_size,
            num_layers=args.layers,
            num_heads=args.heads,
        )
        args.path.parent.mkdir(parents=True, exist_ok=True)
        args.path.write_text(
            json.dumps(config.to_dict(), indent=2) + "\n", encoding="utf-8"
        )
        print(f"Wrote {args.path}")
    elif args.command == "tokenize":
        print(json.dumps(ByteTokenizer().encode(args.text), ensure_ascii=False))
    elif args.command == "train":
        if args.tokenizer == "bpe":
            corpus = args.corpus.read_text(encoding="utf-8")
            tokenizer = BPETokenizer.train(
                corpus,
                vocab_size=args.vocab_size,
                min_frequency=args.min_frequency,
            )
        else:
            tokenizer = ByteTokenizer()
        config = LMLMConfig(
            vocab_size=tokenizer.vocab_size,
            context_length=args.context_length,
            hidden_size=args.hidden_size,
            num_layers=args.layers,
            num_heads=args.heads,
            device=args.device,
        )
        path = train_from_text(
            args.corpus,
            args.output,
            config=config,
            tokenizer=tokenizer,
            steps=args.steps,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
            seed=args.seed,
        )
        print(
            f"Saved local LMLM checkpoint: {path} "
            f"(tokenizer={args.tokenizer}, vocab_size={tokenizer.vocab_size})"
        )
    elif args.command == "generate":
        runtime = LMLMRuntime.from_checkpoint(args.checkpoint, device=args.device)
        print(
            runtime.generate(
                args.prompt,
                max_new_tokens=args.max_new_tokens,
                temperature=args.temperature,
                top_k=args.top_k,
            )
        )
    elif args.command == "evaluate":
        runtime = LMLMRuntime.from_checkpoint(args.checkpoint, device=args.device)
        result = evaluate_file(runtime, args.corpus)
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
