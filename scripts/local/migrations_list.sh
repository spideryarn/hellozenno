#!/bin/bash
set -euo pipefail

# List migrations for local development database
POSTGRES_DB_NAME="hellozenno_development" python -m utils.migrate list 