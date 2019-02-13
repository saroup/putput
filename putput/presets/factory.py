from typing import Callable

from putput.presets.iob import IOB

def get_init_preset(preset: str) -> Callable:
    if preset == 'IOB':
        return IOB().init_preset
    raise ValueError('Unrecoginzed preset.')
