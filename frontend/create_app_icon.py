from PIL import Image

SIZE = 1024
BACKGROUND = "#062A55"

LOGO_PATH = "assets/images/logo.png"
OUTPUT_PATH = "assets/images/app_icon.png"

background = Image.new(
    "RGBA",
    (SIZE, SIZE),
    BACKGROUND,
)

logo = Image.open(LOGO_PATH).convert("RGBA")

logo.thumbnail(
    (SIZE, SIZE),
    Image.Resampling.LANCZOS,
)

x = (SIZE - logo.width) // 2
y = (SIZE - logo.height) // 2 + 30

background.alpha_composite(
    logo,
    (x, y),
)

background.convert("RGB").save(
    OUTPUT_PATH,
    "PNG",
)

print(f"Gotowe: {OUTPUT_PATH}")