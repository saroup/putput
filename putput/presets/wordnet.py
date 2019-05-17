import re
import random
from typing import Sequence
from typing import Mapping
from typing import Tuple
from typing import Iterable
from collections import defaultdict

def _concatenate_groups(groups: Sequence[str]) -> str:
    return '|'.join(groups)

def extract_words(concatenated_groups: str) -> Iterable[Tuple[int, int]]:
    num_parens = 0
    for i, char in enumerate(concatenated_groups):
        if char == '(':
            num_parens += 1
            if num_parens == 2:
                start = i + 1
        if char == ')':
            num_parens -= 1
            if num_parens == 1:
                end = i
                yield start, end

def extract_tokens(concatenated_groups: str) -> Iterable[str]:
    for i, char in enumerate(concatenated_groups):
        if char == '[':
            start = i
        if char == ']':
            end = i + 1
            yield concatenated_groups[start: end]

def extract_word_positions(concatenated_groups: str) -> Mapping[str, Tuple[int, int]]:
    word_positions = defaultdict(list)
    for m in extract_words(concatenated_groups):
        start, end = m
        print(start, end)
        words = concatenated_groups[start:end].split()
        prev_start = start
        for word in words:
            word_positions[word].append((prev_start, prev_start+len(word)))
            prev_start += len(word) + 1
    return word_positions

def replace_words(utterance: str,
                  concatenated_groups: str,
                  word_positions: Mapping[str, Tuple[int, int]]
                  ) -> Tuple[str, str]:
    reverse_utterance = utterance.split(' ')[::-1]
    for i, word in enumerate(reverse_utterance):
        synonym = _get_synonym(word, 20)
        reverse_utterance[i] = synonym
        start, end = word_positions[word].pop()
        concatenated_groups = concatenated_groups[:start] + synonym + concatenated_groups[end:]
    return ' '.join(reverse_utterance[::-1]), concatenated_groups
    
def _get_synonym(word: str, chance: float) -> str:
    if random.random() < (chance / 100):
        # TODO: Wordnet goes here
        return "synonym!"
    return word


# def replace_with_synonyms(utterance: str,
#                           handled_tokens: Sequence[str],
#                           handled_groups: Sequence[str]
#                           ) -> Tuple[str, Sequence[str], Sequence[str]]:
#     label_extractor = lambda s: s[s.index('{') + 1: s.index('(')]
#     ents = _convert_to_ents(utterance, handled_groups, label_extractor)
#     return utterance, handled_tokens, ents


if __name__ == '__main__':
    # steps:
    # 1) concatenate the groups
    # 2) get the position in the concatenated groups of every word
    # 3) iterate over the utterance IN REVERSE and replace the words in the utterance with a synonym
    # 4) replace the words in the concatenated group string, according to their position
    # 5) extract the tokens from the group
    # 6) return the utterance, tokens and group
    utterance = 'hi he will play want to play'
    handled_groups = ('{None([WAKE(hi)])}', '{PLAY_PHRASE([START(he will play want)] [PLAY(to play)])}')
    concatenated_groups = _concatenate_groups(handled_groups)
    word_positions = extract_word_positions(concatenated_groups)
    new_utterance, groups = replace_words(utterance, concatenated_groups, word_positions)
    print(new_utterance, list(extract_tokens(groups)), groups)

    # TODO: - extract tokens from groups so we can return utterance, groups, and tokens
    #       - use nltk part of speech tagger for the synonyms
