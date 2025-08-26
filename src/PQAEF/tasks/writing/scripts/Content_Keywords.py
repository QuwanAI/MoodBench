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


class Content_Keywords_Each:
    def __init__(self):
        # Patterns for format detection
        self.table_re = re.compile(r'^\s*\|.+\|', re.M)
        self.bullet_re = re.compile(r'^\s*[-*] ')
        self.json_re = re.compile(r'^\s*[{\[]')
        self.numbered_re = re.compile(r'^\s*\d+\.\s+')
        # Pattern for "each" constraints
        self.each_pattern = re.compile(
            r'\b(each|every)\s+(.+?)\s+(must|should|needs to|has to)\s+(.*)', re.I)

    def detect_format(self, text):
        """Detect the primary format of the text."""
        if self.json_re.search(text):
            return 'json'
        if self.table_re.search(text):
            return 'table'
        if self.numbered_re.search(text):
            return 'numbered'
        if self.bullet_re.search(text):
            return 'bullet'
        return 'plain'

    def parse_constraint(self, constraint):
        """Parse the constraint to extract target and keyword rule."""
        match = self.each_pattern.search(constraint)
        if not match:
            return None
        target = match.group(2).lower()  # e.g., "entry", "cell"
        # e.g., "include the keyword 'example'"
        condition = match.group(4)
        # Use Content_Keywords to parse the keyword condition
        parser = Content_Keywords()
        rule = parser._parse_constraint(condition)
        return {'target': target, 'rule': rule}

    def is_separator(self, line):
        line = line.strip()
        if len(line) < 3:
            return False
        first_char = line[0]
        return all(c == first_char for c in line) and first_char in {'-', '*', '='}

    def extract_elements(self, text, target):
        """Extract elements to check based on format and target."""
        fmt = self.detect_format(text)
        # print("fmt:", fmt)
        if fmt == 'table':
            return self.parse_table(text, target)
        elif fmt == 'json':
            return self.parse_json(text, target)
        elif fmt == 'numbered':
            return self.parse_numbered(text)
        elif fmt == 'bullet':
            return self.parse_bullet(text)
        else:
            # process normal text, split by separator
            lines = text.split('\n')
            sections = []
            current_section = []
            for line in lines:
                if self.is_separator(line):
                    if current_section:
                        sections.append('\n'.join(current_section).strip())
                        current_section = []
                else:
                    current_section.append(line)
            if current_section:
                sections.append('\n'.join(current_section).strip())
            # if no split, return the whole text
            return sections if sections else [text]

    def parse_table(self, text, target):
        """Parse table content, prioritizing the header that best matches the target."""
        # Extract table rows (lines starting and ending with '|')
        table_lines = [line.strip() for line in text.split('\n')
                       if line.strip().startswith('|') and line.strip().endswith('|')]
        if len(table_lines) < 3:  # Need header, separator, and at least one data row
            return []

        # Parse headers from the first row
        headers = [h.strip() for h in table_lines[0].split('|')[1:-1]]
        if not headers:
            return []

        # Parse data rows (skip separator at index 1)
        data = []
        for line in table_lines[2:]:
            row = [cell.strip() for cell in line.split('|')[1:-1]]
            if len(row) == len(headers):
                data.append(dict(zip(headers, row)))
        if not data:
            return []

        # Function to clean cell content
        def clean_cell(cell):
            """Remove Markdown heading markers"""
            return re.sub(r'^#+\s*', '', cell).strip()

        # Function to normalize words
        def normalize_word(word):
            return re.sub(r'\W', '', word).lower()

        # Normalize target words into a set
        normalized_target_words = set(normalize_word(
            word) for word in target.split() if normalize_word(word))

        # Find the best matching header
        best_header = None
        max_matches = -1
        for header in headers:
            header_words = [normalize_word(
                word) for word in header.split() if normalize_word(word)]
            matches = sum(
                1 for word in header_words if word in normalized_target_words)
            if matches > max_matches:
                max_matches = matches
                best_header = header

        # If a matching header is found, return its cleaned cells
        if max_matches > 0:
            return [clean_cell(row[best_header]) for row in data if best_header in row]
        else:
            # Fallback: select column with highest average word count
            column_word_counts = {}
            for header in headers:
                total_words = sum(
                    len(clean_cell(row[header]).split()) for row in data if header in row)
                num_cells = sum(1 for row in data if header in row)
                if num_cells > 0:
                    column_word_counts[header] = total_words / num_cells
            if column_word_counts:
                content_header = max(column_word_counts,
                                     key=column_word_counts.get)
                return [clean_cell(row[content_header]) for row in data if content_header in row]
            return []

    def parse_json(self, text, target):
        """Parse JSON and extract string values."""
        try:
            data = json.loads(text)
            if isinstance(data, dict):
                return [str(v) for v in data.values()]
            elif isinstance(data, list):
                return [str(item) for item in data]
        except json.JSONDecodeError:
            return []

    def parse_numbered(self, text):
        """Parse numbered list and extract items."""
        return [line.split('.', 1)[1].strip() for line in text.split('\n') if self.numbered_re.match(line)]

    def parse_bullet(self, text):
        """Parse bullet list and extract items."""
        return [line.split(' ', 1)[1].strip() for line in text.split('\n') if self.bullet_re.match(line)]

    def check(self, constraint, text):
        """Check if each element satisfies the keyword constraint."""
        # print("====================== begin each check ==========================")
        constraint_info = self.parse_constraint(constraint)
        # print("constraint_info:", constraint_info)
        if not constraint_info:
            return False
        target = constraint_info['target']
        rule = constraint_info['rule']
        elements = self.extract_elements(text, target)
        # print("elements:", elements)
        if not elements:
            return False
        validator = Content_Keywords()
        return all(validator._validate_rule(elem, rule) for elem in elements)


