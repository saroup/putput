import random
from functools import partial
from itertools import repeat
from typing import Callable
from typing import Mapping
from typing import Sequence
from typing import Tuple


def preset(*, chance: int = 20) -> Callable:
    return partial(_preset, chance=chance)


def _preset(chance=20) -> Mapping:
    combo_hooks_map = {
        'DEFAULT': (partial(_replace_with_synonyms, chance=chance),)
    }
    return {
        'combo_hooks_map': combo_hooks_map
    }


def _replace_with_synonyms(utterance: str,
                          handled_tokens: Sequence[str],
                          handled_groups: Sequence[str],
                          chance: int
                          ) -> Tuple[str, Sequence[str], Sequence[str]]:
    return _replace_utterance_tokens_groups(handled_groups, chance)


def _replace_utterance_tokens_groups(handled_groups: Sequence[str],
                                     chance: int
                                     ) -> Tuple[str, Sequence[str], Sequence[str]]:
    synonym_utterances, synonym_tokens, synonym_groups = [], [], []
    for handled_group in handled_groups:
        num_parens = 0
        utterance_components, token_components, group_components = [], [], []
        for position, char in enumerate(handled_group):
            if char == '{':
                start_group_index = position + 1
            if char == '[':
                start_tokens_index = position + 1
            if char == '(':
                num_parens += 1
                if num_parens == 1:
                    end_group_index = position
                    group_components.append(handled_group[start_group_index:end_group_index])
                if num_parens == 2:
                    end_tokens_index = position
                    token_components.append(handled_group[start_tokens_index:end_tokens_index])
                    start_utterance_index = position + 1
            if char == ')':
                num_parens -= 1
                if num_parens == 1:
                    end_utterance_index = position
                    original_utterance_component = handled_group[start_utterance_index:end_utterance_index]
                    utterance_component = ' '.join(map(get_synonym,
                                                       original_utterance_component.split(),
                                                       repeat(chance)))
                    utterance_components.append(utterance_component)

        synonym_utterance_component = ' '.join(utterance_components)
        synonym_utterances.append(synonym_utterance_component)

        synonym_token_components = ['[{}({})]'.format(t, u) for u, t in zip(utterance_components, token_components)]
        synonym_tokens += synonym_token_components

        synonym_group_component = '{{{}}}'.format(' '.join(synonym_token_components))
        synonym_groups.append(synonym_group_component)
    return ' '.join(synonym_utterances), synonym_tokens, synonym_groups


def get_synonym(word: str, chance: float) -> str:
    if random.random() < (chance / 100):
        # TODO: Wordnet goes here
        return "synonym!"
    return word


if __name__ == '__main__':
    handled_groups = ['{None([WAKE(hi)])}', '{PLAY_PHRASE([START(he will want)] [PLAY(to play)])}']
    utterances, tokens, groups = replace_with_synonyms('lo', ['w'], handled_groups, 20)
    print("handled utterance: ", utterances)
    print("handled tokens:", tokens)
    print("handled groups:", groups)
