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
from zhconv import convert


class Language_Chinese:
    def __init__(self):
        self.rules = [
            {
                'pattern': re.compile(r'Must include the phrase "{1,2}(.+?)"{1,2}', re.IGNORECASE),
                'handler': self._handle_phrase
            },
            {
                'pattern': re.compile(r'Must write the name "Shen Lim" in Simplified Chinese', re.IGNORECASE),
                'handler': self._handle_shen_lim
            },
            {  # key fix: expand the regex to match "convert into"
                'pattern': re.compile(r'Must (?:use|convert into|be converted into) Traditional Chinese characters', re.IGNORECASE),
                'handler': self._handle_entirely_traditional
            },
            {
                'pattern': re.compile(r'include .*?Traditional Chinese characters', re.IGNORECASE),
                'handler': self._handle_has_traditional
            },
            {
                'pattern': re.compile(r'use .*?Traditional Chinese characters', re.IGNORECASE),
                'handler': self._handle_has_traditional
            },
            {
                'pattern': re.compile(r'使用繁體中文', re.IGNORECASE),
                'handler': self._handle_has_traditional
            },
            {
                'pattern': re.compile(r'(The answer must ){0,1}include some content in Simplified Chinese', re.IGNORECASE),
                'handler': self._handle_has_simplified
            },
            {
                'pattern': re.compile(r'Use Simplified Chinese characters', re.IGNORECASE),
                'handler': self._handle_has_simplified
            },
            {
                'pattern': re.compile(r'(?:must be|must use|must write|must be presented|answer must be|essential|is|should be|必须|请|需要) {0,1}(?:in|provided in|written in|to use|conducted in|用|使用|提供|书写|翻译为|将文本翻译为) {0,1}(?:Simplified Chinese|简体中文)', re.IGNORECASE),
                'handler': self._handle_has_simplified
            },
            {
                'pattern': re.compile(r'用中文简体描述', re.IGNORECASE),
                'handler': self._handle_has_simplified
            },
            {
                'pattern': re.compile(r'Names must be in Simplified Chinese', re.IGNORECASE),
                'handler': self._handle_has_simplified
            },
            {
                'pattern': re.compile(r'Must translate the text into Simplified Chinese', re.IGNORECASE),
                'handler': self._handle_entirely_simplified
            },
            {
                'pattern': re.compile(r'Simplified', re.IGNORECASE),
                'handler': self._handle_has_simplified
            }
        ]

    def check(self, constraint, text):
        for rule in self.rules:
            match = rule['pattern'].search(constraint)
            if match:
                groups = match.groups()
                return rule['handler'](text, *groups)
        return False

    def _handle_phrase(self, text, phrase, *args):
        return phrase in text

    def _handle_shen_lim(self, text, *args):
        return '沈林' in text

    def _handle_entirely_traditional(self, text, *args):
        return self._is_entirely_traditional(text)

    def _handle_has_traditional(self, text, *args):
        return self._has_traditional_chars(text)

    def _handle_has_simplified(self, text, *args):
        return self._has_simplified_chars(text)

    def _handle_entirely_simplified(self, text, *args):
        return self._is_entirely_simplified(text)

    def _is_entirely_simplified(self, text):
        if re.search(r'[A-Za-z]', text):
            return False
        return convert(text, 'zh-cn') == text

    def _is_entirely_traditional(self, text):
        if re.search(r'[A-Za-z]', text):
            return False
        return convert(text, 'zh-tw') == text

    def _has_traditional_chars(self, text):
        return any(convert(c, 'zh-cn') != c for c in text)

    def _has_simplified_chars(self, text):
        return any(convert(c, 'zh-tw') != c for c in text)


