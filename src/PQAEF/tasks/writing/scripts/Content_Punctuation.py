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
import string

# 简单的句子分割函数，替代NLTK的sent_tokenize
def simple_sent_tokenize(text):
    """简单的句子分割，替代NLTK"""
    # 按句号、问号、感叹号分割
    sentences = re.split(r'[.!?]+\s+', text.strip())
    # 过滤空字符串并去除首尾空格
    return [s.strip() for s in sentences if s.strip()]

# 直接使用简单分割函数
sent_tokenize = simple_sent_tokenize

# 注释掉所有NLTK相关代码
# import nltk
# try:
#     from nltk.tokenize import sent_tokenize
# except ImportError:
#     import nltk
#     nltk.download('punkt')
#     nltk.download('punkt_tab')
#     from nltk.tokenize import sent_tokenize


class Content_Punctuation:
    def __init__(self):
        self.punctuation_map = {
            'period': '.',
            'question mark': '?',
            'exclamation mark': '!',
            'semicolon': ';',
        }
        self.negative_keywords = re.compile(
            r'\b(must not|avoid|exclude|not end with|do not use)\b', re.IGNORECASE)
        self.special_pattern = re.compile(
            r'(period|question mark|exclamation mark|semicolon)\s+followed by a `([^`]+)`',
            re.IGNORECASE
        )

    def check(self, constraint, text):
        constraint_clean = constraint.strip().lower().rstrip('.')
        original_text = text.strip()

        # split by paragraph
        if 'paragraph' in constraint_clean or "section" in constraint_clean:
            sentences = [sentence.strip() for sentence in original_text.split(
                '\n') if sentence.strip()]
        # split by sentence
        else:
            # if the keyword "each" appears
            if 'each' in constraint_clean or "any" in constraint_clean or "all" in constraint_clean:
                sentences = sent_tokenize(original_text)
            else:
                # do not split sentences, only check the last punctuation of the text
                sentences = [original_text]

        if 'table' in constraint_clean or 'cell' in constraint_clean:
            rows = original_text.split('\n')
            if len(rows) > 1:
                # remove the header
                rows = rows[2:]
            # split by table format, each cell/entry is a independent sentence
            sentences = [sentence for sentence in [cell.strip() for row in rows for cell in re.split(
                r'\s*\|\s*', row.strip('|')) if cell.strip()] if sentence.strip('-')]

        special_match = self.special_pattern.search(constraint_clean)

        # check if "bullet point" appears in constraint
        if 'bullet point' in constraint_clean:
            bullet_points = re.findall(
                r'^[\-\*\•]\s.*$', original_text, re.MULTILINE)
            # determine the punctuation to check
            required_punctuation = None
            for key, value in self.punctuation_map.items():
                if key in constraint_clean:
                    required_punctuation = value
                    break
            # check if each bullet point ends with the specified punctuation
            return all(
                all(sent.strip().endswith(required_punctuation) if required_punctuation else sent.strip(
                )[-1] in string.punctuation for sent in sent_tokenize(point))
                for point in bullet_points
            )

        # check if the constraint is a negative condition
        is_negative = self.negative_keywords.search(
            constraint_clean) is not None

        # print the check
        for sentence in sentences:
            # check if the sentence is not empty
            if not sentence:
                return False if not is_negative else True

        # process the special structure: punctuation followed by specific characters (e.g., .~)
        if special_match:
            base_punct = self.punctuation_map.get(
                special_match.group(1).lower(), '')
            additional = special_match.group(2)
            expected_end = base_punct + additional
            return all(sentence.endswith(expected_end) for sentence in sentences)

        # extract the punctuation name (allow plural form)
        punctuation_names = re.findall(
            r'\b(periods?|question marks?|exclamation marks?|semicolons?|punctuation marks?)\b',
            constraint_clean
        )
        # remove the plural and standardize
        punctuation_names = [name.rstrip('s').replace(
            'mark', 'mark') for name in punctuation_names]

        allowed_punctuations = []
        if any('punctuation mark' in name for name in punctuation_names):
            allowed_punctuations = list(string.punctuation)
        else:
            for name in punctuation_names:
                punct = self.punctuation_map.get(name, None)
                if punct:
                    allowed_punctuations.append(punct)

        # check if all sentences satisfy the condition
        if is_negative:
            return all(sentence[-1] not in allowed_punctuations for sentence in sentences if sentence)
        else:
            return all(sentence[-1] in allowed_punctuations for sentence in sentences if sentence)


