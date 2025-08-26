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
import json


class LengthWords_Each:
    def __init__(self):
        # numbers
        self.number_words = {
            "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
            "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
            "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
            "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
            "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40,
            "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80,
            "ninety": 90, "hundred": 100
        }
        # constraint parsing regex
        self.constraint_patterns = [
            (re.compile(r'between (\d+) and (\d+) words', re.I), 'range'),
            (re.compile(r'range: (\d+)-(\d+) words', re.I), 'range'),
            (re.compile(r'at least (\d+) words', re.I), 'min'),
            (re.compile(r'a minimum of (\d+) words', re.I), 'min'),
            (re.compile(r'a minimum length of (\d+) words', re.I), 'min'),
            (re.compile(r'at most (\d+) words', re.I), 'max'),
            (re.compile(r'exactly (\d+) words', re.I), 'exact'),
            (re.compile(r'no more than (\d+) words', re.I), 'max'),
            (re.compile(r'not exceed (\d+) words', re.I), 'max'),
            (re.compile(r'a maximum of (\d+) words', re.I), 'max'),
            (re.compile(r'a maximum length of (\d+) words', re.I), 'max'),
            (re.compile(r'limit of (\d+) words', re.I), 'max'),
            (re.compile(r'not exceeding (\d+) words', re.I), 'max'),
            (re.compile(r'less than (\d+) words', re.I), 'max'),

        ]

        # format detection regex
        self.table_re = re.compile(r'^\s*\|.+\|', re.M)
        self.bullet_re = re.compile(r'^\s*[-*] ')
        self.json_re = re.compile(r'^\s*[{\[]')
        self.numbered_re = re.compile(r'^\s*\d+\.\s+')

    def parse_constraint(self, constraint):
        """parse the constraint, return the target field and the limit range"""
        # preprocess the constraint, convert the English numbers to Chinese numbers
        constraint = re.sub(
            r'\b(' + '|'.join(self.number_words.keys()) + r')\b',
            lambda m: str(self.number_words[m.group().lower()]),
            constraint,
            flags=re.IGNORECASE
        )
        # extract the constraint target
        target_match = re.search(
            r'(?:each entry in the|Each entry in the|Each|each|The|the)\s+(.+?)\s+(?:is|in the table|column|must|consists of|contains?|should|have)',
            constraint,
            re.I
        )
        if not target_match:
            target = None
        else:
            target = target_match.group(1).lower()
            target = target.replace('"', '').replace("'", '')

        # extract the numerical limit
        min_val = max_val = None
        for pattern, c_type in self.constraint_patterns:
            if match := pattern.search(constraint):
                if c_type == 'range':
                    min_val, max_val = int(match[1]), int(match[2])
                elif c_type == 'min':
                    min_val = int(match[1])
                elif c_type == 'max':
                    max_val = int(match[1])
                elif c_type == 'exact':
                    min_val = max_val = int(match[1])
                break
        else:
            return None

        return {'target': target, 'min': min_val, 'max': max_val}

    def detect_format(self, text):
        """identify the main format of the text"""
        if self.json_re.search(text):
            return 'json'
        if self.table_re.search(text):
            return 'table'
        if self.numbered_re.search(text):
            return 'numbered'
        if self.bullet_re.search(text):
            return 'bullet'
        return 'plain'

    def extract_elements(self, text, target):
        """extract the elements to check according to the format"""

        fmt = self.detect_format(text)

        # table format processing
        if fmt == 'table':
            if (target == None):
                target = "cells"
            return self.parse_table(text, target)

        # JSON format processing
        if fmt == 'json':
            try:
                data = json.loads(text)
                if 'entry' in target:
                    return [str(v) for v in data.values()]
                return [str(data.get(target.split()[-1], ""))]
            except:
                return []
        if fmt == 'numbered':
            return [
                line.split(':', 1)[-1].split('.', 1)[-1].strip()
                for line in text.split('\n')
                if self.numbered_re.match(line)
            ]
        if fmt == 'bullet':
            return [line.split(' ', 1)[1].strip()
                    for line in text.split('\n')
                    if self.bullet_re.match(line)]

        # plain text processing
        return [
            line.strip().lstrip('#').strip()
            for line in text.split('\n')
            if line.strip()
            and not line.strip().strip('*#\'"').endswith(':')
            and not re.match(r'^\|.*\|$', line.strip())

        ]

    def parse_table(self, text, target="cells"):
        """parse the table content, return all non-empty cells"""

        cells = []
        for line in text.split('\n'):
            line = line.strip()
            if not line.startswith('|'):
                continue
            if re.match(r'^[\s|*-]+$', line):
                cells.append("<TitleSplit>")
            else:
                cells.extend([
                    cell.strip()
                    for cell in line[1:-1].split('|')
                    if cell.strip()
                ])
        try:
            split_index = cells.index("<TitleSplit>")
            headers = cells[:split_index]
            data_cells = [cell for cell in cells[split_index+1:]
                          if cell != "<TitleSplit>"]
        except ValueError:
            headers = cells
            data_cells = []

        # group the data by the number of headers
        row_length = len(headers)
        if row_length == 0:
            return []
        results = []
        for i in range(0, len(data_cells), row_length):
            row = data_cells[i:i+row_length]
            if len(row) == row_length:
                results.append(dict(zip(headers, row)))
        # target
        final_results = []
        # if target == "cells" or target == "cell": return cells
        has_target = False
        for item in results:
            # iterate the dictionary
            for key, value in item.items():
                if key.lower() == value.lower():
                    continue
                if target.lower() in key.lower():
                    final_results.append(value)
                    if has_target == False:
                        has_target = True
        if has_target == False:
            return cells
        else:
            return final_results

    def check_word_count(self, text, min_val, max_val):
        """check the word count of a single element"""
        words = text.split()
        count = len(words)

        if min_val is not None and max_val is not None:
            return min_val <= count <= max_val
        if min_val is not None:
            return count >= min_val
        if max_val is not None:
            return count <= max_val
        return False

    def check(self, constraint, text):
        """main check method"""
        if re.search(r"each word must be", constraint, re.IGNORECASE):
            match = re.search(
                r'(?i)must be (at most|at least) (\b(?:one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b) characters',
                constraint
            )
            words = text.split(' ')
            if match.group(1) == 'at most':
                for word in words:
                    if not len(word) <= int(match.group(2)):
                        return False
                return True
            if match.group(1) == 'at least':
                for word in words:
                    if not len(word) >= int(match.group(2)):
                        return False
                return True

        # replace the English numbers with Chinese numbers
        constraint_info = self.parse_constraint(constraint)
        if not constraint_info:
            return False
        elements = self.extract_elements(text, constraint_info['target'])
        if not elements:
            return False

        # check each element
        return all(
            self.check_word_count(
                elem, constraint_info['min'], constraint_info['max'])
            for elem in elements
        )


