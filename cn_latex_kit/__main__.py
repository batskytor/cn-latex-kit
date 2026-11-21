"""Allow running the CLI with ``python -m cn_latex_kit``."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
