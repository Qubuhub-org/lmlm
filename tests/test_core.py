import importlib.util
import math
import tempfile
import unittest
from pathlib import Path

from lmlm_core.config import LMLMConfig
from lmlm_core.tokenizer import (
    BASE_VOCAB_SIZE,
    BOS_TOKEN_ID,
    EOS_TOKEN_ID,
    BPETokenizer,
    ByteTokenizer,
    tokenizer_from_dict,
)


class ConfigTests(unittest.TestCase):
    def test_default_vocabulary_matches_byte_tokenizer(self):
        self.assertEqual(LMLMConfig().vocab_size, ByteTokenizer.vocab_size)

    def test_dynamic_vocabulary_is_supported(self):
        self.assertEqual(LMLMConfig(vocab_size=512).vocab_size, 512)

    def test_vocabulary_below_base_size_is_rejected(self):
        with self.assertRaises(ValueError):
            LMLMConfig(vocab_size=BASE_VOCAB_SIZE - 1)

    def test_invalid_head_dimension_is_rejected(self):
        with self.assertRaises(ValueError):
            LMLMConfig(hidden_size=127, num_heads=4)

    def test_unknown_config_keys_are_rejected(self):
        with self.assertRaises(ValueError):
            LMLMConfig.from_dict({"hidden_szie": 128})

    def test_config_round_trip(self):
        config = LMLMConfig(context_length=64, hidden_size=64, num_heads=4)
        self.assertEqual(LMLMConfig.from_dict(config.to_dict()), config)


class TokenizerTests(unittest.TestCase):
    def setUp(self):
        self.tokenizer = ByteTokenizer()

    def test_ascii_and_unicode_round_trip(self):
        value = "LMLM — Nigeria 🇳🇬"
        self.assertEqual(self.tokenizer.decode(self.tokenizer.encode(value)), value)

    def test_control_tokens(self):
        self.assertEqual(
            self.tokenizer.encode("A", add_bos=True, add_eos=True),
            [BOS_TOKEN_ID, ord("A") + 4, EOS_TOKEN_ID],
        )

    def test_out_of_range_token_is_rejected(self):
        with self.assertRaises(ValueError):
            self.tokenizer.validate_ids([9999])

    def test_non_string_input_is_rejected(self):
        with self.assertRaises(TypeError):
            self.tokenizer.encode(123)


class BPETokenizerTests(unittest.TestCase):
    def setUp(self):
        self.text = "LMLM banana banana banana — Nigeria Nigeria."

    def test_training_learns_merges_and_round_trips(self):
        tokenizer = BPETokenizer.train(
            self.text, vocab_size=280, min_frequency=2
        )
        self.assertGreater(tokenizer.vocab_size, BASE_VOCAB_SIZE)
        self.assertEqual(tokenizer.decode(tokenizer.encode(self.text)), self.text)

    def test_training_is_deterministic(self):
        first = BPETokenizer.train(self.text, vocab_size=280, min_frequency=2)
        second = BPETokenizer.train(self.text, vocab_size=280, min_frequency=2)
        self.assertEqual(first.merges, second.merges)

    def test_tokenizer_metadata_round_trip(self):
        tokenizer = BPETokenizer.train(self.text, vocab_size=275, min_frequency=2)
        restored = tokenizer_from_dict(tokenizer.to_dict())
        self.assertIsInstance(restored, BPETokenizer)
        self.assertEqual(restored.merges, tokenizer.merges)
        self.assertEqual(restored.decode(restored.encode(self.text)), self.text)

    def test_invalid_merge_vocabulary_is_rejected(self):
        with self.assertRaises(ValueError):
            BPETokenizer([(999, 1000)])


@unittest.skipUnless(importlib.util.find_spec("torch"), "PyTorch runtime is optional")
class ModelTests(unittest.TestCase):
    def setUp(self):
        from lmlm_core.runtime import LMLMRuntime

        config = LMLMConfig(
            context_length=8, hidden_size=16, num_layers=1, num_heads=4, dropout=0
        )
        self.runtime = LMLMRuntime.create_untrained(config)

    def test_forward_returns_logits_and_loss(self):
        import torch
        from lmlm_core.model import LMLMModel

        config = LMLMConfig(
            context_length=8, hidden_size=16, num_layers=1, num_heads=4, dropout=0
        )
        model = LMLMModel(config)
        inputs = torch.randint(0, config.vocab_size, (2, 8))
        targets = torch.randint(0, config.vocab_size, (2, 8))
        logits, loss = model(inputs, targets)
        self.assertEqual(tuple(logits.shape), (2, 8, config.vocab_size))
        self.assertTrue(torch.isfinite(loss).item())

    def test_bpe_checkpoint_preserves_tokenizer(self):
        from lmlm_core.runtime import LMLMRuntime

        text = "LMLM local model " * 12
        tokenizer = BPETokenizer.train(text, vocab_size=275, min_frequency=2)
        config = LMLMConfig(
            vocab_size=tokenizer.vocab_size,
            context_length=8,
            hidden_size=16,
            num_layers=1,
            num_heads=4,
            dropout=0,
        )
        runtime = LMLMRuntime.create_untrained(config, tokenizer)
        with tempfile.TemporaryDirectory() as directory:
            checkpoint = Path(directory) / "lmlm-bpe.pt"
            runtime.save_checkpoint(checkpoint)
            restored = LMLMRuntime.from_checkpoint(checkpoint, device="cpu")
            self.assertIsInstance(restored.tokenizer, BPETokenizer)
            self.assertEqual(
                restored.tokenizer.decode(restored.tokenizer.encode(text)), text
            )
            self.assertTrue(
                restored.generate("LMLM", max_new_tokens=1, top_k=8).startswith("LMLM")
            )

    def test_evaluation_scores_each_next_token_once(self):
        from lmlm_core.evaluate import evaluate_text

        result = evaluate_text(self.runtime, "LMLM evaluation windows")
        expected = len(self.runtime.tokenizer.encode("LMLM evaluation windows")) - 1
        self.assertEqual(result["token_count"], expected)
        self.assertEqual(result["sequence_count"], math.ceil(expected / 8))
        self.assertTrue(math.isfinite(result["loss"]))
        self.assertGreater(result["perplexity"], 0)

    def test_evaluation_rejects_too_short_text(self):
        from lmlm_core.evaluate import evaluate_text

        with self.assertRaises(ValueError):
            evaluate_text(self.runtime, "")

    def test_evaluation_does_not_leave_model_in_training_mode(self):
        from lmlm_core.evaluate import evaluate_text

        self.runtime.model.train()
        evaluate_text(self.runtime, "evaluation mode restoration")
        self.assertTrue(self.runtime.model.training)


if __name__ == "__main__":
    unittest.main()
