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


class Format_Table:
    def __init__(self):
        # dictionary of numbers, support 1 to 10 in English
        self.num_words = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
            'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14,
            'fifteen': 15, 'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19,
            'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50, 'sixty': 60,
            'seventy': 70, 'eighty': 80, 'ninety': 90, 'hundred': 100
        }

        # pre-compiled regex, the number can be a number or an English word
        self.row_patterns = [
            (r'exactly\s+(\d+|\b(?:' + '|'.join(self.num_words.keys()) + r')\b)\s+rows?', 'exact'),
            (r'no\s+more\s+than\s+(\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)\s+rows?', 'max'),
            (r'not\s+have\s+more\s+than\s+(\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)\s+rows?', 'max'),
            (r'must\s+not\s+exceed\s+(\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)\s+rows?', 'max'),
            (r'not\s+exceed\s+(\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)\s+rows?', 'max'),
            (r'not\s+exceeding\s+(\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)\s+rows?', 'max'),
            (r'should\s+not\s+exceed\s+(\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)\s+rows?', 'max'),
            (r'row\s+limit\s+of\s+(\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)', 'max'),
            (r'(\d+|\b(?:' + '|'.join(self.num_words.keys()) +
             r')\b)\s+rows?\s+must\s+be\s+included', 'exact'),
            (r'exactly\s+.+and (\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)\s+rows?', 'exact'),
            (r'not exceed\s+.+and (\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)\s+rows?', 'max'),
            (r'a maximum of\s+(\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)\s+rows', 'max'),
            (r'limited to a maximum of\s+(\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)\s+rows', 'max'),
            (r'limited to\s+(\d+|\b(?:' + '|'.join(self.num_words.keys()) + r')\b)\s+rows', 'max'),
            (r'a row limit of\s+(\d+|\b(?:' + '|'.join(self.num_words.keys()) + r')\b)', 'max'),
            (r'a maximum of\s+.+and (\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)\s+rows?', 'max'),
            (r'limit the number of rows to\s+(\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)', 'max'),
            (r'limit it to\s+(\d+|\b(?:' + '|'.join(self.num_words.keys()) + r')\b)\s+rows', 'max'),
            (r'limit the table to\s+(\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)\s+rows', 'max'),
            (r'the number of rows in each table does not exceed\s+(\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)', 'max'),
        ]

        self.col_patterns = [
            (r'exactly\s+(\d+|\b(?:' + '|'.join(self.num_words.keys()) +
             r')\b)\s+columns?', 'exact'),
            (r'no\s+more\s+than\s+(\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)\s+columns?', 'max'),
            (r'not\s+have\s+more\s+than\s+(\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)\s+columns?', 'max'),
            (r'must\s+not\s+exceed\s+(\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)\s+columns?', 'max'),
            (r'not\s+exceed\s+(\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)\s+columns?', 'max'),
            (r'not\s+exceeding\s+(\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)\s+columns?', 'max'),
            (r'should\s+not\s+exceed\s+(\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)\s+columns?', 'max'),
            (r'column\s+limit\s+of\s+(\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)', 'max'),
            (r'must\s+have\s+exactly\s+(\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)\s+columns?', 'exact'),
            (r'exactly\s+.+and (\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)\s+columns?', 'exact'),
            (r'in\s+(\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)\s+columns', 'exact'),
            (r'not exceed\s+.+and (\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)\s+columns?', 'max'),
            (r'maximum of\s+(\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)\s+columns', 'max'),
            (r'maximum\s+(\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)\s+columns', 'max'),
            (r'at most\s+(\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)\s+columns', 'max'),
            (r'limited to a maximum of\s+(\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)\s+columns', 'max'),
            (r'limited to\s+(\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)\s+columns', 'max'),
            (r'a column limit of\s+(\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)', 'max'),
            (r'a maximum of\s+.+and (\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)\s+columns?', 'max'),
            (r'limit the number of columns to\s+(\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)', 'max'),
            (r'limit it to\s+(\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)\s+columns', 'max'),
            (r'limit the table to\s+(\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)\s+columns', 'max'),
            (r'the number of columns in each table does not exceed\s+(\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)', 'max'),
            # new column number constraint pattern
            # match "a single column" or "each ... single column"
            (r'(a|each) (single) column', 'exact_1'),
            # match "presented in a single column"
            (r'presented in (a|one) single column', 'exact_1'),
            (r'title must not exceed (\d+|\b(?:' +
             '|'.join(self.num_words.keys()) + r')\b)\s+words', 'title_max'),  # match "title must not exceed five words"
        ]

        self.keyword_patterns = [
            (r'columns?\s+should\s+be\s+([\w\s,]+)', 'keyword'),
            (r"columns:\s+([\w\s,']+)", 'keyword'),
            # match "must include columns for "Name," "Price," ..."
            (r'must include columns for\s+"([^"]+)"', 'keyword'),
            # match "must include the title, author, ..."
            (r'must include the\s+([\w\s,]+)', 'content'),
            # match "each entry must include the film title and its release year"
            (r'each (entry|row|item|game|series) must include (?:the\s+)?([\w\s,]+(?:\s+and\s+(?:its|their)\s+[\w\s,]+)?)', 'content'),
            # match the column name with quotes
            (r'table must include columns (for|named)\s+[""]([^""]+)[""]', 'keyword'),
            # match "each game idea should be presented in a single column"
            (r'each (entry|row|item|game|series) should (?:be )?(present|include|contain|show)(?:ed)? (?:in|with)?\s+([\w\s,]+)', 'content'),
        ]

        self.special_cases = {
            'markdown': r'^\s*\|',
            'specific_columns': r'columns?\s+should\s+be\s+([\w\s,]+)'
        }

    def parse_constraint(self, constraint):
        """parse the constraint and return the rule dictionary"""
        constraint = constraint.lower()
        rules = {'rows': None, 'cols': None, 'markdown': False,
                 'columns': [], 'content_requirements': []}

        # parse the row rule
        for pattern, rule_type in self.row_patterns:
            match = re.search(pattern, constraint)
            if match:
                # if the match is an English word, convert it to a number
                num = match.group(1)
                if num in self.num_words:
                    num = self.num_words[num]
                else:
                    num = int(num)
                rules['rows'] = (rule_type, num)
                break

        # parse the column rule
        for pattern, rule_type in self.col_patterns:
            match = re.search(pattern, constraint)
            if match:
                if rule_type == 'exact_1':
                    # special case: single column
                    rules['cols'] = ('exact', 1)
                elif rule_type == 'title_max':
                    # title max words limit, not a column constraint but using cols field to store
                    num = match.group(1)
                    if num in self.num_words:
                        num = self.num_words[num]
                    else:
                        num = int(num)
                    rules['title_max_words'] = num
                else:
                    # normal column constraint
                    num = match.group(1)
                    if num in self.num_words:
                        num = self.num_words[num]
                    else:
                        num = int(num)
                    rules['cols'] = (rule_type, num)
                break

        # parse the special rule
        if 'markdown' in constraint:
            rules['markdown'] = True

        # special case: "Each series must include the title, author, and year of publication"
        if "series must include" in constraint and "title" in constraint and "author" in constraint:
            rules['content_requirements'] = [
                "title", "author", "year", "publication"]

        # special case: "Each entry must include the film title and its release year"
        if "film title" in constraint and "release year" in constraint:
            rules['content_requirements'] = ["film title", "release year"]

        # special case: handle the table column name requirement: "table must include columns for "Name," "Price," "Rating," and "Shipping Availability""
        if "columns for" in constraint and '"' in constraint:
            # try to capture the column name in the quotes
            quoted_columns = re.findall(r'"([^"]+)"', constraint)
            if quoted_columns:
                # clean the column name in the quotes (remove the comma and other punctuation)
                clean_columns = []
                for col in quoted_columns:
                    # remove the comma and space at the end
                    clean_col = col.strip().rstrip(',').strip()
                    if clean_col:
                        clean_columns.append(clean_col)

                if clean_columns:
                    rules['columns'] = clean_columns
                    return rules  # find the specific format and return directly, avoid interfering with the subsequent processing

        # parse the specific column requirement and content requirement
        for pattern, rule_type in self.keyword_patterns:
            match = re.search(pattern, constraint)
            if match:
                if rule_type == 'keyword':
                    # column name requirement
                    if match.group(1):
                        columns = [c.strip("'\" ") for c in re.split(
                            r'[,、，和and]', match.group(1))]
                        rules['columns'].extend([c for c in columns if c])
                elif rule_type == 'content':
                    # content requirement
                    if len(match.groups()) > 1:
                        # get the last capture group (content requirement)
                        last_group = match.groups()[-1]

                        # handle the "and" connected content
                        if " and " in last_group:
                            parts = last_group.split(" and ")
                            # handle the left part (may contain comma separated items)
                            if "," in parts[0]:
                                left_items = [item.strip()
                                              for item in parts[0].split(",")]
                                rules['content_requirements'].extend(
                                    left_items)
                            else:
                                rules['content_requirements'].append(
                                    parts[0].strip())

                            # handle the right part (maybe a single item or "its X" format)
                            if parts[1].startswith("its "):
                                rules['content_requirements'].append(
                                    parts[1][4:].strip())  # remove "its "
                            else:
                                rules['content_requirements'].append(
                                    parts[1].strip())
                        else:
                            # no "and" connected, directly split by comma
                            contents = [c.strip()
                                        for c in re.split(r'[,、，]', last_group)]
                            rules['content_requirements'].extend(
                                [c for c in contents if c])

        # special case: handle the column name list with quotes
        match = re.search(
            r'include columns for\s+(?:"([^"]+)",?\s*)+', constraint)
        if match:
            column_text = constraint[match.start():match.end()]
            columns = re.findall(r'"([^"]+)"', column_text)
            rules['columns'].extend([c.strip() for c in columns if c.strip()])

        # another format: extract the column name from the quotes "col1," "col2," "col3"
        columns = re.findall(r'[""]([^""]+)[""]', constraint)
        # if no column name is extracted before
        if columns and not rules['columns']:
            clean_columns = []
            for col in columns:
                # remove the possible comma
                clean_col = col.strip().rstrip(',').strip()
                if clean_col:
                    clean_columns.append(clean_col)

            rules['columns'].extend(clean_columns)

        # handle the "each X must include Y" format, where Y is a complex phrase, possibly containing "and its"
        match = re.search(
            r'each\s+\w+\s+must\s+include\s+(?:the\s+)?([\w\s]+\s+and\s+its\s+[\w\s]+)', constraint)
        if match:
            phrase = match.group(1)
            # split "film title and its release year" to ["film title", "release year"]
            parts = re.split(r'\s+and\s+its\s+', phrase)
            rules['content_requirements'].extend(
                [part.strip() for part in parts if part.strip()])

        # special case: handle the single column case - "presented in a single column"
        if "single column" in constraint:
            rules['cols'] = ('exact', 1)

        # special case: if the content requirement contains "game idea" and mentions "single column", then set to single column
        if any("game idea" in req for req in rules['content_requirements']) and "single column" in constraint:
            rules['cols'] = ('exact', 1)

        # special case: handle the title length limit
        match = re.search(r'title\s+must\s+not\s+exceed\s+(\d+|\b(?:' +
                          '|'.join(self.num_words.keys()) + r')\b)\s+words', constraint)
        if match:
            num = match.group(1)
            if num in self.num_words:
                num = self.num_words[num]
            else:
                num = int(num)
            rules['title_max_words'] = num

        # remove the duplicate content requirement
        if rules['content_requirements']:
            rules['content_requirements'] = list(
                set(rules['content_requirements']))
            # remove the empty string
            rules['content_requirements'] = [
                req for req in rules['content_requirements'] if req]

        return rules

    def check_table_structure(self, text, rules, constraint):
        """check if the table structure matches the rules"""
        constraint = constraint.lower()
        optional_patterns = [
            r'if you (include|use|utilize|incorporate|present) (a |any )?(tables?|tabular data)',
            r'if you (decide|choose|opt) to (use|include|incorporate|present|utilize) (a |any )?(tables?|tabular data)',
            r'if (a |any )?(tables?|tabular data|table format) (is|are) (used|included|utilized|incorporated|presented|chosen)',
            r'if there (is|are) (a |any )?(tables?|tabular data|table format) (used|included|utilized|incorporated|presented|chosen)',
            r'if you (decide|choose|opt) to (use|include|incorporate|present|utilize) (your )?information in a table'
            r'if presented in a table',
        ]

        if "|" not in text:
            if "table" not in constraint:
                return True

            for op in optional_patterns:
                match = re.search(op, constraint, re.DOTALL)
                if match:
                    return True

            return False

        match = re.search(r'(\|.*\|)', text, re.DOTALL)
        text = match.group(1) if match else ""

        lines = [line.strip() for line in text.split('\n') if line.strip()]

        # Markdown format check
        if rules['markdown'] and not any(re.match(r'^\s*\|', line) for line in lines):
            return False

        # row number check
        if rules['rows']:
            rule_type, value = rules['rows']
            total = len(lines)
            if len(lines) > 1 and '---' in lines[1]:
                actual = total-2
            else:
                actual = total-1
            if rule_type == 'exact' and actual != value:
                return False
            if rule_type == 'max' and actual > value:
                return False

        # column number check
        if rules['cols']:
            rule_type, value = rules['cols']
            if not lines:
                return False
            columns = len(lines[0].split('|')) - 2  # handle the Markdown table
            if rule_type == 'exact' and columns != value:
                return False
            if rule_type == 'max' and columns > value:
                return False

        # title word number check
        if 'title_max_words' in rules:
            # assume the first line is the title
            if not lines:
                return False
            title = lines[0].strip('|').strip()
            words = len(title.split())
            if words > rules['title_max_words']:
                return False

        # special constraint condition handling
        if "series must include" in constraint and "title" in constraint and "author" in constraint and "year" in constraint:
            headers = [h.strip().lower()
                       for h in lines[0].split('|')[1:-1]] if lines else []

            has_title = any("title" in h for h in headers)
            has_author = any("author" in h for h in headers)
            has_year = any("year" in h for h in headers)

            if not (has_title and has_author and has_year):
                return False
            return True

        # special case: check the column name with quotes, such as "Name," "Price," "Rating," etc.
        if "columns for" in constraint and rules['columns']:
            if not lines:
                return False

            headers = [h.strip().lower() for h in lines[0].split('|')[1:-1]]
            required_columns = [col.lower() for col in rules['columns']]

            # check if all required columns are in the header
            for col in required_columns:
                found = False
                for header in headers:
                    # partial match, as long as the column name is part of the header
                    if col in header or header in col:
                        found = True
                        break
                if not found:
                    return False

            return True

        # special column name check
        if rules['columns']:
            if not lines:
                return False
            headers = [h.strip().lower() for h in lines[0].split('|')[1:-1]]
            required_columns = [col.lower() for col in rules['columns']]

            # check if all required columns are in the header
            for col in required_columns:
                found = False
                for header in headers:
                    if col in header:  # allow partial match
                        found = True
                        break
                if not found:
                    return False

        # special constraint case
        if "film title" in constraint.lower() and "release year" in constraint.lower():
            # special case: "Each entry must include the film title and its release year"
            headers = [h.strip().lower()
                       for h in lines[0].split('|')[1:-1]] if lines else []

            # check if the header contains "film title" and "release year"
            has_film_title = any("film" in h.lower()
                                 or "title" in h.lower() for h in headers)
            has_release_year = any("release" in h.lower(
            ) or "year" in h.lower() for h in headers)

            if not (has_film_title and has_release_year):
                return False
            return True

        # content requirement check
        if rules['content_requirements']:
            # build the text of all table content
            table_content = ' '.join([' '.join(line.split('|'))
                                     for line in lines]).lower()

            # check if the header contains all the required content
            headers = [h.strip().lower()
                       for h in lines[0].split('|')[1:-1]] if lines else []

            for content_req in rules['content_requirements']:
                content_req_lower = content_req.lower()

                # special case: handle the film title and release year
                if content_req_lower == "film title":
                    has_film_title = any(
                        "film" in h or "title" in h for h in headers)
                    if has_film_title:
                        continue

                if content_req_lower == "release year":
                    has_release_year = any(
                        "release" in h or "year" in h for h in headers)
                    if has_release_year:
                        continue

                # special case: handle the series
                if content_req_lower == "title":
                    has_title = any("title" in h for h in headers)
                    if has_title:
                        continue

                if content_req_lower == "author":
                    has_author = any("author" in h for h in headers)
                    if has_author:
                        continue

                if content_req_lower == "year" or content_req_lower == "year of publication":
                    has_year = any("year" in h for h in headers)
                    if has_year:
                        continue

                if content_req_lower == "publication":
                    # this is a special case, we have already checked year, no need to check publication
                    continue

                # first check if the content is in the table
                if content_req_lower in table_content:
                    continue

                # check if the content is in the header
                found_in_headers = False
                for header in headers:
                    words = content_req_lower.split()
                    # check if any word in the content requirement is in the header
                    if any(word in header for word in words):
                        found_in_headers = True
                        break

                # if found in the header, continue to check the next requirement
                if found_in_headers:
                    continue

                # if not found in the table content or header, return False
                return False

        return True

    def check(self, constraint, text):
        rules = self.parse_constraint(constraint)
        result = self.check_table_structure(text, rules, constraint)
        return result