# test cases
test_cases = [

    ("Any explanatory text must end with a period",
     "This is a test! Wrong one.", False),
    # additional test
    ("Each sentence ends with a period",
     "I don't think this is right. Right? Fair enough.", False),
    ("Additionally, ensure that the answer ends with an exclamation mark to emphasize the dramatic nature of the topic.", "That's true!", True),
    ("Each article's title: it must be capitalized and end with a period to adhere to proper punctuation and presentation standards", "Right.", True),
    ("Each article's title: it must be capitalized and end with a period to adhere to proper punctuation and presentation standards", "Right", False),
    ("Each sentence ends with a period", "Yes. Right. Okay", False),
    ("Each sentence ends with a period", "Yes. Right? Okay!", False),
    ("Each bullet point concludes with an exclamation mark",
     "- This is a test. - This is not!", False),
    ("Each bullet point concludes with an exclamation mark",
     "- This is a test! - This is not!", True),
    ("Each bullet point concludes with an exclamation mark",
     "- This is a test! - This is not! - Another test!", True),
    ("Each bullet point concludes with an exclamation mark",
     "- This is a test! - This is not! - Another test.", False),
    ("Each bullet point ends with a period",
     "- This is a test. - This is not!", False),
    ("Each bullet point ends with a period",
     "- This is a test. - This is not.", True),

    ("Each cell must end with a period",
     "| Date.  | Location | Marked Shift In Air Superiority  |", False),
    ("Each cell must end with a period",
     "| Date. | Location. | Marked Shift In Air Superiority.             |", True),
    ("Each entry in the table must end with a period", """| Core Value        | Description                                                                | Key Focuses                |
|-------------------|----------------------------------------------------------------------------|----------------------------|
| EQUALITY          | The New People Party Advocates For Equal Rights And Opportunities For All. | Social Justice, Inclusivity |
|-------------------|----------------------------------------------------------------------------|----------------------------|
| SUSTAINABILITY    | A Commitment To Environmental And Economic Sustainability For Future Generations. | Green Policies, Climate Change |
| INNOVATION        | Encouraging Cutting-Edge Solutions To Address Modern Challenges.           | Technology, Research, Progress |
| DEMOCRATIC VALUES | Supporting A Transparent, Participatory Government That Prioritizes The People. | Transparency, Accountability |
| ECONOMIC REFORM   | Pushing For A Fair And Resilient Economy With Emphasis On Small Business.   | Economic Equity, Support For Entrepreneurs |
""", False),
    ("Each entry in the table must end with a period",
     "| Date. | Location. | Marked Shift In Air Superiority.             |", True),
    ("Each paragraph must end with a period.",
     "This is a test. This is only a test \n Hi! Hi.", False),
    ("Each paragraph must end with a period.",
     "This is a test. This is only a test. \n Hi! Hi.", True),


    # self-test
    ('The improved title must not end with a period.', 'Hello.', False),
    ('The improved title must not end with a period.', 'Hello', True),
    ('The improved title must not end with a period.', 'Hello!', True),
    ('Names must not end with punctuation marks', 'Hello.', False),
    ('Names must not end with punctuation marks', 'Hello', True),
    ('Names must not end with punctuation marks', 'Hello!', False),
    ('"Ending punctuation, The answer must end with a period."', 'Hello.', True),
    ('"Ending punctuation, The answer must end with a period."', 'Hello', False),
    ('"Ending punctuation, The answer must end with a period."', 'Hello!', False),
    ('"Ending punctuation must include a period, question mark, or exclamation mark"', 'Hello.', True),
    ('"Ending punctuation must include a period, question mark, or exclamation mark"', 'Hello?', True),
    ('"Ending punctuation must include a period, question mark, or exclamation mark"', 'Hello!', True),
    ('"Ending punctuation must include a period, question mark, or exclamation mark"', 'Hello', False),
    ('Ending punctuation must be a semicolon', ';', True),
    ('Ending punctuation must be a semicolon', ';.', False),
    ('Ending punctuation must be a period or a question mark', 'Hello?', True),
    ('Ending punctuation must be a period or a question mark', 'Hello.', True),
    ('Ending punctuation must be a period or a question mark', 'Hello!', False),
    ('Ending punctuation must be a period followed by a `~`', 'End.~', True),
    ('Ending punctuation must be a period followed by a `~`', 'End.', False),
    ('Ending punctuation must be a period followed by a `~`', 'End~', False),
    ('"""The response must end with a period."""', 'Hello.', True),
    ('"""The response must end with a period."""', 'Hello', False),
    ('Avoid using exclamation marks', 'Hello!', False),
    ('Ending punctuation must be a period', 'Hello.', True),
    ('The answer must end with a period.', 'Hello.', True),


    # must end with a period
    ("The answer must end with a period", "Hello.", True),
    ("The answer must end with a period", "Hi", False),
    # must not end with a period
    ("The improved title must not end with a period", "Title.", False),
    ("The improved title must not end with a period", "Title", True),
    # must end with a question mark
    ("Ending punctuation must be a question mark", "Yes?", True),
    ("Ending punctuation must be a question mark", "No.", False),
    # must not end with an exclamation mark
    ("Avoid using exclamation marks", "Hi!", False),
    ("Avoid using exclamation marks", "Hi.", True),
    # plural form test
    ("Ending punctuation must be periods", "Yes.", True),
    ("Names must not end with punctuation marks", "Anna,", False),

    # must not end with any punctuation
    ("Names must not end with punctuation marks", "Alice", True),
    ("Names must not end with punctuation marks", "Bob!", False),
    ("Names must not end with punctuation marks", "Charlie?", False),
    ("Names must not end with punctuation marks",
     "Anna,", False),  # comma is also a punctuation
    # must end with a period or a question mark
    ("Ending punctuation must be a period or a question mark", "Okay.", True),
    ("Ending punctuation must be a period or a question mark", "Why?", True),
    ("Ending punctuation must be a period or a question mark", "No!", False),
    # special structure: period followed by ~
    ("Ending punctuation must be a period followed by a `~`", "End.~", True),
    ("Ending punctuation must be a period followed by a `~`", "End~", False),
    ("Ending punctuation must be a period followed by a `~`", "End.", False),
    # must end with a semicolon
    ("Ending punctuation must be a semicolon", "List;", True),
    ("Ending punctuation must be a semicolon", "List.", False),
    # must not end with a semicolon
    ("Avoid using semicolons", "Here;", False),
    ("Avoid using semicolons", "Here", True),
    # must not end with any punctuation
    ("Ending punctuation must not end with punctuation marks", "Text", True),
    ("Ending punctuation must not end with punctuation marks", "Text.", False),
    ("Ending punctuation must not end with punctuation marks", "Text?", False),
    # allow multiple punctuation
    ("Ending punctuation must include a period, question mark, or exclamation mark", "Yes!", True),
    ("Ending punctuation must include a period, question mark, or exclamation mark", "No.", True),
    ("Ending punctuation must include a period, question mark, or exclamation mark", "Why?", True),
    ("Ending punctuation must include a period, question mark, or exclamation mark", "Hi", False),
    ("Ending punctuation must be a period or a question mark", "Hello?", True),
    ("Ending punctuation must be a period or a question mark", "Hello!", False),
    # other cases
    ("The response must end with an exclamation mark.", "Wow!", True),
    ("The response must end with an exclamation mark.", "Oops", False),
    ("The answer must end with a question mark.", "What?", True),
    ("Ending punctuation must be a period", "Hello.", True),
    ("Ending punctuation must be a period", "Hi", False),
    ("Ending punctuation must be a question mark for all test questions", "Test?", True),
    ("Ending punctuation must be a question mark for all test questions", "Test.", False),
    ("The script must end with a period.", "The end.", True),
    ("The script must end with a period.", "The end", False),
    ("The joke must end with an exclamation mark.", "Haha!", True),
    ("The joke must end with an exclamation mark.", "Haha?", False),
    ("Ending punctuation must be an exclamation mark", "Yay!", True),
    ("Ending punctuation must be an exclamation mark", "Yay.", False),
    # empty string test
    ("The answer must end with a period", "", False),
    ("The answer must end with a period", "Hi.   ", True),
    ("The answer must end with a period", "  hi? Hi.  ", True),
    ("Names must not end with punctuation marks", "", True),

]

if __name__ == "__main__":
    # execute the test
    validator = Content_Punctuation()
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
