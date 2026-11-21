"""Dependency-free byte and learned byte-pair tokenizers."""
from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping

PAD_TOKEN_ID = 0
BOS_TOKEN_ID = 1
EOS_TOKEN_ID = 2
UNK_TOKEN_ID = 3
BYTE_OFFSET = 4
BASE_VOCAB_SIZE = BYTE_OFFSET + 256


class ByteTokenizer:
    """Reversible UTF-8 byte tokenizer with four reserved control tokens."""
    vocab_size = BASE_VOCAB_SIZE
    pad_token_id = PAD_TOKEN_ID
    bos_token_id = BOS_TOKEN_ID
    eos_token_id = EOS_TOKEN_ID
    unk_token_id = UNK_TOKEN_ID

    def encode(self, text: str, *, add_bos: bool = False, add_eos: bool = False) -> list[int]:
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        tokens = [byte + BYTE_OFFSET for byte in text.encode("utf-8")]
        if add_bos:
            tokens.insert(0, BOS_TOKEN_ID)
        if add_eos:
            tokens.append(EOS_TOKEN_ID)
        return tokens

    def decode(self, token_ids: Iterable[int], *, skip_special_tokens: bool = True) -> str:
        payload = bytearray()
        special = {PAD_TOKEN_ID, BOS_TOKEN_ID, EOS_TOKEN_ID, UNK_TOKEN_ID}
        for token_id in token_ids:
            if not isinstance(token_id, int):
                raise TypeError("token IDs must be integers")
            if BYTE_OFFSET <= token_id < BASE_VOCAB_SIZE:
                payload.append(token_id - BYTE_OFFSET)
            elif token_id in special and skip_special_tokens:
                continue
            elif token_id in special:
                payload.extend(f"<{token_id}>".encode("ascii"))
            else:
                raise ValueError(f"token ID out of range: {token_id}")
        return payload.decode("utf-8", errors="replace")

    def validate_ids(self, token_ids: Iterable[int]) -> list[int]:
        result = list(token_ids)
        for token_id in result:
            if not isinstance(token_id, int) or not 0 <= token_id < self.vocab_size:
                raise ValueError(f"invalid token ID: {token_id!r}")
        return result

    def to_dict(self) -> dict:
        return {"type": "byte"}


class BPETokenizer(ByteTokenizer):
    """A small deterministic byte-pair tokenizer trained from local text.

    The first 260 IDs are reserved exactly as in ByteTokenizer. Each learned
    merge adds one token whose byte sequence is the concatenation of its pair.
    """

    def __init__(self, merges: Iterable[Iterable[int]]) -> None:
        self.merges = tuple((int(pair[0]), int(pair[1])) for pair in merges)
        token_bytes: list[bytes | None] = [None, None, None, None]
        token_bytes.extend(bytes([value]) for value in range(256))
        for left, right in self.merges:
            if left < BYTE_OFFSET or right < BYTE_OFFSET:
                raise ValueError("BPE merges cannot consume reserved control tokens")
            if left >= len(token_bytes) or right >= len(token_bytes):
                raise ValueError("BPE merge refers to a token that has not been created")
            left_bytes, right_bytes = token_bytes[left], token_bytes[right]
            if left_bytes is None or right_bytes is None:
                raise ValueError("BPE merge refers to a reserved token")
            token_bytes.append(left_bytes + right_bytes)
        self._token_bytes = tuple(token_bytes)
        self.vocab_size = len(self._token_bytes)

    @classmethod
    def train(
        cls,
        text: str,
        *,
        vocab_size: int = 512,
        min_frequency: int = 2,
    ) -> "BPETokenizer":
        """Learn frequent adjacent byte/token pairs from a local text corpus."""
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        if vocab_size < BASE_VOCAB_SIZE:
            raise ValueError(f"vocab_size must be at least {BASE_VOCAB_SIZE}")
        if min_frequency < 1:
            raise ValueError("min_frequency must be positive")

        tokens = [value + BYTE_OFFSET for value in text.encode("utf-8")]
        merges: list[tuple[int, int]] = []
        while BASE_VOCAB_SIZE + len(merges) < vocab_size and len(tokens) > 1:
            counts = Counter(zip(tokens, tokens[1:]))
            if not counts:
                break
            pair = max(counts, key=lambda item: (counts[item], -item[0], -item[1]))
            if counts[pair] < min_frequency:
                break

            merged_id = BASE_VOCAB_SIZE + len(merges)
            merged: list[int] = []
            index = 0
            while index < len(tokens):
                if index + 1 < len(tokens) and (tokens[index], tokens[index + 1]) == pair:
                    merged.append(merged_id)
                    index += 2
                else:
                    merged.append(tokens[index])
                    index += 1
            tokens = merged
            merges.append(pair)
        return cls(merges)

    def encode(self, text: str, *, add_bos: bool = False, add_eos: bool = False) -> list[int]:
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        tokens = [value + BYTE_OFFSET for value in text.encode("utf-8")]
        for merge_index, pair in enumerate(self.merges):
            merged_id = BASE_VOCAB_SIZE + merge_index
            merged: list[int] = []
            index = 0
            while index < len(tokens):
                if index + 1 < len(tokens) and (tokens[index], tokens[index + 1]) == pair:
                    merged.append(merged_id)
                    index += 2
                else:
                    merged.append(tokens[index])
                    index += 1
            tokens = merged
        if add_bos:
            tokens.insert(0, BOS_TOKEN_ID)
        if add_eos:
            tokens.append(EOS_TOKEN_ID)
        return tokens

    def decode(self, token_ids: Iterable[int], *, skip_special_tokens: bool = True) -> str:
        payload = bytearray()
        special = {PAD_TOKEN_ID, BOS_TOKEN_ID, EOS_TOKEN_ID, UNK_TOKEN_ID}
        for token_id in token_ids:
            if not isinstance(token_id, int):
                raise TypeError("token IDs must be integers")
            if token_id in special:
                if not skip_special_tokens:
                    payload.extend(f"<{token_id}>".encode("ascii"))
                continue
            if token_id < BYTE_OFFSET or token_id >= self.vocab_size:
                raise ValueError(f"token ID out of range: {token_id}")
            token_bytes = self._token_bytes[token_id]
            if token_bytes is None:
                raise ValueError(f"token ID is reserved: {token_id}")
            payload.extend(token_bytes)
        return payload.decode("utf-8", errors="replace")

    def to_dict(self) -> dict:
        return {"type": "bpe", "merges": [list(pair) for pair in self.merges]}

    @classmethod
    def from_dict(cls, values: Mapping) -> "BPETokenizer":
        if values.get("type") != "bpe":
            raise ValueError("tokenizer type must be 'bpe'")
        return cls(values.get("merges", []))


def tokenizer_from_dict(values: Mapping) -> ByteTokenizer | BPETokenizer:
    """Restore a tokenizer from checkpoint metadata."""
    kind = values.get("type", "byte")
    if kind == "byte":
        return ByteTokenizer()
    if kind == "bpe":
        return BPETokenizer.from_dict(values)
    raise ValueError(f"Unsupported tokenizer type: {kind!r}")
