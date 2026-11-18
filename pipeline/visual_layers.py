"""Topic-aware, deterministic 2D/2.5D environments for CurioKids."""
import math
import zlib

PALETTES = {
    "ocean": ("#E9F7FF", "#C8E8FF", "#2D75A5"),
    "sunrise": ("#FFF2D8", "#FFD9C7", "#A85D43"),
    "garden": ("#DDF6FF", "#B8E8D1", "#397A55"),
    "space": ("#EDEBFF", "#D6D3FF", "#5547A5"),
    "candy": ("#FFF0F5", "#FAD7E6", "#A64D79"),
    "paper": ("#FFF9E9", "#F5EBD2", "#7B694B"),
}
STYLES = set(PALETTES) | {"none"}


def resolve_style(episode_visual=None, environment=None):
    if environment:
        style = environment
    elif isinstance(episode_visual, dict):
        style = episode_visual.get("style", "none")
    elif isinstance(episode_visual, str):
        style = episode_visual
    else:
        style = "none"
    return style if style in STYLES else "none"


def _color(skia, value, alpha=255):
    value = value.lstrip("#")
    return skia.ColorSetARGB(alpha, int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))


def _paint(skia, color, alpha=255, stroke=0):
    p = skia.Paint(AntiAlias=True, Color=_color(skia, color, alpha))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeCap(skia.Paint.kRound_Cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    return p


def _path(skia, points, close=False):
    p = skia.Path()
    p.moveTo(*points[0])
    for point in points[1:]:
        p.lineTo(*point)
    if close:
        p.close()
    return p


def _cloud(c, skia, x, y, scale=1.0):
    c.save()
    c.translate(x, y)
    c.scale(scale, scale)
    c.drawOval(skia.Rect.MakeLTRB(-48, -5, 48, 24), _paint(skia, "#FFFFFF", 225))
    for cx, cy, r in [(-25, -8, 22), (0, -22, 29), (27, -7, 23)]:
        c.drawCircle(cx, cy, r, _paint(skia, "#FFFFFF", 238))
        c.drawCircle(cx - 7, cy - 8, r * .28, _paint(skia, "#FFFFFF", 115))
    c.restore()


def _tree(c, skia, x, ground, scale, t):
    c.save()
    c.translate(x, ground)
    c.scale(scale, scale)
    sway = math.sin(t * .8 + x) * 2.2
    c.drawOval(skia.Rect.MakeLTRB(-43, -8, 48, 8), _paint(skia, "#496B53", 45))
    trunk = _path(skia, [(-8, 0), (-5, -86), (1+sway, -145), (13+sway, -142), (8, -82), (13, 0)], True)
    c.drawPath(trunk, _paint(skia, "#98603C"))
    c.drawPath(_path(skia, [(-1, -10), (2, -83), (8, -135)]), _paint(skia, "#C98A55", 180, 5))
    for ox, oy, r, col in [(-28,-151,39,"#2E8055"),(10,-177,46,"#3D9A60"),(42,-145,35,"#2E8055"),(-4,-125,38,"#64B96B")]:
        c.drawCircle(ox+sway, oy, r, _paint(skia, col))
        c.drawCircle(ox-9+sway, oy-11, r*.48, _paint(skia, "#B7E58A", 95))
    c.restore()


def _garden(c, skia, x, y, w, h, t, seed):
    clip = skia.Rect.MakeXYWH(x, y, w, h)
    sky = skia.Paint(AntiAlias=True)
    sky.setShader(skia.GradientShader.MakeLinear(
        [skia.Point(x,y), skia.Point(x,y+h*.78)],
        [_color(skia,"#BDEEFF"),_color(skia,"#F2FCE5")],[0.,1.],skia.TileMode.kClamp))
    c.drawRect(clip, sky)

    sx, sy = x+w*.82, y+h*.20
    glow = skia.Paint(AntiAlias=True)
    glow.setShader(skia.GradientShader.MakeRadial(
        skia.Point(sx,sy),h*.19,[_color(skia,"#FFF6B8",170),_color(skia,"#FFF6B8",0)],
        [0.,1.],skia.TileMode.kClamp))
    c.drawCircle(sx,sy,h*.19,glow)
    for n in range(12):
        a=n*math.tau/12+t*.025
        c.drawLine(sx+math.cos(a)*h*.105,sy+math.sin(a)*h*.105,
                   sx+math.cos(a)*h*.132,sy+math.sin(a)*h*.132,
                   _paint(skia,"#F5B83D",150,3))
    c.drawCircle(sx,sy,h*.075,_paint(skia,"#FFD45B"))
    c.drawCircle(sx-h*.022,sy-h*.025,h*.022,_paint(skia,"#FFF3B0",190))

    drift=math.sin(t*.22)*13
    _cloud(c,skia,x+w*.22+drift,y+h*.20,.68)
    _cloud(c,skia,x+w*.57-drift*.6,y+h*.34,.48)

    far=_path(skia,[(x,y+h*.62),(x+w*.16,y+h*.49),(x+w*.34,y+h*.57),
        (x+w*.54,y+h*.45),(x+w*.75,y+h*.55),(x+w,y+h*.43),(x+w,y+h*.82),(x,y+h*.82)],True)
    c.drawPath(far,_paint(skia,"#9AD99C"))
    near=_path(skia,[(x,y+h*.70),(x+w*.18,y+h*.62),(x+w*.38,y+h*.69),
        (x+w*.62,y+h*.58),(x+w*.82,y+h*.68),(x+w,y+h*.60),(x+w,y+h*.84),(x,y+h*.84)],True)
    c.drawPath(near,_paint(skia,"#69BF79"))
    c.drawPath(_path(skia,[(x,y+h*.70),(x+w*.18,y+h*.62),(x+w*.38,y+h*.69),
        (x+w*.62,y+h*.58),(x+w*.82,y+h*.68),(x+w,y+h*.60)]),_paint(skia,"#B6E88A",210,5))
    _tree(c,skia,x+w*.075,y+h*.77,.48,t)
    _tree(c,skia,x+w*.93,y+h*.77,.58,t)

    soil_top=y+h*.79
    soil_p=skia.Paint(AntiAlias=True)
    soil_p.setShader(skia.GradientShader.MakeLinear(
        [skia.Point(x,soil_top),skia.Point(x,y+h)],
        [_color(skia,"#A96F45"),_color(skia,"#68412F")],[0.,1.],skia.TileMode.kClamp))
    c.drawRect(skia.Rect.MakeLTRB(x,soil_top,x+w,y+h),soil_p)
    c.drawRect(skia.Rect.MakeLTRB(x,soil_top,x+w,soil_top+h*.055),_paint(skia,"#6EBD62"))
    c.drawLine(x,soil_top,x+w,soil_top,_paint(skia,"#D4F28E",230,5))
    c.drawPath(_path(skia,[(x,soil_top+h*.12),(x+w*.24,soil_top+h*.16),
        (x+w*.48,soil_top+h*.11),(x+w*.76,soil_top+h*.17),(x+w,soil_top+h*.12)]),
        _paint(skia,"#D99A61",150,3))
    c.drawPath(_path(skia,[(x,soil_top+h*.28),(x+w*.3,soil_top+h*.24),
        (x+w*.64,soil_top+h*.30),(x+w,soil_top+h*.25)]),_paint(skia,"#4F342B",120,3))

    # Fine roots, grass, pebbles and flowers make the foreground read as a diorama.
    for side in (-1,1):
        rx=x+w*(.20 if side<0 else .80)
        c.drawPath(_path(skia,[(rx,soil_top+2),(rx+side*9,soil_top+h*.08),
            (rx+side*22,soil_top+h*.17),(rx+side*18,soil_top+h*.28)]),
            _paint(skia,"#F1C18A",220,4))
        for branch in (-1,1):
            c.drawPath(_path(skia,[(rx+side*12,soil_top+h*.15),
                (rx+side*28,soil_top+h*.20),(rx+side*35+branch*8,soil_top+h*.27)]),
                _paint(skia,"#E7B47D",185,2.5))
    for n in range(13):
        gx=x+w*((n*17+6)%97)/100
        sway=math.sin(t*1.5+n)*4
        c.drawPath(_path(skia,[(gx,soil_top+2),(gx-5+sway,soil_top-15-(n%3)*3),
            (gx+1,soil_top-7),(gx+7+sway,soil_top-19-(n%2)*4)]),
            _paint(skia,"#2D8E4F",230,3))
    for n in range(8):
        rx=x+w*((n*29+11)%93)/100
        ry=soil_top+h*(.12+(n%3)*.045)
        c.drawOval(skia.Rect.MakeLTRB(rx-7,ry-3,rx+8,ry+4),_paint(skia,"#D7B18A",170))


def draw_backdrop(canvas, skia, bounds, t, style="none", seed="curiokids"):
    """Draw a topic environment behind existing board elements."""
    if style not in PALETTES:
        return
    x,y,w,h=bounds
    canvas.save()
    canvas.clipRect(skia.Rect.MakeXYWH(x,y,w,h),doAntiAlias=True)
    if style=="garden":
        _garden(canvas,skia,x,y,w,h,t,seed)
    else:
        top,bottom,accent=PALETTES[style]
        shader=skia.GradientShader.MakeLinear([skia.Point(x,y),skia.Point(x+w,y+h)],
            [_color(skia,top),_color(skia,bottom)],[0.,1.],skia.TileMode.kClamp)
        p=skia.Paint(AntiAlias=True); p.setShader(shader); canvas.drawRect(skia.Rect.MakeXYWH(x,y,w,h),p)
        translucent=skia.Paint(AntiAlias=True,Color=_color(skia,"#FFFFFF",34))
        canvas.drawCircle(x+w*.12,y+h*.18,h*.23,translucent)
        canvas.drawCircle(x+w*.91,y+h*.82,h*.30,translucent)
    seed_value=zlib.crc32(str(seed).encode("utf-8"))
    dot=_paint(skia,PALETTES[style][2],38)
    for n in range(8):
        phase=(seed_value%997)*.001+n*1.71
        px=x+w*(.06+((n*37)%89)/100)
        py=y+h*(.08+((n*23)%55)/100)+math.sin(t*.65+phase)*4
        canvas.drawCircle(px,py,3+(n%3),dot)
    canvas.restore()
