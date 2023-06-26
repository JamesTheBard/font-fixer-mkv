from font_fixer.fonts import (FontNotFoundError, generate_font_list,
                              generate_font_map, generate_style_map)

font_map = generate_font_map("fonts")
style_map = generate_style_map("videos/subs2.ass")
try:
    font_list = generate_font_list(font_map=font_map, style_map=style_map)
except FontNotFoundError as e:
    print("Missing font for style:", e.style)

print("Styles found in subtitle file:")
print("=" * 70)
[print(i) for i in style_map]
print()

print("Associated fonts:")
print("=" * 70)
font_list = generate_font_list(font_map, style_map)
[print(i) for i in font_list]

print("\nAll styles associated with a font, exiting.")