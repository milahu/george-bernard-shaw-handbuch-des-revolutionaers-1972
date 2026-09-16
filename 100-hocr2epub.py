#!/usr/bin/env python3

import glob
import os
import re
import shutil
import subprocess
import sys
import zipfile
import shlex
from datetime import datetime
from pathlib import Path

from _shared import (
    load_config,
    get_page_num,
)


src = Path("090-ocr")

# write EPUB file
# dst = Path(Path(__file__).stem + ".epub")

# write unpacked EPUB files to workdir
dst = Path(".")


config = load_config()


if dst != Path(".") and dst.exists():
    print(f"error: output exists: {dst}")
    sys.exit(1)


# downscale to 300 dpi
# 600 dpi -> 300 dpi: 90 MB -> 60 MB
scale = 300 / config.scan_resolution


hocr_to_epub_fxl = "hocr-to-epub-fxl"

# TODO dont commit
if 1:
    hocr_to_epub_fxl = "/home/user/src/archive-hocr-tools/bin/hocr-to-epub-fxl"

args = [
    hocr_to_epub_fxl,
    "--output", str(dst),
]

if dst == Path("."):
    args.append("--output-unpacked")


def git_modified():
    return subprocess.check_output(
        ["git", "show", "-s", "--format=%cI", "HEAD"],
        text=True,
    ).strip()


def stat_modified(path):
    ts = Path(path).stat().st_mtime
    dt = datetime.fromtimestamp(ts).astimezone()
    return dt.isoformat(timespec="seconds")


doc_modified = max(
    git_modified(),
    stat_modified(src),
)


args += [
    "--scale", str(scale),
    "--image-format", "avif",
    "--text-format", "html",
    # TODO? move these config items to 000-config.py
    "--doc-modified", doc_modified,
    "--doc-title", "Handbuch des Revolutionärs",
    # "--doc-subtitle", "",
    # "--doc-subject", "",
    "--doc-date", "1972",
    "--doc-edition", "1",
    "--doc-extent", "136 pages",
    "--color-image-pages", "137-140",
    "--doc-author", "George Bernard Shaw",
    # "--doc-introducer", "",
    # "--doc-contributor", "",
    "--doc-translator", "Annemarie Böll",
    "--doc-translator", "Heinrich Böll",
    "--doc-publisher", "Suhrkamp Verlag",
    "--doc-language", "de", # german
    # "--doc-language", "en", # english
    "--doc-isbn", "9783518013090",
    "--doc-cover-image", "072-deskew-fix-page-size/137.tiff",
    "--canonical-url-base", "https://milahu.github.io/george-bernard-shaw-handbuch-des-revolutionaers-1972/",
    "--doc-description", """
Wer zuviel Wahrheit sagt, der ist des Henkers sicher.

Shaws berühmter Anhang zu »Mensch und Übermensch«,
das Handbuch und die Aphorismen des Revolutionärs,
liegt in neuer deutscher Übertragung vor.

Winston Chur­chill bezeichnete Shaw als einen »Heiligen, Weisen und Narren«,
Brecht nannte ihn einen »Terroristen«, freilich »mit der ungewöhnlichen Waffe des Humors«.
Diese Kennzeichnungen treffen in besonderer Weise auf den Autor des »Handbuchs« zu.
Shaws Texte sind genial, geist­voll, witzig, stimmig und — für die siebziger Jahre — durchaus aktuell.
Manche Parolen unserer Jugend von heute
(»Jeder Mensch unter dreißig, der einige Kenntnis der bestehenden Gesellschafts­ordnung besitzt und kein Revolutionär ist, ist minder­wertig«
oder »Jeder Mann über vierzig ist ein Schuft«)
stammen — von Shaw.
""",
]


print(">", shlex.join(args + sys.argv[1:]) + f" {src}/*.hocr")


hocr_files = list(src.glob("*.hocr"))

hocr_files.sort()

subprocess.run(
    args + sys.argv[1:] + hocr_files,
    check=True,
)


if dst == Path("."):
    print("done ./index.xhtml")
    sys.exit(0)


print(f"done {dst}")


# extract the EPUB content files

# rm -rf $dst.unzip
unzip_dir = Path(str(dst) + ".unzip")
shutil.rmtree(unzip_dir, ignore_errors=True)
unzip_dir.mkdir()


# unzip -q ../$dst
with zipfile.ZipFile(dst) as z:
    z.extractall(unzip_dir)


print(f"done {unzip_dir}/index.html")
