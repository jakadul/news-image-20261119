#!/usr/bin/env python3
"""Install the finished make.fun news-image entry.

The front page is already rendered: entry.png (1024x1024) sits committed next to
this file. The artwork is committed rather than drawn on every run because a
make.fun entry is allowed to be exactly that -- an image plus a one-line program
that copies it to the output directory. Rendering it at run time would only add
a renderer, its fonts and its dependencies for a result that never changes.

Resolution order for the output directory:
  1. MAKEFUN_OUTPUT_DIR environment variable
  2. argv[1]
  3. /output
"""

import os
import shutil
import sys
from pathlib import Path

ARTWORK = "entry.png"


def resolve_output_dir() -> Path:
    """Pick the destination: env var, then argv[1], then /output."""
    env = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if env:
        return Path(env)
    if len(sys.argv) > 1 and sys.argv[1]:
        return Path(sys.argv[1])
    return Path("/output")


def main() -> int:
    out_dir = resolve_output_dir()
    out_dir.mkdir(parents=True, exist_ok=True)

    src = Path(__file__).resolve().parent / ARTWORK
    dst = out_dir / ARTWORK
    shutil.copyfile(src, dst)

    size = dst.stat().st_size
    print(f"installed {dst} ({size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())