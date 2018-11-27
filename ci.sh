#!/usr/bin/env bash
export MYPYPATH=$(pwd)/putput
export PYTHONPATH=$(pwd)/putput
mypy putput/putput && \
mypy samples && \
pylint putput/putput && \
pylint samples && \
nose2 putput
exit $?