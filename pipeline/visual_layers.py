"""Optional modern board backdrops for CurioKids.

The existing character and board content renderers remain untouched. This module
adds a deterministic, lightweight 2D/2.5D visual layer behind board content.
"""
import math
import zlib

PALETTES = {
    "ocean": ("#E9F7FF", "#C8E8FF", "#2D75A5"),
    "sunrise": ("#FFF2D8", "#FFD9C7", "#A85D43"),
    "garden": ("#EAF8E9", "#CBECCF", "#397A55"),
    "space": ("#EDEBFF", "#D6D3FF", "#5547A5"),
    "candy": ("#FFF0F5", "#FAD7E6", "#A64D79"),
    "paper": ("#FFF9E9", "#F5EBD2", "#7B694B"),
}
STYLES = set(PALETTES) | {"none"}


def resolve_style(episode_visual=None, environment=None):
    """Resolve optional style without changing legacy episodes."""
    if environment:
        style = environment
    elif isinstance(episode_visual, dict):
        style = episode_visual.get("style", "none")
    elif isinstance(episode_visual, str):
        style = episode_visual
    else:
        style = "none"
    return style if style in STYLES else "none"


def _color(skia, value):
    value = value.lstrip("#")
    return skia.ColorSetRGB(int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))


def draw_backdrop(canvas, skia, bounds, t, style="none", seed="curiokids"):
    """Draw a clipped pastel depth field and restrained decorative geometry."""
    if style not in PALETTES:
        return
    x, y, width, height = bounds
    top, bottom, accent = PALETTES[style]
    canvas.save()
    clip = skia.Rect.MakeXYWH(x, y, width, height)
    canvas.clipRect(clip, doAntiAlias=True)

    shader = skia.GradientShader.MakeLinear(
        [skia.Point(x, y), skia.Point(x + width, y + height)],
        [_color(skia, top), _color(skia, bottom)],
        [0.0, 1.0], skia.TileMode.kClamp)
    paint = skia.Paint(AntiAlias=True)
    paint.setShader(shader)
    canvas.drawRect(clip, paint)

    # Low-contrast oversized shapes create depth without competing with text.
    translucent = skia.Paint(AntiAlias=True, Color=skia.ColorSetARGB(34, 255, 255, 255))
    canvas.drawCircle(x + width * 0.12, y + height * 0.18, height * 0.23, translucent)
    canvas.drawCircle(x + width * 0.91, y + height * 0.82, height * 0.30, translucent)

    # A subtle perspective floor/grid is limited to the lower 22% of the board.
    grid = skia.Paint(AntiAlias=True, Color=_color(skia, accent))
    grid.setAlphaf(0.10)
    grid.setStyle(skia.Paint.kStroke_Style)
    grid.setStrokeWidth(2)
    horizon = y + height * 0.79
    for n in range(1, 7):
        xx = x + width * n / 7
        canvas.drawLine(xx, horizon, x + width * (0.5 + (n / 7 - 0.5) * 1.8), y + height, grid)
    canvas.drawLine(x, horizon, x + width, horizon, grid)

    # Deterministic floating dots: gentle movement, no random flicker between frames.
    seed_value = zlib.crc32(str(seed).encode("utf-8"))
    dot = skia.Paint(AntiAlias=True, Color=_color(skia, accent))
    dot.setAlphaf(0.18)
    for n in range(12):
        phase = (seed_value % 997) * 0.001 + n * 1.71
        px = x + width * (0.06 + ((n * 37) % 89) / 100)
        py = y + height * (0.08 + ((n * 23) % 66) / 100) + math.sin(t * 0.65 + phase) * 5
        radius = 5 + (n % 3) * 2
        canvas.drawCircle(px, py, radius, dot)
    canvas.restore()
