#!/usr/bin/env bash
mypy -p putput && mypy -p samples && pylint putput && pylint samples && nose2
exit $?