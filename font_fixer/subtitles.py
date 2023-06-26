from typing import Union, List
from pathlib import Path
import tomllib

from font_fixer.fonts import Font, get_info


class Parser:

    style_remap: dict

    def __init__(self):
        pass

    def generate_font_map(self, font_directory: Union[Path, str]) -> List[Font]:
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

    

if __name__ == "__main__":
    a = Parser()
    a.load_style_remap("../fonts/style_remap.toml")
    print(a.style_remap)

