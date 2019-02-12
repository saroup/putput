# Contributing Guidelines

## How To Contribute
* ```putput``` is managed through github issues.
* Please open issues and appropriately tag them so they can be found easily.
* When submitting pull requests, new code requires 100% test coverage.
* Pull requests that fail CI will not be merged. Follow instructions in the README for running CI locally via docker.

## Functional Principles
* ```putput``` prioritizes simplicity.
    * Prefer modules of pure functions over classes whenever possible.
    * Use classes for data structions that are too complicated to be understood with built in types + type hinting

## Naming
* Explicit names, even if verbose, are preferred over abbreviations.
* At its core, ```putput``` reshapes input to output. There are many intermediate steps, which can be found here (TODO: Doc). Please choose names that follow this structure. If a new concept is introduced, update the doc if it would be conceptually helpful.

## Style
* Optional arguments must be named. For instance:
```
def func(arg_1: str, *, arg_2: Optional[bool] = True) -> None:
```
* If a function must be split across multiple lines to meet the linter's line length requirements, every argument and the return type must be on separate lines. For instance:
```
def func(arg_1: str,
         arg_2: str
         ) -> None:
```

## Typing
* ```putput``` uses [mypy](http://mypy-lang.org/) for static type analysis. The conventions we follow are:
    * All functions must have types for arguments and return values.
    * Variables within functions do not need explicit types, unless mypy requests it.
    * Types that span multiple modules should be placed in ```putput.types```.
    * Types that are local to one module should be defined at the top of that module, with _ as a prefix.
    * Do not redefine built-in types such as ```str```.
    * If a type is nested, strongly consider creating a new type for it. For instance ```NEW_TYPE = Sequence[Sequence[str]]``` is encouraged. Similarly ```NEW_TYPE = Sequence[str]``` is discouraged.
        * One exception: for return types, of multiple items such as ```Tuple[Sequence[str], Sequence[str]]``` do not make a new type. Instead, only make new types for nested elements. For instance ```Tuple[Sequence[Sequence[str]], Sequence[str]]``` should become ```Tuple[NEW_TYPE, Sequence[str]]``` where ```NEW_TYPE = Sequence[Sequence[str]]```.
    * Define singular types, not plural types. For instance, instead of defining ```NEW_TYPES = Sequence[Sequence[Sequence[str]]]```, define ```NEW_TYPE = Sequence[Sequence[str]]``` and use ```Sequence[NEW_TYPE]``` in places where ```NEW_TYPES``` is required.

## Samples
* Place each sample in its own directory under ```samples```.
* Samples that only use ```putput``` should reside in ```samples/my_sample/__main__.py```.
* If a sample uses ```putput``` as part of a broader use case such as training/testing a model, create a jupyter notebook within the ```my_sample``` directory.
* If a sample relies on external dependencies unrelated to putput (e.g. tensorflow), place them in a file named ```requirements-my_sample-dev.txt```.
* All samples, including jupyter notebooks, will run as part of the CI pipeline. The process that runs them will set an environment variable ```CI```. If a sample take a long time to run on CPU, use this environment variable to speed up the build. For instance, if a jupyter notebook includes a deep learning model, use the ```CI``` environment variable to make sure the model is trained on a small subset of data and only for a few epochs.

## Documentation
* Public facing APIs must have docstrings. Wherever possible, docstrings require doctests with a working example. Doctests will run with the CI.
