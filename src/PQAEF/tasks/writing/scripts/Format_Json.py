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


import json
import re


class Format_Json:
    def __init__(self):
        pass

    def parse_number(self, s):
        number_words = {
            'two': 2,
            'three': 3
        }
        s = s.lower()
        if s in number_words:
            return number_words[s]
        elif s.isdigit():
            return int(s)
        else:
            return None

    def parse_constraint(self, constraint):
        s = constraint.lower()
        s = re.sub(r'[^\w\s]', '', s)  # remove the punctuation

        exact_level = None
        max_level = None
        min_level = None

        # check the exact level (highest priority)
        exact_patterns = [
            (r'exactly (\d+|two|three) levels? of nesting', 1),
            (r'structured as a json object with a nesting level of (\d+|two|three)', 1),
            (r'json example with exactly (\d+|two|three) levels?', 1),
            (r'object nesting levels must be (\d+|two|three)', 1),
            (r'answer must include a json example with exactly (\d+|two|three) levels?', 1),
            (r'nesting level of (\d+|two|three)', 1),
            (r'be limited to (\d+|two|three) levels of nesting', 1),
        ]
        for pattern, group in exact_patterns:
            match = re.search(pattern, s)
            if match:
                value = match.group(group)
                num = self.parse_number(value)
                if num is not None:
                    exact_level = num
                    break

        if exact_level is not None:
            return {'exact': exact_level, 'max': None, 'min': None}

        # check the max level (allow multiple matches)
        max_patterns = [
            (r'must not exceed (\d+|two|three) levels? of nesting', 1),
            (r'no more than (\d+|two|three) levels?', 1),
            (r'maximum of (\d+|two|three) nesting levels', 1),
            (r'maximum of (\d+|two|three) object nesting levels', 1),
            (r'maximum of (\d+|two|three) levels', 1),
            (r'not exceed (\d+|two|three) levels', 1),
            (r'levels not exceeding (\d+|two|three)', 1),
            (r'with the structure not exceeding (\d+|two|three) levels', 1),
            (r'object nesting levels must not exceed (\d+|two|three) levels', 1),
            (r'object nesting levels must not exceed (\d+|two|three)', 1),
            (r'json must have a maximum of (\d+|two|three) nesting levels', 1),
            (r'response must not exceed (\d+|two|three) levels? of nesting', 1),
            (r'and at most (\d+|two|three)', 1),
        ]
        for pattern, group in max_patterns:
            matches = re.findall(pattern, s)
            for match in matches:
                num = self.parse_number(match)
                if num is not None:
                    if max_level is None or num < max_level:
                        max_level = num  # take the strictest value

        # check the min level (allow multiple matches)
        min_patterns = [
            (r'at least (\d+|two|three) levels? of nesting', 1),
            (r'at least (\d+|two|three) levels? deep', 1),
            (r'must include a json object with at least (\d+|two|three) levels?', 1),
            (r'answer must include a json object with at least (\d+|two|three) levels?', 1),
            (r'and at least (\d+|two|three)', 1),
        ]
        for pattern, group in min_patterns:
            matches = re.findall(pattern, s)
            for match in matches:
                num = self.parse_number(match)
                if num is not None:
                    if min_level is None or num > min_level:
                        min_level = num  # take the strictest value

        return {
            'exact': exact_level,
            'max': max_level,
            'min': min_level
        }

    def parse_json(self, json_str):
        # use the regex to extract the content between ```json and ```
        match = re.search(r'```json(.*?)```', json_str, re.DOTALL)
        if match:
            # extract and remove the whitespace
            json_str = match.group(1).strip()
        try:
            return json.loads(json_str)  # parse the JSON string
        except json.JSONDecodeError:
            return None

    def calculate_depth(self, json_obj):
        def _depth_helper(obj, depth):
            if isinstance(obj, dict):
                if not obj:
                    return depth  # the depth of an empty dictionary is the current depth
                return max(_depth_helper(value, depth + 1) for value in obj.values())
            elif isinstance(obj, list):
                if not obj:
                    return depth  # the depth of an empty list is the current depth
                return max(_depth_helper(item, depth + 1) for item in obj)
            else:
                return depth  # the depth of a basic data type is the current depth

        return _depth_helper(json_obj, 0)  # start from 0

    def check(self, constraint, json_str):
        constraints = self.parse_constraint(constraint)
        exact = constraints['exact']
        max_level = constraints['max']
        min_level = constraints['min']

        json_obj = self.parse_json(json_str)
        if json_obj is None:
            return False

        max_depth = self.calculate_depth(json_obj)

        if exact is not None:
            return max_depth == exact

        # handle the boundary of the max and min level
        if max_level is not None and min_level is not None:
            return min_level <= max_depth <= max_level
        elif max_level is not None:
            return max_depth <= max_level
        elif min_level is not None:
            return max_depth >= min_level
        else:
            return False


