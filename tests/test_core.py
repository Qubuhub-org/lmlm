import unittest

from lmlm_core.config import LMLMConfig
from lmlm_core.tokenizer import ByteTokenizer, BOS_TOKEN_ID, EOS_TOKEN_ID


class ConfigTests(unittest.TestCase):
    def test_default_vocabulary_matches_tokenizer(self):
        self.assertEqual(LMLMConfig().vocab_size, ByteTokenizer.vocab_size)

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


if __name__ == "__main__":
    unittest.main()