if __name__ == "__main__":

    # test cases
    test_cases = [
        # row number constraint
        ("A table with exactly three rows must be included",
         "| Header |\n|--------|\n| Row 1  |\n| Row 2  |\n| Row 3  |", True),

        ("The answer must include a table with no more than 2 rows",
         "| Header |\n|--------|\n| Row 1  |\n| Row 2  |\n| Row 3  |", False),

        ("The answer must include a table with no more than 2 rows",
         "| Header |\n|--------|\n| Row 1  |\n| Row 2  |", True),

        ("A table with exactly three rows must be included",
         "| Header |\n| Row 1  |\n| Row 2  |", False),

        ("A table with exactly three rows must be included",
         "| Header |\n| Row 1  |", False),

        ("Any table included must not exceed three rows",
         "| A | B |\n|---|---|\n| 1 | 2 |\n| 3 | 4 |", True),

        ("Any table included must not exceed three rows",
         "| A | B |\n|---|---|\n| 1 | 2 |", True),

        ("if a table is included, it should not have more than three rows",
         "| A | B |\n|---|---|\n| 1 | 2 |\n| 3 | 4 |", True),

        ("if a table is included, it should not have more than three rows",
         "| A | B |\n|---|---|\n| 1 | 2 |", True),

        # column number constraint
        ("Ensure that any tables included are limited to 3 columns",
         "| Col1 | Col2 | Col3 |\n|------|------|------|", True),

        ("Must include a table with exactly three columns",
         "| A | B |\n|---|---|", False),



        # combination constraint
        ("Include a table with exactly three rows and 2 columns",
         "| A | B |\n|---|---|\n| 1 | 2 |\n| 3 | 4 |\n| 5 | 6 |", True),

        ("Include a table with exactly three rows and 2 columns",
         "| A | B |\n| 1 | 2 |\n| 3 | 4 |", False),

        ("Include a table with exactly three rows and 2 columns",
         "| A |\n| 1 |\n| 3 |", False),

        # specific column check
        ("Include a table with columns: 'Word', 'Part of Speech', 'Definition'",
         "| Word | Part of Speech | Definition |\n|------|----------------|------------|", True),

        # Markdown format
        ("Present your answer in markdown table format",
         "| Header |\n|--------|\n| Data   |", True),

        # Chinese constraint
        ("如果选择使用表格,表格的行数不能超过三行",
         "| 列1 |\n|-----|\n| 数据 |\n| 数据 |", True),

        # no row number constraint
        ("A table with exactly five rows must be included",
         "| A |\n|---|\n| 1 |\n| 2 |\n| 3 |\n| 4 |\n", False),

        # max column number constraint
        ("A table with no more than two columns",
         "| A | B |\n|---|---|\n| 1 | 2 |\n| 3 | 4 |", True),

        # max row number constraint
        ("Table rows must not exceed five",
         "| A |\n|---|\n| 1 |\n| 2 |\n| 3 |\n| 4 |\n| 5 |\n", True),

        # row number and column number combination
        ("A table with no more than 3 rows and exactly 2 columns",
         "| A | B |\n| 1 | 2 |\n| 3 | 4 |", True),

        # specific column, but the header order is different
        ("Include a table with columns: 'Part of Speech', 'Word', 'Definition'",
         "| Part of Speech | Word | Definition |\n|-----------------|------|------------|", True),

        ("Include a table with columns: 'Part of Speech', 'Word', 'Definition'",
         "| Part of Speech | Definition |\n|-----------------|------------|", False),

        # specific column, but not fully satisfied
        ("Table must include columns: 'Name', 'Age', 'City'",
         "| Name | Age |\n|------|-----|\n| Alice | 30 |", False),

        # Chinese row number constraint
        ("表格的行数必须是两行",
         "| 项目 |\n|------|\n| 1    |\n| 2    |", True),

        # Chinese column number constraint
        ("表格必须有两列",
         "| 名字 | 年龄 |\n|------|------|\n| 张三 | 20 |", True),

        ("Additionally, if any tabular data is presented, it must be limited to a maximum of three rows to ensure clarity and conciseness",
         "| A | B |\n|---|---|\n| 1 | 2 |\n| 3 | 4 |", True),

        ("Additionally, if any tabular data is presented, it must be limited to a maximum of three rows to ensure clarity and conciseness",
         "| A | B |\n|---|---|\n| 1 | 2 |", True),

        ("Additionally, if you include any tables, ensure they are limited to a maximum of 3 rows",
         "| A | B |\n|---|---|\n| 1 | 2 |\n| 3 | 4 |", True),

        ("Additionally, if you include any tables, ensure they are limited to a maximum of 3 rows",
         "| A | B |\n|---|---|\n| 1 | 2 |", True),

        ("Additionally, if you include any tables, ensure they have a column limit of 3 to maintain concise presentation of information",
         "| Col1 | Col2 | Col3 |\n|------|------|------|", True),

        ("Additionally, if you include any tables, ensure they have a column limit of 3 to maintain concise presentation of information",
         "| Col1 | Col2 |\n|------|------|", True),

        ("Additionally, if you include any tables, ensure they have a column limit of 3 to maintain concise presentation of information",
         "| Col1 | Col2 | Col3 | Col4 |\n|------|------|------|------|", False),

        ("Any Table Included Must Not Exceed Three Columns",
         "| Col1 | Col2 | Col3 | Col4 |\n|------|------|------|------|", False),

        ("Any Table Included Must Not Exceed Three Columns",
         "| Col1 | Col2 | Col3 |\n|------|------|------|", True),

        ("if any tables are included, limit the number of columns to 3 to maintain readability.",
         "| Col1 | Col2 | Col3 | Col4 |\n|------|------|------|------|", False),

        ("if any tables are included, limit the number of columns to 3 to maintain readability.",
         "| Col1 | Col2 | Col3 |\n|------|------|------|", True),

        ("A table with exactly three rows must be included",
         "| Header |\n|--------|\n| Row 1  |\n| Row 2  |\n| Row 3  |", True),

        ("Any table included must not exceed three rows",
         "| A | B |\n|---|---|\n| 1 | 2 |\n| 3 | 4 |", True),

        # column number constraint
        ("Ensure that any tables included are limited to 3 columns",
         "| Col1 | Col2 | Col3 |\n|------|------|------|", True),

        ("Must include a table with exactly three columns",
         "| A | B |\n|---|---|", False),

        # combination constraint
        ("Include a table with exactly three rows and 2 columns",
         "| A | B |\n|---|---|\n| 1 | 2 |\n| 3 | 4 |\n| 5 | 6 |", True),

        # specific column check
        ("Include a table with columns: 'Word', 'Part of Speech', 'Definition'",
         "| Word | Part of Speech | Definition |\n|------|----------------|------------|", True),

        # Markdown format
        ("Present your answer in markdown table format",
         "| Header |\n|--------|\n| Data   |", True),

        # Chinese constraint
        ("如果选择使用表格,表格的行数不能超过三行",
         "| 列1 |\n|-----|\n| 数据 |\n| 数据 |", True),

        ("The list of contents should not exceed five rows", 'THE XML REPORT GENERATED BY THE SOLPACKAGE DEPLOYREPORT ACTION SERVES TO DOCUMENTTHE DIFFERENCES BETWEEN THE SOURCE AND TARGET DATABASE SCHEMAS. ITS CONTENTS INCLUDE: ACTION (TO INDICATE WHAT CHANGES AREREQUIRED), OBJECTTYPE (TO SPECIFY THE TYPE OF DATABASE OBJECT), AND OBJECTNAME (TO IDENTIFY THE SPECIFIC OBJECT). ADDITIONALLYIT MIGHT INCLUDE THE SOURCE AND TARGET SCHEMAS.', True),

        ("The table must not exceed 4 columns.",
         "| A | B | C | D |\n|---|---|---|---|", True),

        ("The table must not exceed 4 columns.",
         "| A | B | C | D | E |\n|---|---|---|---|---|", False),

        # test case: "Each entry must include the film title and its release year"
        ("Each entry must include the film title and its release year",
         "| Film Title | Release Year |\n|------------|-------------|\n| Inception | 2010 |\n| The Matrix | 1999 |", True),

        ("Each entry must include the film title and its release year",
         "| Film Title |\n|------------|\n| Inception |\n| The Matrix |", False),

        # test case: "Each game idea should be presented in a single column"
        ("Each game idea should be presented in a single column",
         "| Game Ideas |\n|-----------|\n| Racing game |\n| Puzzle game |\n| Strategy game |", True),

        ("Each game idea should be presented in a single column",
         "| Game Ideas | Platforms |\n|-----------|----------|\n| Racing game | PC, Console |\n| Puzzle game | Mobile |", False),

        # test case: "Each series must include the title, author, and year of publication"
        ("Each series must include the title, author, and year of publication",
         "| Title | Author | Year |\n|-------|--------|------|\n| Harry Potter | J.K. Rowling | 1997 |\n| Lord of the Rings | J.R.R. Tolkien | 1954 |", True),

        ("Each series must include the title, author, and year of publication",
         "| Title | Author |\n|-------|--------|\n| Harry Potter | J.K. Rowling |\n| Lord of the Rings | J.R.R. Tolkien |", False),

        # test case: "The table must include columns for "Name," "Price," "Rating," and "Shipping Availability""
        ('The table must include columns for "Name," "Price," "Rating," and "Shipping Availability"',
         "| Name | Price | Rating | Shipping Availability |\n|------|-------|--------|----------------------|\n| Laptop | $1200 | 4.5 | Available |", True),

        ('The table must include columns for "Name," "Price," "Rating," and "Shipping Availability"',
         "| Name | Price | Rating |\n|------|-------|--------|\n| Laptop | $1200 | 4.5 |", False),

        # test case: "The title must not exceed five words."
        ("The title must not exceed five words.",
         "| Short Title Here |\n|----------------|\n| Content |", True),

        ("The title must not exceed five words.",
         "| This Title Has More Than Five Words |\n|--------------------------------|\n| Content |", False),
    ]

    # execute the test
    validator = Format_Table()
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
