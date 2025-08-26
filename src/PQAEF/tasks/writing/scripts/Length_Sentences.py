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


class Length_Sentences:
    def __init__(self):
        self.number_words = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
            'eleven': 11, 'twelve': 12, 'fifteen': 15, 'twenty': 20,
            'thirty': 30, 'fifty': 50, 'hundred': 100, 'thousand': 1000,
            '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10, '两': 2,
        }

        self.number_regex = r"(\d+|" + \
            "|".join(self.number_words.keys()) + r")"

        self.patterns = [
            # exactly
            (r'exactly(?:[:])? ' + self.number_regex +
             r' (?:topic )?sentences?', self.parse_exact),
            (r'(?:should|must) contain ' + self.number_regex +
             r' sentences?', self.parse_exact),
            (r'must be exactly ' + self.number_regex +
             r' sentences?', self.parse_exact),

            # Exactly one sentence
            (r'(?:must|should)? be a single sentence', self.parse_single),
            (r'consisting of (?:only )?one sentence', self.parse_single),
            (r'(?:the response|the text|the answer) must be a single sentence',
             self.parse_single),
            (r'in a single sentence', self.parse_single),

            # at least
            (r'at least(?:[:])? ' + self.number_regex +
             r' sentences?', self.parse_min),
            (r'a minimum of ' + self.number_regex +
             r' sentences?', self.parse_min),
            (r'no fewer than ' + self.number_regex +
             r' sentences?', self.parse_min),
            (r'(?:包含)?(?:至少|最少)(?:包含)?' + self.number_regex +
             r'(?:个句子|句话|句|個句子)', self.parse_min),

            # at most
            (r'(?:must )?contain at most ' + self.number_regex +
             r' sentences?', self.parse_max),
            (r'at most(?:[:])? ' + self.number_regex +
             r' sentences?', self.parse_max),
            (r'not exceeding ' + self.number_regex +
             r' sentences?', self.parse_max),
            (r'no (?:more|longer) than ' + self.number_regex +
             r' sentences?', self.parse_max),
            (r'limited to ' + self.number_regex +
             r' sentences?', self.parse_max),
            (r'(?:must|should)? not exceed ' + self.number_regex +
             r' sentences?', self.parse_max),
            (r'a maximum (?:length )?of ' + self.number_regex +
             r' sentences?', self.parse_max),
            (r'not to exceed ' + self.number_regex +
             r' sentences?', self.parse_max),
            (r'not surpass(?: a total of)? ' + self.number_regex +
             r' sentences?', self.parse_max),
            (r'(?:至多|最多)(?:包含)?' + self.number_regex +
             r'(?:个句子|句话|句|個句子)', self.parse_max),


            # range
            (r'range(?:[:])? ' + self.number_regex +
             r'-' + self.number_regex +
             r' sentences?', self.parse_range),
            (r'between ' + self.number_regex +
             r' and ' + self.number_regex +
             r' sentences?', self.parse_range),
            (r'between ' + self.number_regex +
             r' to ' + self.number_regex +
             r' sentences?', self.parse_range),
            (r'into ' + self.number_regex +
             r' to ' + self.number_regex +
             r' sentences?', self.parse_range),
            (r'a range of ' + self.number_regex +
             r' to ' + self.number_regex +
             r' sentences?', self.parse_range),
            (r'be composed of ' + self.number_regex +
             r' to ' + self.number_regex +
             r' sentences?', self.parse_range),
            (r'consists? of ' + self.number_regex +
             r' to ' + self.number_regex +
             r' sentences?', self.parse_range),
            (r'consisting of ' + self.number_regex +
             r' to ' + self.number_regex +
             r' sentences?', self.parse_range),
            (self.number_regex + r'到' + self.number_regex +
             r'(?:个句子|句话|句|個句子)', self.parse_range),

            # Alternative phrasing
            (r'organized into at least ' + self.number_regex +
             r' sentences?', self.parse_min),
            (r'structured into at most ' + self.number_regex +
             r' sentences?', self.parse_max),
        ]

    def _parse_number(self, num_str):
        if num_str.isdigit():
            return int(num_str)
        return self.number_words.get(num_str.lower(), 0)

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
        return self._parse_number(match.group(1)), self._parse_number(match.group(2))

    def _parse_generic_group2(self, match):
        value = self._parse_number(match.group(2))
        keyword = match.group(1).lower()
        if keyword in {'limited to', 'must not exceed', 'at most', 'not more than'}:
            return {'max': value}
        elif keyword == 'exactly':
            return {'exact': value}
        return None

    def _parse_digits(self, match):
        return {'min': int(match.group(1)), 'max': int(match.group(2))}

    def parse_constraint(self, constraint):
        constraint = constraint.lower().strip()
        for pattern, handler in self.patterns:
            match = re.search(pattern, constraint)
            if match:
                return handler(match)
        return None, None

    def count_sentences(self, text):
        sentences = re.findall(r'[^.!?]*[.!?]', text)
        return len([s.strip() for s in sentences if s.strip()])

    def check(self, constraint, text):
        min_s, max_s = self.parse_constraint(constraint)
        params = self.parse_constraint(constraint)
        if not params:
            return False

        count = self.count_sentences(text)
        if min_s is not None and count < min_s:
            return False
        if max_s is not None and count > max_s:
            return False
        return True


