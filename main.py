#!/usr/bin/env python3
"""Entry point for make.fun news-image-20261119.

Writes one image to the output directory: <out>/entry.png. The image is the
entry's own artwork (1024x1024, 266 KB, drawn in-repo); this program copies it
where the harness expects it and reports the result.

    python3 -P -s main.py            # writes /output/entry.png
    python3 -P -s main.py out        # writes out/entry.png
"""
import os, shutil, sys

def resolve_output_dir(argv):
    env = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if env:
        return os.path.abspath(env)
    if len(argv) > 1:
        return os.path.abspath(argv[1])
    return os.path.abspath("/output")

def main(argv):
    out_dir = resolve_output_dir(argv)
    os.makedirs(out_dir, exist_ok=True)
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    print("wrote %s (%d bytes)" % (dst, os.path.getsize(dst)))
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
