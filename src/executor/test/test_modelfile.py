import unittest
import logging
from kuwa.executor.modelfile import extract_text_from_quotes, Script


class TestExtractTextFromQuotes(unittest.TestCase):
    test_cases = {
        '"This is a text"': "This is a text",
        '"It\'s a text"': "It's a text",
        '"""multi-line\ntext"""': "multi-line\ntext",
        '"it\'s a text"': "it's a text",
        "'Made with \"love\"'": 'Made with "love"',
        '"""multi-line\ntext\nMade with "love""""': 'multi-line\ntext\nMade with "love"',
        '"""multi-line\ntext\nMade with \'love\'"""': "multi-line\ntext\nMade with 'love'",
        "'He said, \"Hello!\"'": 'He said, "Hello!"',
        "\"She replied, 'Hi there!'\"": "She replied, 'Hi there!'",
        "No quotes here": "No quotes here",
        "Invalid 'syntax'": "Invalid 'syntax'",
        " No quote with spaces  ": "No quote with spaces",
        ' "Quote with space "   ': "Quote with space ",
        " 'Quote with space '   ": "Quote with space ",
        ' """Quote with new line and space\n """   ': "Quote with new line and space\n ",
    }

    def test(self):
        for test_case, correct_result in self.test_cases.items():
            result = extract_text_from_quotes(test_case)
            self.assertEqual(result, correct_result)


class TestScriptSyntax(unittest.TestCase):
    test_cases = {
        Script.DEFAULT: (True, Script.DEFAULT_CONTENT),
        "000IPO": (True, "IPO"),
        "000": (True, ""),
        " 000 ": (True, ""),
        "000;;;": (True, ";;;"),
        "000OPIII": (True, "OPIII"),
        "000I[PO]": (True, "I[PO]"),
        "123": (False, None),
        "123IPO": (False, None),
        "IPO": (False, None),
        " 1213": (False, None),
        "": (False, None),
    }

    def test(self):
        for test_case, correct_result in self.test_cases.items():
            result = (Script.validate_syntax(test_case), Script.get_content(test_case))
            self.assertEqual(result, correct_result)


if __name__ == "__main__":
    logging.basicConfig(level="DEBUG")
    unittest.main()
