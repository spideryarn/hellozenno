#!/bin/bash

cloc . \
    --exclude-dir=gjdutils,.pytest_cache,__pycache__,.vscode,backup,data,credentials,HelloZenno \
    --exclude-ext=md \
    --not-match-f='.*\.md$' \
    static/css 