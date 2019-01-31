import random
from pathlib import Path
from typing import Callable, Mapping, Tuple, Union # pylint: disable=unused-import

from putput import CombinationOptions, Pipeline


def _include_phrase(token: str, phrase: str) -> str:
    return '[{token}({phrase})]'.format(token=token, phrase=phrase)

def _sample_utterance_combination(utterance_combination: Tuple[Tuple[str, ...], ...],
                                  tokens: Tuple[str, ...],
                                  token_to_sample: str,
                                  sample_size: int,
                                  ) -> Tuple[Tuple[Tuple[str, ...], ...], Tuple[str, ...]]:
    TOKEN_INDEX = tokens.index(token_to_sample)
    utterance_combination_list = list(utterance_combination)
    sampled_combinations = tuple(random.sample(utterance_combination_list.pop(TOKEN_INDEX), sample_size))
    utterance_combination_list.insert(TOKEN_INDEX, sampled_combinations)
    utterance_combination = tuple(utterance_combination_list)
    return utterance_combination, tokens

def _sample_play(utterance_combination: Tuple[Tuple[str, ...], ...],
                 tokens: Tuple[str, ...],
                 ) -> Tuple[Tuple[Tuple[str, ...], ...], Tuple[str, ...]]:
    return _sample_utterance_combination(utterance_combination, tokens, 'PLAY', 2)

def _sample_artist(utterance_combination: Tuple[Tuple[str, ...], ...],
                   tokens: Tuple[str, ...],
                   ) -> Tuple[Tuple[Tuple[str, ...], ...], Tuple[str, ...]]:
    return _sample_utterance_combination(utterance_combination, tokens, 'ARTIST', 1)

def _add_random_words(utterance: str, handled_tokens: str) -> Tuple[str, str]:
    utterances = utterance.split()
    random_words = ['hmmmm', 'uh', 'um', 'please']
    insert_index = random.randint(0, len(utterances))
    random_word = random.choice(random_words)
    utterances.insert(insert_index, random_word)
    utterance = ' '.join(utterances)
    return utterance, handled_tokens

def main() -> None:
    pattern_definition_path = Path(__file__).parent / 'patterns.yml'
    dynamic_token_to_token_patterns = {
        'SONG': ((('here comes the sun', 'stronger'),),)
    }
    token_to_token_handlers = {
        'WAKE': _include_phrase,
        'SONG': _include_phrase,
    }

    utterance_pattern_tokens_to_combination_options = {
        'DEFAULT': CombinationOptions(max_sample_size=5, with_replacement=False, seed=0)
    } # type: Mapping[Union[str, Tuple[str, ...]], CombinationOptions]

    before_flow_hooks = {
        ('PLAY', 'ARTIST'): (_sample_play, _sample_artist)
    } # type: Mapping[Union[str, Tuple[str, ...]], Tuple[Callable[[Tuple[Tuple[str, ...], ...], Tuple[str, ...]], Tuple[Tuple[Tuple[str, ...], ...], Tuple[str, ...]]], ...]]

    after_flow_hooks = {
        'DEFAULT' : (_add_random_words, _add_random_words)
    } # type: Mapping[Union[str, Tuple[str, ...]], Tuple[Callable[[str, str], Tuple[str, str]], ...]]

    p = Pipeline()
    p.register_hooks(before_flow_hooks, stage='BEFORE_FLOW')
    p.register_hooks(after_flow_hooks, stage='AFTER_FLOW')
    for utterance, tokens in p.flow(pattern_definition_path,
                                    dynamic_token_to_token_patterns,
                                    token_to_token_handlers,
                                    utterance_pattern_tokens_to_combination_options):
        # import pdb; pdb.set_trace()
        print('utterance:', utterance)
        print('tokens:', tokens)


if __name__ == '__main__':
    main()
