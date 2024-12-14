setup:
    rye sync
    rye run python3 -c "import nltk; nltk.download('stopwords')"
    echo "!!!"
    echo "Download Microsoft Edge Driver: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver?form=MA13LH#downloads and put it inside driver folder"
    echo "!!!"


check:
    rye run ruff check .

tidy:
    rye run ruff check --select I --fix
    rye run ruff format

build:
    rye sync
    rye build --wheel --clean

run:
    rye run agnia-smart-digest

build-docker: build
    docker buildx build . -t agnia-smart-digest-image

run-docker: build-docker
    docker run agnia-smart-digest-image agnia-smart-digest
