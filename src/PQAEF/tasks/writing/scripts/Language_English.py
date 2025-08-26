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


class Language_English:
    def check(self, constraint, text):
        # handle empty string or pure space
        if not text.strip():
            return False

        # first check if there is a specific format requirement
        format_type, specific_part = self._get_format_requirements(constraint)

        # if there is a specific format, extract the text by format
        if format_type:
            extracted_text = self._extract_text_by_format(
                text, format_type, specific_part)
            if extracted_text is None:  # if cannot extract text, check the original text
                # for text that cannot be recognized, we directly check the original text
                extracted_text = text

            # after extracting text, check by constraint type
            constraint_type = self._get_constraint_type(constraint)
            if constraint_type == "all_uppercase":
                return self._is_all_uppercase(extracted_text)
            elif constraint_type == "title_case":
                return self._is_title_case(extracted_text)
            elif constraint_type == "all_lowercase":
                return self._is_all_lowercase(extracted_text)
            elif constraint_type == "short_blurb":
                return self._is_short_blurb(extracted_text)
            else:
                return False
        else:
            # no specific format requirement, check directly
            constraint_type = self._get_constraint_type(constraint)
            if constraint_type == "all_uppercase":
                return self._is_all_uppercase(text)
            elif constraint_type == "title_case":
                return self._is_title_case(text)
            elif constraint_type == "all_lowercase":
                return self._is_all_lowercase(text)
            elif constraint_type == "short_blurb":
                return self._is_short_blurb(text)
            else:
                return False  # unknown type default processing

    def _get_format_requirements(self, constraint):
        """
        check if the constraint contains specific format requirements
        return (format_type, specific_part)
        format_type: 'table', 'json', 'heading' 或 None
        specific_part: 'headers', 'entries', 'content', 'keys' 等或 None
        """
        constraint_lower = constraint.strip().lower()

        # the case that the constraint contains multiple format requirements
        if "headings" in constraint_lower and "table" in constraint_lower:
            # both require title and table format
            if "entries" in constraint_lower:
                return ("mixed", "all")
            else:
                return ("mixed", "all")

        # check if the constraint requires table format
        if "table" in constraint_lower:
            if "headers" in constraint_lower or "header" in constraint_lower:
                return ("table", "headers")
            elif "entries" in constraint_lower:
                return ("table", "entries")
            elif "content" in constraint_lower:
                return ("table", "content")
            elif "headings" in constraint_lower:
                return ("table", "headers")
            else:
                return ("table", "all")

        # check if the constraint requires JSON format
        elif "json" in constraint_lower:
            if "keys" in constraint_lower:
                return ("json", "keys")
            elif "values" in constraint_lower:
                return ("json", "values")
            else:
                return ("json", "all")

        # check if the constraint requires title format
        elif "heading" in constraint_lower or "headings" in constraint_lower:
            return ("heading", "all")

        # no specific format requirement
        return (None, None)

    def _extract_text_by_format(self, text, format_type, specific_part):
        """
        extract the text that needs to be checked based on the format type
        if cannot extract the text, return the original text
        """
        # handle the case that the constraint contains multiple formats
        if format_type == "mixed":
            # try to extract text from various formats, if any one succeeds, return it
            # try to extract table content
            table_text = self._extract_table_content(text)
            if table_text:
                return table_text

            # try to extract title content
            heading_text = self._extract_heading_content(text)
            if heading_text:
                return heading_text

            # if all above fail, return the original text
            return text

        if format_type == "table":
            return self._extract_table_content(text, specific_part)
        elif format_type == "json":
            return self._extract_json_content(text, specific_part)
        elif format_type == "heading":
            return self._extract_heading_content(text)

        # default case
        return text

    def _extract_table_content(self, text, specific_part="all"):
        """extract the content of the table"""
        # simple table format processing
        if not "|" in text:  # simple check if it is a table format
            return text  # return the original text instead of None

        # split the table rows
        rows = [row.strip() for row in text.split('\n') if row.strip()]
        if not rows:
            return text

        # extract the table content
        if specific_part == "headers":
            # assume the first row is the header
            if len(rows) > 0:
                header_cells = [cell.strip()
                                for cell in rows[0].split('|') if cell.strip()]
                return " ".join(header_cells)
        elif specific_part == "entries":
            # assume all rows except the first row are the entries
            if len(rows) > 1:
                entry_cells = []
                for row in rows[1:]:
                    entry_cells.extend([cell.strip()
                                       for cell in row.split('|') if cell.strip()])
                return " ".join(entry_cells)
        elif specific_part == "content" or specific_part == "all":
            # extract all cell contents
            all_cells = []
            for row in rows:
                all_cells.extend([cell.strip()
                                 for cell in row.split('|') if cell.strip()])
            return " ".join(all_cells)

        # return the text of the whole table
        return text

    def _extract_json_content(self, text, specific_part="all"):
        """extract the content of the JSON"""
        # simplified JSON format processing
        # simple check if it contains the basic symbols of JSON format
        if not "{" in text or not "}" in text:
            return text  # return the original text instead of None

        if specific_part == "keys":
            # very simplified extraction logic, actually more complex JSON parsing is needed
            keys = re.findall(r'"([^"]+)"\s*:', text)
            if keys:
                return " ".join(keys)
        elif specific_part == "values":
            # simplified extraction logic of values
            values = re.findall(r':\s*"([^"]+)"', text)
            if values:
                return " ".join(values)

        # return the original text
        return text

    def _extract_heading_content(self, text):
        """extract the content of the heading"""
        # simplified heading extraction
        # consider recognizing the title format (start with #)
        headings = re.findall(r'^#+\s*(.+)$', text, re.MULTILINE)
        if headings:
            return " ".join(headings)

        # if there is no clear Markdown title format, return the original text
        return text

    def _get_constraint_type(self, constraint):
        constraint_lower = constraint.strip().lower()
        # check if the constraint requires all uppercase
        if (
            re.search(r"\ball[- ]?uppercase\b", constraint_lower)
            or "in all uppercase letters" in constraint_lower
            or "be provided in all uppercase letters" in constraint_lower
            or "in capitalized form" in constraint_lower
            or constraint_lower == "all uppercase"
        ):
            return "all_uppercase"
        # check if the constraint requires title case
        elif (
            "capitalize the first letter of each word" in constraint_lower
            or "capitalized letters for each word" in constraint_lower
            or "have each word capitalized" in constraint_lower
            or "each word must be capitalized" in constraint_lower
            or "each word in" in constraint_lower
            or ("a capital letter" in constraint_lower and "each" in constraint_lower)
            or re.search(r"\bcapitalized\b", constraint_lower)
            or ("capitalize" in constraint_lower and "each" in constraint_lower)
            or ("capitalized" in constraint_lower and "each" in constraint_lower)
            or ("capital" in constraint_lower and "each" in constraint_lower)
        ):
            return "title_case"
        # check if the constraint requires all lowercase
        elif (
            "must be in lowercase" in constraint_lower
            or "all lowercase" in constraint_lower
            or re.search(r"\blowercase\b", constraint_lower)
        ):
            return "all_lowercase"
        elif "written as a short blurb" in constraint_lower:
            return "short_blurb"
        else:
            return None  # unknown type

    def _is_all_uppercase(self, text):
        return text == text.upper()

    def _is_title_case(self, text):
        for word in text.split():
            if word and 'a' <= word[0] <= 'z':
                return False
        return True

    def _is_all_lowercase(self, text):
        return text == text.lower()

    def _is_short_blurb(self, text):
        return True


