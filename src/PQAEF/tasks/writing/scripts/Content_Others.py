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


class Content_Others:
    def __init__(self):
        self.emoji_pattern = re.compile(
            r'['
            '\U0001F600-\U0001F64F'  # emoticons
            '\U0001F300-\U0001F5FF'  # symbols & pictographs
            '\U0001F680-\U0001F6FF'  # transport & map symbols
            '\U0001F700-\U0001F77F'  # alchemical symbols
            '\U0001F780-\U0001F7FF'  # Geometric Shapes Extended
            '\U0001F800-\U0001F8FF'  # Supplemental Arrows-C
            '\U0001F900-\U0001F9FF'  # Supplemental Symbols and Pictographs
            '\U0001FA00-\U0001FA6F'  # Chess Symbols
            '\U0001FA70-\U0001FAFF'  # Symbols and Pictographs Extended-A
            '\U00002702-\U000027B0'  # Dingbats
            '\U000024C2-\U0001F251'  # Enclosed characters
            # Supplementary Multilingual Plane (may include rare emojis)
            '\U00010000-\U0010FFFF'
            ']+', flags=re.UNICODE
        )

    def check(self, constraint, text):
        if constraint == "Keep it a paragraph long":
            # calculate the number of line breaks in the text
            line_count = text.count("\n")
            # if the number of line breaks is greater than 0, then there are multiple paragraphs
            return line_count == 0

        # process the start identifier
        start_match = re.match(
            r"Start identifier( must be|:)(?:.*)?\s'([^']+)'", constraint)

        if "Each example must start with" in constraint:
            expected_start = start_match.group(2)
            return expected_start in text

        if start_match:
            expected_start = start_match.group(2)
            return text.lstrip(' #').lower().startswith((expected_start.lower()))

        # process the start identifier
        start_match = re.search(
            r"(?:Start|start|begin|it is essential to start) (?:with|by) the (?:identifier|phrase) '?([^']+)'?", constraint, re.IGNORECASE)
        if start_match:
            expected_start = start_match.group(1)
            return text.lstrip(' #').lower().startswith((expected_start.lower()))

        # process the end identifier
        if constraint == "End identifier: Sources must be cited at the end of the response":
            return bool(re.search(r'Sources:\s*.+$', text.strip()))

        # process the end identifier
        if constraint == "make sure to conclude your response by citing your sources, as this is a crucial part of the answer":
            return bool(re.search(r'Sources:\s*.+$', text.strip()))

        # process the showroom name starting with a specific letter
        showroom_match = re.match(
            r"The name of the showroom must start with the letter '([A-Za-z])'\.", constraint)
        if showroom_match:
            letter = showroom_match.group(1).upper()
            return bool(re.search(rf'\b{letter}[a-zA-Z]*\b', text))

        # process the short blurb
        if constraint in [
            "Response must be written as a short blurb",
            "ensure that the response is written as a short blurb",
            "ensure the response is a short blurb",
            "The response must be short and simple",
        ]:
            return len(text) <= 200

        if constraint == "The response should be concise, with a maximum of 50 words":
            return len(text.split()) <= 50

        # process the sentence with at least three emojis
        if constraint == "Each sentence must include at least three emojis.":
            # use forward lookahead to split sentences, ensuring that the emoji belongs to the correct sentence
            sentences = re.split(r'(?<=[.!?])\s+(?=\S)', text)
            # print(sentences)
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                emojis = self.emoji_pattern.findall(sentence)
                if len(emojis) < 3:
                    return False
            return True

        # process the must include keyword
        mention_match = re.search(
            r"[Mm]ust mention (.+) and the (.+)", constraint)
        if mention_match:
            keyword1 = mention_match.group(1)
            keyword2 = f"the {mention_match.group(2)}"
            return keyword1 in text and keyword2 in text

        # process the must include quotes
        if constraint == "Must include quotes from the sources" or constraint == "with quotes from these sources":
            return bool(re.search(r'["“”‘’\']', text))

        # process the must provide source reference
        if constraint == "Must provide sources that are cited" or constraint == "The response must include sources that are cited":
            return bool(re.search(r'Sources:\s*.+$', text) and re.search(r'\[\d+\]', text))

        # process the in-text citations
        if constraint == "It must include in-text citations":
            # 形如 [1] 或 (Smith, 2020)
            return bool(re.search(r'\[\d+\]|\([A-Za-z]+, \d{4}\)', text))

        if "be in full sentences" in constraint:
            return True

        return False


