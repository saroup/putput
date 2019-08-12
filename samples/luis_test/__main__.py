import json
import random
from pathlib import Path

from putput import ComboOptions
from putput import Pipeline

random.seed(0)

def main() -> None:
    pattern_def_path = Path(__file__).parent / 'patterns.yml'
    dynamic_token_patterns_map = {
        'Field': ('janitorial', 'fullstack typescript programming with azure',
                  'fullstack typescript programming', 'database', 'machine learning', 'ml',
                  'artificial intelligence', 'ai', 'backend development', 'frontend development',
                  'program managment', 'pm', 'android software engineering'),
        'Job': ('software developer', 'programmer', 'engineeer', 'software engineer', 'politician',
                'garbage collector', 'fast food worker', 'fry cook', 'doctor', 'nurse', 'nurse practicioner',
                'pediatrician', 'actor', 'actress', 'farmer', 'baker', 'barber', 'hair dresser', 'bus driver',
                'chemical engineer', 'mechanical engineer', 'line cook', 'head chef', 'SQL database engineer',
                'anthropologist'),
        'Locations': ('new york', 'new york city', 'nyc', 'Los Angeles', 'LA',
                      'Austin', 'West Coast', 'Boston'),
        'datetimeV2': ('today', 'this week', 'this month', 'next six months', 'upcoming',
                       'next month', 'next year'),
    }

    combo_options_map = {
        'DEFAULT': ComboOptions(max_sample_size=50, with_replacement=False)
    }
    p = Pipeline.from_preset('LUIS',
                             pattern_def_path,
                             combo_options_map=combo_options_map,
                             dynamic_token_patterns_map=dynamic_token_patterns_map)
    generator = p.flow(disable_progress_bar=True)

    tests = list(generator)
    # LUIS can only batch test up to 1000 examples per file
    if len(tests) > 1000:
        tests = random.sample(tests, 1000)

    test_file = Path(__file__).parent.joinpath('HumanResources-jobs-batch.json')
    with test_file.open(mode='w', encoding='UTF-8') as f:
        json.dump(tests, f, indent=4)

if __name__ == '__main__':
    main()
