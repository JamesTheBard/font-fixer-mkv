import sys
import re
import tomllib
from typing import List, NamedTuple, Union
from dataclasses import dataclass

from fontTools import ttLib, otlLib
from wcmatch.pathlib import Path

FONT_FAMILY_SPECIFIER = 1
FONT_SUBFAMILY_SPECIFIER = 2
FONT_NAME_SPECIFIER = 4


@dataclass
class Font:
    name: str
    family: str
    subfamily: list
    file: Path
    ignore_subfamily: bool


@dataclass
class Style:
    style: str
    family: str
    subfamily: list


# class SubtitleInfo:
#     input_file: Path
#     styles: List[Style]

#     def __init__(self, input_file: Union[str, List]):
#         self.input_file = Path(input_file)
#         self.styles = list()
#         self.__generate_style_map()

#     def __generate_style_map(self) -> None:
#         with self.input_file.open("r") as f:
#             subtitles = f.readlines()
#         subtitles = [i for i in subtitles if i.startswith("Style: ")]
#         styles = [i.split(",") for i in subtitles]
#         for style in styles:
#             subfamily = list()
#             s = style[0].split(": ")[1]
#             family = style[1]
#             if int(style[7]):
#                 subfamily.append("Bold")
#             if int(style[8]):
#                 subfamily.append("Italic")
#             if not subfamily:
#                 subfamily.append("Regular")
#             style_info = Style(style=s, family=family, subfamily=subfamily)
#             self.styles.append(style_info)

def get_info(font_file: Union[Path, str]) -> Font:
    if font_file.suffix.lower() == ".ttf":
        return get_ttf_info(font_file)
    if font_file.suffix.lower() == ".otf":
        return get_ttf_info(font_file)
    
def get_ttf_info(font_file: Union[Path, str]) -> Font:
    ignore_subfamily = Path(f"{str(font_file)}.all_styles").exists()
    override = Path(f"{str(font_file)}.override")
    font = ttLib.TTFont(str(font_file))
    name = str()
    family = str()
    subfamily = str()
    for record in font["name"].names:
        if record.nameID == FONT_NAME_SPECIFIER and not name:
            if b"\000" in record.string:
                name = str(record.string, "utf-16-be").encode("utf-8")
            else:
                name = record.string
        elif record.nameID == FONT_FAMILY_SPECIFIER and not family:
            if b"\000" in record.string:
                family = str(record.string, "utf-16-be").encode("utf-8")
            else:
                family = record.string
        elif record.nameID == FONT_SUBFAMILY_SPECIFIER and not subfamily:
            if b"\000" in record.string:
                subfamily = str(record.string, "utf-16-be").encode("utf-8")
            else:
                subfamily = record.string
        if name and family and subfamily:
            break

    subfamily = [
        i if i != "Oblique" else "Italic" for i in subfamily.decode().split(" ")
    ]

    f = Font(
        name=name.decode() if type(name) == bytes else name,
        family=family.decode() if type(name) == bytes else family,
        subfamily=subfamily,
        file=font_file,
        ignore_subfamily=ignore_subfamily,
    )

    if override.exists():
        with override.open('rb') as g:
            o_content = tomllib.load(g)
        for i in o_content.keys():
            print(o_content[i])
            setattr(f, i, o_content[i])

    return f
            

def generate_font_map(font_directory: Union[Path, str]) -> List[Font]:
    font_directory = Path(font_directory)
    font_map = list()
    for file in font_directory.iterdir():
        if file.suffix.lower() in [".ttf", ".otf"]:
            font_map.append(get_info(file))
    return font_map


def generate_style_map(subtitle_file: Union[Path, str]) -> List[Style]:
    header_style_map = get_styles_from_headers(subtitle_file)
    header_style_map.extend(get_styles_from_override_codes(subtitle_file))
    return header_style_map


def generate_style_map_from_content(content: List[str]) -> List[Style]:
    header_style_map = get_styles_from_headers_content(content)
    header_style_map.extend(get_styles_from_override_codes_content(content))
    return header_style_map


