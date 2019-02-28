import json
import random
from pathlib import Path

from putput import ComboOptions
from putput import Pipeline
from putput.presets import luis

random.seed(0)

def main() -> None:
    pattern_def_path = Path(__file__).parent / 'patterns.yml'
    dynamic_token_patterns_map = {
        'Field': ((('janitorial', 'fullstack typescript programming with azure',
                    'fullstack typescript programming', 'database', 'machine learning', 'ml',
                    'artificial intelligence', 'ai', 'backend development', 'frontend development',
                    'program managment', 'pm', 'android software engineering'),),),
        'Job': ((('software developer', 'programmer', 'engineeer', 'software engineer', 'politician',
                  'garbage collector', 'fast food worker', 'fry cook', 'doctor', 'nurse', 'nurse practicioner',
                  'pediatrician', 'actor', 'actress', 'farmer', 'baker', 'barber', 'hair dresser', 'bus driver',
                  'chemical engineer', 'mechanical engineer', 'line cook', 'head chef', 'SQL database engineer',
                  'anthropologist'),),),
        'Locations': ((('new york', 'new york city', 'nyc', 'Los Angeles', 'LA',
                        'Austin', 'West Coast', 'Boston'),),),
        'datetimeV2': ((('today', 'this week', 'this month', 'next six months', 'upcoming',
                         'next month', 'next year'),),),
    }

    combo_options_map = {
        'DEFAULT': ComboOptions(max_sample_size=50, with_replacement=False, seed=0)
    }

    patterns_to_intents = {
        'QUESTION, AVAILABILITY, Field, POSITION, QUESTION_MARK': "GetJobInformation",
        'QUESTION, Field, POSITION, AVAILABILITY, QUESTION_MARK': "GetJobInformation",
        'QUESTION, AVAILABILITY, Field, POSITION, OR, Field, POSITION, QUESTION_MARK': "GetJobInformation",
        'QUESTION, Field, POSITION, OR, Field, POSITION, AVAILABILITY, QUESTION_MARK': "GetJobInformation",
        'QUESTION, AVAILABILITY, Field, POSITION, IN, Locations, QUESTION_MARK': "GetJobInformation",
        'QUESTION, Field, POSITION, AVAILABILITY, IN, Locations, QUESTION_MARK': "GetJobInformation",
        'QUESTION, AVAILABILITY, Field, POSITION, datetimeV2, QUESTION_MARK': "GetJobInformation",
        'QUESTION, Field, POSITION, AVAILABILITY, datetimeV2, QUESTION_MARK': "GetJobInformation",
        'QUESTION, AVAILABILITY, Field, POSITION, IN, Locations, datetimeV2, QUESTION_MARK': "GetJobInformation",
        'QUESTION, Field, POSITION, AVAILABILITY, IN, Locations, datetimeV2, QUESTION_MARK': "GetJobInformation",
        'FIND, Field, POSITION, AVAILABILITY': "GetJobInformation",
        'FIND, Field, POSITION, AVAILABILITY, datetimeV2': "GetJobInformation",
        'FIND, Field, POSITION, AVAILABILITY, IN, Locations': "GetJobInformation",
        'FIND, Field, POSITION, AVAILABILITY, datetimeV2, IN, Locations': "GetJobInformation",
        'GIVE, RESUME, FOR_THE, Job, POSITION': 'ApplyForJob',
        'GIVE, RESUME, FOR_THE, Field, POSITION': 'ApplyForJob',
        'GIVE, Field, RESUME': 'ApplyForJob',
        'GIVE, Job, RESUME': 'ApplyForJob',
        'GIVE, Field, POSITION, RESUME': 'ApplyForJob',
        'GIVE, Job, POSITION, RESUME': 'ApplyForJob',
        'APPLY, FOR_THE, Field, POSITION': 'ApplyForJob',
        'APPLY, FOR_THE, Job, POSITION': 'ApplyForJob',
        'CURRENT, Job, GIVE, RESUME': 'ApplyForJob',
        'MY, RESUME, ATTACHED': 'ApplyForJob',
        'MY, RESUME, FOR_THE, Job, ATTACHED': 'ApplyForJob',
        'MY, RESUME, FOR_THE, Job, POSITION, ATTACHED': 'ApplyForJob'
    }
    entities = ('Job', 'datetimeV2', 'Locations')
    p = Pipeline.from_preset(luis.preset(patterns_to_intents=patterns_to_intents, entities=entities),
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
