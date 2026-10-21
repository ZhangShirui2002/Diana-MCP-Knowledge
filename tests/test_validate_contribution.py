import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "validate_contribution.py"
SPEC = importlib.util.spec_from_file_location("validate_contribution", MODULE_PATH)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class GitHubContentDecodingTests(unittest.TestCase):
    def test_accepts_line_wrapped_base64_from_contents_api(self):
        self.assertEqual(VALIDATOR.decode_github_content("aGVs\nbG8=\n"), b"hello")

    def test_rejects_non_base64_content(self):
        with self.assertRaises(VALIDATOR.Rejected):
            VALIDATOR.decode_github_content("not-base64!")


if __name__ == "__main__":
    unittest.main()
