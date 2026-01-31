#!/bin/sh
set -e

DOMAINS_FILE="${DOMAINS_FILE:-/app/input/domains.txt}"
OUTPUT_DIR="${OUTPUT_DIR:-/app/output}"
NUCLEI_TEMPLATE_DIR="${NUCLEI_TEMPLATE_DIR:-/root/nuclei-templates/http/takeovers}"
MAX_THREADS="${MAX_THREADS:-8}"

mkdir -p "$(dirname "$DOMAINS_FILE")" "$OUTPUT_DIR"

if [ ! -f "$DOMAINS_FILE" ]; then
	echo "Domains file not found: $DOMAINS_FILE" >&2
	exit 1
fi

exec TakeOver \
	--input "$DOMAINS_FILE" \
	--output "$OUTPUT_DIR" \
	--nuclei-template-dir "$NUCLEI_TEMPLATE_DIR" \
	--max-threads "$MAX_THREADS" \
	"$@"
