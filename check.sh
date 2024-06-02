set -e  # Exit immediately if a command exits with a non-zero status.

echox() {
    echo "\033[34m$@\033[0m"  # Manually echo the command
    "$@" | while IFS= read -r line; do echo "  \033[32m$line\033[0m"; done
}

if [ "$1" == "--no-fix" ]; then
    echox poetry run ruff format --check
    echox poetry run ruff check --select I
    echox poetry run ruff check
else
    echox poetry run ruff format
    echox poetry run ruff check --fix --select I
    echox poetry run ruff check --fix
fi

echox poetry check
echox poetry run pip check
cd ./doc
echox poetry run doc8 --ignore-path build --max-line-length 100 -q
set +e  # Turn off the -e flag to allow the sphinx-build command to fail.
# check for broken links in the docs ############
echox poetry run sphinx-build -b linkcheck -q -D linkcheck_timeout=5 ./source ./build > /dev/null 2>&1
if [ $? -ne 0 ]; then
    cat ./build/output.txt
    exit 1
fi
#################################################
cd ..
