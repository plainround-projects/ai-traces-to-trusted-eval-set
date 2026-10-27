# argparse (command-line programs)

## What it is

`argparse` is Python's standard library module for command-line programs. You declare the commands, sub-commands and options your program accepts; `argparse` reads `sys.argv` (the words typed after the program name), checks them, converts them, and prints help and error messages for you.

## Why this repository uses it

The program's commands (`eval-set`) are how the Makefile and a person run each part of the lesson. `argparse` gives them sub-commands, options, validation and `--help` from the standard library, with no extra dependency.

## Where it appears

| File | What it does with argparse (command-line programs) |
| --- | --- |
| `src/eval_set_builder/interfaces/cli.py` | the parser and `main` |

## How it works underneath

When you run `refund-agent gate --weaken ownership`, the operating system starts Python and hands the program the list of words `["gate", "--weaken", "ownership"]`. `ArgumentParser` builds a description of what is allowed. `add_subparsers(dest="command", required=True)` creates *sub-commands* (like `git commit`): the first word chooses one. `add_argument("--runs", type=int, default=3)` adds an *option* with a name, a converter and a default. `parse_args(argv)` returns an object whose attributes hold the values (`arguments.command`, `arguments.runs`); a bad value prints a usage message and exits with code 2.

The program's `main(argv=None)` function takes the list as an optional argument, so tests call `main(["gate"])` directly without starting a new process, and returns an integer that becomes the *exit code*: 0 for success. At the bottom, `raise SystemExit(main())` turns the return value into the process's exit code. Installing the package creates a console command that calls `main`.

## Walkthrough of this repository's use

The program is `eval-set` (created from `[project.scripts]` in `pyproject.toml`). First, the function that declares what the command line accepts:

From `src/eval_set_builder/interfaces/cli.py`:

```python
def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="eval-set", description="Build the versioned eval set from raw traces.")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("generate", help="write the raw traces and the answer key from the seed")
    for stage in STAGES:
        commands.add_parser(stage.replace("_", "-"), help=f"run the {stage} stage")
    commands.add_parser("run-all", help="every stage from the raw file to the frozen set")
    commands.add_parser("rebuild-check", help="rebuild in a temporary folder and compare hashes with the committed set")
    commands.add_parser("record-synthetic", help="call the real model for every seed and write the cassette")
    return parser
```

- `def _parser() -> argparse.ArgumentParser:`: A function that builds the parser. `-> argparse.ArgumentParser` says it returns one.
- `parser = argparse.ArgumentParser(prog="eval-set", description="Build the versioned eval set from raw traces.")`: Creates the parser. `prog` (`eval-set`) is the program name shown in usage messages and `description` (`Build the versioned eval set from raw traces.`) is the text shown under `--help`.
- `commands = parser.add_subparsers(dest="command", required=True)`: Makes room for sub-commands. `dest="command"` stores the chosen one in `arguments.command`; `required=True` means one must be chosen.
- `commands.add_parser("generate", help="write the raw traces and the answer key from the seed")`: Declares the sub-command `generate`. Help text: write the raw traces and the answer key from the seed
- `for stage in STAGES:`: A loop over STAGES.
- `commands.add_parser(stage.replace("_", "-"), help=f"run the {stage} stage")`: Declares one sub-command per pipeline stage; `stage.replace("_", "-")` turns `sample_and_guide` into `sample-and-guide`.
- `commands.add_parser("run-all", help="every stage from the raw file to the frozen set")`: Declares the sub-command `run-all`. Help text: every stage from the raw file to the frozen set
- `commands.add_parser("rebuild-check", help="rebuild in a temporary folder and compare hashes with the committed set")`: Declares the sub-command `rebuild-check`. Help text: rebuild in a temporary folder and compare hashes with the committed set
- `commands.add_parser("record-synthetic", help="call the real model for every seed and write the cassette")`: Declares the sub-command `record-synthetic`. Help text: call the real model for every seed and write the cassette
- `return parser`: Hands the finished parser back.

