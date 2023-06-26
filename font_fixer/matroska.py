from typing import Union
from pathlib import Path
from box import Box

import tempfile
import subprocess
import json

class Matroska:

    def __init__(self, filename: Union[Path, str]):
        self.filename = Path(filename)
        self.data = self.parse_matroska_file()
    
    def parse_matroska_file(self):
        command = f'mkvmerge -J "{self.filename}'
        result = subprocess.Popen(command, stdout=subprocess.PIPE)
        output, _ = result.communicate()
        output = Box(json.loads(output))
        return output
    
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
    


        
        