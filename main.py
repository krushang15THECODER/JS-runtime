"""Entry point for the mini JavaScript interpreter."""

import sys

from runtime import build_runtime
from translator import translate


def run_javascript(js_source):
    """Translate JavaScript source and execute it."""
    python_source = translate(js_source)
    runtime = build_runtime()
    exec(python_source, runtime)


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as file:
            js_source = file.read()
    else:
        js_source = sys.stdin.read()

    run_javascript(js_source)


if __name__ == "__main__":
    main()
