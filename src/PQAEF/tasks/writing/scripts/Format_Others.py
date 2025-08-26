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


class Format_Others:
    def __init__(self):
        self.number_words = {
            "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
            "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
        }
        self.rules = [
            (r'no more than (\d+|one|two|three|four|five|six|seven|eight|nine|ten) attributes?',
             self._check_max_attributes),
            (r'must not exceed (\d+|one|two|three|four|five|six|seven|eight|nine|ten)(?:.*)?attributes?',
             self._check_max_attributes),
            (r'Limit the number of attributes to two', self._check_attributes, 2),
            (r'Number of attributes must be exactly (\d+|one|two|three|four|five|six|seven|eight|nine|ten)',
             self._check_attributes),
            (r'must have exactly (\d+|one|two|three|four|five|six|seven|eight|nine|ten) attributes?',
             self._check_attributes),
            (r'must include exactly (\d+|one|two|three|four|five|six|seven|eight|nine|ten) attributes?',
             self._check_attributes),
            (r'at least (\d+|one|two|three|four|five|six|seven|eight|nine|ten) attributes?',
             self._check_min_attributes),
            (r'Must include \'(.*?)\'', self._check_contains_phrase),
            (r'Must be in APA format', self._check_apa_format),
            (r'must be provided in APA format', self._check_apa_format),
            (r'No bullet points', self._check_no_bullets),
            (r'Must be listed as bullet points', self._check_has_bullets),
            (r'is structured as bullet points', self._check_has_bullets),
            (r'block quotes format', self._check_block_quotes),
            (r'be formatted in block quotes', self._check_block_quotes),
            (r'no more than (\d+|one|two|three|four|five|six|seven|eight|nine|ten) rows',
             self._check_table_rows),
            (r'table with no more than (\d+|one|two|three|four|five|six|seven|eight|nine|ten) rows',
             self._check_table_rows),
            (r'a table, which is limited to a maximum of (\d+|one|two|three|four|five|six|seven|eight|nine|ten) rows', self._check_table_rows),
            (r'full sentences', self._check_full_sentences),
            (r'short blurb', self._check_short_blurb),
            (r'The answer must include at least (\d+|one|two|three|four|five|six|seven|eight|nine|ten) references?',
             self._check_min_references),
            (r'No lists', self._check_no_lists),
            (r'No number points', self._check_no_number_points),
            (r'Response must be written at medium length', self._check_medium_length),
        ]

    def check(self, constraint, text):
        for rule in self.rules:
            pattern, handler = rule[0], rule[1]
            args = rule[2:] if len(rule) > 2 else []
            match = re.search(pattern, constraint, flags=re.IGNORECASE)
            if match:
                params = list(match.groups()) + list(args)
                # convert the word to number
                params = [self.number_words.get(p.lower(), p) if isinstance(
                    p, str) and p.lower() in self.number_words else p for p in params]
                return handler(text, *params)
        return False  # default not match

    def _check_attributes(self, text, count):
        return self._check_max_attributes(text, count) and self._check_min_attributes(text, count)

    def _check_max_attributes(self, text, max_count):
        if '```xml' in text:
            match = re.search(r"```xml(.*?)```", text, re.DOTALL)
            if match:
                text = match.group(1)
            else:
                return False

        max_count = int(max_count)
        # match the tag with multiple attributes
        pattern = r"<\s*([a-zA-Z_:][\w:.-]*)\s*(?:\s+[a-zA-Z_:][\w:.-]*=['\"][^'\"]*['\"])*\s*/?>"

        for match in re.finditer(pattern, text):
            tag_content = match.group(0)  # get the whole tag content
            # match the attribute key-value pair
            attrs = re.findall(r"(\w+)=[\"'][^\"']*[\"']", tag_content)
            if len(attrs) > max_count:
                return False
        return True

    def _check_min_attributes(self, text, min_count):
        if '```xml' in text:
            match = re.search(r"```xml(.*?)```", text, re.DOTALL)
            if match:
                text = match.group(1)
            else:
                return False

        min_count = int(min_count)
        # match the tag with multiple attributes
        pattern = r"<\s*([a-zA-Z_:][\w:.-]*)\s*(?:\s+[a-zA-Z_:][\w:.-]*=['\"][^'\"]*['\"])*\s*/?>"

        for match in re.finditer(pattern, text):
            tag_content = match.group(0)  # get the whole tag content
            # match the attribute key-value pair
            attrs = re.findall(r"(\w+)=[\"'][^\"']*[\"']", tag_content)
            if len(attrs) < min_count:
                return False
        return True

    def _check_contains_phrase(self, text, phrase):
        return bool(re.search(r'\b' + re.escape(phrase) + r'\b', text, flags=re.IGNORECASE))

    def _check_apa_format(self, text):
        return bool(re.search(r'\(\s*\w+,\s*\d{4}\s*\)', text))

    def _check_no_bullets(self, text):
        return not re.search(r'^\s*[-*]', text, flags=re.MULTILINE)

    def _check_has_bullets(self, text):
        return bool(re.search(r'^\s*[-*]', text, flags=re.MULTILINE))

    def _check_block_quotes(self, text):
        return bool(re.search(r'^>', text, flags=re.MULTILINE)) or '<blockquote>' in text.lower()

    def _check_table_rows(self, text, max_rows):
        max_rows = int(max_rows)
        md_rows = re.findall(r'^\|.*\|$', text, flags=re.MULTILINE)
        separator = re.compile(r'^\|(\s*-+\s*\|)+$')
        data_rows = [row for row in md_rows if not separator.match(row)]
        html_rows = text.lower().count('<tr>')
        return len(data_rows) <= max_rows and html_rows <= max_rows

    def _check_full_sentences(self, text):
        return True

    def _check_short_blurb(self, text):
        return len(text) <= 200

    def _check_no_lists(self, text):
        # Matches numbered lists (1., 2., etc.)
        return not re.search(r'^\s*(\d+\.)\s', text, flags=re.MULTILINE)

    def _check_no_number_points(self, text):
        # Matches lists with number points (1., 2., etc.)
        return not re.search(r'^\s*\d+\.', text, flags=re.MULTILINE)

    def _check_medium_length(self, text):
        return 200 < len(text) <= 400

    def _check_min_references(self, text, min_references):
        min_references = int(min_references)

        # Match references like [1], [2], ... or (Author, year)
        # Match citations like [1], [2], [3], or (Smith, 2020)
        pattern = r'(\[\d+\]|\([A-Za-z]+, \d{4}\))'
        references = re.findall(pattern, text)

        # If the number of references is greater than or equal to the minimum required
        return len(references) >= min_references