# ====================================================================================================================================

class Length_Words:
    def __init__(self):
        self.number_words = {
            "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
            "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
            "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
            "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
            "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40,
            "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80,
            "ninety": 90, "hundred": 100
        }

    def _word_to_number(self, word_str):  # support up to one hundred
        """parse the compound English numbers"""
        parts = re.split(r'[\s-]+', word_str.strip().lower())
        total = 0
        current = 0
        for part in parts:
            if part not in self.number_words:
                return None
            value = self.number_words[part]
            if value >= 100:
                if current == 0:
                    current = 1
                current *= value
                total += current
                current = 0
            elif value >= 10:
                current += value
            else:
                current += value
        return total + current

    def _parse_number(self, num_str):
        """parse the number"""
        num_str = num_str.strip().replace(',', '')
        if num_str.isdigit():
            return int(num_str)
        return self._word_to_number(num_str)

    def _build_keyword_info(self, keyword: str) -> dict:
        """build the keyword information"""
        return {
            "text": keyword,
            "is_chinese": any('\u4e00' <= c <= '\u9fff' for c in keyword)
        }

    def _build_pattern(self, keyword: str, is_chinese: bool) -> re.Pattern:
        """build the regex pattern"""
        flags = re.IGNORECASE if not is_chinese else re.UNICODE

        if is_chinese:
            pattern = re.escape(keyword)
        else:
            pattern = r'(?<!\w){}(?!\w)'.format(re.escape(keyword))

        return re.compile(pattern, flags)

    def check(self, constraint, text):
        if re.search(r'\beach\b', constraint, re.I) or re.search(r'\bEach\b', constraint, re.I):
            return LengthWords_Each().check(constraint, text)
        constraint_copy = constraint
        constraint = constraint.lower()
        constraint = constraint.strip('"').strip()
        constraint = re.sub(r'\s+', ' ', constraint).replace('-word', ' word').replace(
            'a total of ', '').replace('words', 'word').replace('a single', 'exactly one').strip()

        # basic text statistics: word count and sentence count

        if (bool(re.search(r'[\u4e00-\u9fff\u3400-\u4dbf\U00020000-\U0002a6df\u3000-\u303f\uff00-\uffef]', text)) == True):
            word_count = len(re.findall(
                r'[\u4e00-\u9fff\u3400-\u4dbf\U00020000-\U0002a6df\u3000-\u303f\uff00-\uffef]',
                text
            ))
        else:
            words = text.split()
            word_count = len(words)
        sentence_count = len(re.findall(r'[.!?]+', text))
        min_words, max_words = None, None
        min_sentences, max_sentences = None, None

        # 1. exact match pattern (handle exactly X words format)
        exact_pattern = r'exactly\s+([a-z0-9-, ]+?)\s+(\S+)'
        if exactly_match := re.search(exact_pattern, constraint):
            num_str = exactly_match.group(1).strip()
            exact_num = self._parse_number(num_str)
            if exact_num is not None:
                return word_count == exact_num

        # 2. range match (enhance the regex matching ability)
        range_patterns = [
            # 1. match "between X to Y word" format (English to)
            r'between\s+([a-z0-9-– ]+?)\s+to\s+([a-z0-9-– ]+?)(?=\s*word|$|\b)',
            # 2. match "between X and Y word" format (English and)
            r'between\s+([a-z0-9-– ]+?)\s+and\s+([a-z0-9-– ]+?)(?=\s*word|$|\b)',
            # 3. match the range description with prefix (optional colon)
            r'range:?\s*([a-z0-9-– ]+?)\s+to\s+([a-z0-9-– ]+?)(?=\s*word|$|\b)',
            # 4. match the range description with prefix (optional colon)
            r'range:?\s*([a-z0-9-– ]+?)\s*[-–]\s*([a-z0-9-– ]+?)(?=\s*word|$|\b)',
            # 5. match the range description without prefix (add word boundary)
            r'(\b[a-z0-9-–]+\b)\s+to\s+(\b[a-z0-9-–]+\b)(?=\s*word|$|\b)',
            # 6. match the range description without prefix (add word boundary)
            r'(\b[a-z0-9-–]+\b)\s*[-–]\s*(\b[a-z0-9-–]+\b)(?=\s*word|$|\b)',
            # Chinese
            r'([0-9]+)\s*到\s*([0-9]+)(?=\s*个|字)',

        ]
        for pattern in range_patterns:
            if match := re.search(pattern, constraint):
                min_val = match.group(1).strip()
                max_val = match.group(2).strip()
                min_words = self._parse_number(min_val)
                max_words = self._parse_number(max_val)

                if min_words is not None and max_words is not None:
                    if min_words > max_words:
                        min_words, max_words = max_words, min_words
                    break

        # 3. minimum word count match at least/minimum of/minimum length of/no less than
        if min_words is None:
            min_pattern = r'(?:at\s+least|minimum\s+of|minimum\s+length\s+of|no\s+less\s+than)\s+(\S+)\s+word'
            if at_least_match := re.search(min_pattern, constraint):
                num_str = at_least_match.group(1).strip()
                min_words = self._parse_number(num_str)
        if max_words is None:
            max_pattern = r'(?:not\s+exceed|not\s+exceeding|not\s+surpass|at\s+most|no\s+more\s+than|maximum\s+of|maximum\s+length\s+of|no\s+longer\s+than|limit\s+of|within|within\s+a)\s+(\S+)\s+word'
            if at_most_match := re.search(max_pattern, constraint):
                num_str = at_most_match.group(1).strip()
                max_words = self._parse_number(num_str)
        if max_words is None:
            max_patterns = [r'(?:最多)([0-9]+)(?:个|字)',
                            r'(?:在)([0-9]+)\s*(?:个单词以内|个字以内|字以内|单词以内|词以内|字)']
            for max_pattern in max_patterns:
                at_most_match = re.search(max_pattern, constraint)
                if at_most_match and max_words is None:
                    num_str = at_most_match.group(1).strip()
                    max_words = self._parse_number(num_str)
        # minimum sentence count match at least/minimum of
        if min_sentences is None:
            min_sentence_pattern = r'(?:at\s+least|minimum\s+of)\s+(\S+)\s+sentence'
            if at_least_sentence_match := re.search(min_sentence_pattern, constraint):
                num_str = at_least_sentence_match.group(1).strip()
                min_sentences = self._parse_number(num_str)
        # maximum sentence count match not exceed /at most /no more than /maximun of
        if max_sentences is None:
            max_sentence_pattern = r'(?:not\s+exceed|at\s+most|no\s+more\s+than|maximum\s+of|maximum\s+length\s+of|no\s+longer\s+than)\s+(\S+)\s+sentence'
            if at_most_sentence_match := re.search(max_sentence_pattern, constraint):
                num_str = at_most_sentence_match.group(1).strip()
                max_sentences = self._parse_number(num_str)
        keywords = []
        for match in re.finditer(r"[\"']([^\']*)[\"']", constraint):
            kw = match.group(1)
            keywords.append(self._build_keyword_info(kw))

        # final verification logic
        for kw in keywords:
            pattern = self._build_pattern(kw["text"], kw["is_chinese"])
            if len(pattern.findall(text)) < 1:
                return False
        if min_words is not None and word_count < min_words:
            return False
        if max_words is not None and word_count > max_words:
            return False
        if min_sentences is not None and sentence_count < min_sentences:
            return False
        if max_sentences is not None and sentence_count > max_sentences:
            return False
        return True


