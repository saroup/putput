from pathlib import Path

from putput import generate_utterances_and_tokens, generate_utterance_pattern_and_tokens, CombinationOptions


def _custom_token_handler(token: str, phrase: str) -> str:
    return '[{token}({phrase})]'.format(token=token, phrase=phrase)

def main() -> None:
    pattern_definition_path = Path(__file__).parent / 'patterns.yml'
    dynamic_token_to_token_patterns = {
        'SONG': ((('here comes the sun', 'stronger'),),)
    }
    token_handlers = {
        'WAKE': _custom_token_handler,
        'SONG': _custom_token_handler,
    }
    for utt_pattern, utt_pattern_tokens in generate_utterance_pattern_and_tokens(pattern_definition_path,
                                                                                 dynamic_token_to_token_patterns):
        # here you could set combination options specific to each utterance_pattern
        combination_options = CombinationOptions(max_sample_size=5, with_replacement=False, seed=0)
        for utterance, tokens in generate_utterances_and_tokens(utt_pattern,
                                                                utt_pattern_tokens,
                                                                token_handlers,
                                                                combination_options):
            print('utterance: ', utterance)
            print('tokens: ', tokens)


if __name__ == '__main__':
    main()