if __name__ == "__main__":
    # test cases
    test_cases = [
        # max level 2
        ('"Any JSON data included must be nested at least two levels deep, such as {""level1"": {""level2"": ""value""}}."', '{"a": {"b": 1}}', True),
        ('"Any JSON data included must be nested at least two levels deep, such as {""level1"": {""level2"": ""value""}}."', '{"a": 1}', False),
        (
            "Any JSON example provided must not exceed two levels of nesting",
            '{"a": {"b": 1}}',
            True
        ),
        (
            "Any JSON example provided must not exceed two levels of nesting",
            '{"a": {"b": {"c": 1}}}',
            False
        ),
        # max level 3
        (
            "JSON must have a maximum of three nesting levels",
            '{"a": {"b": {"c": 1}}}',
            True
        ),
        (
            "Object nesting levels must not exceed 3",
            '{"a": {"b": {"c": {"d": 1}}}}',
            False
        ),
        (
            "JSON must have a maximum of three nesting levels",
            '{"a": {"b": {"c": {"d": 1}}}}',
            False
        ),
        # exact level 2
        (
            "The answer must include a JSON example with exactly two levels of nesting.",
            '{"a": {"b": 1}}',
            True
        ),
        (
            "The answer must include a JSON example with exactly two levels of nesting.",
            '{"a": 1}',
            False
        ),
        # min level 3
        (
            "The answer must include a JSON object with at least three levels of nesting to detail the reverse engineering process.",
            '{"a": {"b": {"c": 1}}}',
            True
        ),
        (
            "The answer must include a JSON object with at least three levels of nesting to detail the reverse engineering process.",
            '{"a": {"b": 1}}',
            False
        ),
        # exact level 2 (text description)
        (
            "Object nesting levels must be two",
            '{"a": {"b": 1}}',
            True
        ),
        (
            "Object nesting levels must be two",
            '{"a": 1}',
            False
        ),
        # invalid JSON
        (
            "Any JSON example provided must not exceed two levels of nesting",
            '{"a": {',
            False
        ),
        # min level 2 and max level 3
        (
            "The JSON object must have a maximum of three nesting levels and at least two.",
            '{"a": {"b": 1}}',
            True
        ),
        (
            "The JSON object must have a maximum of three nesting levels and at least two.",
            '{"a": {"b": {"c": 1}}}',
            True
        ),
        (
            "The JSON object must have a maximum of three nesting levels and at least two.",
            '{"a": 1}',
            False
        ),
        (
            "If any JSON object is included, it should not exceed two levels of nesting to maintain simplicity",
            '{"a": {"b": 1}}',
            True
        ),
        (
            "The JSON object nesting levels must not exceed three levels",
            '{"a": {"b": {"c": {"d": 1}}}}',
            False
        ),
        (
            "The answer must be in JSON format with object nesting levels limited to 2",
            '{"a": {"b": {"c": 1}}}',
            False
        ),
        (
            "The answer must include a JSON object with a nesting level of 2 to clearly outline the steps or settings involved",
            '{"a": {"b": 1}}',
            True
        ),
        (
            "The answer must include a JSON object with at least two levels of nesting",
            '{"a": 1}',
            False
        ),
        (
            "The answer must include a JSON object with at least two levels of nesting to organize the information clearly",
            '{"a": {"b": 1}}',
            True
        ),
        (
            "The answer must include a JSON object with at least two levels of nesting to provide detailed information about \"I'd Engine 4.\"",
            '{"game_engine": {"version": "4.27"}}',
            True
        ),
        (
            "The database should be structured in JSON format, with object nesting levels not exceeding three to ensure simplicity and readability",
            '{"db": {"users": {"id": 1}}}',
            True
        ),
        (
            "The explanation should be in JSON format with object nesting levels not exceeding 3",
            '{"a": {"b": {"c": {"d": 1}}}}',
            False
        ),
        (
            "The response must be formatted using JSON, with object nesting levels not exceeding two",
            '{"a": {"b": {"c": 1}}}',
            False
        ),
        (
            "ensure it is formatted in JSON, with the structure not exceeding two levels of object nesting",
            '{"a": {"b": 1}}',
            True
        ),
        (
            "ensure that any JSON data you mention is structured in such a way that it does not exceed two levels of nesting",
            '{"a": {"b": {"c": 1}}}',
            False
        ),
        (
            "ensure that the object nesting levels do not exceed two levels, which means that any JSON object should not contain another object more than one level deep",
            '{"a": {"b": {"c": 1}}}',
            False
        ),
        (
            "ensuring that the JSON structure is limited to a maximum of two object nesting levels, which means that objects within the JSON should not be nested more than twice",
            '{"a": {"b": 1}}',
            True
        ),
        (
            "include a JSON example with exactly two levels of nesting to illustrate the configuration of the parental link program",
            '{"parent": {"child": "data"}}',
            True
        ),
        (
            "include a JSON object that demonstrates the structure of AI concepts, ensuring that this JSON object contains at least two levels of nesting to effectively illustrate the hierarchical nature of these concepts",
            '{"AI": {"concepts": "machine learning"}}',
            True
        ),
        (
            "must provide a JSON example with no more than 2 levels of nesting",
            '{"a": {"b": {"c": 1}}}',
            False
        ),
        (
            "please ensure it is in a JSON format where the object nesting levels do not exceed two levels, as this is crucial for maintaining simplicity and clarity",
            '{"a": {"b": 1}}',
            True
        ),
        (
            "provide your answer in a JSON format that includes a structured explanation with at least two levels of nesting, ensuring clarity and organization",
            '{"a": {"b": {"c": 1}}}',
            True
        ),
        (
            "structured as a JSON object with a nesting level of 2 to clearly organize the information",
            '{"a": {"b": 1}}',
            True
        ),
        (
            "the explanation should be structured in JSON format, ensuring that it does not exceed two levels of nesting",
            '{"a": {"b": {"c": 1}}}',
            False
        ),
        ("If any JSON examples are provided, they must be limited to two levels of nesting to ensure simplicity",
         '{"a": {"b": 1}}', True),
        ("The answer must be structured in JSON format with no more than two levels of nesting to ensure clarity and simplicity.",
         '{"a": {"b": 1}}', True),
        ("The JSON output must not exceed two levels of nesting",
         '{"a": {"b": {"c": 1}}}', False),
        ("The response should be structured as a JSON object with at least two levels of nesting",
         '{"a": {"b": 1}}', True),
        ("ensure it is in JSON format with a maximum of two levels of nesting to maintain clarity and simplicity",
         '{"a": {"b": {"c": 1}}}', False),
        ("the answer must include a JSON example with exactly two levels of nesting",
         '{"a": {"b": 1}}', True),
        ("the data must be structured with at least two levels of nesting",
         '{"Organizations": {"Name": "Org1", "Details": {"Location": "USA", "Focus": "Quantum Threat Remediation"}}}', True)
    ]

    validator = Format_Json()
    for constraint, json_str, expected in test_cases:
        result = validator.check(constraint, json_str)
        assert result == expected, f"""
        Failed Case:
        Constraint: {constraint}
        JSON: {json_str}
        Expected: {expected}
        Actual: {result}
        """
    print("All test cases passed!")
