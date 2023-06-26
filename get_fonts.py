import sys
from argparse import ArgumentParser
from pathlib import Path

from font_fixer.fonts import (generate_font_list, generate_font_map,
                              generate_style_map_from_content, FontNotFoundError)
from font_fixer.matroska import Matroska

parser = ArgumentParser()
parser.add_argument("-v", "--video", help="The video to parse for fonts.")
args = parser.parse_args()

video = Path(args.video)
if not video.exists():
    print(f"File does not exist: {video.absolute()}")
    sys.exit(1)

a = Matroska(args.video)
c = a.get_substation_alpha_content()

font_map = generate_font_map("fonts")
[print(i) for i in font_map]

style_map = list()
for id in c.keys():
    style_map.extend(generate_style_map_from_content(c[id]))

try:
    font_list = generate_font_list(font_map, style_map)
except FontNotFoundError as e:
    print(f"Could not find a font for style: {e.style}")

[print(str(i.file)) for i in font_list]
