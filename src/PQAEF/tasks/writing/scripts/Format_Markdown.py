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


class Format_Markdown:
    def __init__(self):
        self.number_words = {
            "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
            "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
        }

    def check(self, constraint, text):
        # check the Markdown format of block quotes
        if 'block quotes' in constraint.lower():
            if not self._check_block_quotes(constraint, text):
                return False
        # check the bold
        if 'bold' in constraint.lower():
            if not self._check_bold(constraint, text):
                return False

        # check the bullet points
        if 'bullet points' in constraint.lower():
            if not self._check_bullet_points(constraint, text):
                return False

        rules = self._parse_constraint(constraint)
        headings = self._extract_headings(text)
        if 'each' in constraint.lower() or 'any' in constraint.lower():
            return self._check_each(rules, headings)
        else:
            return self._check_rules(rules, headings)

    def _parse_constraint(self, constraint):
        clauses = re.split(r'\b(?:,)\b', constraint, flags=re.IGNORECASE)
        rules = []
        for clause in clauses:

            # special cases
            if "include headings at two levels: main and subheadings" in constraint.lower() or "be structured with a main heading and subheadings" in constraint.lower():
                clause = clause.strip().lower().rstrip('.')
                rules.append({'type': 'required_levels', 'levels': {1, 2}})
                continue

            if constraint == "Questions must be organized under a level 2 heading.":
                clause = clause.strip().rstrip('.')
                rules.append({'type': 'must_be_questions', 'levels': {2}})
                continue
            if "include a single level 1 heading" in constraint.lower():
                rules.append(
                    {'type': 'just_xx_level_xx_heading', 'level': 1, 'count': 1})
                continue
            if "be structured using a minimum of two heading levels" in constraint.lower() or "include headings at two levels" in constraint.lower():
                rules.append({'type': 'level_count_condition',
                             'operator': 'at least', 'count': 2})
                continue

            if constraint == "format the response using Markdown, employing '##' for main points and '###' for subpoints to clearly organize the information":
                rules.append({'type': 'required_levels', 'levels': {2, 3}})
                continue
            # Match: must use heading levels N and M
            match = re.search(
                r'(?i)use heading levels (\b(?:one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b) and (\b(?:one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b)',
                clause
            )
            if match == None:
                match = re.search(
                    r'(?i)use heading levels.*?level\s*(\b(?:one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b).*?level\s*(\b(?:one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b)',
                    clause
                )
            if match:
                level1 = self._word_to_number(match.group(1))
                level2 = self._word_to_number(match.group(2))
                if level1 is not None and level2 is not None:
                    rules.append({'type': 'required_levels',
                                 'levels': {level1, level2}})
                continue
            match = re.findall(
                r"(?i)a heading level (\b(?:one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b)",
                clause,
            )
            if len(match) == 0:
                match = re.findall(
                    r"(?i)H(\d+)",
                    clause,
                )
            if len(match) == 0:
                match = re.findall(
                    r"(?i)Level (\b(?:one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b) for",
                    clause,
                )
            if match and ("must include" in clause or "should" in clause):
                levels_multiple = set()
                for m in match:
                    m1 = self._word_to_number(m)
                    levels_multiple.add(m1)
                rules.append({'type': 'required_levels',
                             'levels': levels_multiple})
                continue

            # Match: level N heading titled '...'
            if 'titled' in clause:
                clause = clause.strip().rstrip('.')
                match = re.search(
                    r'(?i)level (\b(?:one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b) heading titled ["\'](.*?)["\']',
                    clause
                )
                if match == None:
                    match = re.search(
                        r'(?i)(?:a|at least one|two|three|four|five|six|seven|eight|nine|ten|\d+) level (\b(?:one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b) heading with the text ["\'](.*?)["\']',
                        clause
                    )
                if match:
                    level = self._word_to_number(match.group(1))
                    content = match.group(2)
                    if level is not None:
                        rules.append({'type': 'exact_heading',
                                     'level': level, 'content': content})
                    continue

            # do not consider the content case
            clause = clause.strip().lower().rstrip('.')

            if re.search(r'include|includes|included|including|use|using|used|uses|formatted|presented|organized|structured|feature|should be|incorporate', clause, re.I):
                match = re.search(
                    r'(?i)(?:a|at least \d+) heading level (\b(?:one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b)',
                    clause
                )
                if match == None:
                    match = re.search(
                        r'(?i)(?:a|at least one|two|three|four|five|six|seven|eight|nine|ten|\d+) level (\b(?:one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b) heading',
                        clause
                    )
                if match == None:
                    match = re.search(
                        r'(?i)must use a heading level of H(\d+)',
                        clause
                    )
                if match:
                    level = self._word_to_number(match.group(1))
                    if level is not None:
                        rules.append({'type': 'min_level_count',
                                     'level': level, 'min': 1})
                    continue

            if re.search(r'include|includes|included|including|use|using|used|uses|formatted|presented|organized|structured|feature|should be|incorporate', clause, re.I):
                # Match: must use (at least/at most/exactly) N heading levels
                match = re.search(
                    r'(?i)(at least|at most|exactly|up to|a maximum of|under) (\b(?:one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b) heading levels?',
                    clause
                )
                if match == None:
                    match = re.search(
                        r'(?i)(at least|at most|exactly|up to|a maximum of|under) (\b(?:one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b) levels?',
                        clause
                    )
                if match:
                    op = match.group(1).lower()
                    if op == 'up to':
                        op = 'at most'
                    elif op == 'a maximum of':
                        op = 'at most'
                    elif op == 'under':
                        op = 'at most'
                    count = self._word_to_number(match.group(2))
                    if count is not None:
                        rules.append(
                            {'type': 'level_count_condition', 'operator': op, 'count': count})
                    continue

            # Match: heading levels must be limited to N
            match = re.search(
                r'(?i)(?:heading levels)? must (?:not exceed|be limited to)\s+(?:level\s+)?(\b(?:one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b)',
                clause
            )
            if match:
                max_level = self._word_to_number(match.group(1))
                if max_level is not None:
                    rules.append({'type': 'max_level', 'max_level': max_level})
                continue

            # Match: must begin with level N
            match = re.search(
                r'(?i)must begin with a level (\b(?:one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b) heading',
                clause
            )
            if match:
                level = self._word_to_number(match.group(1))
                if level is not None:
                    rules.append({'type': 'starts_with_level', 'level': level})
                continue

            # Use heading level 2 in Markdown format
            match = re.search(
                r'(?i)use heading level (\b(?:one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b)', clause)
            if match:
                wanted_level = self._word_to_number(match.group(1))
                if wanted_level is not None:
                    rules.append({'type': 'min_level_count',
                                 'level': wanted_level, 'min': 1})
                continue

            if "include headings" in constraint.lower() or "includes headings" in constraint.lower() or "use heading levels" in constraint.lower() or "using heading levels" in constraint.lower() or "presented under a separate heading" in constraint.lower() or "separated with headings" in constraint.lower() or "with headings" in constraint.lower():
                rules.append({'type': 'min_level_count',
                             'level': 'any_level', 'min': 1})
                continue

        return rules

    def _word_to_number(self, word_str):
        word = word_str.strip().lower()
        if word.isdigit():
            return int(word)
        return self.number_words.get(word, None)

    def _extract_headings(self, text):
        headings = []
        for line in text.split('\n'):
            line = line.strip()
            match = re.match(r'^(#+)\s+(.*?)\s*$', line)
            if match:
                level = len(match.group(1))
                content = match.group(2).strip()
                headings.append({'level': level, 'content': content})
        return headings

    def _check_rules(self, rules, headings):
        for rule in rules:
            if not self._check_rule(rule, headings):
                return False
        return True

    def _check_rule(self, rule, headings):
        if rule['type'] == 'min_level_count':
            if not headings:
                return False
            count = sum(1 for h in headings if (h['level'] == rule['level'] or (
                rule['level'] == 'any_level' and h['level'] > 0)))
            return count >= rule.get('min', 1)
        elif rule['type'] == 'exact_heading':
            if not headings:
                return False
            return any(h['level'] == rule['level'] and h['content'] == rule['content'] for h in headings)
        elif rule['type'] == 'level_count_condition':
            levels = {h['level'] for h in headings if h}
            actual = len(levels)

            op = rule['operator']
            req = rule['count']
            if op == 'at least':
                return actual >= req
            elif op == 'at most':
                return actual <= req
            elif op == 'exactly':
                return actual == req
            return False
        elif rule['type'] == 'max_level':
            if not headings:
                return False
            return all(h['level'] <= rule['max_level'] for h in headings) if headings else True
        elif rule['type'] == 'starts_with_level':
            if not headings:
                return False
            return headings[0]['level'] == rule['level'] if headings else False
        elif rule['type'] == 'required_levels':
            if not headings:
                return False
            existing = {h['level'] for h in headings}
            return rule['levels'].issubset(existing)
        elif rule['type'] == 'must_be_questions':
            if not headings:
                return False
            # 检查含？的标题是否都是level 2
            return all(h['level'] in rule['levels'] for h in headings if '?' in h['content'])
        elif rule['type'] == 'just_xx_level_xx_heading':
            if not headings:
                return False
            count_in_headings = 0
            for h in headings:
                if h['level'] == rule['level']:
                    count_in_headings += 1
            return count_in_headings == rule['count']

        return False

    def _check_each(self, rules, headings):
        if not headings:
            return False
        for h in headings:
            each_result = self._check_rules(rules, [h])
            if not each_result:
                return False
        return True

    def _check_block_quotes(self, constraint, text):
        # ensure each quote starts with `>`
        lines = text.split('\n')
        total_lines = 0
        quoted_lines = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue
            total_lines += 1
            if line.strip().startswith('>'):
                quoted_lines += 1

        if "at least" in constraint.lower():
            match = re.search(
                r'(?i)(\b(?:one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b) block quotes',
                constraint
            )
            required_quotes = self._word_to_number(match.group(1))
            if quoted_lines < required_quotes:
                return False
        elif "use block quotes" in constraint.lower() or "using block quotes" in constraint.lower() or "include a block quote" in constraint.lower() or "using markdown block quotes" in constraint.lower() or "employ block quotes" in constraint.lower() or "present the headline as a block quote" in constraint.lower():
            if quoted_lines == 0:
                return False
        else:
            if quoted_lines != len(lines):
                return False
        return True

    def _check_bold(self, constraint, text):
        # regex match the bold text wrapped by `**` or `__`
        pattern = r'(\*\*.*?\*\*|__.*?__)'

        # use re.search to find if there is any bold text
        if re.search(pattern, text):
            return True
        return False

    def _check_bullet_points(self, constraint, text):
        # regex match the bullet points (start with -, *, +, followed by a space)
        pattern = r'^\s*[-\*\+]\s'

        # split the text by line and check if each line matches the pattern
        lines = text.split('\n')
        for line in lines:
            if re.search(pattern, line):
                return True
        return False


