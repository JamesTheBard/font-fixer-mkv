import sys
from argparse import ArgumentParser
from pathlib import Path

from font_fixer import fonts
from font_fixer.matroska import Matroska

parser = ArgumentParser()
parser.add_argument("-v", "--video", help="The video to parse for fonts.")
args = parser.parse_args()

video = Path(args.video)
if not video.exists():
    print(f"File does not exist: {video.absolute()}")
    sys.exit(1)

a = Matroska(args.video, font_dir="temp")
a.load_style_remap("style_remap.toml")

try:
    [print(f"{i.family:.<24}: {i.file}") for i in a.create_font_list()]
except fonts.FontNotFoundError as e:
    print(e.message, e.style)
