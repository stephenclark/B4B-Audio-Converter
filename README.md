# B4B Audio Converter

Splits an audiobook (`.b4b` / `.m4b`) into one file per chapter, using ffmpeg inside a Docker container. Nothing is installed on your computer apart from Docker itself.

By default the audio is copied as-is into `.m4a` files: lossless and fast. Chapter titles, book title, author and track numbers are written into each file's tags.

## Files

| File | Purpose |
|---|---|
| `Dockerfile` | Builds a small image (Python + ffmpeg) with the script baked in |
| `docker-compose.yml` | Starts the container and shares the `books/` folder with it |
| `split_audiobook.py` | The splitter script |
| `books/` | Put audiobooks here; chapter folders appear here too |

## Usage

1. Copy your audiobook into the `books/` folder.
2. In Terminal, from this folder:

   ```
   docker compose build                # first time, or after editing the script
   docker compose run --rm audiobook   # opens a shell in the container
   ```

3. Inside the container:

   ```
   split_audiobook.py books/my_book.m4b             # lossless M4A chapters
   split_audiobook.py books/my_book.m4b --mp3       # re-encode to MP3 instead
   split_audiobook.py books/my_book.m4b -o books/out # choose output folder
   ```

4. Type `exit` to leave. The container is deleted automatically.

Output lands in `books/<book name>_chapters/`, with files named like `02 - Chapter 1 - The Boy Who Lived.m4a`.

## Notes

- `.b4b` and `.m4b` are the same thing (AAC audio in an MP4 container with chapter markers), so the script handles both.
- The book must contain chapter markers. If it doesn't, the script says so and stops.
- DRM-protected books (e.g. Audible) can't be read by ffmpeg.
- `--mp3` re-encodes (VBR quality 2, roughly 190 kbps), so it's slower and slightly lossy. Use it only if your player won't take M4A.
- The script is copied into the image at build time. After editing `split_audiobook.py`, run `docker compose build` again.

## Cleanup

```
docker rmi audiobook-tool    # remove the image
```

Deleting this folder removes everything else.
