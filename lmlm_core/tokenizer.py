"""Deterministic UTF-8 byte tokenizer with reserved control tokens."""
from __future__ import annotations

from collections.abc import Iterable

PAD_TOKEN_ID = 0
BOS_TOKEN_ID = 1
EOS_TOKEN_ID = 2
UNK_TOKEN_ID = 3
BYTE_OFFSET = 4
VOCAB_SIZE = BYTE_OFFSET + 256


class ByteTokenizer:
    """Reversible UTF-8 byte tokenizer; no vocabulary download is required."""
    vocab_size = VOCAB_SIZE
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
            if BYTE_OFFSET <= token_id < VOCAB_SIZE:
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