if __name__ == "__main__":
    validator = Language_English()

    test_cases = [
        ("Response must be written as a short blurb.", "hiii", True),
        # self-test
        ("The table headers must use all uppercase letters for each word",
         " | HELLO WORLD |", True),
        ("The table headers must use all uppercase letters for each word",
         " | HeLLO WORLD |", False),
        ("The table headers must use capitalized letters for each word",
         " | HELLO WORLD | Hello World | Hello World", True),
        ("The table headers must use capitalized letters for each word",
         " | HELLO WORLD | Hello World | hello world", False),
        ('"""The names of all characters must be capitalized."""', 'HELLO WORLD', True),
        ('"""The names of all characters must be capitalized."""', 'hello world', False),
        ('"""The names of all characters must be capitalized."""', 'Hello World', True),

        ('"""The answer must use capitalized letters for each word."""',
         'Hello World', True),
        ('"""The answer must use capitalized letters for each word."""',
         'HELLO WORLD', True),

        # ----------------------------
        # all uppercase constraint test
        # ----------------------------
        # explicitly require all uppercase
        ("The answer must be in all uppercase letters.", "HELLO", True),
        ("The answer must be in all uppercase letters.", "Hello", False),
        ("The answer must be provided in all uppercase letters.", "TEST123", True),
        ("The answer must be in all uppercase letters.", "lowercase", False),
        ("All Uppercase", "ALL CAPS", True),
        ("All Uppercase", "Mixed Case", False),
        ("The response must be written in all uppercase letters.", "YES", True),
        ("The response must be written in all uppercase letters.", "No", False),
        ("The translation must be in all uppercase letters.", "BONJOUR", True),

        # ----------------------------
        # title case constraint test
        # ----------------------------
        # explicitly require title case
        ("The answer must capitalize the first letter of each word.", "Hello World", True),
        ("The answer must capitalize the first letter of each word.", "hello World", False),
        ("The answer must use capitalized letters for each word.", "Python Code", True),
        ("The answer must use capitalized letters for each word.", "python code", False),
        ("Each word must be capitalized", "Title Case Example", True),
        ("Each word must be capitalized", "title case example", False),
        ("Capitalized: The response must use capitalized letters for each word", "Hello", True),
        ("The script must use capitalized letters for each word.",
         "Hello_World", True),  # 含下划线
        ("The answer must capitalize the first letter of each word",
         "Hello-world", True),  # 含连字符
        ("Each word in the answer must start with a capital letter.",
         "Hi There this is wrong.", False),
        ("Each word in the answer must start with a capital letter.",
         "Hi There This Is Correct.", True),
        ("The answer must capitalize each word", "Hello World", True),
        ("The answer must capitalize each word", "hello World", False),
        ("The answer must capitalize each word", "Hello world", False),
        ("\"\"\"The answer must use capitalized letters for each word.\"\"\"",
         "Hello World", True),
        ("\"\"\"The answer must use capitalized letters for each word.\"\"\"",
         "hello world", False),
        ("\"\"\"The answer must use capitalized letters for each word.\"\"\"",
         "Hello World", True),
        # ----------------------------
        # short constraint "Capitalized" test
        # ----------------------------
        ("Capitalized", "Hello World", True),
        ("capitalized", "Hello World", True),
        # hyphen is considered as part of the word
        ("Capitalized", "Hello-world", True),
        # the first letter is not capitalized
        ("Capitalized", "hello world", False),
        # the first letter is not capitalized
        ("capitalized", "hello world", False),
        # camel case (considered as a single word)
        ("Capitalized", "HelloWorld", True),
        ("Capitalized", "Hello123", True),       # contains numbers
        ("Capitalized", "", False),              # empty string
        ("The text must be in capitalized form.", "Hello World", False),
        ("The text must be in capitalized form.", "HELLO WORLD", True),

        # ----------------------------
        # empty string or pure space test
        # ----------------------------
        ("All Uppercase", "", False),
        ("Capitalized", "", False),
        ("All lowercase", "", False),
        ("All Uppercase", "   ", False),
        ("Capitalized", "   ", False),
        ("All lowercase", "   ", False),

        # case boundary test
        ("The answer must use capitalized letters for each word.",
         "", False),  # empty string
        ("The answer must use capitalized letters for each word.",
         "   ", False),  # pure space
        ("All Uppercase", "", False),  # empty string all uppercase check
        ("The answer must use capitalized letters for each word.",
         "A", True),  # single letter
        ("The answer must use capitalized letters for each word.",
         "a", False),  # single letter lowercase
        ("The answer must use capitalized letters for each word.",
         "Hello   World", True),  # multiple spaces
        ("The answer must use capitalized letters for each word.",
         "Hello   world", False),  # multiple spaces
        ("The answer must use capitalized letters for each word.",
         "Hello123", True),  # contains numbers
        ("The answer must use capitalized letters for each word.",
         "Hello!", True),  # contains punctuation

        # ----------------------------
        # all lowercase constraint test
        # ----------------------------
        ("The answer must be in lowercase.", "hello", True),
        ("The answer must be in lowercase.", "Hello", False),
        ("All lowercase", "test123", True),
        ("All lowercase", "Test123", False),
        ("The response must be in lowercase.", "yes", True),
        ("The response must be in lowercase.", "Yes", False),
        ("The translation must be lowercase.", "bonjour", True),
        ("The translation must be lowercase.", "Bonjour", False),

        # case boundary test
        ("The answer must be in lowercase.", "", False),  # empty string
        ("The answer must be in lowercase.", "   ", False),  # pure space
        ("The answer must be in lowercase.", "hello world", True),
        ("The answer must be in lowercase.", "hello World", False),
        ("The answer must be in lowercase.",
         "hello_world", True),  # contains underscore
        ("The answer must be in lowercase.",
         "hello-world", True),  # contains hyphen
        ("The answer must be in lowercase.", "hello123", True),  # contains numbers
        ("The answer must be in lowercase.",
         "hello!", True),  # contains punctuation


        # self-test
        ('"""All headings and table entries must be capitalized."""', 'Title', True),
        ('"""All headings and table entries must be capitalized."""', 'title', False),
        ('"""All headings and table entries must be capitalized."""', 'TITLE', True),
        ("Each word in the answer should start with a capital letter",
         "Hi There This Is Correct.", True),
        ("Each word in the answer should start with a capital letter",
         "Hi There This is Wrong.", False),

        # special format
        # basic test
        ("The answer must capitalize the first letter of each word.", "Hello World", True),
        ("The answer must capitalize the first letter of each word.", "hello World", False),
        ("The answer must use capitalized letters for each word.", "Python Code", True),
        ("The answer must use capitalized letters for each word.", "python code", False),
        ("Each word must be capitalized", "Title Case Example", True),
        ("Each word must be capitalized", "title case example", False),

        # table related test - use real table format
        ("The table headers must be capitalized",
         "| Column One | Column Two |\n| --------- | --------- |", True),
        ("The table headers must be capitalized",
         "| column one | column two |\n| --------- | --------- |", False),
        ("Each word in the table entries must be capitalized.",
         "| Header One | Header Two |\n| Content One | Content Two |", True),
        ("Each word in the table entries must be capitalized.",
         "| Header One | Header Two |\n| content one | content two |", False),
        ("The table content must use capitalized letters for each word",
         "| Product Name | Price |\n| Coffee Mug | $10.99 |", True),
        ("The table content must use capitalized letters for each word",
         "| product name | price |\n| coffee mug | $10.99 |", False),

        # JSON related test - use real JSON format
        ('All keys in the JSON object must be capitalized.',
         '{"Name": "John", "Age": 30}', True),
        ('All keys in the JSON object must be capitalized.',
         '{"name": "John", "age": 30}', False),

        # title related test - use Markdown title format
        ('Headings must use capitalized letters for each word',
         '# Main Title\n## Sub Heading', True),
        ('Headings must use capitalized letters for each word',
         '# main title\n## sub heading', False),
        ('All headings in the article must use capitalized letters for each word to maintain a formal academic style.',
         '# Research Methods\n## Data Analysis Techniques', True),
        ('All headings in the article must use capitalized letters for each word to maintain a formal academic style.',
         '# research methods\n## data analysis techniques', False),

        # more test from CSV file - use appropriate format
        ('"""The table\'s title or header must be capitalized."""',
         '| Table Title | Data |\n| ----------- | ---- |', True),
        ('"""The table\'s title or header must be capitalized."""',
         '| table title | data |\n| ----------- | ---- |', False),
        ('Each application name in the list must be capitalized',
         '| Microsoft Word | Adobe Photoshop | Google Chrome |', True),
        ('Each application name in the list must be capitalized',
         '| microsoft word | adobe photoshop | google chrome |', False),
        ('The content in the table must have each word capitalized',
         '| Product | Price |\n| Coffee Maker | $50.00 |\n| Water Bottle | $15.00 |', True),
        ('The content in the table must have each word capitalized',
         '| Product | Price |\n| coffee maker | $50.00 |\n| water bottle | $15.00 |', False),
        ('The content in the table must use capitalized letters for each word in video topics, titles, and descriptions',
         '| Video Topic | Title | Description |\n| Home Decor | Room Makeover | Budget Friendly Tips |', True),
        ('The content in the table must use capitalized letters for each word in video topics, titles, and descriptions',
         '| video topic | title | description |\n| home decor | room makeover | budget friendly tips |', False),
        ('The company names in the table must be capitalized',
         '| Apple Inc. | Microsoft Corporation | Google LLC |', True),
        ('The company names in the table must be capitalized',
         '| apple inc. | microsoft corporation | google llc |', False),

    ]

    # execute the test
    for i, (constraint, text, expected) in enumerate(test_cases, 1):
        result = validator.check(constraint, text)
        assert result == expected, f"""
        Failed Case #{i}:
        Constraint: {constraint}
        Text:       {text}
        Expected:   {expected}
        Actual:     {result}
        """
    print("All test cases passed!")
