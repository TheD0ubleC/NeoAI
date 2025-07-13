import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from level.common import extract_code, extract_callback, extract_all_code, extract_all_callbacks

class ExtractionTests(unittest.TestCase):
    def test_extract_code_and_callback(self):
        text = "before >>>RUN>>>print('hi')<<<RUN<<< middle >>>CALLBACK>>>done<<<CALLBACK<<< end"
        self.assertEqual(extract_code(text), "print('hi')")
        self.assertEqual(extract_callback(text), "done")

    def test_extract_all(self):
        text = (
            ">>>RUN>>>a<<<RUN<<< text >>>RUN>>>b<<<RUN<<< >>>CALLBACK>>>cb1<<<CALLBACK<<< >>>CALLBACK>>>cb2<<<CALLBACK<<<"
        )
        self.assertEqual(extract_all_code(text), ["a", "b"])
        self.assertEqual(extract_all_callbacks(text), ["cb1", "cb2"])

if __name__ == '__main__':
    unittest.main()