class Content_Keywords:
    def __init__(self):
        self.word_to_number = {
            'once': 1, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
            'twice': 2
        }
        self.checks = [self.check_01, self.check_02]

    def _word_to_number_way(self, word_str):
        """解析复合英文数字（增强版）"""
        parts = re.split(r'[\s-]+', word_str.strip().lower())
        total = 0
        current = 0
        for part in parts:
            if part not in self.word_to_number:
                return None
            value = self.word_to_number[part]
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
        """parse number (enhanced version)"""
        num_str = num_str.strip().replace(',', '')
        if num_str.isdigit():
            return int(num_str)
        return self._word_to_number_way(num_str)

    def check_01(self, constraint: str, text: str):
        match = False
        include_match = re.search(
            r"includes?\s+the\s+keyword\s+[\"']([^\"']+)[\"']",
            constraint,
            re.IGNORECASE
        )
        avoid_match = re.search(
            r"avoids?\s+the\s+keyword\s+[\"']([^\"']+)[\"']",
            constraint,
            re.IGNORECASE
        )
        # if both actions exist, then make a judgment
        if include_match and avoid_match:
            match = True
            include_kw = include_match.group(1)
            avoid_kw = avoid_match.group(1)
            # if the text contains the include keyword and does not contain the avoid keyword, then return True, otherwise return False
            if include_kw in text and avoid_kw not in text:
                return match, True
            else:
                return match, False

        # if it does not match the special pattern, then return None, indicating that this constraint is not processed
        return match, None

    def check_02(self, constraint: str, text: str):
        # use regex to find all the (topic, keyword) pairs that meet the conditions
        conditions = re.findall(
            r"If discussing\s+([^,]+),\s*the summary must include the keyword\s+[\"']([^\"']+)[\"']",
            constraint,
            re.IGNORECASE
        )

        # if no related conditions are found, then it means that this constraint is not applicable to this special rule
        if not conditions:
            return False, None

        applicable = False  # whether there is a condition applicable to the current text
        for topic, keyword in conditions:
            topic_found = False
            if "/" in topic:
                # process the slash case, try to extract the common prefix and suffix
                m = re.match(r"^(.*\s)(\S+)\/(\S+)(\s.*)$", topic)
                if m:
                    prefix = m.group(1)
                    alt1 = m.group(2)
                    alt2 = m.group(3)
                    suffix = m.group(4)
                    topic1 = prefix + alt1 + suffix
                    topic2 = prefix + alt2 + suffix
                    topic_found = (topic1 in text or topic2 in text)
                else:
                    # if the regex matching fails, then split by the slash, remove the whitespace at both ends, and check whether any part is in text
                    parts = [part.strip() for part in topic.split("/")]
                    topic_found = any(part in text for part in parts)
            else:
                topic_found = (topic in text)

            if topic_found:
                applicable = True
                # if the text does not contain the required keyword, then return (True, False)
                if keyword not in text:
                    return True, False

        return True, True

    def check_03(self, constraint: str, text: str):
        constraint = constraint.strip('"').strip()
        pattern = r'the\s+([\w\s,]+)(?=,\s+ensuring\s+that\s+these\s+terms\s+are\s+explicitly\s+included)'
        matches = re.search(pattern, constraint)
        if matches:
            # get the results of all capture groups
            all_words = []
            for group in matches.groups():
                if group:
                    all_words.append(self._build_keyword_info(group))
        else:
            return False, None
        for kw in all_words:
            pattern = self._build_pattern(kw["text"], kw["is_chinese"])
            if len(pattern.findall(text)) < 1:
                return True, False
        return True, True

    def check(self, constraint: str, text: str) -> bool:
        # if the constraint contains "each" or "every" (not case-sensitive), enter Content_Keywords_Each
        if re.search(r'\b(each|every)\b', constraint, re.I) and "for each word" not in constraint:
            return Content_Keywords_Each().check(constraint, text)
        for check_i in self.checks:
            match, result = check_i(constraint, text)
            if match:
                return result
        rule = self._parse_constraint(constraint)
        return self._validate_rule(text, rule)

    def _parse_constraint(self, constraint: str) -> dict:
        constraint = constraint.strip()
        while re.match(r'^"+(.*[^"])"+$', constraint):
            constraint = re.sub(r'^"+(.*[^"])"+$', r'\1', constraint)  # 仅去除最外层

        rule = {
            "keywords": [],
            "min_count": 1,
            "exclude": False,
            "logical_or": False,
            "must_end_with_period": False,
            "capitalize_required": False,
            "min_words": 0,
            "max_words": float('inf')
        }

        if re.search(r"must\s+end\s+with\s+(a\s+)?period", constraint, re.IGNORECASE):
            rule["must_end_with_period"] = True

        capitalize_match = re.search(
            r"must\s+use\s+capitalized\s+letters\s+for\s+each\s+word", constraint, re.IGNORECASE)
        if capitalize_match:
            rule["capitalize_required"] = True

        min_pattern = r'(?:at\s+least|minimum\s+of)\s+(\S+)\s+word'
        at_least_match = re.search(min_pattern, constraint, re.IGNORECASE)
        if at_least_match:
            num_str = at_least_match.group(1).strip()
            rule["min_words"] = self._parse_number(num_str)

        max_pattern = r'(?:not\s+exceed|at\s+most|no\s+more\s+than|maximum\s+of)\s+(\S+)\s+word'
        at_most_match = re.search(max_pattern, constraint, re.IGNORECASE)
        if at_most_match:
            num_str = at_most_match.group(1).strip()
            rule["max_words"] = self._parse_number(num_str)

        if re.search(r"is\s+a\s+single\s+word", constraint, re.IGNORECASE):
            rule["min_words"] = 1
            rule["max_words"] = 1

        # parse the exclusion constraint
        if re.search(r"(avoid\s+using\s+(the\s+)?term|must\s+be\s+avoided)", constraint, re.IGNORECASE):
          # whether it contains "avoid using (the) term"
            match = re.search(r"[\"']([^\"']+)[\"']",
                              constraint)  # extract the keywords between the quotes
            if match:
                keyword = match.group(1)
                rule.update({
                    "keywords": [self._build_keyword_info(keyword)],
                    "exclude": True
                })
            return rule

        # parse the logical OR (supports case and space)
        if re.search(r"\bOR\b", constraint, re.IGNORECASE):
            rule["logical_or"] = True

        # parse the number of occurrences (supports "at least twice" or "at least 2 times")
        count_match = re.search(
            r"at least (\d+|one|two|three|four|five|six|seven|eight|nine|ten|once|twice)(?:\s+times?)?\b(?!\s+words\s+long)",
            constraint,
            re.IGNORECASE
        )
        if count_match:
            # extract the string and convert to lowercase
            count = count_match.group(1).lower()
            if count.isdigit():
                rule["min_count"] = int(count)
            else:
                rule["min_count"] = self.word_to_number.get(count, 1)

        count_match_multi = re.search(
            r"must appear multiple times",
            constraint,
            re.IGNORECASE
        )
        if count_match_multi:
            rule["min_count"] = 2

        # extract keywords
        keywords = []
        double_match = re.search(
            r'["”]{2}([^"“]+)["“]{2}', constraint, re.IGNORECASE)
        if double_match:
            for match in re.finditer(r'["”]{2}([^"“]+)["“]{2}', constraint):
                kw = match.group(1)
                keywords.append(self._build_keyword_info(kw))
        else:
            # extract all the content inside the single quotes, and put it into the keywords list one by one
            for match in re.finditer(r"[\"'「“]([^\"']+)[\"'」”]", constraint):
                kw = match.group(1)
                keywords.append(self._build_keyword_info(kw))
        rule["keywords"] = keywords

        return rule

    def _build_keyword_info(self, keyword: str) -> dict:
        """build the keyword metadata"""
        return {
            "text": keyword,
            # whether the keyword contains at least one Chinese character
            "is_chinese": any('\u4e00' <= c <= '\u9fff' for c in keyword)
        }

    def _build_pattern(self, keyword: str, is_chinese: bool):
        """build the regex matching pattern (enhanced version)"""
        flags = re.IGNORECASE if not is_chinese else re.UNICODE

        if is_chinese:
            # Chinese direct existence matching
            pattern = re.escape(keyword)
        else:
            # English strict boundaries: allow punctuation or spaces before and after, but not followed by letters or numbers
            pattern = r'(?<!\w){}(?!\w)'.format(re.escape(keyword))

        return re.compile(pattern, flags)

    def _validate_rule(self, text: str, rule: dict) -> bool:
        if rule["capitalize_required"]:
            # check if the first letter of each word is capitalized
            words = text.split()
            for word in words:
                # if the first letter of a word is not capitalized, return False
                if not word[0].isupper():
                    return False

        if rule["must_end_with_period"]:
            if not text.strip().endswith('.'):
                return False

        word_count = len(text.split())
        if word_count < rule["min_words"]:
            return False
        if word_count > rule["max_words"]:
            return False

        # validate a single rule
        if rule["exclude"]:
            for kw in rule["keywords"]:
                pattern = self._build_pattern(kw["text"], kw["is_chinese"])
                if pattern.search(text):
                    return False
            return True

        # process the inclusion rule
        if rule["logical_or"]:
            for kw in rule["keywords"]:
                pattern = self._build_pattern(kw["text"], kw["is_chinese"])
                if len(pattern.findall(text)) >= rule["min_count"]:
                    return True
            return False
        else:
            for kw in rule["keywords"]:
                pattern = self._build_pattern(kw["text"], kw["is_chinese"])
                if len(pattern.findall(text)) < rule["min_count"]:
                    return False
            return True


