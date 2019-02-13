from typing import Callable

from putput.presets import iob2


def get_preset(preset: str) -> Callable:
    supported_presets = ('IOB2',)
    if preset == 'IOB2':
        return iob2.preset()
    raise ValueError('Unrecoginzed preset. Please choose from the supported presets: {}'.format(supported_presets))
