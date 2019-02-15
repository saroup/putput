import random
from pathlib import Path
from typing import Sequence
from typing import Tuple

from putput import ComboOptions
from putput import Pipeline
from putput.presets import iob2
from putput.types import COMBO
from putput.types import GROUP


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
    before_joining_hooks_map = {
        ('WAKE', 'PLAY', 'ARTIST'): (_sample_play, _sample_play)
    }

    p = Pipeline(before_joining_hooks_map=before_joining_hooks_map)
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
    after_joining_hooks_map = {
        ('WAKE', 'PLAY', 'ARTIST'): (_add_random_words_to_utterance,)
    }

    p = Pipeline(after_joining_hooks_map=after_joining_hooks_map)
    for utterance, tokens, groups in p.flow(pattern_def_path,
                                            dynamic_token_patterns_map=dynamic_token_patterns_map,
                                            combo_options_map=combo_options_map):
        print('utterance:', utterance)
        print('tokens:', tokens)
        print('groups:', groups)

    print('*' * 50 + 'AFTER JOINING HOOK' + '*' * 50)
    print('\n' * 2)

    # IOB preset format
    print('*' * 50 + 'IOB(using preset)' + '*' * 50)
    p = Pipeline(preset='IOB2')
    for utterance, tokens, groups in p.flow(pattern_def_path,
                                            dynamic_token_patterns_map=dynamic_token_patterns_map,
                                            combo_options_map=combo_options_map):
        print('utterance:', utterance)
        print('tokens:', tokens)
        print('groups:', groups)
    print('*' * 50 + 'IOB(using preset)' + '*' * 50)

    # IOB preset format with object
    print('*' * 50 + 'IOB(using preset with object)' + '*' * 50)
    p = Pipeline(preset=iob2.preset(tokens_to_exclude=('WAKE',)))
    for utterance, tokens, groups in p.flow(pattern_def_path,
                                            dynamic_token_patterns_map=dynamic_token_patterns_map,
                                            combo_options_map=combo_options_map):
        print('utterance:', utterance)
        print('tokens:', tokens)
        print('groups:', groups)
    print('*' * 50 + 'IOB(using preset with object)' + '*' * 50)

    # displaCy preset
    print('*' * 50 + 'displaCy' + '*' * 50)
    p = Pipeline(preset='DISPLACY')
    for token_visualizer, group_visualizer in p.flow(pattern_def_path,
                                                     dynamic_token_patterns_map=dynamic_token_patterns_map,
                                                     combo_options_map=combo_options_map):
        print('token visualizer: ', token_visualizer)
        print()
        print('group visualizer: ', group_visualizer)

    print('*' * 50 + 'displaCy' + '*' * 50)

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

def _sample_play(utterance_combination: COMBO,
                 tokens: Sequence[str],
                 groups: Sequence[GROUP]
                 ) -> Tuple[COMBO, Sequence[str], Sequence[GROUP]]:
    return _sample_utterance_component(utterance_combination, tokens, groups, 'PLAY', 1)

def _sample_utterance_component(utterance_combination: COMBO,
                                tokens: Sequence[str],
                                groups: Sequence[GROUP],
                                token_to_sample: str,
                                sample_size: int
                                ) -> Tuple[COMBO, Sequence[str], Sequence[GROUP]]:
    token_index = tokens.index(token_to_sample)
    utterance_combination_list = list(utterance_combination)
    sampled_combinations = tuple(random.sample(utterance_combination_list.pop(token_index), sample_size))
    utterance_combination_list.insert(token_index, sampled_combinations)
    utterance_combination = tuple(utterance_combination_list)
    return utterance_combination, tokens, groups

if __name__ == '__main__':
    main()
