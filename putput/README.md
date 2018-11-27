# About
[![Build Status](https://travis-ci.org/michaelperel/putput.svg?branch=master)](https://travis-ci.org/michaelperel/putput)

In NLP, and especially when working with chatbots, it is useful to map utterances to tokens for further processing. For example, if you tell a smart speaker to "play Summer Hits on Spotify", a tokenizer may convert that utterance to the 3 tokens, ```[ACTION(play)] [PLAYLIST(Summer Hits)] [MUSIC_SERVICE(Spotify)]```. Given these tokens, the speaker can process your request.

While building or testing a tokenizer, it's likely that you do not have enough utterances and corresponding tokens. Often, it is not possible to source them organically. Therefore, you have to come up with them yourself.

putput (pattern-utterance, repeated in a pattern) makes it trivial to create utterances and tokens in abundance by defining simple patterns via a YAML file.

# Algorithm
With only two types of patterns, all utterances and tokens can be created. Once again, let's consider the example of a smart speaker.

The first type of pattern, a **token pattern**, describes the combinations of words that make up a token. For instance, one example of the ```PLAY``` token could be described with the pattern ```[[he, she], [wants], [to play, to listen to]]```. This pattern means that all ordered permutations, (he wants to play, she wants to play, he wants to listen to, she wants to listen to) describe the ```PLAY``` token.

The second type of pattern, an **utterance pattern**, describes the structure of an utterance as a combination of tokens. Examples of utterance patterns include ```[WAKE]```, ```[WAKE, PLAY, SONG, INDICATOR, ARTIST]```, and so forth.


By defining these two types of patterns in a YAML file, putput can create utterances and associated tokens by:
* combining the ordered permutations of words to create phrases described by token patterns
* combining phrases described by token patterns to create utterances described by utterance patterns

For illustrative purposes, the YAML file may look like:
```
tokens:
  - static:
    - WAKE:
      - [[hey, ok], [speaker, sound system]]
    - PLAY:
      - [[he, she], [wants, needs], [to play, to listen to]]
      - [[play, turn on]]
    - SONG:
      - [[here comes the sun, stronger]]
    - INDICATOR:
      - [[by, performed by]]
    - ARTIST:
      - [[the beatles, kanye west]]
utterances:
  - [WAKE]
  - [WAKE, PLAY, SONG, INDICATOR, ARTIST]
```

For the utterance pattern ```[WAKE]```, putput will generate the utterances:
```[hey speaker, hey sound system, ok sound system, ok speaker]```.

For the utterance pattern ```[WAKE, PLAY, SONG, INDICATOR, ARTIST]```, putput can generate 320 utterances. Here is a sample of 5 of them:
```[ok speaker he wants to play here comes the sun by kanye west, ok sound system she needs to play stronger by the beatles, ok sound system play here comes the sun by the beatles, hey speaker she needs to play here comes the sun performed by kanye west, hey sound system play here comes the sun by kanye west]```.

Note: Although some of the utterances are not valid (for example, "here comes the sun" is not by kanye west), they can still provide utility in testing.

Even with just a few patterns, it is possible to generate millions of utterances and tokens. Don't worry -- putput can be configured to generate as few utterances as you'd like, so you will not run into the issue of running out of computational power.

# Usage
Sample applications can be found in ```samples/```. Each sample exists in its own directory, with a ```main.py``` module. To run a sample, execute ```python -m samples.specific_sample.main```. For instance, to run the smart speaker example from the README, execute ```python -m samples.smart_speaker.main```.

The following notes provide context for trickier parts of the samples.

## Static vs dynamic token patterns
Not every token pattern can be specified before runtime. Inside the YAML file, underneath ```token_patterns```, you may specify ```static``` or ```dynamic``` token patterns. Static means all of the token patterns can be specified before the application runs. For instance, there are only a few ways to tell a smart speaker to wake. Dynamic means the token patterns will be specified at runtime. For instance, you may have thousands of songs that change daily, so you could not specify them as part of a YAML file. Instead, you can load them at runtime, perhaps after calling a web service, and pass them to the input processor.

## Token handlers
Applications using putput should have the ability to specify how to create a token. Consider two smart speakers. A simpler speaker can only wake on the phrase "hey speaker". A more advanced speaker can wake on "hey speaker" and "ok speaker", and it performs slightly different actions depending on the phrase. For the simpler speaker, tokenizing "hey speaker" to ```WAKE``` is enough. For the advanced speaker, tokenizing "hey speaker" and "ok speaker" to ```WAKE``` is not enough because the difference between the two phrases would be lost. Therefore, token handlers, or functions that accept as input the phrase to be tokenized, can be specified. For instance, a token handler could be specified for ```WAKE``` so output tokens could look like ```[WAKE(hey speaker)]``` and ```[WAKE(ok speaker)]```.

By default, phrases are tokenized to ```[token]```. Default behavior can be overridden with a token handler just like an any other token. To do so, specify the token ```DEFAULT``` in the token handler dictionary.

# Tests
To run tests, clone this repo and run ```pip install -r requirements.txt```, followed by ```nose2```. To see a coverage report, run ```nose2 --with-coverage```.