def get_styles_from_override_codes(subtitle_file: Union[Path, str]) -> List[Style]:
    subtitle_file = Path(subtitle_file)
    with subtitle_file.open("r") as f:
        subtitles = f.readlines()
    return get_styles_from_override_codes_content(subtitles)
    

def get_styles_from_override_codes_content(content: List[str]) -> List[Style]:
    temp_style_map = get_styles_from_headers_content(content)
    font_override_regex = r'\{.*?\\fn(.+?)(?:}|\\)'
    font_italics_regex = r'\{.*?\\i1(?:}|\\)'
    font_bold_regex = r'\{.*?\\b1(?:}|\\)'

    r_override = re.compile(font_override_regex)
    r_italics = re.compile(font_italics_regex)
    r_bold = re.compile(font_bold_regex)

    style_map = list()
    data_section = False
    for i in content:
        if not i.startswith('Dialogue'):
            continue
        style = i.split(",")[3]
        subfamily = ["Regular"]
        o = r_override.findall(i)
        bold = r_bold.findall(i)
        italics = r_italics.findall(i)
        if bold or italics:
            subfamily = list()
            if bold:
                subfamily.append('Bold')
            if italics:
                subfamily.append('Italic')
        s = [i for i in temp_style_map if i.style == style][0]
        if o:
            style_override = Style(family=o[0], subfamily=s.subfamily, style=f'FOverride:{style}:{"+".join(s.subfamily)}')
            style_map.append(style_override)
            subfamily = list(set(subfamily) | set(s.subfamily))
            if "Regular" in subfamily and len(subfamily) > 1:
                subfamily.remove("Regular")
            if set(s.subfamily) != set(subfamily):
                style_map.append(Style(family=o[0], subfamily=subfamily, style=f'FOverride:{style}:{"+".join(subfamily)}'))
        elif style and (italics or bold):
            if s.subfamily == subfamily:
                continue
            subfamily = list(set(subfamily) | set(s.subfamily))
            if "Regular" in subfamily and len(subfamily) > 1:
                subfamily.remove("Regular")
            j = Style(family=s.family, subfamily=subfamily, style=f'SOverride:{style}:{"+".join(subfamily)}')
            style_map.append(j)
            
    return style_map


def get_styles_from_headers(subtitle_file: Union[Path, str]) -> List[Style]:
    subtitle_file = Path(subtitle_file)
    with subtitle_file.open("r") as f:
        subtitles = f.readlines()
    return get_styles_from_headers_content(subtitles)
    

def get_styles_from_headers_content(content: List[str]) -> List[Style]:
    subtitles = [i for i in content if i.startswith("Style: ")]
    styles = [i.split(",") for i in subtitles]
    style_map = list()
    for style in styles:
        subfamily = list()
        s = style[0].split(": ")[1]
        family = style[1]
        if int(style[7]):
            subfamily.append("Bold")
        if int(style[8]):
            subfamily.append("Italic")
        if not subfamily:
            subfamily.append("Regular")
        style_info = Style(style=s, family=family, subfamily=subfamily)
        style_map.append(style_info)
    return style_map


def generate_font_list(font_map: List[Font], style_map: List[Style]) -> List[Font]:
    fonts = list()
    for s in style_map:
        p = [
            i
            for i in font_map
            if i.family == s.family and not (set(i.subfamily) ^ set(s.subfamily))
        ]
        if len(p) == 1:
            fonts.append(p[0])
        else:
            p = [i for i in font_map if i.family ==
                 s.family and i.ignore_subfamily]
            if len(p) == 1:
                fonts.append(p[0])
            else:
                raise FontNotFoundError(style=s)
    return remove_duplicates(fonts)


def remove_duplicates(font_map: List[Font]) -> List[Font]:
    new_map = list()
    for font in font_map:
        if font.file not in [i.file for i in new_map]:
            new_map.append(font)
    return new_map


class FontError(Exception):
    pass


class FontNotFoundError(FontError):
    def __init__(self, style: Style, message: str = "Font file missing for a Style."):
        self.message = message
        self.style = style

class FontMultpleFoundError(FontError):
    def __init__(self, style: Style, message: str = "Multiple fonts found for a Style."):
        self.message = message
        self.style = style
