set -e

if [ "$1" == "--no-fix" ]; then
    poetry run ruff format --check
    poetry run ruff check --select I
    poetry run ruff check
else
    poetry run ruff format
    poetry run ruff check --fix --select I
    poetry run ruff check --fix
fi

poetry check
poetry run pip check
cd ./doc
poetry run doc8 --ignore-path build --max-line-length 100 -q
set +e  # Turn off the -e flag to allow the sphinx-build command to fail.
# check for broken links in the docs ############
poetry run sphinx-build -b linkcheck -q -D linkcheck_timeout=5 ./source ./build > /dev/null 2>&1
if [ $? -ne 0 ]; then
    cat ./build/output.txt
    exit 1
fi
#################################################
cd ..
