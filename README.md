# make.fun news-image entry — Thursday 19 November 2026

This repository is the accepted simplest form of a make.fun news-image entry:
an image plus a one-line program that copies it to the output directory.

## What is here

- `entry.png` — the finished 1024x1024 front page for Thursday 19 November 2026.
  It carries 42 stories across seven colour-coded regions, a world map, and a
  printed date check.
- `main.py` — the whole program. It only installs the committed artwork into the
  output directory; it does not draw anything.

The artwork is committed rather than rendered on every run. A news-image entry
is allowed to be exactly an image plus a copy step, and rendering at run time
would only pull in a renderer, its fonts and its dependencies for a result that
never changes.

## Run

```
MAKEFUN_OUTPUT_DIR=out python3 -P -s main.py
```

The output directory is resolved in this order:

1. the `MAKEFUN_OUTPUT_DIR` environment variable
2. the first command-line argument
3. `/output`

The directory is created if it is missing, `entry.png` is copied into it, and
the program prints one line naming the destination and the byte count before
exiting 0.