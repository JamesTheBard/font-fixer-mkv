from font_fixer.subtitles import Parser

a = Parser()
a.load_style_remap("fonts/style_remap.toml")
a.generate_font_map("fonts")
