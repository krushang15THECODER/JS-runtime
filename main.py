"""Entry point for the mini JavaScript interpreter."""

import sys

from runtime import build_runtime
from translator import translate


def repl():
    print("Mini JS Interpreter REPL 🔥 (type exit to quit)\n")

    runtime = build_runtime()

    while True:
        try:
            js_source = input("JS > ").strip()

            # 🔥 IMPORTANT: handle exit BEFORE anything else
            if js_source.lower() == "exit":
                print("Bye 👋")
                break

            if not js_source:
                continue

            python_source = translate(js_source)

            exec(python_source, runtime)

        except Exception as e:
            print("Error:", e)

def run_file(path):
    with open(path, encoding="utf-8") as file:
        js_source = file.read()

    python_source = translate(js_source)
    runtime = build_runtime()
    exec(python_source, runtime)


def main():
    if len(sys.argv) == 1:
        repl()
        return

    arg = sys.argv[1]

    if arg == "--repl":
        repl()
    else:
        run_file(arg)


if __name__ == "__main__":
    main()
