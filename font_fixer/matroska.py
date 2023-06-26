from typing import Union
from pathlib import Path
from box import Box
import tomllib

import tempfile
import subprocess
import json

from font_fixer import fonts

class Matroska:

    def __init__(self, filename: Union[Path, str], font_dir: Union[Path, str] = "fonts"):
        self.font_dir = Path(font_dir)
        self.font_map = self.create_font_map()
        self.filename = Path(filename)
        self.data = self.parse_matroska_file()
        self.content = self.get_substation_alpha_content()
        self.style_map = self.generate_style_map()
        self.style_remap = dict()
    
    def parse_matroska_file(self):
        command = f'mkvmerge -J "{self.filename}'
        result = subprocess.Popen(command, stdout=subprocess.PIPE)
        output, _ = result.communicate()
        output = Box(json.loads(output))
        return output
    
    def load_style_remap(self, remap: Union[Path, str], verbose: bool = True) -> None:
        remap = Path(remap)
        with remap.open('rb') as f:
            self.style_remap = tomllib.load(f)
    
    def get_substation_alpha_content(self):
        content = dict()
        ssa_track_ids = [i.id for i in self.data.tracks if i.codec == "SubStationAlpha"]
        for id in ssa_track_ids:
            filename = Path(tempfile.gettempdir())
            filename = Path(filename, f"subtitles_{id:02}.ass")
            command = f'mkvextract "{self.filename}" tracks {id}:{str(filename)}'
            result = subprocess.Popen(command, stdout=subprocess.PIPE)
            output, _ = result.communicate()
            with filename.open("r", encoding="utf8") as f:
                content[id] = f.readlines()
            filename.unlink()
        return content
    
    def generate_style_map(self) -> list:
        style_map = list()
        for key in self.content.keys():
            style_map.extend(fonts.generate_style_map_from_content(self.content[key]))
        return style_map
    
    def create_font_map(self) -> list:
        return fonts.generate_font_map(self.font_dir)
    
    def create_font_list(self) -> list:
        font_list = list()
        for s in self.style_map:
            try:
                remap = Box(self.style_remap[s.family]['_'.join(sorted(s.subfamily))])
                family = remap.family
                subfamily = remap.subfamily
                candidates = [i for i in self.font_map if i.family == family and not (set(i.subfamily) ^ set(subfamily))]
            except KeyError:
                candidates = [i for i in self.font_map if i.family == s.family and not (set(i.subfamily) ^ set(s.subfamily))]

            if len(candidates) == 1:
                font_list.append(candidates[0])
            elif len(candidates) > 1:
                [print(i) for i in candidates]
                raise fonts.FontMultpleFoundError(style=s)
            else:
                raise fonts.FontNotFoundError(style=s)
        return fonts.remove_duplicates(font_list)
        # return font_list
    