if __name__ == "__main__":
    # initialize the validator
    validator = Content_Keywords()

    # test cases
    test_cases = [
        ("The answer must include the keyword 'Mulan'.", "hihi Mulan", True),
        ("The answer must include the keyword 'Mulan'.", "hihi MULAN", True),
        ("The answer must include the keyword 'Mulan'.", "hihi mulan", True),
        ("The answer must include the keyword 'Mulan'.", "hihi MluAN", False),
        ("The answer must include the keyword 'Mulan'.", "hihi", False),
        ("Must include the keywords 'trophy', 'achievement', and 'Dead Island 2'",
         "Dead Island 2 is a game with a trophy and achievement.", True),
        ("Must include the keywords 'trophy', 'achievement', and 'Dead Island 2'",
         "Dead Island 2 is a game with achievement", False),
        ("Must include the term 'matrilineal descent'",
         "Matrilineal descent is a term", True),
        ("Must include the term 'matrilineal descent'",
         "Matrili descent is a term", False),
        ("Must include the terms 'cooling capacity' and 'energy efficiency ratio'",
         "Cooling capacity and energy efficiency ratio are terms", True),
        ("Must include the terms 'cooling capacity' and 'energy efficiency ratio'",
         "Cooling and energy efficiency ratio are terms", False),


        # self-test
        ("The quote must include the keyword 'freedom'", "Freedom is XZXXX .", True),
        ("The quote must include the keyword 'freedom'",
         "FreSSedom is freEedom.", False),


        ('"Additionally, the answer must include the keyword \'post-apocalyptic\' to ensure relevance to the theme of the movie"',
         "post-apocalyptic is a keyword", True),
        ('"Additionally, the answer must include the keyword \'post-apocalyptic\' to ensure relevance to the theme of the movie"',
         "Security Wendys is a keyword", False),

        ("The word 'data' must be included in the answer.", "Data is a keyword", True),
        ("The word 'data' must be included in the answer.",
         "Date is not a keyword", False),
        ("\"Must include the keywords 'Likert scale', 'graph', and 'data analysis'\"",
         "Likert scale Graphs are used to visualize data analysis.", False),
        ("\"Must include the keywords 'Likert scale', 'graph', and 'data analysis'\"",
         "Likert scale Graph are used to visualize data analysis.", True),
        ('"""Must include the keyword \'psychosis\'."""', 'this is a psychosis', True),
        ('"""Must include the keyword \'psychosis\'."""', 'this is a abc', False),
        # other languages
        ("Must include the Japanese word '食べます'", "I eat 食べます.", True),
        ("Must include the Japanese word '食べます'", "I eat 食べま", False),
        # avoid and include
        ("Ensure the edited statement includes the keyword 'Natwest' and avoids the keyword 'dormant'.",
         "Natwest is a dormant keywo", False),
        ("Ensure the edited statement includes the keyword 'Natwest' and avoids the keyword 'dormant'.",
         "Natwest is a keywo", True),

        ("the keyword 'explosive' must be avoided in the answer",
         "explosive is a keyword", False),
        ("the keyword 'explosive' must be avoided in the answer",
         "explosieee is a keyword.", True),
        # both appear
        ("If discussing Iranian culture, the summary must include the keyword 'tradition'. If discussing California housing/property laws, the summary must include the keyword 'regulation'.", "Iranian culture is tradition", True),
        ("If discussing Iranian culture, the summary must include the keyword 'tradition'. If discussing California housing/property laws, the summary must include the keyword 'regulation'.",
         "California housing laws is tradition", False),
        # end with a period
        ("Furthermore, every item must include the keyword 'heel pain' and must end with a period, ensuring consistency and focus on the topic.",
         "Heel pain is a keyword.", True),
        ("Furthermore, every item must include the keyword 'heel pain' and must end with a period, ensuring consistency and focus on the topic.",
         "Heel pain is a keyword", False),
        # capitalize
        ("The answer must use capitalized letters for each word and must include the keyword 'beasts'.",
         "Beasts Are Great", True),
        ("The answer must use capitalized letters for each word and must include the keyword 'beasts'.",
         "Beasts are great", False),

        ("The description in the table must use capitalized letters for each word, be at least 5 words long, and include the keyword 'gas giant'.",
         "Gas Giant Is A Large Planet", True),
        # capitalize + keyword + word count
        ("The description in the table must use capitalized letters for each word, be at least 5 words long, and include the keyword 'gas giant'.",
         "Gas Giant Is A", False),
        # not capitalize
        ("The description in the table must use capitalized letters for each word, be at least 5 words long, and include the keyword 'gas giant'.",
         "Gas giant is a large planet", False),

        ("ensure that the word 'Friend' is included, and the translation does not exceed three words",
         "Friend is like my family", False),
        ("ensure that the word 'Friend' is included, and the translation does not exceed three words",
         "Friend is family", True),

        ("the response is a single word that includes the keyword 'five'", "five", True),
        ("the response is a single word that includes the keyword 'five'",
         "five words", False),

        ("The names \"\"LSU\"\" and \"\"Zach Wilson\"\" must appear multiple times in the text",
         "LSU and Zach Wilson are both key players", False),

        ("The names \"\"LSU\"\" and \"\"Zach Wilson\"\" must appear multiple times in the text",
         "LSU and Zach Wilson are both key players,especially LSU", False),
        ("The names \"\"LSU\"\" and \"\"Zach Wilson\"\" must appear multiple times in the text",
         "LSU and Zach Wilson are both key players,and LSU learn a lot from Zach Wilson", True),

        # English full word matching
        ("Must include 'key'", "The keyword is key", True),
        ("Must include 'key'", "These are keys", False),

        # Chinese full word matching
        ("必须包含'小明'", "今天小明上学了", True),
        ("必须包含'小明'", "小明的朋友来了", True),

        # exclude constraint
        ("Avoid using term 'slur'", "This is normal text", True),
        ("Avoid using term 'slur'", "Contains slur word", False),

        # combination logic
        ("Must include 'apple' or 'orange'", "I like banana.", False),
        ("Must include 'apple' or 'orange'", "I like apple.", True),
        ("Must include 'apple' and 'orange'", "We have apple.", False),
        ("Must include 'apple' and 'orange'", "We have apple and banana.", False),
        ("Must include 'apple' and 'orange'", "We have apple and orange.", True),


        # test word count
        ("Must include 'test' at least three times", "test test test", True),
        ("Must include 'test' at least three times", "test test", False),
        ("Must include 'demo' at least five times",
         "demo demo demo demo demo", True),
        ("Must include 'demo' at least twice", "demo demo", True),

        # test logic or case
        ("Must include 'apple' OR 'orange'", "I like orange", True),
        ("Must include 'apple' OR 'orange'", "I like banana", False),
        ("Must include 'cat' Or 'dog'", "A dog is here", True),
        ("Must include 'cat' Or 'dog'", "No animals", False),

        # mixed test
        ("Must include 'foo' OR 'bar' at least two times", "foo bar foo", True),
        ("Avoid using term 'error'", "This is correct", True),


        # self-test
        ("Must include the keyword 'Wendy'.", "Security Wendy is a keyword", True),
        ("Must include the keyword 'Wendy'.",
         "Security Wendys is a keyword", False),
        ("Must include the keyword \"Wendy\".",
         "Security Wendy is a keyword", True),
        ("Must include the keyword \"Wendy\".",
         "Security Wendys is a keyword", False),
        ("\"The answer must include the keywords 'offseason', 'English football', and 'schedule'.\"",
         "The answer is English football and schedule.", False),
        ("\"The answer must include the keywords \"offseason\", 'English football', and'schedule'.\"",
         "The answer is offseason English football and schedule.", True),
        ("The training examples must include the keyword 'dependent' to highlight the nature of follow-up questions.",
         "Follow-up questions are Dependent on the training examples.", True),
        ("The training examples must include the keyword 'dependent' to highlight the nature of follow-up questions.",
         "Follow-up questions are Dapendent on the training examples.", False),
        (r"""The answer must include the keyword 'iPhone 15'""",
         "The answer is iPhone 15.", True),
        (r"""The answer must include the keyword 'iPhone 15'""",
         "The answer is iPhone 12.", False),
        ('"The answer must include the keyword ""AI""."', "The answer is AI.", True),
        ('"The answer must include the keyword ""AI""."', "The answer is AII.", False),

        ("The answer must include the keyword 'Cleopatra' at least twice.",
         "Cleopatra is a famous figure.", False),
        ("The answer must include the keyword 'Cleopatra' at least twice.",
         "Cleopatra is a famous figure. Cleopatra is a famous figure.", True),
        ("The answer must include the keyword 'Cleopatra' at least twice.",
         "Cleopatra and Cleopatra", True),

        # other extreme cases
        ("Must include 'C++' at least three times", "C++ C++ C++", True),
        ("Must include 'C++' at least 3 times", "C++ C++ C++", True),
        ("Must include 'C++' at least three times", "C++", False),
        ("Must include 'C++' at least 3 times", "C++", False),

        ("Must include the keyword \"\"Wendy's\"\"", "Wendy's is a keyword", True),
        ("Must include the keyword \"\"Wendy's\"\"", "Wendy is a keyword", False),

        # csv
        ("\"Additionally, the answer must include the keywords 'Diddy', 'Usher', and 'Lawsuit'.\"",
         "'Diddy', 'Usher', and 'Lawsuit'", True),
        ("\"Additionally, the answer must include the keywords 'Diddy', 'Usher', and 'Lawsuit'.\"",
         "'Diddy', 'sher', and 'Lawsuit'", False),
        ("The answer must include the keyword 'Windows 10 features'",
         "Windows 10 features", True),
        ("The answer must include the keyword 'Windows 10 features'",
         "Windows10 features", False),
        ("\"ответ должен включать ключевое слово 'Present Simple', что означает, что это ключевое слово должно быть использовано в ответе\"",
         "ово 'Present Simple', что ", True),
        ("\"ответ должен включать ключевое слово 'Present Simple', что означает, что это ключевое слово должно быть использовано в ответе\"",
         "ово 'Presnt Simple', что ", False),
        ("該句必須包含關鍵詞「代表」", "「代表」", True),
        ("該句必須包含關鍵詞「代表」", "「liu表」", False),

        # each
        ("Each day's description in the workout plan must include the keyword 'upper body'.",
            """Here is a 3-day upper body workout plan presented in a table format:

    | Day | Workout Plan                                                                 |
    |-----|-----------------------------------------------------------------------------|
    | 1   | Focus on upper body strength. PERFORM BENCH PRESS AND OVERHEAD PRESS. Upper body endurance improves with consistency. Push-ups are essential. |
    | 2   | Build upper body muscles. INCLUDE PULL-UPS AND BARBELL ROWS. Upper body definition requires targeted exercises. Dumbbell curls help too. |
    | 3   | Enhance upper body power. ADD INCLINE BENCH PRESS AND SHOULDER FLY. Upper body workouts should vary daily. Finish strong today. |""",
            True
         ),
        ("Each day's description in the workout plan must include the keyword 'upper body'.",
            """Here is a 3-day upper body workout plan presented in a table format:

    | Day | Workout Plan                                                                 |
    |-----|-----------------------------------------------------------------------------|
    | 1   | Focus on uper body strength. PERFORM BENCH PRESS AND OVERHEAD PRESS. pper body endurance improves with consistency. Push-ups are essential. |
    | 2   | Build uppe body muscles. INCLUDE PULL-UPS AND BARBELL ROWS. Uppe body definition requires targeted exercises. Dumbbell curls help too. |
    | 3   | Enhance upper bdy power. ADD INCLINE BENCH PRESS AND SHOULDER FLY. Uper body workouts should vary daily. Finish strong today. |""",
            False
         ),

        ("Each event description must include the keyword 'technology' or 'internet'",
            "1. Facebook Acquired WhatsApp For $19 Billion, Revolutionizing Internet Communication.\n2. Apple Released iPhone 6, Advancing Mobile Technology Worldwide.\n3. Google Announced Android Lollipop, Enhancing Internet User Experience.\n4. Alibaba's IPO Became Largest In Technology History.\n5. Microsoft Acquired Minecraft, Expanding Its Technology Portfolio.\n6. Amazon Launched Echo, Introducing Voice Technology To Homes.\n7. Sony's PlayStation 4 Dominated The Gaming Technology Market.\n8. Uber Expanded Globally, Transforming Internet-Based Transportation.\n9. Tesla Unveiled Autopilot, Innovating Automotive Technology.\n10. Net Neutrality Debated Intensely, Impacting Internet Policies.\n11. Heartbleed Bug Exposed Internet Security Vulnerabilities.\n12. Apple Introduced Apple Pay, Advancing Mobile Payment Technology.\n13. Google Glass Discontinued, Reflecting Wearable Technology Challenges.\n14. Facebook Launched Oculus Rift, Pioneering Virtual Reality Technology.\n15. Twitter's User Growth Stagnated, Affecting Internet Influence.\n16. Samsung Released Gear VR, Entering Virtual Reality Technology.\n17. Snapchat Introduced Stories, Changing Internet Social Media Dynamics.\n18. Microsoft Launched Windows 10, Unifying Technology Platforms.\n19. Netflix Expanded Internationally, Revolutionizing Internet Streaming.\n20. Yahoo Acquired Tumblr, Enhancing Its Internet Presence.",
            True
         ),
        ("Each new episode title must include the keyword 'Scooby'",
            """Here is the table with the new Scooby-Doo episode titles formatted according to your requirements:

    | Original Title                  | New Episode Title                                                                 |
    |---------------------------------|----------------------------------------------------------------------------------|
    | The Ghost of the Red Baron      | #### Scooby Faces Red Baron Ghost.                                              |
    | The Ghost of Bigfoot            | #### Scooby Meets Bigfoot Spirit.                                               |
    | The Ghost of the Bad Humor Man  | #### Scooby Encounters Grumpy Ghost.                                            |

    Each title has each word capitalized, includes the keyword "Scooby," does not exceed six words, and is formatted as a level 2 heading in Markdown.""",
            True
         ),
        ("Each new episode title must include the keyword 'Scooby'",
            """Here is the table with the new Scooby-Doo episode titles formatted according to your requirements:

    | Original Title                  | New Episode Title                                                                 |
    |---------------------------------|----------------------------------------------------------------------------------|
    | The Ghost of the Red Baron      | #### Scooy Faces Red Baron Ghost.                                              |
    | The Ghost of Bigfoot            | #### Scooby Meets Bigfoot Spirit.                                               |
    | The Ghost of the Bad Humor Man  | #### Scooby Encounters Grumpy Ghost.                                            |

    Each title has each word capitalized, includes the keyword "Scooby," does not exceed six words, and is formatted as a level 2 heading in Markdown.""",
            False
         ),
        ("Each expression must include the keyword 'strategy'",
            """| Expression               | Explanation/Synonym                          |
    |--------------------------|----------------------------------------------|
    | Marketing Strategy       | STRATEGY TO PROMOTE PRODUCTS.                |
    | Business Strategy        | STRATEGY FOR COMPANY SUCCESS.                |
    | Growth Strategy          | STRATEGY TO EXPAND BUSINESS.                 |
    | Pricing Strategy         | STRATEGY FOR SETTING PRODUCT PRICES.         |
    | Content Strategy         | STRATEGY FOR CREATING DIGITAL CONTENT.       |
    | Branding Strategy        | STRATEGY TO BUILD BRAND IDENTITY.            |
    | Product Strategy         | STRATEGY FOR DEVELOPING NEW PRODUCTS.        |
    | Digital Strategy         | STRATEGY FOR ONLINE BUSINESS ACTIVITIES.     |
    | Customer Strategy        | STRATEGY TO ENGAGE AND RETAIN CUSTOMERS.     |
    | Competitive Strategy     | STRATEGY TO OUTPERFORM COMPETITORS.          |""",
            True
         ),
        ("Each expression must include the keyword 'strategy'",
            """| Expression               | Explanation/Synonym                          |
    |--------------------------|----------------------------------------------|
    | Marketing Strategy       | STRATEGY TO PROMOTE PRODUCTS.                |
    | Business Strategy        | STRATEGY FOR COMPANY SUCCESS.                |
    | Growth Strategy          | STRATEGY TO EXPAND BUSINESS.                 |
    | Pricing Strategy         | STRATEGY FOR SETTING PRODUCT PRICES.         |
    | Content Strategy         | STRATEGY FOR CREATING DIGITAL CONTENT.       |
    | Branding Strategy        | STRATEGY TO BUILD BRAND IDENTITY.            |
    | Product Stratey         | STRATEGY FOR DEVELOPING NEW PRODUCTS.        |
    | Digital Strategy         | STRATEGY FOR ONLINE BUSINESS ACTIVITIES.     |
    | Customer Strategy        | STRATEGY TO ENGAGE AND RETAIN CUSTOMERS.     |
    | Competitive Strategy     | STRATEGY TO OUTPERFORM COMPETITORS.          |""",
            False
         ),
        ("Each justification must include the keyword 'faction'",
            """Below is the table assessing the level of interest among native speakers of specified languages in various medieval factions on a 100-point scale, following the provided rules:

    | Language       | Medieval Faction         | Interest Score | Justification                                                                 |
    |----------------|--------------------------|----------------|-------------------------------------------------------------------------------|
    | English        | KNIGHTS TEMPLAR          | 95             | MANY ENGLISH SPEAKERS ARE FASCINATED BY THIS FACTION'S MYSTERIOUS HISTORY AND RELIGIOUS SIGNIFICANCE. |
    | Spanish        | VIKINGS                  | 88             | SPANISH SPEAKERS ADMIRE THE VIKINGS' BOLD EXPEDITIONS AND WARRIOR FACTION CULTURE. |
    | French         | BURGUNDY FACTION         | 82             | FRENCH SPEAKERS RELATE TO THIS FACTION AS IT ORIGINATES FROM THEIR REGIONAL HISTORY. |
    | German         | HOLY ROMAN EMPIRE        | 90             | GERMAN NATIVE SPEAKERS FEEL A STRONG CONNECTION TO THIS FACTION'S IMPACT ON EUROPEAN HISTORY. |
    | Italian        | BYZANTINE EMPIRE         | 86             | ITALIAN SPEAKERS APPRECIATE THE ARTISTIC AND POLITICAL INFLUENCE OF THIS FACTION. |
    | Portuguese     | MOORS                    | 84             | PORTUGUESE SPEAKERS ARE INTERESTED IN THE MOORS' FACTION FOR ITS ROLE IN IBERIAN HISTORY. |
    | Russian        | KIEVAN RUS'              | 92             | RUSSIAN SPEAKERS VIEW THIS FACTION AS A FOUNDATION OF THEIR CULTURAL HERITAGE. |
    | Arabic         | CRUSADE FACTION          | 78             | ARABIC SPEAKERS STUDY THIS FACTION DUE TO ITS HISTORICAL CONFLICT WITH THEIR REGIONS. |
    | Chinese        | MONGOL HORDES            | 80             | CHINESE SPEAKERS ARE CURIOUS ABOUT THIS FACTION'S IMPACT ON ASIA'S HISTORY. |
    | Japanese       | KNIGHTS TEUTONIC         | 75             | JAPANESE SPEAKERS FIND THIS FACTION INTERESTING FOR ITS DISTINCT MILITARY ORDER. |""",
            True
         ),
        ("Each justification must include the keyword 'faction'",
            """Below is the table assessing the level of interest among native speakers of specified languages in various medieval factions on a 100-point scale, following the provided rules:

    | Language       | Medieval Faction         | Interest Score | Justification                                                                 |
    |----------------|--------------------------|----------------|-------------------------------------------------------------------------------|
    | English        | KNIGHTS TEMPLAR          | 95             | MANY ENGLISH SPEAKERS ARE FASCINATED BY THIS FACTION'S MYSTERIOUS HISTORY AND RELIGIOUS SIGNIFICANCE. |
    | Spanish        | VIKINGS                  | 88             | SPANISH SPEAKERS ADMIRE THE VIKINGS' BOLD EXPEDITIONS AND WARRIOR FACTION CULTURE. |
    | French         | BURGUNDY FACTION         | 82             | FRENCH SPEAKERS RELATE TO THIS FACTION AS IT ORIGINATES FROM THEIR REGIONAL HISTORY. |
    | German         | HOLY ROMAN EMPIRE        | 90             | GERMAN NATIVE SPEAKERS FEEL A STRONG CONNECTION TO THIS FACTION'S IMPACT ON EUROPEAN HISTORY. |
    | Italian        | BYZANTINE EMPIRE         | 86             | ITALIAN SPEAKERS APPRECIATE THE ARTISTIC AND POLITICAL INFLUENCE OF THIS FACTION. |
    | Portuguese     | MOORS                    | 84             | PORTUGUESE SPEAKERS ARE INTERESTED IN THE MOORS' FACTION FOR ITS ROLE IN IBERIAN HISTORY. |
    | Russian        | KIEVAN RUS'              | 92             | RUSSIAN SPEAKERS VIEW THIS FACTION AS A FOUNDATION OF THEIR CULTURAL HERITAGE. |
    | Arabic         | CRUSADE FACTION          | 78             | ARABIC SPEAKERS STUDY THIS FACION DUE TO ITS HISTORICAL CONFLICT WITH THEIR REGIONS. |
    | Chinese        | MONGOL HORDES            | 80             | CHINESE SPEAKERS ARE CURIOUS ABOUT THIS FACTION'S IMPACT ON ASIA'S HISTORY. |
    | Japanese       | KNIGHTS TEUTONIC         | 75             | JAPANESE SPEAKERS FIND THIS FACTION INTERESTING FOR ITS DISTINCT MILITARY ORDER. |""",
            False
         ),
        ("Each answer should explicitly incorporate the keyword 'solution'",
            """**Riddle 1 Solution:**  
    The solution lies in recognizing that children with smaller feet grow into adults with larger feet, correlating growth with education and intelligence. This riddle plays on developmental patterns.

    ---

    **Riddle 2 Solution:**  
    The solution involves sorting the list numerically: [1, 1, 2, 3, 3, 4, 5, 5, 5, 6, 9]. Sorting algorithms rearrange numbers systematically for clarity.

    ---

    **Riddle 3 Solution:**  
    The solution is "the queen." A king's throne is traditionally next to his queen's, symbolizing royal partnership. This riddle relies on historical context.

    ---

    **Riddle 4 Solution:**  
    The solution is "darkness." As darkness grows, visibility decreases because light diminishes. This riddle hinges on understanding natural phenomena.

    ---

    **Riddle 5 Solution:**  
    The solution involves starting near the North Pole or specific points around it. Walking south, east, and north creates a triangular path due to Earth's curvature.

    ---

    **Riddle 6 Solution:**  
    The solution reveals four sisters and three brothers. Each sibling count aligns when considering perspectives of girls versus boys within the family structure.

    ---

    **Riddle 7 Solution:**  
    The solution calculates remaining laps as 37 1/2 out of 50, leaving 3/4 of the race unfinished. Fractions represent portions of completed versus remaining tasks.

    ---

    **Riddle 8 Solution:**  
    The solution is "time." Time erodes mountains, causes extinction, ruins structures, and breaks objects into fragments, emphasizing its unstoppable force.

    ---

    **Riddle 9 Solution:**  
    The solution explains that the boy was born in 2005 B.C., making him younger as years decrease backward in time. This riddle plays with calendar systems.

    ---

    **Riddle 10 :**  
    The solution refers to the first riddle about foot size correlating with intelligence. It explores psychological observations and their implications in village studies.""",
            True
         ),
        ("Each answer should explicitly incorporate the keyword 'solution'",
            """**Riddle 1 Solution:**  
    The solution lies in recognizing that children with smaller feet grow into adults with larger feet, correlating growth with education and intelligence. This riddle plays on developmental patterns.

    ---

    **Riddle 2 Solution:**  
    The solution involves sorting the list numerically: [1, 1, 2, 3, 3, 4, 5, 5, 5, 6, 9]. Sorting algorithms rearrange numbers systematically for clarity.

    ---

    **Riddle 3 Solution:**  
    The solution is "the queen." A king's throne is traditionally next to his queen's, symbolizing royal partnership. This riddle relies on historical context.

    ---

    **Riddle 4 Solution:**  
    The solution is "darkness." As darkness grows, visibility decreases because light diminishes. This riddle hinges on understanding natural phenomena.

    ---

    **Riddle 5 Solution:**  
    The solution involves starting near the North Pole or specific points around it. Walking south, east, and north creates a triangular path due to Earth's curvature.

    ---

    **Riddle 6 Solution:**  
    The solution reveals four sisters and three brothers. Each sibling count aligns when considering perspectives of girls versus boys within the family structure.

    ---

    **Riddle 7 Solution:**  
    The solution calculates remaining laps as 37 1/2 out of 50, leaving 3/4 of the race unfinished. Fractions represent portions of completed versus remaining tasks.

    ---

    **Riddle 8 Solution:**  
    The solution is "time." Time erodes mountains, causes extinction, ruins structures, and breaks objects into fragments, emphasizing its unstoppable force.

    ---

    **Riddle 9 Solution:**  
    The solution explains that the boy was born in 2005 B.C., making him younger as years decrease backward in time. This riddle plays with calendar systems.

    ---

    **Riddle 10 :**  
    The soltion refers to the first riddle about foot size correlating with intelligence. It explores psychological observations and their implications in village studies.""",
            False
         ),
    ]

    # execute the test
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
