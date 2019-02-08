import random
from pathlib import Path
from typing import Sequence
from typing import Tuple
from putput import ComboOptions
from putput import Pipeline
from putput.types import COMBO

def main() -> None:
    pattern_def_path = Path(__file__).parent / 'patterns.yml'
    dynamic_token_patterns_map = {
        'SONG': ((('here comes the sun', 'stronger'),),)
    }

    combo_options_map = {
        'DEFAULT': ComboOptions(max_sample_size=5, with_replacement=False, seed=0)
    }

    # default format
    print('*' * 50 + 'DEFAULT' + '*' * 50)
    p = Pipeline()
    for utterance, tokens, groups in p.flow(pattern_def_path,
                                            dynamic_token_patterns_map=dynamic_token_patterns_map,
                                            combo_options_map=combo_options_map):
        print('utterance:', utterance)
        print('tokens:', tokens)
        print('groups:', groups)
    print('*' * 50 + 'DEFAULT' + '*' * 50)
    print('\n' * 2)

    # default format with before joining hook
    print('*' * 50 + 'BEFORE JOINING HOOK' + '*' * 50)
    before_flow_hooks = {
        ('WAKE', 'PLAY', 'ARTIST'): (_sample_play, _sample_play)
    }

    p = Pipeline()
    p.register_hooks(before_flow_hooks, 'BEFORE_JOINING')
    for utterance, tokens, groups in p.flow(pattern_def_path,
                                            dynamic_token_patterns_map=dynamic_token_patterns_map,
                                            combo_options_map=combo_options_map):
        print('utterance:', utterance)
        print('tokens:', tokens)
        print('groups:', groups)
    print('*' * 50 + 'BEFORE JOINING HOOK' + '*' * 50)
    print('\n' * 2)


    # default format with after joining hook
    print('*' * 50 + 'AFTER JOINING HOOK' + '*' * 50)
    after_flow_hooks = {
        ('WAKE', 'PLAY', 'ARTIST'): (_add_random_words_to_utterance,)
    }

    p = Pipeline()
    p.register_hooks(after_flow_hooks, 'AFTER_JOINING')
    for utterance, tokens, groups in p.flow(pattern_def_path,
                                            dynamic_token_patterns_map=dynamic_token_patterns_map,
                                            combo_options_map=combo_options_map):
        print('utterance:', utterance)
        print('tokens:', tokens)
        print('groups:', groups)

    print('*' * 50 + 'AFTER JOINING HOOK' + '*' * 50)
    print('\n' * 2)


    token_handler_map = {
        'DEFAULT': _bio_token_handler
    }

    group_handler_map = {
        'DEFAULT': _bio_group_handler
    }

    # BIO format
    print('*' * 50 + 'BIO' + '*' * 50)
    p = Pipeline()
    for utterance, tokens, groups in p.flow(pattern_def_path,
                                            dynamic_token_patterns_map=dynamic_token_patterns_map,
                                            token_handler_map=token_handler_map,
                                            group_handler_map=group_handler_map,
                                            combo_options_map=combo_options_map):
        print('utterance:', utterance)
        print('tokens:', tokens)
        print('groups:', groups)
    print('*' * 50 + 'BIO' + '*' * 50)

def _add_random_words_to_utterance(utterance: str,
                                   handled_tokens: Sequence[str],
                                   handled_groups: Sequence[str]
                                   ) -> Tuple[str, Sequence[str], Sequence[str]]:
    utterances = utterance.split()
    random_words = ['hmmmm', 'uh', 'um', 'please']
    insert_index = random.randint(0, len(utterances))
    random_word = random.choice(random_words)
    utterances.insert(insert_index, random_word)
    utterance = ' '.join(utterances)
    return utterance, handled_tokens, handled_groups

def _bio_token_handler(token: str, phrase: str) -> str:
    tokens = ['{}-{}'.format('B' if i == 0 else 'I', token)
              for i, _ in enumerate(phrase.replace(" '", "'").split())]
    return ' '.join(tokens)

def _bio_group_handler(group_name: str, handled_tokens: Sequence[str]) -> str:
    num_tokens = 0
    for tokenized_phrase in handled_tokens:
        num_tokens += len(tokenized_phrase.split())
    groups = ['{}-{}'.format('B' if i == 0 else 'I', group_name)
              for i in range(num_tokens)]
    return ' '.join(groups)

def _sample_play(utterance_combination: COMBO,
                 tokens: Sequence[str],
                 ) -> Tuple[COMBO, Sequence[str]]:
    return _sample_utterance_component(utterance_combination, tokens, 'PLAY', 1)

def _sample_utterance_component(utterance_combination: COMBO,
                                tokens: Sequence[str],
                                token_to_sample: str,
                                sample_size: int,
                                ) -> Tuple[COMBO, Sequence[str]]:
    token_index = tokens.index(token_to_sample)
    utterance_combination_list = list(utterance_combination)
    sampled_combinations = tuple(random.sample(utterance_combination_list.pop(token_index), sample_size))
    utterance_combination_list.insert(token_index, sampled_combinations)
    utterance_combination = tuple(utterance_combination_list)
    return utterance_combination, tokens

if __name__ == '__main__':
    main()