if __name__ == "__main__":

    # Test cases covering all CSV constraints
    test_cases = [
        ("The answer must include at least 10 references.",
         "This is a text with [1], [2], [3], [4], [5], [6], [7], [8], [9], [10] references.", True),
        ("The answer must include at least 10 references.",
         "This text has [1], [2], [3], [4], [5] references.", False),
        ("The answer must include at least 10 references.",
         "No references here.", False),
        ("No bullet points", "This text has no bullets.", True),
        ("No bullet points", "* This text has bullets.", False),
        ("No lists", "1. Item 1", False),
        ("No lists", "Just regular text.", True),
        ("No number points", "1. Point", False),
        ("No number points", "This is not a numbered point.", True),
        ("Response must be written as a short blurb", "Short blurb.", True),
        ("Response must be written as a short blurb",
         "This is a text longer than 150 characters" * 30, False),
        ("Response must be written at medium length",
         "This is a medium-length text " * 10, True),
        ("Response must be written at medium length", "Short", False),
        # Attribute count constraints
        ("Each slide in the presentation must not exceed three visual elements or attributes, such as images, timelines, or quotes.",
         "<element a='1' b='2' c='3'/>", True),
        ("Each slide in the presentation must not exceed three visual elements or attributes, such as images, timelines, or quotes.",
         "<element a='1' b='2' c='3' d='4'/>", False),
        ("Each XML element must have no more than three attributes",
         "<element a='1' b='2' c='3'/>", True),
        ("Each XML element must have no more than three attributes",
         "<element a='1' b='2' c='3' d='4'/>", False),
        ("Number of attributes must be exactly 5",
         "<element a='1' b='2' c='3' d='4' e='5/>", True),
        ("Number of attributes must be exactly 5",
         "<element a='1' b='2' c='3' d='4'/>", False),
        ("Must describe the XML data structure with at least 5 attributes",
         "<a x='1' y='2' z='3' w='4' v='5'/>", True),
        ("Must describe the XML data structure with at least 5 attributes",
         "<a x='1'/>", False),
        ("Limit the number of attributes to two when describing each comic",
         "<comic title='x' author='y'/>", True),
        ("Limit the number of attributes to two when describing each comic",
         "<comic title='x'/>", False),
        ("limit the number of attributes to two when describing each comic in XML format",
         "<comic title='x' author='y'/>", True),
        ("limit the number of attributes to two when describing each comic in XML format",
         "<comic title='x'/>", False),

        ("Each XML element must have no more than 10 attributes",
         "To identify the language of an audio file in an unknown African language, you can follow these steps, using JSON and XML as specified in your request:\n\n### Step 1: Upload the Audio File to a Service\nFirst, you need to upload the audio file to a service that can transcribe or analyze it. Many cloud-based services offer this functionality. For example, you can use Alibaba Cloud's Speech Recognition Service.\n\n### Step 2: Transcribe the Audio\nUse the service to transcribe the audio into text. This step may require specifying some parameters, such as the format of the audio file and the expected language. Since the language is unknown, you might need to use a service that supports multiple languages or has an automatic language detection feature.\n\n### Step 3: Analyze the Transcribed Text\nOnce the text is transcribed, you can use a language detection API to determine the language of the text. This can be done using various online tools or APIs that support multiple languages, including African languages.\n\n### Step 4: Use JSON for Structuring the Data\nTo keep the data structured and maintainable, use JSON to manage the data. Here’s an example of how you can structure the data in JSON:\n\n```json\n{\n  \"audioFile\": {\n    \"fileName\": \"unknown_language_audio.wav\",\n    \"fileFormat\": \"wav\",\n    \"uploadDate\": \"2023-10-05T10:00:00Z\"\n  },\n  \"transcription\": {\n    \"serviceUsed\": \"AlibabaCloudSpeechRecognition\",\n    \"transcribedText\": \"The transcribed text from the audio file...\"\n  },\n  \"languageDetection\": {\n    \"serviceUsed\": \"GoogleLanguageDetectionAPI\",\n    \"detectedLanguage\": \"Swahili\",\n    \"languageCode\": \"sw\",\n    \"confidenceScore\": 0.95\n  }\n}\n```\n\n### Step 5: Use XML for Detailed Data Representation\nFor a detailed and consistent data representation, you can use XML as specified. Here’s an example of how you can structure the data in XML with exactly 5 attributes:\n\n```xml\n<LanguageDetectionResult\n  file=\"unknown_language_audio.wav\"\n  format=\"wav\"\n  service=\"AlibabaCloudSpeechRecognition\"\n  detectedLanguage=\"Swahili\"\n  confidenceScore=\"0.95\">\n  <TranscribedText>\n    The transcribed text from the audio file...\n  </TranscribedText>\n</LanguageDetectionResult>\n```\n\n### Summary\n1. **Upload the audio file** to a transcription service.\n2. **Transcribe the audio** to text.\n3. **Analyze the text** using a language detection API.\n4. **Structure the data** using JSON with nesting levels not exceeding 3.\n5. **Represent detailed data** using XML with exactly 5 attributes.\n\nBy following these steps, you should be able to identify the language of the audio file and manage the data in a structured and consistent manner.", True),
        # Phrase inclusion
        ("Must include 'key'", "The key is present", True),
        ("Must include 'key'", "No keyword here", False),
        # APA format
        ("Must be in APA format", "According to (Smith, 2020).", True),
        ("Must be in APA format", "No citations.", False),
        ("References must be provided in APA format",
         "According to (Smith, 2020).", True),
        ("References must be provided in APA format", "No citations.", False),
        # Bullet points
        ("No bullet points", "Line without bullets.", True),
        ("No bullet points", "* Bullet point", False),
        ("Must be listed as bullet points", "* Item 1\n* Item 2", True),
        ("Must be listed as bullet points", "Item 1\nItem 2", False),
        ("Ensure that the response is structured as bullet points",
         "* Item 1\n* Item 2", True),
        ("Ensure that the response is structured as bullet points",
         "Item 1\nItem 2", False),
        # Block quotes
        ("The quotes must be presented in block quotes format", "> Quote", True),
        ("The quotes must be presented in block quotes format", "Regular quote.", False),
        ("the quotes should be formatted in block quotes using Markdown, as specified", "> Quote", True),
        ("the quotes should be formatted in block quotes using Markdown, as specified",
         "Regular quote.", False),
        # Table rows
        ("The answer must include a table with no more than 3 rows", "|A|\n|B|\n|C|", True),
        ("The answer must include a table with no more than 3 rows",
         "|A|\n|B|\n|C|\n|D|", False),
        ("the answer should include a table, which is limited to a maximum of 3 rows, to present relevant information concisely", "|A|\n|B|\n|C|", True),
        ("the answer should include a table, which is limited to a maximum of 3 rows, to present relevant information concisely",
         "|A|\n|B|\n|C|\n|D|", False),
        # Full sentences
        ("The answer must be in full sentences", "Hello. World!", True),
        # Short blurb
        ("Response must be written as a short blurb", "Short text.", True),
        ("Response must be written as a short blurb", "Long text" * 50, False),
        ("the response should be concise, resembling a short blurb", "Short text.", True),
        ("the response should be concise, resembling a short blurb",
         "Long text" * 50, False),
    ]

    # Execute tests
    validator = Format_Others()
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
