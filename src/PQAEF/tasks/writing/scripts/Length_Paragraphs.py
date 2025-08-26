'''
Copyright Junjie Ye

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''


import re


class Length_Paragraphs:
    def __init__(self):
        self.number_words = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
            '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10, '两': 2,
        }
        self.patterns = [
            # exactly
            (r'exactly (\d+|one|two|three|four|five|six|seven|eight|nine|ten) paragraphs?', self.parse_exact),
            (r'must be exactly (\d+|one|two|three|four|five|six|seven|eight|nine|ten) paragraphs?', self.parse_exact),
            (r'(?:should|must) contain (\d+|one|two|three|four|five|six|seven|eight|nine|ten) paragraphs?', self.parse_exact),
            # Exactly one paragraph
            (r'(?:must|should)? be a single paragraph', self.parse_single),
            (r'(?:the response|the text|the answer) must be a single paragraph',
             self.parse_single),

            # at least
            (r'at least (\d+|one|two|three|four|five|six|seven|eight|nine|ten) paragraphs?', self.parse_min),
            (r'least: (\d+|one|two|three|four|five|six|seven|eight|nine|ten) paragraphs?', self.parse_min),
            (r'a minimum of (\d+|one|two|three|four|five|six|seven|eight|nine|ten)(?: distinct)? paragraphs?', self.parse_min),

            # at most
            (r'at most (\d+|one|two|three|four|five|six|seven|eight|nine|ten) paragraphs?', self.parse_max),
            (r'not exceeding (\d+|one|two|three|four|five|six|seven|eight|nine|ten) paragraphs?', self.parse_max),
            (r'no more than (\d+|one|two|three|four|five|six|seven|eight|nine|ten) paragraphs?', self.parse_max),
            (r'最多(?:分为)?(\d+|一|两|二|三|四|五|六|七|八|九|十)个段落', self.parse_max),

            # range
            (r'range (\d+)-(\d+) paragraphs?', self.parse_range),
            (r'range: (\d+)-(\d+)', self.parse_range),
            (r'between (\d+) and (\d+) paragraphs?', self.parse_range),
            (r'between (\d+) to (\d+) paragraphs?', self.parse_range),
            (r'(\d+) to (\d+) paragraphs?', self.parse_range),
            (r'(?:divided)? into (\d+) to (\d+) paragraphs?', self.parse_range),
            (r'a range of (\d+) to (\d+) paragraphs?', self.parse_range),

            (r'organized into at least (\d+|one|two|three|four|five|six|seven|eight|nine|ten) paragraphs?', self.parse_min),
            (r'structured into at most (\d+|one|two|three|four|five|six|seven|eight|nine|ten) paragraphs?', self.parse_max),
        ]

    def parse_exact(self, match):
        num = match.group(1)
        value = self._parse_number(num)
        return (value, value)

    def parse_single(self, match):
        return (1, 1)

    def parse_min(self, match):
        num = match.group(1)
        value = self._parse_number(num)
        return (value, None)

    def parse_max(self, match):
        num = match.group(1)
        value = self._parse_number(num)
        return (None, value)

    def parse_range(self, match):
        min_val = int(match.group(1))
        max_val = int(match.group(2))
        return (min_val, max_val)

    def _parse_number(self, num_str):
        if num_str.isdigit():
            return int(num_str)
        return self.number_words.get(num_str.lower(), 0)

    def _parse_constraint(self, constraint):
        constraint = constraint.lower()
        for pattern, handler in self.patterns:
            match = re.search(pattern, constraint, re.IGNORECASE)
            if match:
                return handler(match)
        return (None, None)

    def count_paragraphs(self, text):
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        return len(paragraphs)

    def check(self, constraint, text):
        min_p, max_p = self._parse_constraint(constraint)
        if min_p is None and max_p is None:
            return False
        count = self.count_paragraphs(text)
        if min_p is not None and count < min_p:
            return False
        if max_p is not None and count > max_p:
            return False
        return True


if __name__ == "__main__":
    # test cases
    test_cases = [
        # At least
        ("At least 2 paragraphs", "Paragraph 1\n\nParagraph 2", True),
        ("At least 2 paragraphs", "Single paragraph", False),
        ("At least five paragraphs", "P1\n\nP2\n\nP3\n\nP4\n\nP5", True),
        ("At least five paragraphs", "P1\n\nP2", False),
        ("it is divided into a minimum of three distinct paragraphs",
         "P1\n\nP2\n\nP3", True),
        ("it is divided into a minimum of three distinct paragraphs", "P1\n\nP2", False),
        ("it is divided into a minimum of three distinct paragraphs",
         "P1\n\nP2\n\nP3\n\nP4", True),
        # At most
        ("At most 3 paragraphs", "P1\n\nP2\n\nP3", True),
        ("At most 3 paragraphs", "P1\n\nP2\n\nP3\n\nP4", False),
        ("not exceeding three paragraphs", "P1\n\nP2", True),
        ("not exceeding three paragraphs", "P1\n\nP2\n\nP3\n\nP4", False),
        ("no more than 10 paragraphs",
         "P1\n\nP2\n\nP3\n\nP4\n\nP5\n\nP6\n\nP7\n\nP8\n\nP9\n\nP10", True),
        ("no more than 10 paragraphs",
         "P1\n\nP2\n\nP3\n\nP4\n\nP5\n\nP6\n\nP7\n\nP8\n\nP9\n\nP10\n\nP11", False),
        ("最多分为2个段落", "P1\n\nP2", True),
        ("最多分为2个段落", "P1\n\nP2\n\nP3", False),
        # Exactly
        ("Must be exactly 2 paragraphs", "P1\n\nP2", True),
        ("Must be exactly 2 paragraphs", "P1", False),
        ("exactly three paragraphs", "P1\n\nP2\n\nP3", True),
        ("exactly three paragraphs", "P1\n\nP2", False),
        ("The response must be a single paragraph", "P1", True),
        ("The response must be a single paragraph", "P1\n\nP2", False),
        # Range
        ("Range 3-5 paragraphs", "P1\n\nP2\n\nP3", True),
        ("Range 3-5 paragraphs", "P1\n\nP2\n\nP3\n\nP4\n\nP5", True),
        ("Range 3-5 paragraphs", "P1", False),
        ("between 3 and 5 paragraphs", "P1\n\nP2\n\nP3\n\nP4", True),
        ("between 3 and 5 paragraphs", "P1\n\nP2", False),
        ("between 3 to 5 paragraphs", "P1\n\nP2\n\nP3\n\nP4\n\nP5", True),
        ("between 3 to 5 paragraphs", "P1\n\nP2", False),
        ("into 3 to 5 paragraphs", "P1\n\nP2\n\nP3\n\nP4\n\nP5", True),
        ("into 3 to 5 paragraphs", "P1\n\nP2", False),
        ("divided into 3 to 5 paragraphs", "P1\n\nP2\n\nP3\n\nP4\n\nP5", True),
        ("within a range of 2 to 4 paragraphs", "P1\n\nP2\n\nP3\n\nP4", True),
        ("within a range of 2 to 4 paragraphs", "P1\n\nP2", True),
        # Complex cases
        ("The answer must be organized into at least three paragraphs.",
         "P1\n\nP2\n\nP3", True),
        ("The script must contain between 3 and 5 paragraphs.",
         "P1\n\nP2\n\nP3\n\nP4", True),
        ("Each slide must contain at least 1 paragraph", "P1", True),
        # Invalid constraints (no paragraph keyword)
        ("The table must have at most five rows", "Some text", False),
        ("The list must contain at least five names", "Text", False),
        ("The answer should be organized into at least 3 paragraphs, indicating that the response must be divided into a minimum of three distinct sections", "P1\n\nP2\n\nP3", True),
        ("The answer should be organized into at least 3 paragraphs, indicating that the response must be divided into a minimum of three distinct sections", "P1\n\nP2", False),
    ]

    # execute the test
    validator = Length_Paragraphs()
    for i, (constraint, text, expected) in enumerate(test_cases):
        result = validator.check(constraint, text)
        assert result == expected, f"""
        Failed Case {i + 1}:
        Constraint: {constraint}
        Text: {text}
        Expected: {expected}
        Actual: {result}
        """
    print("All test cases passed!")