if __name__ == "__main__":

    # test cases
    test_cases = [
        ("Each word must be at most 8 characters long",
         "This is a test case with a single word that is toooooooo long.", False),
        ("Each word must be at most 8 characters long",
         "This is a test case with a single word that is fine.", True),
        ("Each slide must contain no more than 50 words.", "This is a test case with more than 50 words in a single slide. This is a test case with more than 50 words. This is a test case with more than 50 words. This is a test case with more than 50 words. This is a test case with more than 50 words.", False),
        ("Each slide must contain no more than 50 words.",
         "This is a test case in a single slide.", True),

        # table test
        (
            "Each name must be at most 3 words long.",
            '''| Name                     |  
    |--------------------------|  
    | Global Wave Cargo        |  
    | Global Link Ships        |  
    | Global Sea Trade         |  
    | International Ocean |''',
            True
        ),
        (
            "Each name must be at most 3 words long.",
            '''| Name                     |  
    |--------------------------|  
    | Global Wave Cargo        |  
    | Global Link Ships        |  
    | Global Sea Trade         |  
    | International Ocean Logistics Group |''',
            False
        ),
        (
            "Each cell must contain at most 10 words",
            "| Short text | Longer text with exactly ten words one two three four five six seven eight nine ten |",
            False
        ),
        (
            "Each cell must contain at most 10 words",
            "| Short text | Longer text with exactly ten words |",
            True
        ),
        # JSON test
        (
            "Each entry must contain between 2 and 4 words",
            '{"name": "John Doe", "title": "Senior Software Engineer"}',
            True  # title field has 4 words, but overall视为单个entry
        ),
        (
            "Each entry must contain between 2 and 4 words",
            '{"name": "John Doe", "title": "Senior Software Engineer abc 123"}',
            False  # title字段有4个单词，但整体视为单个entry
        ),
        # bullet point test
        (
            "Each bullet point must contain at most 5 words",
            "- First point\n- Second point with too many words here",
            False
        ),
        # mixed format test (handle table first)
        (
            "Each cell must contain at most 3 words",
            '''Text header
    | Column1       | Column2       |
    |---------------|---------------|
    | Valid entry   | Invalid entry with extra words |''',
            False
        ),
        # name test
        (
            "Each name must be at most 3 words long.",
            "Maria Lopez Garcia",
            True
        ),
        (
            "Each name must be at most 3 words long.",
            "Maria Lopez Garcia accac",
            False
        ),
        # csv test
        ('each movie title consists of between 2 and 5 words',
            """| Movie Title            | Release Year |
            |-------------------------|--------------|
            | Everything Everywhere All at Once | 2022         |
            | Top Gun Maverick       | 2022         |
            | The Batman             | 2022         |""",
            True
         ),
        ("Each cell must contain between five and ten words", 'word ' * 7, True),
        ("Each entry in the checklist must contain at most 15 words to ensure clarity and brevity",
            """#TABLE1
    | Skill Area | Checklist Item |
    |------------|----------------|
    | Ball Control | Throw a ball with one hand |
    | Ball Control | Catch a large ball with both hands |
    #TABLE2
    | Skill Area | Checklist Item |
    |------------|----------------|
    | Mobility   | Walk up and down stairs with support |
    | Mobility   | Run with control and coordination |
            """,
            True
         ),
        ("Each definition must be at most 10 words long",
            """1. SOCIETY: A GROUP OF INDIVIDUALS LIVING TOGETHER UNDER SIMILAR RULES.  
    2. MORALITY: BELIEFS AND PRINCIPLES DISTINGUISHING RIGHT FROM WRONG.  
    3. ETHICS: GUIDELINES FOR BEHAVIOR BASED ON MORAL VALUES AND DUTIES.
            """,
            True
         ),
        (
            "Each name must be at most 3 words long.",
            '''1. MediaCorp\n2. Global Media\n3. MediaWorks\n4. MediaGroup\n5. Prime Media\n6. MediaLink\n7. MediaSphere\n8. MediaFusion''',
            True
        ),
        (
            "Each name must be at most 3 words long.",
            '''1. MediaCorp hi hi hi\n2. Global Media\n3. MediaWorks\n4. MediaGroup\n5. Prime Media\n6. MediaLink\n7. MediaSphere\n8. MediaFusion''',
            False
        ),
        ("Each question must contain at most ten words.",
            """WHAT IS THE NAME OF YOUR SITH CHARACTER?
    WHERE DID YOUR SITH CHARACTER ORIGINATE FROM?
    HOW DID YOUR SITH GAIN POWER?
    WHICH SITH LORD INSPIRED YOUR CHARACTER?
    DOES YOUR SITH HAVE A LIGHTSABER?
    WHAT COLOR IS YOUR SITH'S LIGHTSABER?
    WHO IS THE ENEMY OF YOUR SITH?
    DOES YOUR SITH FEAR ANYTHING?
    HOW DOES YOUR SITH VIEW THE JEDI?
    WILL YOUR SITH EVER CHANGE ALIGNMENT?
            """,
            True
         ),
        ("\"each pronunciation guide is concise, with a maximum of 5 words to maintain clarity and brevity\"",
            """| Zootopia Character | Pronunciation Guide               |
    |--------------------|----------------------------------|
    | Judy Hopps         | Joo-dee Hops.                   |
    | Nick Wilde         | Nik Wild.                       |
    | Flash              | Flask.                          |
    | Chief Bogo         | Bee-go.                         |
    | Mr. Big            | Muh Big.                        |
    | Bellwether         | Bell-weather.                   |
    | Clawhauser         | Claw-house-er.                  |
    | Benjamin Clawhauser| Ben-jah-min Claw-house-er.       |
    | Gideon Grey        | Ji-don Gray.                    |
    | Yax                | Yaks.                           |
    | Finnick            | Fi-nik.                         |
    | Doug               | Dowg.                           |""",
            True
         ),
        ("\"ensure that it is concise and clear, with a maximum length of 50 words for each term\"",
            """**Public:**  
    The `public` keyword allows a class, method, or variable to be accessed from any other class. It provides unrestricted access within the Java application.

    **Final:**  
    The `final` keyword is used for classes, methods, or variables to prevent modification. Final classes cannot be extended, final methods cannot be overridden, and final variables cannot change their value once assigned.

    **Static:**  
    The `static` keyword belongs to the class rather than an instance. Static members (methods or variables) can be accessed without creating an object of the class, promoting shared access across all instances.

    **Void:**  
    The `void` keyword specifies that a method does not return any value. It indicates the absence of a return type, meaning the method performs an action but does not provide a result.

    **Private:**  
    The `private` keyword restricts access to a class, method, or variable. Private members are only accessible within the same class, ensuring encapsulation and hiding implementation details from other classes.""",
            True
         ),
        ("Each translation must be at most 10 words long.",
            """## Por Qué Las Sirenas No Te Complacieron?
    ## Por Qué Las Sirenas No Te Gustaron?
    ## Por Qué Las Sirenas No Te Satisficieron?""",
            True
         ),
    ]

    # execute the test
    validator = LengthWords_Each()
    for i, (constraint, text, expected) in enumerate(test_cases):
        result = validator.check(constraint, text)
        assert result == expected, f"""
        Failed Case {i+1}:
        Constraint: {constraint}
        Text: {text}
        Expected: {expected}
        Actual: {result}
        """
    print("All test cases passed!")

    # test cases
    test_cases = [

        # ===========================================================================
        # exact exactly
        ('The answer must be a single word.', 'word ' * 300, False),
        ('The answer must be a single word.', 'word ' * 0, False),
        ('The answer must be a single word.', 'word ' * 1, True),

        ('The script must be exactly 300 words long.', 'word ' * 300, True),
        ('The script must be exactly 300 words long.', 'word ' * 301, False),
        ('Exactly 3,500 words', 'word ' * 3500, True),
        ('Exactly 3,500 words', 'word ' * 3499, False),
        ('Exactly one word', 'word', True),
        ('Exactly one word', 'word word', False),
        ('Exactly 35 words', 'word ' * 35, True),
        ('Each dialog line must contain exactly 10 words.', 'word ' * 35, False),
        ('Each dialog line must contain exactly 10 words.', 'word ' * 10, True),
        ('Exactly 30 words', 'word ' * 35, False),
        ('Exactly 3 words', 'word is happy.', True),
        ('Exactly 0 words', '', True),
        ('Exactly 0 words', 'word', False),
        ("Must be exactly five words", 'word ' * 5, True),
        ("Must be exactly five words", 'word ' * 4, False),
        ("Must be exactly 30 words", ' '.join(['word '] * 30), True),
        ("Must be exactly 30 words", ' '.join(['word '] * 29), False),
        ("Exactly 1 word", "word", True),
        ("Exactly 1 word", "", False),
        # ===========================================================================
        # range
        ("Range: five to ten words", 'word ' * 4, False),
        ("Range: five to ten words", 'word ' * 7, True),
        ("Range: 50-100 words", 'word ' * 51, True),
        ("Range: 50-100 words", 'word ' * 40, False),
        ("Range: 50-100 words", 'word ' * 101, False),
        ("Between fifteen and twenty words", 'word ' * 16, True),
        ('Range: The response must be between 50 to 100 words', 'word ' * 60, True),
        ("10-15 words", 'word ' * 14, True),
        ("10-15 words", 'word ' * 16, False),
        ("between twenty five and forty", 'word ' * 30, True),
        ("between twenty five and forty", 'word ' * 50, False),
        ("50 to sixty", 'word ' * 55, True),
        ("50 to sixty", 'word ' * 65, False),
        ('Between twenty-five and 30 words', 'word ' * 28, True),
        ('From 10 to 20 words', 'word ' * 15, True),
        ('From 10 to 20 words', 'word ' * 25, False),
        ('Range: fifty-five to sixty-five words', 'word ' * 60, True),
        ('Range: fifty-five to sixty-five words', 'word ' * 70, False),
        ('Between 100 and 50 words', 'word ' * 75, True),
        ('Between 100 and 50 words', 'word ' * 30, False),
        ('"Range, The answer must be between 50 and 100 words."', 'word ' * 75, True),
        ('"Range, The answer must be between 50 and 100 words."', 'word ' * 30, False),
        ('Range: twenty-five to thirty-five words', 'word ' * 30, True),
        ('Range: twenty-five to thirty-five words', 'word ' * 40, False),
        ('Range: 25 to thirty words', 'word ' * 27, True),
        ('Range: 25 to thirty words', 'word ' * 35, False),
        ('Range: 100-200 words', 'word ' * 150, True),
        ('Range: 100-200 words', 'word ' * 201, False),
        ("Range: 150-200 words", 'word ' * 170, True),
        ("Range: 150-200 words", 'word ' * 199, True),
        ("Range: 150-200 words", 'word ' * 149, False),
        ("Range: 50-100 words", 'word ' * 50, True),
        ("Range: 50-100 words", 'word ' * 100, True),
        ("Range: 50-100 words", 'word ' * 49, False),
        ("Range: 50-100 words", 'word ' * 101, False),
        ('Range: The answer must be between 20 to 50 words', 'word ' * 20, True),
        ('Range: The answer must be between 20 to 50 words', 'word ' * 19, False),
        ('Range: The answer must be between five to ten words', 'word ' * 19, False),
        ('Range: The answer must be between five to ten words', 'word ' * 7, True),
        ('Range: The answer must be between twenty one to thirty words', 'word ' * 25, True),
        ("range 150-200 word", 'word ' * 201, False),
        ("range:300-500", 'word ' * 400, True),  # 无"word"关键词
        ("Range:50–100", 'word ' * 75, True),
        ("The answer must be between 50 and 100 words.", 'word ' * 75, True),
        ("The answer must be between 50 to 100 words.", 'word ' * 50, True),
        ("The answer must be between 50-100 words.", 'word ' * 99, True),
        ("between 20 and 50 words", 'word ' * 19, False),
        ("between 20 and 50 words", 'word ' * 20, True),
        ("50 to 100 words", 'word ' * 99, True),


        ('The answer must be between 10 and 20 words', 'word ' * 21, False),
        ('The answer must be between 10 and 20 words', 'word ' * 11, True),
        ('The answer must be between 50 to 100 words',
         'This is a sentence. ' * 9, False),
        ('The answer must be between 50 to 100 words',
         'This is a sentence. ' * 20, True),
        ('The joke must contain between 10 and 20 words, ensuring it falls within the required length range', 'word ' * 20, True),
        ('the answer must be composed of 10 to 20 words', 'word ' * 11, True),
        ('the answer must be composed of 10 to 20 words', 'word ' * 1, False),
        ('"the response should be detailed, consisting of between 50 and 100 words"',
         'word ' * 56, True),
        ('"the response should be detailed, consisting of between 50 and 100 words"',
         'word ' * 10000, False),
        ('"the response should be concise yet informative, with a word count ranging between 50 and 100 words"', 'word ' * 100, True),
        ('"the response should be concise yet informative, with a word count ranging between 50 and 100 words"', 'word ' * 49, False),
        ('ensure that your response is between 50 and 100 words', 'word ' * 10086, False),
        ('ensure that your response is between 50 and 100 words', 'word ' * 50, True),
        ('"Additionally, ensure that your response is between 50 and 100 words"',
         'word ' * 2, False),
        ('"Additionally, ensure that your response is between 50 and 100 words"',
         'word ' * 53, True),


        # ===========================================================================
        # at least
        ("At least ten words", 'word ' * 9, False),
        ("At least ten words", 'word ' * 10, True),
        ('Contain at least 5 words', 'word ' * 5, True),
        ('The essay must contain at least 2,500 words.', 'word ' * 2499, False),
        ('The answer must be at least 10 words.', 'word ' * 10, True),
        ('The answer must be at least 10 words.', 'word ' * 9, False),
        ('The answer must contain at least 100 words', 'word ' * 100, True),
        ('The answer must contain at least 100 words', 'word ' * 99, False),
        ("At least 150 words", 'word ' * 150, True),
        ("At least 150 words", 'word ' * 149, False),
        ('The essay must contain at least 2,500 words.', 'word ' * 2500, True),
        ('The essay must contain at least 2,500 words.', 'word ' * 2499, False),
        ('The corrected email must contain at least 50 words', 'word ' * 50, True),
        ('The corrected email must contain at least 50 words', 'word ' * 49, False),
        ('The presentation must contain at least 1000 words.', 'word ' * 1000, True),
        ('The presentation must contain at least 1000 words.', 'word ' * 999, False),
        ('The sentence must contain at least fifteen words.', 'word ' * 15, True),
        ('The sentence must contain at least fifteen words.', 'word ' * 14, False),
        ('The answer must be at least 150 words long', 'word ' * 150, True),
        ('The answer must be at least 150 words long', 'word ' * 149, False),
        ("At least 0 words", "", True),
        ("At least 0 words", "word", True),
        ("The answer must contain at least 150 words to ensure a comprehensive response.",
         'word ' * 150, True),
        ("The answer must contain at least 150 words to ensure a comprehensive response.",
         'word ' * 149, False),
        ('The answer must contain at least 300 words to provide comprehensive coverage of the topic.',
         'word ' * 150, False),
        ('The answer must contain at least 300 words to provide comprehensive coverage of the topic.', 'word ' * 390, True),
        ('The essay should be a minimum of 2,500 words in length, ensuring thorough exploration of the topic.', 'word ' * 2400, False),
        ('The essay should be a minimum of 2,500 words in length, ensuring thorough exploration of the topic.', 'word ' * 2550, True),
        ("Your solution must include the keyword 'solution' and be at least 20 words long",
         'solution ' * 20, True),
        ("Your solution must include the keyword 'solution' and be at least 20 words long",
         'soul ' * 20, False),
        ("Your solution must include the keyword 'solution' and be at least 20 words long",
         'solution ' * 19, False),
        ('The response should contain at least 150 words but must not exceed 10 sentences to maintain clarity and conciseness.',
         'word ' * 100 + 'This is a sentence. ' * 9, False),
        ('The response should contain at least 150 words but must not exceed 10 sentences to maintain clarity and conciseness.',
         'word ' * 160 + 'This is a sentence. ' * 9, True),
        ('The response should contain at least 150 words but must not exceed 10 sentences to maintain clarity and conciseness.',
         'word ' * 160 + 'This is a sentence. ' * 11, False),
        ('Minimum of 20 words', 'word ' * 19, False),
        ('Minimum of 20 words', 'word ' * 20, True),

        # each
        ('Each answer must be at least 20 words long', 'word ' * 20, True),
        ('Each answer must be at least 20 words long', 'word ' * 19, False),
        ('Each article must contain at least 300 words', 'word ' * 300, True),
        ('Each article must contain at least 300 words', 'word ' * 299, False),

        ('provide a detailed discussion that is no less than 150 words in length',
         'word ' * 299, True),
        ('provide a detailed discussion that is no less than 150 words in length',
         'word ' * 99, False),


        # ===========================================================================
        # at most
        ('The name of the college football quarterback must contain at most three words.',
         'John Smith', True),
        ('The name of the college football quarterback must contain at most three words.',
         'John Smith is.', True),
        ('The name of the college football quarterback must contain at most three words.',
         'John Smith Smith is abc', False),
        ('Up to five words', 'word ' * 5, True),
        ('Up to five words', 'word ' * 6, False),
        ('The response must be up to 100 words', 'word ' * 100, True),
        ('Up to five words', 'word ' * 5, True),
        ('Up to five words', 'word ' * 6, False),
        ('The response must be up to 100 words', 'word ' * 100, True),
        ('The response must be up to 100 words', 'word ' * 101, False),
        ('The answer must contain no more than five words.', 'word ' * 5, True),
        ('The answer must contain no more than five words.', 'word ' * 6, False),
        ('"At most: The book must not exceed 50,000 words"', 'word ' * 50001, False),
        ('"At most: The book must not exceed 50,000 words"', 'word ' * 1, True),
        ("The response should not exceed 25 words", 'word ' * 24, True),
        ('At most 0 words', '', True),
        ('At most 0 words', 'word', False),
        ('Maximum of 30 words', 'word ' * 30, True),
        ('Maximum of 30 words', 'word ' * 31, False),
        ('The maximum of 50 words applies', 'word ' * 50, True),
        ('The maximum of 50 words applies', 'word ' * 51, False),
        ('"The response should be concise, with no more than 100 words."',
         'word ' * 100, True),
        ('"The response should be concise, with no more than 100 words."',
         'word ' * 101, False),
        ("Each MCQ must contain at most 50 words", 'word ' * 50, True),
        ("Each MCQ must contain at most 50 words", 'word ' * 51, False),
        ('The answer must not exceed five words.', 'word ' * 6, False),
        ("Each MCQ must contain at most 50 words", 'word ' * 50, True),
        ("Each definition must be at most 30 words to fit on an index card",
         'word ' * 30, True),
        ("Each definition must be at most 30 words to fit on an index card",
         'word ' * 31, False),
        ("The response should be concise, with no more than 100 words.",
         ' word' * 100, True),
        ("The response should be concise, with no more than 100 words.", ' word' * 99, True),
        ("The response should be concise, with no more than 100 words.",
         ' word' * 101, False),
        ("The answer must not exceed five words.", ' word' * 5, True),
        ("The answer must not exceed five words.", ' word' * 6, False),
        ("The answer must not exceed five words.", 'word ' * 6, False),  # 6词应失败
        ("The answer must not exceed five words.", 'word ' * 5, True),   # 5词应通过
        ("At most 50 words", 'word ' * 50, True),
        ("At most 50 words", 'word ' * 51, False),
        ("The answer must not exceed 100 words.", 'word ' * 100, True),
        ("The answer must not exceed 100 words.", 'word ' * 101, False),
        ("At most 0 words", "", True),
        ("At most 0 words", "word", False),
        ("Not exceed twenty words", 'word ' * 21, False),
        ('"The answer must contain at most 300 words."', 'word ' * 300, True),
        ('Must not exceed 20 words.', 'word ' * 20, True),
        ('No more than 10 words', 'word ' * 10, True),

        ("The response should be concise, containing no more than ten words in total",
         "word " * 9, True),
        ("The response should be concise, containing no more than ten words in total",
         "word " * 11, False),
        ("be no longer than 50 words", "word " * 11, True),
        ("be no longer than 50 words", "word " * 101, False),
        ('"The explanation should be concise, with a maximum length of 150 words"',
         "word " * 1, True),
        ('"The explanation should be concise, with a maximum length of 150 words"',
         "word " * 151, False),
        ("hi hi hi hi limit the response to 150 words", "word " * 150, True),
        ("limit the response to 150 words", "word " * 151, False),
        ("limit the response to 149 words", "word " * 149, True),
        ("Limit the answer to a maximum of 50 words", "word " * 149, False),
        ("Limit the answer to a maximum of 50 words", "word " * 49, True),

        # Chinese
        ('"The entire response must be concise, not exceeding 300 words, to maintain clarity and focus"', "word " * 200, True),
        ('"The entire response must be concise, not exceeding 300 words, to maintain clarity and focus"', "word " * 301, False),
        ("the total word count must not surpass 100 words", "word " * 151, False),
        ("the total word count must not surpass 100 words", "word " * 51, True),
        ("keep it within a limit of 50 words", "word " * 151, False),
        ("keep it within a limit of 50 words", "word " * 50, True),

        ('"ensure it is concise and does not exceed a total of 100 words, as the response must be limited to a maximum word count of 100"', "word " * 151, False),
        ('"ensure it is concise and does not exceed a total of 100 words, as the response must be limited to a maximum word count of 100"', "word " * 1, True),

        ("The answer must contain at most 100 words and include at least 3 sentences to ensure conciseness and sufficient detail",
         "word " * 151 + "This is sentence." * 3, False),
        ("The answer must contain at most 100 words and include at least 3 sentences to ensure conciseness and sufficient detail",
         "word " * 91 + "This is sentence." * 3, True),
        ("The answer must contain at most 100 words and include at least 3 sentences to ensure conciseness and sufficient detail",
         "word " * 91 + "This is sentence." * 2, False),

        ("Revise the following statement to be concise and within 50 words",
         "word " * 151, False),
        ("Revise the following statement to be concise and within 50 words",
         "word " * 32, True),

        ("Please revise the statement to be concise and within a 50-word limit",
         "word " * 151, False),
        ("Please revise the statement to be concise and within a 50-word limit",
         "word " * 50, True),
        ("答案应包含最多150个字", "六" * 151, False),
        ("答案应包含最多150个字", "六" * 150, True),
        ("字數需介於50到100字之間", "間" * 50, True),
        ("字數需介於50到100字之間", "間" * 150, False),

        ("润色后的句子必须在50个单词以内", "句子" * 30, False),
        ("润色后的句子必须在50个单词以内", "句子" * 10, True),

        # each

        ("Maintain a concise format with each heading being at most 10 words long",
            """# H1. **Eurocentrism: A Paradigm of Epistemological Supremacy**  

## H2. **The Binary Construction of Eurocentrism: West and East**  

### H3. **The Epistemological Framework of Eurocentrism**  

Eurocentrism is an epistemological framework that situates European culture, history, and values as the defining center of the world, while disregarding or belittling the contributions of other cultures and civilizations.  

## H2. **The Consequences of Eurocentric Discourse**  

### H3. **The Perpetuation of False Dichotomies**  

Eurocentric discourse breeds a false dichotomy between the West and non-European societies, perpetuating the notion that the West is superior and in control of all areas of life, including social, political, cultural, scientific, military, and economic fields.  

## H2. **The Reinforcement of Western Supremacy**  

### H3. **The Role of Discourse in Consolidating Western Supremacy**  

This paradigm is reinforced through various forms of discourse, including history, literature, art, music, etc., which consistently depict non-European societies as inferior and exotic.  

## H2. **The Orientalist Perspective**  

### H3. **The Construction of the Orient as a Mirror to the West**  

Edward Said's seminal text *Orientalism* (1979) asserts that European culture gained strength and identity by setting itself off against the Orient as a sort of surrogate and even underground self.  

## H2. **The Consequences of Eurocentric Discourse**  

### H3. **The Justification of Colonization and Exploitation**  

This discourse of exoticism, essentialism, and stereotyping of the East and its people has been used to justify colonization, exploitation, and violence against Eastern civilizations.  

## H2. **The Impact of Eurocentrism on Global Power Structures**  

### H3. **The Perpetuation of Subordination**  

Eurocentrism perpetuates the subordination of non-European societies within global power structures, and the spheres of knowledge and influence.  

| **Discourse Form** | **Contribution to Eurocentrism** | **Impact** |  
| --- | --- | --- |  
| History | Depiction of non-European societies as inferior | Perpetuation of false dichotomies |  
| Literature | Portrayal of non-European cultures as exotic | Reinforcement of Western supremacy |  
| Art | Representation of non-European societies as static and archaic | Justification of colonization and exploitation |""",
            True
         ),
    ]

    # execute the test
    validator = Length_Words()
    for constraint, text, expected in test_cases:
        result = validator.check(constraint, text)
        assert result == expected, f"""
        Failed Case:
        Constraint: {constraint}
        Text: {text}
        Expected: {expected}
        Actual: {result}
        Word count: {len(text.split())}
        """
    print("All test cases passed!")
