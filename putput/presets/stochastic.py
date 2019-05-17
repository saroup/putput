import os
import random
from functools import partial
from itertools import repeat
from typing import Callable
from typing import Mapping
from typing import Sequence
from typing import Tuple

import gensim.downloader as api
from gensim.models import Word2Vec

from putput.logger import get_logger


def preset(*, model_name: str = 'word2vec.model', corpus: str = 'glove-twitter-25', chance: int = 20) -> Callable:
    """Randomly replaces words with similar words based on embeddings.

    For every word, given a chance randomly replace it with a similar word based on
    embedding distance.

    The first time this function is used, it will download a corpus,
    train a Word2Vec model, and save the model to disk. While this can take
    several minutes and requires internet connection, for every subsequent use,
    the saved model will be loaded, which will be mucher quicker.

    Args:
        model_name: Name of model to save in presets directory. If a model
            with this name already exists, it will be loaded. If a model with
            this name does not exist, the corpus will be downloaded, a
            Word2Vec model will be trained, and it will be saved in the presets
            directory with this name.

        corpus: Text to train a Word2Vec model. The same corpus as in
            gensim.downloader.load.

        chance: The chance between [0, 100] for each word to be replaced by
            another word with a similar embedding.

    Returns:
        A Callable that when called returns parameters for instantiating a Pipeline.
        This Callable can be passed into putput.Pipeline as the 'preset' argument.

    Examples:
        >>> from pathlib import Path
        >>> from putput.pipeline import Pipeline
        >>> pattern_def_path = Path(__file__).parent.parent.parent / 'tests' / 'doc' / 'example_pattern_definition.yml'
        >>> dynamic_token_patterns_map = {'ITEM': ('fries',)}
        >>> p = Pipeline.from_preset(preset(model_name='word2vec.test.model', chance=50),
        ...                          pattern_def_path,
        ...                          dynamic_token_patterns_map=dynamic_token_patterns_map,
        ...                          seed=0)
        >>> generator = p.flow(disable_progress_bar=True)
        >>> for utterance, tokens, groups in generator:
        ...     print(utterance)
        ...     print(tokens)
        ...     print(groups)
        ...     break
        can she steal curry can herself get fries whilst fries
        ('[ADD(can she steal)]', '[ITEM(curry)]', '[ADD(can herself get)]',
         '[ITEM(fries)]', '[CONJUNCTION(whilst)]', '[ITEM(fries)]')
        ('{ADD_ITEM([ADD(can she steal)] [ITEM(curry)])}', '{ADD_ITEM([ADD(can herself get)] [ITEM(fries)])}',
         '{None([CONJUNCTION(whilst)])}', '{None([ITEM(fries)])}')
    """
    if chance not in range(101):
        raise ValueError('Invalid chance: {}. Chance accepts any integer between [0, 100]')
    logger = get_logger(__name__)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, model_name)
    if os.path.isfile(model_path):
        warning_msg = 'Loading existing model from: {}'.format(model_path)
        logger.warning(warning_msg)
        model = Word2Vec.load(model_path)
    else: # pragma: no cover
        warning_msg = 'Downloading and training Word2Vec on {}. This will take time.'.format(corpus)
        logger.warning(warning_msg)
        model = Word2Vec(api.load(corpus))
        warning_msg = 'Saving model to: {}'.format(model_path)
        logger.warning(warning_msg)
        model.save(model_path)
    return partial(_preset, model=model, chance=chance)

def _preset(model: Word2Vec, chance: int) -> Mapping:
    expansion_hooks_map = {'DEFAULT': (partial(_add_synonyms, model=model, chance=chance),)}
    return {
        'expansion_hooks_map': expansion_hooks_map
    }

def _add_synonyms(utterance_combination: Sequence[Sequence[str]],
                  tokens: Sequence[str],
                  groups: Sequence[Tuple[str, int]],
                  model: Word2Vec,
                  chance: int,
                  ) -> Tuple[Sequence[Sequence[str]], Sequence[str], Sequence[Tuple[str, int]]]:
    utterance_combination_with_synonyms = tuple(map(_get_utterance_combination_with_synonyms,
                                                    utterance_combination,
                                                    repeat(model),
                                                    repeat(chance)))
    return utterance_combination_with_synonyms, tokens, groups

def _get_utterance_combination_with_synonyms(component: Sequence[str], model: Word2Vec, chance: int) -> Sequence[str]:
    return tuple(map(_get_phrase_with_synonym, component, repeat(model), repeat(chance)))

def _get_phrase_with_synonym(phrase: str, model: Word2Vec, chance: int) -> str:
    return ' '.join(map(_get_synonym, phrase.split(), repeat(model), repeat(chance)))

def _get_synonym(word: str, model: Word2Vec, chance: int) -> str:
    try:
        if random.random() < (chance / 100):
            return random.choice(model.most_similar(word))[0]
    except KeyError: # pragma: no cover
        pass
    return word
