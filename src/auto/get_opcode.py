import json
import re
import sys

import nltk

nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')

from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.probability import FreqDist
from nltk import pos_tag


def classify_and_sum_verbs(text):
    # Define a list of stopwords
    stopwords = ['is', 'be']

    # Tokenize sentences
    sentences = sent_tokenize(text)

    verb_freq = FreqDist()
    verb_sentence_map = {}

    for idx, sentence in enumerate(sentences):
        # Tokenize words
        words = word_tokenize(sentence)

        # Filter out words with no meaning or single-letter words using a regular expression
        meaningful_words = [word for word in words if re.match(r'\b\w{2,}\b', word) and word.lower() not in stopwords]

        # Part of Speech tagging
        pos_tags = pos_tag(meaningful_words)

        # Filter verbs (VB, VBD, VBG, VBN, VBP, VBZ)
        verbs = [word for word, pos in pos_tags if pos.startswith('VB')]

        # Update verb frequency and store the sentence
        for verb in verbs:
            verb_freq[verb] += 1
            if verb not in verb_sentence_map:
                verb_sentence_map[verb] = [sentence]
            else:
                verb_sentence_map[verb].append(sentence)

    return verb_freq, verb_sentence_map


def parse_file(path, filename):
    with open(path + filename, 'r') as f:
        data = json.load(f)
        for text in data["content"]:
            if text["header"] == "Procedure":
                procedure_text = text["content"]
                verb_frequency, verb_sentence_map = classify_and_sum_verbs(procedure_text)

        result = {
            verb: {"Frequency": freq, "Sentences": sentences}
            for verb, freq in verb_frequency.items()
            for sentences in [verb_sentence_map[verb]]
        }

        with open("../../output/auto/" + "opcode_" + filename + "l", "w", encoding='utf8') as out:
            json.dump(result, out, indent=4)


if __name__ == "__main__":
    f_name = sys.argv[1]
    print("../../protocols/" + f_name)
    parse_file('../../protocols/', f_name)
