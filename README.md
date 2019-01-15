# About
[![Build Status](https://travis-ci.org/michaelperel/putput.svg?branch=master)](https://travis-ci.org/michaelperel/putput)

```putput``` (pattern-utterance-tokens, pattern-utterance-tokens) is a library that generates inputs and labels for NLP tokenizers. Specifically, you define **patterns** in YAML and ```putput``` generates **utterances** (inputs to a tokenizer) and **tokens** (labels for the utterances). ```putput``` is memory efficient, relying on generators and sampling, so it can handle the majority of workloads on a commodity computer.

```putput``` should be used to:
* generate utterances and tokens to train a machine learning based tokenizer in scenarios where you do not have access to real data.
* generate utterances and tokens to augment training specific patterns in a machine learning based tokenizer.
* generate utterances and tokens to test tokenizers for specific patterns.

# Installation
```putput``` currently supports python >= 3.4. To install the production release, execute ```pip install putput```.

# Example
Here is a sample **pattern definition**:
```
token_patterns:
  - static:
    - WAKE:
      - [[hey, ok], [speaker, sound system]]
    - PLAY:
      - [[he, she], [wants, needs], [to play, to listen to]]
      - [[play, turn on]]
    - INDICATOR:
      - [[by, performed by]]
    - ARTIST:
      - [[the beatles, kanye west]]
  - dynamic:
    - SONG
utterance_patterns:
  - [WAKE, PLAY, SONG]
  - [WAKE, PLAY, SONG, INDICATOR, ARTIST]
```

Focusing on the last utterance pattern, ```putput``` could generate hundreds of utterances and tokens of the form:
* utterance:  hey speaker he wants to play here comes the sun by the beatles
* tokens:  [WAKE(hey speaker)] [PLAY(he wants to play)] [SONG(here comes the sun)] [INDICATOR(by)] [ARTIST(the beatles)]
* utterance:  ok sound system she needs to listen to stronger by kanye west
* tokens:  [WAKE(ok sound system)] [PLAY(she needs to listen to)] [SONG(stronger)] [INDICATOR(by)] [ARTIST(kanye west)]

# Usage
## Samples
* Fetch the code:
  ```git clone https://github.com/michaelperel/putput.git```
* Move into the project directory:
  ```cd putput```
* Ensure docker is running:
  ```docker --version```
* Build the runtime environment:
  ```docker build -t putput .```
* The project ships with several usage samples which you can execute, for example:
  ```docker run putput smart_speaker```

## Development
There are various checks that Travis (our CI server) executes to ensure code quality.
You can also run the checks locally:

1. Install the development dependencies via: ```pip install -e .[dev]```
2. Run the linter: ```python setup.py pylint```
3. Run the type checker: ```python setup.py mypy```
4. Run the tests: ```python setup.py test```

Alternatively, you can run all the steps via Docker: ```docker build --target=build -t putput .```

## Pattern Definition
### Token Patterns and Utterance Patterns
```putput``` requires you to define two types of patterns. A **token pattern** describes the product of words that constitutes a token, and an **utterance pattern** describes the product of phrases described by token patterns that constitutes an utterance.

Using the smart speaker example from above, one token pattern for the ```PLAY``` token would be ```[[he, she], [wants], [to play, to listen to]]```. Each element of the product of the token pattern (```[he wants to play, he wants to listen to, she wants to play, she wants to listen to]```) describes a valid ```PLAY``` token.

One utterance pattern would be ```[WAKE, PLAY, SONG]```. The product of phrases described by token patterns (```[[hey speaker, hey sound system, ok speaker, ok sound system], [he wants to play, he wants to listen to, she wants to play, she wants to listen to, play, turn on], [here comes the sun, stronger]]```) describes a valid ```[WAKE, PLAY, SONG]``` utterance pattern. One example of such a product would be ```hey speaker he wants to play here comes the sun```.

### Static vs Dynamic Token Patterns
Not every token pattern can be specified before runtime. Inside the YAML file, underneath ```token_patterns```, you may specify ```static``` or ```dynamic``` token patterns. Static means all of the token patterns can be specified before the application runs. For instance, there are only a few ways to tell a smart speaker to wake. Dynamic means the token patterns will be specified at runtime. For instance, you may have thousands of songs that change daily, so you could not specify them as part of a YAML file. Instead, you can load them at runtime, perhaps after calling a web service that retrieves an updated list of songs, and pass those to the pattern definition processor.
