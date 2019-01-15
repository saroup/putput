from pathlib import Path

from putput import generate_utterances_and_tokens, generate_utterance_pattern_and_tokens, CombinationOptions


def _custom_token_handler(token: str, tokenized_phrase: str) -> str:
    return "[{token}({tokenized_phrase})]".format(token=token, tokenized_phrase=tokenized_phrase)

def main() -> None:
    input_path = Path(__file__).parent / "patterns.yml"
    dynamic_token_patterns_definition = {
        "ACTION": ((("tell me the news", "what's the weather"),),)
    }
    token_handlers = {
        "WAKE": _custom_token_handler,
        "SONG": _custom_token_handler,
        "ACTION": _custom_token_handler
    }
    for utterance_pattern, tokens in generate_utterance_pattern_and_tokens(input_path,
                                                                           dynamic_token_patterns_definition):
        # set options specific to each utterance_pattern
        combination_options = CombinationOptions(max_sample_size=5, seed=0)
        for utterance, token_str in generate_utterances_and_tokens(utterance_pattern,
                                                                   tokens,
                                                                   token_handlers,
                                                                   combination_options):
            print("utterance: ", utterance)
            print("tokens: ", token_str)
        # cap iteration at X to speed it up


if __name__ == '__main__':
    main()
