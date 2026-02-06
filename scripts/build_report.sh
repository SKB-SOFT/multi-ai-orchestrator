#!/usr/bin/env bash
set -euo pipefail

INPUT=${1:-docs/report-generated.md}
OUTPUT=${2:-docs/report.pdf}

if [ ! -f "$INPUT" ]; then
  echo "Input report not found: $INPUT. Generate it first with python server/scripts/generate_report.py" >&2
  exit 1
fi

if ! command -v pandoc >/dev/null 2>&1; then
  echo "pandoc not found. Install it from https://pandoc.org/installing.html" >&2
  exit 1
fi

pandoc "$INPUT" -o "$OUTPUT"
echo "Report generated: $OUTPUT"
