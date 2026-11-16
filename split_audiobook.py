#!/usr/bin/env python3
"""Split a .b4b / .m4b audiobook into per-chapter .m4a files (no re-encoding).

Usage:
    python3 split_audiobook.py book.b4b [-o outdir] [--mp3]

Requires ffmpeg + ffprobe: either on PATH or placed in the same folder as this script.
Default: stream copy -> lossless, fast, M4A/AAC output.
--mp3 : re-encode each chapter to MP3 (V2 VBR) if your player dislikes M4A.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent


def tool(name):
    """Prefer a binary sitting next to this script, else fall back to PATH."""
    local = HERE / name
    if local.exists():
        return str(local)
    return shutil.which(name)


FFMPEG = tool("ffmpeg")
FFPROBE = tool("ffprobe")


def run_probe(src):
    out = subprocess.run(
        [FFPROBE, "-v", "error", "-print_format", "json",
         "-show_chapters", "-show_format", str(src)],
        capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def safe(name):
    return re.sub(r'[\\/:*?"<>|]+', "_", name).strip() or "Chapter"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("-o", "--outdir")
    ap.add_argument("--mp3", action="store_true", help="re-encode to MP3 instead of copying AAC")
    a = ap.parse_args()

    if not (FFMPEG and FFPROBE):
        sys.exit("ffmpeg/ffprobe not found. Put both binaries in the same folder as this script.")

    src = Path(a.input).expanduser().resolve()
    outdir = Path(a.outdir).expanduser() if a.outdir else src.with_suffix("").parent / (src.stem + "_chapters")
    outdir.mkdir(parents=True, exist_ok=True)

    info = run_probe(src)
    chapters = info.get("chapters", [])
    tags = info.get("format", {}).get("tags", {})
    book = tags.get("title") or tags.get("album") or src.stem
    author = tags.get("artist") or tags.get("album_artist") or ""
    ext = "mp3" if a.mp3 else "m4a"

    if not chapters:
        sys.exit("No chapter markers found in this file. "
                 "Convert whole file instead: ffmpeg -i in.b4b -vn -c:a copy out.m4a")

    n = len(chapters)
    width = max(2, len(str(n)))
    for i, ch in enumerate(chapters, 1):
        title = ch.get("tags", {}).get("title") or f"Chapter {i}"
        out = outdir / f"{i:0{width}d} - {safe(title)}.{ext}"
        cmd = [FFMPEG, "-y", "-v", "error", "-i", str(src),
               "-ss", ch["start_time"], "-to", ch["end_time"],
               "-map", "0:a:0", "-vn", "-map_chapters", "-1",
               "-metadata", f"title={title}",
               "-metadata", f"album={book}",
               "-metadata", f"track={i}/{n}"]
        if author:
            cmd += ["-metadata", f"artist={author}"]
        cmd += (["-c:a", "libmp3lame", "-q:a", "2"] if a.mp3 else ["-c:a", "copy"])
        cmd.append(str(out))
        subprocess.run(cmd, check=True)
        print(f"[{i}/{n}] {out.name}")

    print(f"\nDone: {n} files in {outdir}")


if __name__ == "__main__":
    main()
