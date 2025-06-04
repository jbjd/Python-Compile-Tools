#!/bin/sh

status=0

#######################################
# Runs a command that validates code and updates status
# Globals:
#   status
# Arguments:
#   Description of the step to be echo'ed
#   Command to run
#######################################
validate_step () {
    echo "$1"
    $2
    status=$(($status + $?))
    echo
}

validate_step \
"Running isort" \
"isort . -m 3 --tc --check"

validate_step \
"Running flake8" \
"flake8 ."

validate_step \
"Running black formatter" \
"black . --check"

validate_step \
"Running mypy type checker" \
"mypy . --check-untyped-defs"

validate_step \
"Running spell checker" \
"codespell personal_compile_tools tests README.md"

if [ $status -ne 0 ]
then
    printf "Some checks failed"
    exit 1
else
    printf "All checks passed"
fi
