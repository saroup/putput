#!/usr/bin/env bash
mypy -p putput && pylint putput && nose2
exit $?