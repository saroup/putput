import re
from functools import partial
from typing import Callable
from typing import Mapping
from typing import Optional
from typing import Sequence
from typing import Tuple


def preset(*,
           patterns_to_intents: Mapping[str, str],
           entities: Optional[Sequence[str]] = None
           ) -> Callable:
    """Configures the Pipeline for LUIS test format.

    Adheres to: https://docs.microsoft.com/en-us/azure/cognitive-services/luis/luis-tutorial-batch-testing.

    This function should be used as the 'preset' argument of putput.Pipeline and patterns_to_intents must be included.

    Examples:
        >>> from pathlib import Path
        >>> from putput.pipeline import Pipeline
        >>> from pprint import pprint
        >>> import random
        >>> random.seed(0)
        >>> pattern_def_path = Path(__file__).parent.parent.parent / 'tests' / 'doc' / 'example_pattern_definition.yml'
        >>> dynamic_token_patterns_map = {'ITEM': ((('fries',),),)}
        >>> patterns_to_intents = {'ADD_ITEM, 2, CONJUNCTION, ITEM': 'ADD_INTENT'}
        >>> p = Pipeline.from_preset(preset(patterns_to_intents=patterns_to_intents, entities=('ITEM',)),
        ...                          pattern_def_path,
        ...                          dynamic_token_patterns_map=dynamic_token_patterns_map)
        >>> generator = p.flow(disable_progress_bar=True)
        >>> first_test = next(generator)
        >>> first_test == {'entities': [{'endPos': 17, 'entity': 'ITEM', 'startPos': 12},
        ...                             {'endPos': 35, 'entity': 'ITEM', 'startPos': 30},
        ...                             {'endPos': 45, 'entity': 'ITEM', 'startPos': 40}],
        ...                'intent': 'ADD_INTENT',
        ...                'text': 'can she get fries can she get fries and fries'}
        True

    Args:
        patterns_to_intents: Required. A mapping from an utterance pattern string to a single intent.

        entities: A sequence of tokens that are considered entities.

    Returns:
        A Callable that when called returns parameters for instantiating a Pipeline.
        This Callable can be passed into putput.Pipeline as the 'preset' argument.
    """
    return partial(_preset,
                   entities=entities,
                   patterns_to_intents=patterns_to_intents)

def _preset(*,
            patterns_to_intents: Mapping[str, str],
            entities: Optional[Sequence[str]] = None
            ) -> Mapping:
    combo_hooks_map = {}
    for pattern, intent in patterns_to_intents.items():
        combo_hooks_map[tuple(pattern.replace(',', '').split())] = (partial(_handle_intent, intent=intent),)
    combo_hooks_map['DEFAULT'] = (partial(_handle_intent, intent='No Intent'),) # type: ignore

    return {
        'combo_hooks_map': combo_hooks_map,
        'final_hook': partial(_handle_entities, entities=entities)
    }

def _convert_to_luis_entities(utterance: str,
                              entities: Sequence[str],
                              handled_items: Sequence[str],
                              label_extractor: Callable[[str], str]
                              ) -> Sequence[Mapping]:
    ents = []
    offset = 0
    for handled_item in handled_items:
        label = label_extractor(handled_item)
        phrase = ' '.join(re.findall(r'\(([^()]+)\)', handled_item))
        start = offset + utterance[offset:].index(phrase)
        end = start + len(phrase)
        if label in entities:
            ent = {
                "entity": label,
                "startPos": start,
                "endPos": end
            }
            ents.append(ent)
        offset = end
    return ents

def _handle_intent(utterance: str,
                   handled_tokens: Sequence[str],
                   _: Sequence[str],
                   intent: str
                   ) -> Tuple[str, Sequence, Sequence[str]]:
    return utterance, handled_tokens, intent

def _handle_entities(utterance: str,
                     handled_tokens: Sequence[str],
                     intent: str,
                     entities: Optional[Sequence[str]] = None
                     ) -> Optional[Mapping]:
    if intent == 'No Intent':
        return None
    label_extractor = lambda s: s[s.index('[') + 1: s.index('(')]
    luis_entities = [] # type: Sequence[Mapping]
    if entities:
        luis_entities = _convert_to_luis_entities(utterance, entities, list(handled_tokens), label_extractor)
    return {
        "text": utterance,
        "intent": intent,
        "entities": luis_entities
    }
