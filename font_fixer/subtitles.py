from typing import Union, List
from pathlib import Path
import tomllib

from font_fixer.fonts import Font, get_info


class Parser:

    style_remap: dict

    def __init__(self):
        pass

    def generate_font_map(self, font_directory: Union[Path, str]) -> None:
        font_directory = Path(font_directory)
        font_map = list()
        for file in font_directory.iterdir():
            if file.suffix.lower() in [".ttf", ".otf"]:
                font_map.append(get_info(file))
        self.font_map = font_map

    def load_style_remap(self, remap: Union[Path, str], verbose: bool = True) -> None:
        remap = Path(remap)
        with remap.open('rb') as f:
            self.style_remap = tomllib.load(f)

    def __get_styles_from_dialog_content(content: List[str]) -> List[Style]:
        regex = r'\{.*?\\fn(.+?)(?:}|\\)'
        r = re.compile(regex)
        override_fonts = list()
        for i in content:
            a = r.findall(i)
            if a:
                override_fonts.append(a[0])
        override_fonts = list(set(override_fonts))
        return [Style(family=f, subfamily=['Regular'], style=f'Override:{f}') for f in override_fonts]

    def __get_styles_from_style_content(content: List[str]) -> List[Style]:
        header_style_map = get_styles_from_headers_content(content)
        header_style_map.extend(get_styles_from_override_codes_content(content))
        return header_style_map


    def parse_matroska_file(self, mkv_file: Union[Path, str]):
        mkv_file = Path(mkv_file)


    

if __name__ == "__main__":
    a = Parser()
    a.load_style_remap("../fonts/style_remap.toml")
    print(a.style_remap)

