import random
from pathlib import Path
from typing import Mapping # pylint: disable=unused-import
from typing import Tuple
from typing import Union # pylint: disable=unused-import

from putput import CombinationOptions
from putput import Pipeline
from putput.types import AFTER_FLOW_HOOKS # pylint: disable=unused-import
from putput.types import BEFORE_FLOW_HOOKS # pylint: disable=unused-import
from putput.types import HANDLED_TOKEN
from putput.types import HANDLED_TOKENS
from putput.types import HASHABLE_TOKENS # pylint: disable=unused-import
from putput.types import TOKEN
from putput.types import TOKEN_PHRASE
from putput.types import TOKENS
from putput.types import UTTERANCE
from putput.types import UTTERANCE_COMBINATION


def _include_phrase(token: TOKEN, phrase: TOKEN_PHRASE) -> HANDLED_TOKEN:
    return '[{token}({phrase})]'.format(token=token, phrase=phrase)

def _sample_utterance_combination(utterance_combination: UTTERANCE_COMBINATION,
                                  tokens: TOKENS,
                                  token_to_sample: TOKEN,
                                  sample_size: int,
                                  ) -> Tuple[UTTERANCE_COMBINATION, TOKENS]:
    TOKEN_INDEX = tokens.index(token_to_sample)
    utterance_combination_list = list(utterance_combination)
    sampled_combinations = tuple(random.sample(utterance_combination_list.pop(TOKEN_INDEX), sample_size))
    utterance_combination_list.insert(TOKEN_INDEX, sampled_combinations)
    utterance_combination = tuple(utterance_combination_list)
    return utterance_combination, tokens

def _sample_play(utterance_combination: UTTERANCE_COMBINATION,
                 tokens: TOKENS,
                 ) -> Tuple[UTTERANCE_COMBINATION, TOKENS]:
    return _sample_utterance_combination(utterance_combination, tokens, 'PLAY', 2)

def _sample_artist(utterance_combination: UTTERANCE_COMBINATION,
                   tokens: TOKENS,
                   ) -> Tuple[UTTERANCE_COMBINATION, TOKENS]:
    return _sample_utterance_combination(utterance_combination, tokens, 'ARTIST', 1)

def _add_random_words(utterance: UTTERANCE,
                      handled_tokens: HANDLED_TOKENS
                      ) -> Tuple[UTTERANCE, HANDLED_TOKENS]:
    utterances = utterance.split()
    random_words = ['hmmmm', 'uh', 'um', 'please']
    insert_index = random.randint(0, len(utterances))
    random_word = random.choice(random_words)
    utterances.insert(insert_index, random_word)
    utterance = ' '.join(utterances)
    return utterance, handled_tokens

def main() -> None:
    pattern_definition_path = Path(__file__).parent / 'patterns.yml'
    dynamic_token_patterns_map = {
        'SONG': ((('here comes the sun', 'stronger'),),)
    }
    token_handler_map = {
        'WAKE': _include_phrase,
        'SONG': _include_phrase,
    }

    utterance_pattern_tokens_to_combination_options = {
        'DEFAULT': CombinationOptions(max_sample_size=5, with_replacement=False, seed=0)
    } # type: Mapping[Union[TOKEN, HASHABLE_TOKENS], CombinationOptions]

    before_flow_hooks = {
        ('PLAY', 'ARTIST'): (_sample_play, _sample_artist)
    } # type: Mapping[Union[TOKEN, HASHABLE_TOKENS], BEFORE_FLOW_HOOKS]

    after_flow_hooks = {
        'DEFAULT' : (_add_random_words, _add_random_words)
    } # type: Mapping[Union[TOKEN, HASHABLE_TOKENS], AFTER_FLOW_HOOKS]

    p = Pipeline()
    p.register_hooks(before_flow_hooks, stage='BEFORE_FLOW')
    p.register_hooks(after_flow_hooks, stage='AFTER_FLOW')
    for utterance, tokens in p.flow(pattern_definition_path,
                                    dynamic_token_patterns_map,
                                    token_handler_map,
                                    utterance_pattern_tokens_to_combination_options):
        print('utterance:', utterance)
        print('tokens:', tokens)


if __name__ == '__main__':
    main()
