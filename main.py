#!/usr/bin/env python3
"""Entry point for the make.fun bounty news-image-20261119.

Reads nothing, fetches nothing, writes one file: <output_dir>/entry.png —
the front page of THE WORLD for Thursday 19 November 2026.

    python3 main.py                     # writes /output/entry.png
    python3 main.py out                 # writes out/entry.png

The output directory resolves in this order: the MAKEFUN_OUTPUT_DIR
environment variable (what the harness exports), then argv[1], then
/output.  Grader runs it as `python3 -P -s main.py` — isolated mode, so the
script's own directory is not on sys.path; it is inserted explicitly so the
sibling modules import without relying on any site or user package.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import frontpage  # noqa: E402


def resolve_output_dir(argv):
    """MAKEFUN_OUTPUT_DIR, else argv[1], else /output — all absolute."""
    env = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if env:
        return os.path.abspath(env)
    if len(argv) > 1:
        return os.path.abspath(argv[1])
    return os.path.abspath("/output")


def main(argv):
    out_dir = resolve_output_dir(argv)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")

    audit = []
    width, height = frontpage.save_page(path, audit=audit)

    print("wrote %s (%dx%d, %d bytes)"
          % (path, width, height, os.path.getsize(path)))

    bad = frontpage.overruns(audit)
    if bad:
        for label, used, limit in bad:
            print("OVERRUN %s: %.1f > %.1f px" % (label, used, limit),
                  file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))