if __name__ == "__main__":
    # test cases
    test_cases = [
        ("The text must be in simplified Chinese characters", "这是简体", True),
        ("The text must be in simplified Chinese characters", "你好嗎？我不會號", False),
        ("Use Simplified Chinese characters", "这是简体", True),
        ("Use Simplified Chinese characters", "你好嗎？我不會號", False),
        ("Any Chinese terms or examples must be written in Simplified Chinese", "这是简体", True),
        ("Any Chinese terms or examples must be provided in Simplified Chinese", "這是繁體", False),
        # include specific phrase
        (
            'Must include the phrase "中国是一个国家" meaning "China is a country" in Simplified Chinese.',
            '中国是一个国家',
            True
        ),
        (
            'Must include the phrase "中国是一个国家" meaning "China is a country" in Simplified Chinese.',
            '中国',
            False
        ),
        # must use simplified Chinese
        (
            'The answer must be in Simplified Chinese.',
            '这是简体',
            True
        ),
        (
            'The answer must be in Simplified Chinese.',
            '這是繁體',
            False
        ),
        (
            'The answer must be in Simplified Chinese.',
            'This is English',
            False
        ),
        # must include traditional characters (e.g. verb conjugations)
        (
            'Must include conjugations in Traditional Chinese characters',
            '喜歡',
            True
        ),
        (
            'Must include conjugations in Traditional Chinese characters',
            '喜欢',
            False
        ),
        (
            'Must include conjugations in Traditional Chinese characters',
            'Like',
            False
        ),
        # must use traditional characters
        (
            'Must use Traditional Chinese characters',
            '這是繁體字',
            True
        ),
        (
            'Must use Traditional Chinese characters',
            '这是简繁混合',
            False
        ),
        # must write Shen Lim
        (
            'Must write the name "Shen Lim" in Simplified Chinese',
            '沈林',
            True
        ),
        (
            'Must write the name "Shen Lim" in Simplified Chinese',
            'Shen Lim',
            False
        ),
        # must include some simplified characters
        (
            'The answer must include some content in Simplified Chinese.',
            '這有繁體字和简体字',
            True
        ),
        (
            'The answer must include some content in Simplified Chinese.',
            '全部都是繁體字',
            False
        ),
        (
            'The answer must include some content in Simplified Chinese.',
            'All is English',
            False
        ),
        # names must be simplified (视为整体检查)
        (
            'Names must be in Simplified Chinese',
            '张三',
            True
        ),
        (
            'Names must be in Simplified Chinese',
            '張三',
            False
        ),
        (
            'The sentence must be converted into Traditional Chinese characters.',
            '這是繁體字',
            True
        ),
        (
            'The sentence must be converted into Traditional Chinese characters.',
            '这是简体',
            False
        ),
        (
            'The sentence must be converted into Traditional Chinese characters.',
            'Mixed 繁體 and English',
            False
        ),
        # new test cases
        ("The answer must be provided in Simplified Chinese", "这是简体", True),
        ('"The answer must include the phrase ""中国是一个国家"" meaning ""China is a country"" in Simplified Chinese"', "中国是一个国家", True),
        ('"The answer must include the phrase ""中国是一个国家"" meaning ""China is a country"" in Simplified Chinese."', "中国是一个国家", True),
        ("the answer must be provided in Simplified Chinese", "这是简体", True),
        ("the text must be in Simplified Chinese characters", "这是简体", True),
        ("List some conjugations for 'to read' in Mandarin Chinese. The response must include the conjugations in Traditional Chinese characters", "喜歡", True),
        # ("Must provide the names of the villains in Simplified Chinese characters", "反派", True),
        ("The answer must be provided in Simplified Chinese", "这是简体", True),
        ("The answer must be provided in Simplified Chinese.", "这是简体", True),
        # ('"The names of these doctors should be presented in Simplified Chinese, reflecting their cultural and linguistic background"', "张医生", True),
        ("include some content in Simplified Chinese", "这是简体", True),
        ('"it is essential to use Simplified Chinese, ensuring that the language used aligns with this requirement"', "这是简体", True),
        ("please ensure that the response is provided in Simplified Chinese", "这是简体", True),
        ("the answer must be provided in Simplified Chinese", "这是简体", True),
        ("the answer should be provided in Simplified Chinese to ensure it meets the language requirement", "这是简体", True),
        ('"the answer should be provided in Simplified Chinese, ensuring that the language requirement is met"', "这是简体", True),
        ('"the communication must be conducted in Simplified Chinese, ensuring that the language used is not Traditional Chinese"', "这是简体", True),
        ("回答必须使用简体中文", "这是简体", True),
        ("回答必须用简体中文书写", "这是简体", True),
        ("回答必须用简体中文提供", "这是简体", True),
        ("必须将文本翻译为简体中文", "这是简体", True),
        ('"答案必須使用繁體中文,以反映台灣所使用的語言"', "这是简体", False),
        ('"请注意,问题必须用简体中文书写"', "这是简体", True),
        ("请用中文简体描述", "这是简体", True),

        ("the response must be provided in Simplified Chinese.",
         "### 解释\n| 翻译 | 这个标的知识疯了 |\n| --- | --- |", True),
        ("the response must be provided in Simplified Chinese", "Chinese idiom", False),
        ("the response must be provided in Simplified Chinese",
         "### 解释\n| 词语 | 意思 |\n| --- | --- |\n| 这个标子疯了 | 这个Chinese idiom形容某人行为异常疯狂. |", True),
        ("答案必須使用繁體中文", "台灣的中文與中國大陸的中文存在差異，主要源於歷史、政治和文化因素。自1949年國民政府遷台後，台灣保持了繁體字的使用，而中國大陸推行簡體字。此外，兩地在詞彙、語法和發音上也逐漸發展出各自的特色。這些差異反映了兩地分隔後各自發展的獨特社會環境。", True),
        ("The answer must be provided in Simplified Chinese.",
         "Mulan的故事背景设定在北魏时期，这个时期是中国历史上一个重要的阶段，Mulan的传奇故事就发生在这个动荡的时代。", True),


    ]

    # execute the test
    validator = Language_Chinese()
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