if __name__ == "__main__":

    # test cases
    test_cases = [
        ("Keep it a paragraph long",
         "This is a single paragraph without any line breaks.", True),
        ("Keep it a paragraph long",
         "This is the first paragraph.\nThis is the second paragraph.", False),
        ("Start identifier: Each example must start with the word 'Example:'", "nope", False),
        ("Start identifier: Each example must start with the word 'Example:'",
         "Example: aha \n Example: nope", True),
        ("Start identifier must be 'Absolutely! Here's'",
         "Absolutely! Here's the response", True),
        ("Start identifier must be 'Absolutely! Here's'", "Wrong start", False),
        ("it is essential to start with the phrase 'Absolutely! Here's'",
         "Absolutely! Here's the response", True),
        ("it is essential to start with the phrase 'Absolutely! Here's'",
         "Wrong start", False),
        ("Start identifier: 'List of Models:'",
         "List of Models: model1, model2", True),
        ("Start identifier: 'List of Models:'", "No match here", False),
        ("Start with the identifier 'List of Models:' to clearly structure the information",
         "List of Models: model1, model2", True),
        ("Start with the identifier 'List of Models:' to clearly structure the information",
         "No match here", False),
        ("begin with the identifier 'The following are free government grant websites:'",
         "The following are free government grant websites: website1, website2", True),
        ("begin with the identifier 'The following are free government grant websites:'",
         "Government grant list:", False),
        ("the response should begin with the identifier 'The following are free government grant websites:'",
         "The following are free government grant websites: website1, website2", True),
        ("the response should begin with the identifier 'The following are free government grant websites:'",
         "Government grant list:", False),

        # process the end identifier
        ("End identifier: Sources must be cited at the end of the response",
         "Text\nSources: [source1]", True),
        ("End identifier: Sources must be cited at the end of the response",
         "No sources here", False),

        # process the showroom name starting with a specific letter
        ("The name of the showroom must start with the letter 'P'.",
         "Visit Pristine Showroom", True),
        ("The name of the showroom must start with the letter 'P'.",
         "Best Showroom", False),

        ("make sure to conclude your response by citing your sources, as this is a crucial part of the answer",
         "Some information. Sources: Reference1.", True),
        ("make sure to conclude your response by citing your sources, as this is a crucial part of the answer",
         "No sources mentioned.", False),

        # process the short blurb
        ("Response must be written as a short blurb", "A" * 150, True),
        ("Response must be written as a short blurb", "A" * 250, False),
        ("ensure that the response is written as a short blurb",
         "Brief summary here.", True),
        ("ensure the response is a short blurb",
         "A detailed and lengthy explanation that is not a short blurb.", True),
        ("The response should be concise, with a maximum of 50 words",
         "This text is under 50 words, so it should be valid.", True),
        ("The response should be concise, with a maximum of 50 words", "A " * 100, False),

        # process the must include keyword
        ("Must mention old steam trains and the famous DNA model",
         "old steam trains and the famous DNA model", True),
        ("Must mention old steam trains and the famous DNA model",
         "only old steam trains", False),
        ("It must mention old steam trains and the famous DNA model",
         "old steam trains and the famous DNA model", True),
        ("It must mention old steam trains and the famous DNA model",
         "only old steam trains", False),

        # process the must include quotes
        ("Must include quotes from the sources", "He said 'quote'", True),
        ("Must include quotes from the sources", "No quotes", False),
        ("with quotes from these sources", "He said 'quote'", True),
        ("with quotes from these sources", "No quotes", False),

        # process the must provide source reference
        ("Must provide sources that are cited",
         "Cite [1]. Sources: [1] ref", True),
        ("Must provide sources that are cited", "No sources", False),
        ("The response must include sources that are cited",
         "Cite [1]. Sources: [1] ref", True),
        ("The response must include sources that are cited", "No sources", False),

        # process the in-text citations
        ("It must include in-text citations",
         "This is an argument supported by previous research [1].", True),
        ("It must include in-text citations",
         "According to (Smith, 2020), this is important.", True),
        ("It must include in-text citations", "There is no citation here.", False),

        ("The answer must start with the identifier 'List of Models:'",
         "## List Of Models: Chat GPT Models\n\nChat GPT Models Are Available In Various Versions, Each With Different Capabilities And Features.", True)
    ]

    # execute the test
    validator = Content_Others()
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