if __name__ == "__main__":
    # test cases
    test_cases = [

        ("Use heading levels to organize the answer", "## hi", True),
        ("Use heading levels to organize the answer", "hi", False),
        ("Use heading level 2 in Markdown format", "## hi", True),
        ("Use heading level 2 in Markdown format", "### hi", False),
        ("The essay must include at least three heading levels: H1 for the main title, H2 for major sections, and H3 for subsections.",
         "# Main Title\n## Major Section\n#### Wrong", False),
        ("The answer must use heading levels, with the main title as a level 1 heading and subtopics as level 2 headings.",
         "# Main Title\n## Subtopic 1\n## Subtopic 2", True),
        ("The answer must use heading levels, with the main title as a level 1 heading and subtopics as level 2 headings.",
         "# Main Title\n# Subtopic 1\n# Subtopic 2", False),
        ("must use a heading level of H2", "## hi", True),
        ("must use a heading level of H2", "### hi", False),
        # bullet point
        ("Format your response using markdown, ensuring the use of headings, subheadings, bullet points, and bold to organize the information. Your response must include at least three heading levels: H1, H2, and H3",
         "# hi \n ## hi \n ### hi\n - hi\n **hi**", True),
        ("Format your response using markdown, ensuring the use of headings, subheadings, bullet points, and bold to organize the information. Your response must include at least three heading levels: H1, H2, and H3",
         "# hi \n ## hi \n ### hi\n - hi\n hi", False),
        ("Format your response using markdown, ensuring the use of headings, subheadings, bullet points, and bold to organize the information. Your response must include at least three heading levels: H1, H2, and H3",
         "# hi \n ## hi \n ### hi\n  hi\n **hi**", False),
        ("Format your response using markdown, ensuring the use of headings, subheadings, bullet points, and bold to organize the information. Your response must include at least three heading levels: H1, H2, and H3", "# hi \n \n ### hi\n  hi\n **hi**", False),
        ("The answer must use heading levels to organize the information, with at least two levels: one for main topics and one for subtopics", "## hi \n ### hi \n", True),
        ("The answer must use heading levels to organize the information, with at least two levels: one for main topics and one for subtopics", "## hi \n ## hi \n", False),

        # self-test
        ("The answer must include a heading level 2 for the definition and a heading level 3 for the symbol.",
         "## Definition\n### Symbol", True),
        ("The answer must include a heading level 2 for the definition and a heading level 3 for the symbol.",
         "## Definition", False),
        ("The answer must include a heading level 2 for the definition and a heading level 3 for the symbol.", "### Symbol", False),
        ("The answer must include a heading level 2 for the definition and a heading level 3 for the symbol.",
         "## Definition\n### Symbol\n### Symbol", True),
        ("Include a level 1 heading with the text 'Invoice Details'",
         "# Invoice Details \n ## Hi", True),
        ("The corrected email must include a level 1 heading with the text 'Invoice Details'",
         "## Invoice Details", False),
        ("The explanation must use Markdown with at least two heading levels, such as '## Introduction' and '### Details'.",
         "## Introtion \n ### tails", True),
        ("The explanation must use Markdown with at least two heading levels, such as '## Introduction' and '### Details'.",
         "## Introduction \n ", False),
        ("The response should also feature a level 2 heading in Markdown format to organize the content effectively",
         "## Introduction", True),
        ("The response should also feature a level 2 heading in Markdown format to organize the content effectively",
         "# Introduction", False),
        ("The response should also feature a level 2 heading in Markdown format to organize the content effectively",
         "### HI \n ## Introduction", True),
        ("The answer must include a heading level 2 for the main title and a heading level 3 for subtopics",
         "## Main Title\n### Subtopic 1\n### Subtopic 2\n### Subtopic 3", True),
        ("The answer must include a heading level 2 for the main title and a heading level 3 for subtopics",
         "## Main Title\n", False),
        ("The explanation must be structured using a minimum of two heading levels for clarity",
         "# hi \n ## hi \n", True),
        ("The explanation must be structured using a minimum of two heading levels for clarity", "# hi", False),
        ("The explanation should be organized using at least two heading levels in Markdown",
         "# hi \n ## hi \n", True),
        ("The explanation should be organized using at least two heading levels in Markdown", "# hi ", False),
        ("The index should utilize three heading levels: Level 1 for main topics, Level 2 for subtopics, and Level 3 for detailed points.",
         "# hi \n ## hi \n ### hi \n", True),
        ("The index should utilize three heading levels: Level 1 for main topics, Level 2 for subtopics, and Level 3 for detailed points.", "## hi \n ### hi \n", False),
        ("The index should utilize three heading levels: Level 1 for main topics, Level 2 for subtopics, and Level 3 for detailed points.", "", False),
        ("The response must include headings at two levels: one for the main sections and one for subsections",
         "## Main Section\n### Subsection\n#### Sub-subsection", True),
        ("The response must include headings at two levels: one for the main sections and one for subsections",
         "## Main Section\n", False),
        ("ensuring that the information is organized with clarity and structure by using at least two heading levels",
         "## Main Section\n### Subsection\n#### Sub-subsection", True),
        ("ensuring that the information is organized with clarity and structure by using at least two heading levels",
         "## Main Section\n", False),




        (
            "\"Heading levels: The response must include at least two heading levels, such as '## Overview' and '### Steps'\"",
            "# Title\n## Section\n### Subsection",
            True

        ),
        # must include specific heading level combination (digital form)
        (
            "The answer must use heading levels 1 and 2",
            "# Title\n## Section",
            True
        ),
        (
            "The answer must use heading levels 1 and 2",
            "## Section\n### Subsection",
            False
        ),
        # must include multiple specific titles
        (
            "Must include headings for different sections such as 'Introduction', 'Body', 'Conclusion'",
            "## Introduction\n## Body\n## Conclusion",
            True
        ),
        ("If you use headings, the answer must include headings at two levels: main and subheadings",
         "# Main Heading\n## Subheading", True),
        ("If you use headings, the answer must include headings at two levels: main and subheadings",
         "# Main Heading\n### Subheading", False),
        ("The answer must be formatted as a level 2 heading in Markdown",
         "### Mutiple", False),
        ("The answer must be formatted as a level 2 heading in Markdown", "## Mutiple", True),
        ("The answer must include a level 2 heading titled \"Research Questions\"",
         "## Research Questions", True),
        ("The answer must include a level 2 heading titled \"Research Questions\"",
         "# Research Questions", False),
        ("The answer must include a level 2 heading titled \"Research Questions\"",
         "## Research", False),
        ("The answer must include at least two heading levels if using Markdown",
         "## Research Questions\n### What is the problem?", True),
        ("The answer must include at least two heading levels if using Markdown",
         "## Research Questions", False),
        ("The answer must include headings for each section, such as 'Introduction', 'Examples', and 'Explanation'.",
         "## Introduction\n## Examples\n## Explanation", True),
        ("The answer must include headings for each section, such as 'Introduction', 'Examples', and 'Explanation'.",
         "Introduction\nExamples", False),
        ("The answer must include at least one level 2 heading.",
         "## Research Questions", True),
        ("The answer must include at least one level 2 heading.",
         "## Research Questions\n## Research Questionsss", True),
        ("The answer must include at least one level 2 heading.",
         "# Research Questions", False),



        # must include level two heading (digital form)
        (
            "Must include a heading level 2",
            "## Overview\nContent here",
            True
        ),
        (
            "Must include a heading level 2",
            "# Title\n### Subtitle",
            False
        ),
        # must include level two heading (English form)
        (
            "Must include a heading level two",
            "## Overview",
            True
        ),
        (
            "Must include a heading level two",
            "# Title\n### Subtitle",
            False
        ),
        # must include specific title content
        (
            "Must include a level 2 heading titled 'Overview'",
            "## Overview",
            True
        ),
        (
            "Must include a level 2 heading titled 'Overview'",
            "## Introduction",
            False
        ),
        # must use at least two heading levels (digital form)
        (
            "Must use at least two heading levels",
            "## Title\n### Subtitle",
            True
        ),
        (
            "Must use at least two heading levels",
            "## Title\n## Another Title",
            False
        ),
        # must use at least two heading levels (English form)
        (
            "Must use at least two heading levels",
            "# Title\n## Section",
            True
        ),
        (
            "Must use at least two heading levels",
            "### Title\n### Section",
            False
        ),
        # maximum heading level is 3 (digital form)
        (
            "Heading levels must be limited to three",
            "### Subtitle",
            True
        ),
        (
            "Heading levels must be limited to three",
            "#### Subtitle",
            False
        ),
        # maximum heading level is 3 (English form)
        (
            "Heading levels must be limited to three",
            "### Subtitle",
            True
        ),
        (
            "Heading levels must be limited to three",
            "#### Subtitle",
            False
        ),
        # must begin with level two heading (digital form)
        (
            "The answer must begin with a level 2 heading",
            "## First Section\n# Title",
            True
        ),
        (
            "The answer must begin with a level 2 heading",
            "# Title\n## Section",
            False
        ),
        # must begin with level two heading (English form)
        (
            "The answer must begin with a level two heading",
            "## First Section",
            True
        ),
        (
            "The answer must begin with a level two heading",
            "# Title\n## Section",
            False
        ),
        # must include multiple specific titles
        (
            "Must include headings for different sections such as 'Introduction', 'Body', 'Conclusion'",
            "## Introduction\n## Body\n## Conclusion",
            True
        ),
        # must include specific heading level combination (digital form)
        (
            "The answer must use heading levels 1 and 2",
            "# Title\n## Section",
            True
        ),
        (
            "The answer must use heading levels 1 and 2",
            "## Section\n### Subsection",
            False
        ),
        # must include specific heading level combination (English form)
        (
            "The answer must use heading levels one and two",
            "# Title\n## Section",
            True
        ),
        (
            "The answer must use heading levels one and two",
            "## Section\n### Subsection",
            False
        ),
        # exact number constraint (English form)
        (
            "Must use exactly three heading levels",
            "# A\n## B\n### C",
            True
        ),
        (
            "Must use exactly three heading levels",
            "# A\n## B",
            False
        ),
        # start with level one heading (English form)
        (
            "The answer must begin with a level one heading",
            "# Title",
            True
        ),
        (
            "The answer must begin with a level one heading",
            "## Title",
            False
        ),
        ("The essay must include at least three heading levels: H1 for the main title, H2 for major sections, and H3 for subsections.",
         "# Main Title\n## Major Section\n### Subsection", True),
        ("The essay must include at least three heading levels: H1 for the main title, H2 for major sections, and H3 for subsections.",
         "# Main Title\n## Major Section", False),
        ("Use heading levels to organize the explanation with '##' for main concepts and '###' for supporting details",
         "## Main Concept\n### Supporting Detail", True),
        ("Use heading levels to organize the explanation with '##' for main concepts and '###' for supporting details",
         "upporting Detail", False),
    ]

    # execute the test
    validator = Format_Markdown()
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
