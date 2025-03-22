#!/bin/bash

# --by-file \
cloc . \
    --exclude-dir=gjdutils,.pytest_cache,__pycache__,.vscode,backup,data,credentials,package-lock.json,HelloZenno,node_modules,extern,dist,.svelte-kit,build,.vite,logs,screenshots,.cursor,obsolete,.vercel \
    --exclude-ext=md,pyc,pyo,pyd,log,png \
    --not-match-f='.*\.md$|_secrets\.py|\.env\..*|npm-debug\.log.*|yarn-debug\.log.*|yarn-error\.log.*|\.pnpm-debug\.log.*' \
    static/css 