if __name__ == "__main__":
    # test cases
    test_cases = [
        ("The answer must be composed of no more than 5 sentences",
         "hi. hi. hi. hi. hi. hi.", False),
        # exact match
        ("Exactly 1 sentence", "Hello.", True),
        ("The answer must be a single sentence.", "Hi.", True),
        ("The answer must consist of exactly one sentence", "Hi. Hello.", False),
        ("The list must be presented in a single sentence without additional descriptions",
         "Hi. Hello.", False),

        # minimum value
        ("At least 3 sentences", "One. Two. Three.", True),
        ("The answer must contain at least five sentences.", "S. S. S. S. S.", True),
        ("At least: 5 sentences", "S. S. S. S.", False),

        # maximum value
        ("At most 2 sentences", "One. Two.", True),
        ("The answer must be at most three sentences long.", "S. S. S. S.", False),

        # range
        ("Between 3 and 5 sentences", "One. Two. Three. Four.", True),
        ("The answer must be between five and ten sentences.", "S. " * 7, True),
        ("Range: 10-15 sentences", "S. " * 12, True),

        # mixed format
        ("The answer must contain between 5 and 10 sentences.", "S. " * 7, True),
        ("The answer must be between 3 to 5 sentences long.", "S. " * 4, True),

        ("The summary must include at least five sentences.", "S. S. S. S. S.", True),
        ("The summary must include at least five sentences.", "S. S. S. S.", False),
        ("The answer must contain at most three sentences.", "S. S.", True),
        ("The answer must contain at most three sentences.", "S. S. S. S.", False),
        ("The answer must be between five and ten sentences.", "S. " * 7, True),
        ("The script must contain at least twenty sentences.", "S. " * 20, True),
        ("The summary must include at least five sentences.", "S. S. S. S. S.", True),
        ("The summary must include at least five sentences.", "S. S. S. S.", False),
        ("The answer must contain at most three sentences.", "S. S.", True),
        ("The answer must contain at most three sentences.", "S. S. S. S.", False),

        ("Use at least 10 sentences in the response", "Ss! " * 10, True),
        ("Use at least 10 sentences in the response", "Ss of is! " * 9, False),
        ("The summary must include at least five sentences.", "S. S. S. S. S.", True),
        ("The summary must include at least five sentences.", "S. S. S. S.", False),


        ("Exactly 1 sentence", "Hello.", True),
        ("Exactly 1 sentence", "Hello! Hi.", False),
        ("At least 3 sentences", "One. Two. Three.", True),
        ("At least 3 sentences", "One. Two.", False),
        ("At most 2 sentences", "One. Two.", True),
        ("At most 2 sentences", "One. Two. Three.", False),
        ("Between 3 and 5 sentences", "One. Two. Three. Four.", True),
        ("Between 3 and 5 sentences", "One. Two.", False),
        ("Range 5-7 sentences", "One. Two. Three. Four. Five. Six.", True),
        ("Range 5-7 sentences", "One. Two.", False),
        ("The answer must be a single sentence.", "Hi.", True),
        ("The answer must be a single sentence.", "Hi. Hello.", False),
        ("At least: 5 sentences", "S. S. S. S. S.", True),
        ("At least: 5 sentences", "S. S. S. S.", False),
        ("The answer must contain between 5 and 10 sentences.", "S. " * 7, True),
        ("The answer must be between 3 to 5 sentences long.", "S. " * 4, True),
        ("Range: 10-15 sentences", "S. " * 12, True),
        ("The answer must be at most five sentences long.", "S. " * 6, False),

        ("包含至少5個句子", "S. " * 4, False),
        ("描述应由3到5个句子组成", "S. " * 4, True),
        ("至多包含三句话", "S. " * 4, False),


    ]

    validator = Length_Sentences()
    for constraint, text, expected in test_cases:
        result = validator.check(constraint, text)
        assert result == expected, f"""
        Failed Case:
        Constraint: {constraint}
        Text: {text}
        Expected: {expected}
        Actual: {result}
        """
    print("All test cases passed!")