Then the start of `main`, which every sub-command passes through:

```python
def main(argv: Sequence[str] | None = None) -> int:
    """Run one subcommand; returns the process exit code."""
    arguments = _parser().parse_args(argv)
    try:
        settings = Settings.from_environ(os.environ)
    except ConfigurationError as error:
        print(f"configuration error: {error}", file=sys.stderr)
        return 2
    configure_logging(settings.log_level)
    try:
```

- `def main(argv: Sequence[str] | None = None) -> int:`: The program's entry. `argv` is the list of arguments; `None` means 'use the real command line'. It returns the exit code.
- `"""Run one subcommand; returns the process exit code."""`: The docstring.
- `arguments = _parser().parse_args(argv)`: Builds the parser and parses the words. On a usage error argparse prints a message and exits with code 2 here.
- `try:`: Starts a block whose errors are handled below.
- `settings = Settings.from_environ(os.environ)`: Reads and validates every environment variable once (see `dotenv.md`).
- `except ConfigurationError as error:`: A bad setting.
- `print(f"configuration error: {error}", file=sys.stderr)`: Prints the message on standard error, where error messages belong.
- `return 2`: Exit code 2: the same code argparse uses for bad usage.
- `configure_logging(settings.log_level)`: Turns logging on at the chosen level (see `logging.md`).
- `try:`: Starts a block whose errors are handled below.

After that, `main` chooses what to run by the sub-command. Each branch calls one helper; this table is read from the file:

| Sub-command | Help text | Helper `main` calls | What the helper's docstring says |
| --- | --- | --- | --- |
| `generate` | write the raw traces and the answer key from the seed | (handled inline in `main`) |  |
| `run-all` | every stage from the raw file to the frozen set | (handled inline in `main`) |  |
| `rebuild-check` | rebuild in a temporary folder and compare hashes with the committed set | `_rebuild_check` | Run one subcommand; returns the process exit code. |
| `record-synthetic` | call the real model for every seed and write the cassette | `_record_synthetic` | Run one subcommand; returns the process exit code. |
| `_` | - | (handled inline in `main`) |  |
| `-` | _ | (handled inline in `main`) |  |

And the last two lines of the file:

```python
if __name__ == "__main__":
    raise SystemExit(main())
```

- `if __name__ == "__main__":`: True only when the file is run directly, not when it is imported.
- `raise SystemExit(main())`: Runs `main` and ends the process with the number it returned as the exit code.

## Try it yourself

Run these from the repository folder (after `make up`).

```bash
.venv/bin/eval-set --help
```

Prints the usage line and the list of sub-commands with their help text.

```bash
.venv/bin/eval-set not-a-command; echo $?
```

Prints a usage error and then `2`, argparse's exit code for bad usage.

## Mistakes people make

- Reading `sys.argv` by hand; `argparse` gives validation and `--help` for free.
- Calling `sys.exit` deep inside the code. The functions return codes to `main`, so tests can check them.
- Forgetting `required=True` on sub-parsers, which makes a bare command silently do nothing.
- Returning nothing instead of an exit code; shells and CI rely on a non-zero code to detect failure.
- Parsing numbers by hand. `type=int` and `type=float` report bad input clearly.

## Check yourself

1. What does `add_subparsers` do?
   *Answer:* Creates sub-commands, such as `program gate` and `program serve`.
2. What happens on an invalid option value?
   *Answer:* A usage message is printed and the program exits with code 2.
3. Why does `main` accept an optional list of arguments?
   *Answer:* So tests can call it directly with a list.
4. What is an exit code?
   *Answer:* A number a program returns to the shell: 0 for success, anything else for failure.
5. What does `type=int` do?
   *Answer:* Converts the text to an integer and rejects text that is not one.

## Further reading

- [argparse](https://docs.python.org/3.12/library/argparse.html)
- [argparse tutorial](https://docs.python.org/3.12/howto/argparse.html)
