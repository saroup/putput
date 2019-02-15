from typing import Callable

from putput.presets import iob2
from putput.presets import displaCy


def get_preset(preset: str) -> Callable:
    supported_presets = ('IOB2', 'displaCy')
    if preset == 'IOB2':
        return iob2.preset()
    if preset == 'displaCy':
        return displaCy.preset()
    raise ValueError('Unrecoginzed preset. Please choose from the supported presets: {}'.format(supported_presets))
