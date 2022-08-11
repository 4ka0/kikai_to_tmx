#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Explanatory docstring.
"""

import sys
import deepl
from docx import Document
from environs import Env


class Segment():
    def __init__(self, source_text, target_text):
        self.source_text = source_text
        self.target_text = target_text


def check_user_input(user_input):

    format_message = (
        "Expected input: python3 translate.py translation.docx glossary.txt\n"
        "(glossary.txt is optional.)\n"
    )

    # Should be 2 or 3 args
    if len(user_input) < 2 or len(user_input) > 3:
        print("\nError: Incorrect number of arguments.")
        print(format_message)
        return False, None, None

    # 2nd arg should be a docx file
    translation_file = user_input[1]
    if not translation_file.lower().endswith('.docx'):
        print("\nError: Second argument should be a docx file.")
        print(format_message)
        return False, None, None

    # 3rd arg, if present, should be a txt file
    if len(user_input) == 3:
        glossary_file = user_input[2]
        if not glossary_file.lower().endswith('.txt'):
            print("\nError: Third argument should be a txt file.")
            print(format_message)
            return False, None, None
    else:
        glossary_file = None

    return True, translation_file, glossary_file


def setup_deepl_translator():
    env = Env()
    env.read_env()
    auth_key = env.str("AUTH_KEY")
    translator = deepl.Translator(auth_key)
    return translator


def get_source_segments(source_file):
    """
    Reads in text from user-specified docx file.
    File is already split into paragraphs by Document module.
    Text is further split into sentences if a paragraph contains multiple sentences.
    """
    document = Document(source_file)
    segments = []

    for para in document.paragraphs:

        # Split again if paragraph contains multiple sentences.
        if para.text.count("。") >= 2:
            sentences = para.text.split("。")

            for sentence in sentences:
                # Add each single sentence to source_segments list.
                # However, if "。" appears at the end of a string, split() creates an empty string
                # representing the substring that follows "。". Using "if sentence" skips such
                # empty strings. Also, split() removes the "。" delim, so have to add this back on.
                if sentence:
                    segment = Segment(source_text=sentence + "。", target_text="")
                    segments.append(segment)
        else:
            segment = Segment(source_text=para.text, target_text="")
            segments.append(segment)

    return segments


def get_source_char_count(source_segments):
    source_strings = [segment.source_text for segment in source_segments]
    char_count = sum(len(i) for i in source_strings)
    return char_count


def check_deepl_usage(source_char_count, translator):
    """
    The monthly limit for the free API is 500000.
    This is set to 499900 to create a buffer of 100 character to allow for
    potential differences in how characters are counted.
    """
    monthly_limit = 499900
    usage = translator.get_usage()
    if source_char_count + usage.character.count >= monthly_limit:
        return False
    return True


def translate_segments(translator, segments, glossary_file):
    """
    Obtains translations for source_segments by calling the DeepL API.
    Returns list of Segment objects with the source_text and target_text
    attributes populated.
    """
    for segment in segments:
        target_text = translator.translate_text(
            segment.source_text,
            source_lang="JA",
            target_lang="en-US",
        )
        segment.target_text = target_text

    return segments


if __name__ == "__main__":

    valid, source_file, glossary_file = check_user_input(sys.argv)

    if valid:
        translator = setup_deepl_translator()
        source_segments = get_source_segments(source_file)
        source_char_count = get_source_char_count(source_segments)

        if check_deepl_usage(source_char_count, translator):
            full_segments = translate_segments(translator, source_segments, glossary_file)

        for segment in full_segments:
            print()
            print(segment.source_text)
            print(segment.target_text)
