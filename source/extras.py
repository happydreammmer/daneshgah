"""Digits, punctuation and combining marks for Daneshgah."""
import math
from shapely.geometry import Point
from design import R, P, ring, Glyph, hamza, shift, mirror, mark_t, N, T, B, disk

AXIS = 250          # centre line of the hyphen, dashes and math signs


def _g(sp, shapes, ink_w, sb=None):
    sb = sp.SB + 40 if sb is None else sb
    return Glyph(shift(shapes, sb), ink_w + 2 * sb, sb + ink_w / 2)


def slant(x0, y0, x1, y1, w):
    """Stroke from (x0, y0) at the bottom to (x1, y1) at the top, horizontal width w."""
    return P((x0, y0), (x0 + w, y0), (x1 + w, y1), (x1, y1))


def V(sp, W, H, invert=False):
    """۷ / ۸: two slanted strokes meeting in a flat point."""
    S = sp.S
    ang = math.atan2(W / 2, H)
    w = S / math.cos(ang)                  # horizontal width of a stroke of weight S
    c = W / 2
    fb = w / 2
    if not invert:   # ۷: point at the bottom
        return [P((0, H), (w, H), (c + fb, 0), (c - fb, 0)), P((W - w, H), (W, H), (c + fb, 0), (c - fb, 0))]
    return [P((0, 0), (w, 0), (c + fb, H), (c - fb, H)), P((W - w, 0), (W, 0), (c + fb, H), (c - fb, H))]


DW = 440            # common ink width of the Persian digits (tabular advance)


def five(sp):
    """۵: the emblem's ن semicircle turned over as the roof (the ۵ is pointed / round at the
    top), on straight walls and a square foot, the full digit height."""
    S = sp.S
    W, H = DW, N
    Rr = W / 2
    cy = H - Rr
    arch = disk(Rr, cy, Rr).difference(disk(Rr, cy, Rr - S)).intersection(R(0, cy, W, H))
    return [arch, R(0, 0, S, cy + 1), R(W - S, 0, W, cy + 1), R(0, 0, W, S)]


def six(sp):
    """۶: the hook at the top left (the arm's left end turns down) over a straight stem on the
    right: the Arabic ٦ with the Persian hook."""
    S = sp.S
    W, H = DW, N
    lip = 130
    return [R(0, H - S, W, H), R(0, H - S - lip, S, H), R(W - S, 0, W, H)]


def fa_digit(sp, n):
    """Persian digits, built from the same strokes as the letters: full digit height N, square
    ends; the ۵ is roofed with the ن curve."""
    S = sp.S
    if n == 0:
        d = round(sp.DOT * 1.3)
        c = 230                         # same centre in every weight
        sh = [R(0, c - d / 2, d, c + d / 2)]
        return _g(sp, shift(sh, (DW - d) / 2), DW)
    if n == 1:
        return _g(sp, [R((DW - S) / 2, 0, (DW + S) / 2, N)], DW)
    # ۲ ۳: a stem on the left, teeth rising from an arm at the top
    arm = N - 210                      # top of the arm; the teeth rise 210 above it
    if n == 2:
        x0 = 60
        return _g(sp, [R(x0, 0, x0 + S, arm), R(x0, arm - S, DW, arm), R(DW - S, arm - S, DW, N)], DW)
    if n == 3:
        x0 = 20
        mid = (x0 + DW - S) / 2 + 25
        return _g(sp, [R(x0, 0, x0 + S, arm), R(x0, arm - S, DW, arm),
                       R(mid, arm - S, mid + S, N - 60), R(DW - S, arm - S, DW, N)], DW)
    if n == 4:
        # ۴: stem on the left; a ⊏ on its right whose lower arm runs back into the stem
        x0 = 30
        sx = x0 + S + 110
        lo = N - 330
        return _g(sp, [R(x0, 0, x0 + S, N), R(sx, N - S, DW, N), R(sx, lo, sx + S, N), R(x0, lo, DW, lo + S)], DW)
    if n == 5:
        return _g(sp, five(sp), DW)
    if n == 6:
        return _g(sp, six(sp), DW)
    if n == 7:
        return _g(sp, V(sp, DW, N), DW)
    if n == 8:
        return _g(sp, V(sp, DW, N, True), DW)
    if n == 9:
        H = 320
        return _g(sp, ring(0, N - H, DW, H, S) + [R(DW - S, 0, DW, N)], DW)


def ar_digit(sp, n):
    """Arabic-Indic forms that differ from the Persian ones: ٤ ٥ ٦."""
    S = sp.S
    if n == 4:
        sh = [R(0, N - S, DW, N), R(0, (N - S) / 2 + 20, S, N), R(0, (N - S) / 2 + 20, DW - 60, (N + S) / 2 + 20),
              R(0, 0, S, (N - S) / 2 + 20), R(0, 0, DW, S)]
        return _g(sp, sh, DW)
    if n == 5:
        # ٥: a plain ring, the full digit height (narrower than Latin 0)
        return _g(sp, ring(60, 0, DW - 120, N, S), DW)
    if n == 6:
        return _g(sp, [R(0, N - S, DW, N), R(DW - S, 0, DW, N)], DW)


SEG = {0: "abcdef", 2: "abged", 3: "abgcd", 5: "afgcd", 6: "afgedc", 8: "abcdefg", 9: "abcdfg"}


def la_digit(sp, n):
    """Latin digits built as square segments, same height and width as the Persian ones."""
    S = sp.S
    W = DW
    m = N / 2
    seg = {"a": R(0, N - S, W, N), "b": R(W - S, m, W, N), "c": R(W - S, 0, W, m),
           "d": R(0, 0, W, S), "e": R(0, 0, S, m), "f": R(0, m, S, N), "g": R(0, m - S / 2, W, m + S / 2)}
    if n == 1:
        return _g(sp, [R((W + S) / 2 - S + 60, 0, (W + S) / 2 + 60, N), R((W + S) / 2 - 140 + 60, N - S, (W + S) / 2 + 60, N)], W)
    if n == 4:
        return _g(sp, [R(0, m - S / 2, S, N), R(0, m - S / 2, W, m + S / 2), R(W - S, 0, W, N)], W)
    if n == 7:
        return _g(sp, [seg["a"], R(W - S, 0, W, N)], W)
    return _g(sp, [seg[k] for k in SEG[n]], W)


# ------------------------------------------------------------------ punctuation
def chevron(x, y0, w, h, t, left):
    k = t / math.cos(math.atan2(h / 2, w))
    n = 2 * w * k / h
    yc = y0 + h / 2
    if left:
        return [P((x, yc), (x + w, y0 + h), (x + w, y0 + h - k), (x + n, yc), (x + w, y0 + k), (x + w, y0))]
    return [P((x + w, yc), (x, y0 + h), (x, y0 + h - k), (x + w - n, yc), (x, y0 + k), (x, y0))]


def punct(sp):
    S, t = sp.S, sp.t
    d = sp.DOT
    out = {}
    up = T                       # upper dot of : ; ؛ sits on the teeth line
    out["period"] = _g(sp, [R(0, 0, d, d)], d)
    out["colon"] = _g(sp, [R(0, 0, d, d), R(0, up - d, d, up)], d)
    out["comma"] = _g(sp, [R(0, 0, d, d), R(d - t, -150, d, d)], d)
    out["semicolon"] = _g(sp, [R(0, up - d, d, up), R(0, 0, d, d), R(d - t, -150, d, d)], d)
    # Persian comma / semicolon: the tail rises from the dot, turned the other way
    out["uni060C"] = _g(sp, [R(0, 0, d, d), R(0, 0, t, d + 150)], d)
    out["uni061B"] = _g(sp, [R(0, 0, d, d), R(0, 0, t, d + 150), R(0, d + 150 + sp.DG + 20, d, 2 * d + 150 + sp.DG + 20)], d)
    out["exclam"] = _g(sp, [R(0, 0, d, d), R((d - S) / 2, d + sp.DG + 40, (d + S) / 2, N)], d)
    W = 2 * S + 170
    q = [R(0, N - S, W, N), R(W - S, N - 2.6 * S - 20, W, N), R((W - S) / 2, N - 2.6 * S - 20, W, N - 1.6 * S - 20),
         R((W - S) / 2, d + sp.DG + 40, (W + S) / 2, N - 1.6 * S - 20), R((W - d) / 2, 0, (W + d) / 2, d)]
    out["question"] = _g(sp, q, W)
    out["uni061F"] = _g(sp, mirror(q, W / 2), W)
    out["hyphen"] = _g(sp, [R(0, AXIS - S / 2, 260, AXIS + S / 2)], 260, 50)
    out["endash"] = _g(sp, [R(0, AXIS - S / 2, 480, AXIS + S / 2)], 480, 50)
    out["emdash"] = _g(sp, [R(0, AXIS - S / 2, 920, AXIS + S / 2)], 920, 40)
    out["underscore"] = _g(sp, [R(0, -160, 520, -160 + S)], 520, 0)
    out["slash"] = _g(sp, [slant(0, -110, 360 - 1.25 * S, N + 60, 1.25 * S)], 360, 30)
    out["backslash"] = _g(sp, [slant(360 - 1.25 * S, -110, 0, N + 60, 1.25 * S)], 360, 30)
    yb, yt = -170, N + 80
    pw = 200
    out["parenleft"] = _g(sp, [R(0, yb, S, yt), R(0, yt - S, pw, yt), R(0, yb, pw, yb + S),
                               R(pw - S, yt - S - 60, pw, yt), R(pw - S, yb, pw, yb + S + 60)], pw, 60)
    out["parenright"] = Glyph(mirror(out["parenleft"].shapes, out["parenleft"].adv / 2), out["parenleft"].adv)
    bw = 200
    out["bracketleft"] = _g(sp, [R(0, yb, S, yt), R(0, yb, bw, yb + S), R(0, yt - S, bw, yt)], bw, 70)
    out["bracketright"] = _g(sp, [R(bw - S, yb, bw, yt), R(0, yb, bw, yb + S), R(0, yt - S, bw, yt)], bw, 70)
    out["plus"] = _g(sp, [R(0, AXIS - S / 2, 440, AXIS + S / 2), R(220 - S / 2, 30, 220 + S / 2, 470)], 440)
    out["equal"] = _g(sp, [R(0, 130, 440, 130 + S), R(0, 370 - S, 440, 370)], 440)
    out["less"] = _g(sp, chevron(0, AXIS - 200, 380, 400, 0.85 * S, True), 380)
    out["greater"] = _g(sp, chevron(0, AXIS - 200, 380, 400, 0.85 * S, False), 380)

    def chev(x, left):
        return chevron(x, 40, 220, 370, 0.8 * S, left)
    out["guillemotleft"] = _g(sp, chev(0, True) + chev(240, True), 460, 50)
    out["guillemotright"] = _g(sp, chev(0, False) + chev(240, False), 460, 50)
    out["quotesingle"] = _g(sp, [R(0, N - 250, S, N)], S, 70)
    out["quotedbl"] = _g(sp, [R(0, N - 250, S, N), R(S + 90, N - 250, 2 * S + 90, N)], 2 * S + 90, 70)
    g = sp.DG + 55
    out["ellipsis"] = _g(sp, [R(0, 0, d, d), R(d + g, 0, 2 * d + g, d), R(2 * d + 2 * g, 0, 3 * d + 2 * g, d)], 3 * d + 2 * g)
    pr = [R(0, N - d, d, N), R(380 - d, 0, 380, d), slant(0, 0, 380 - 1.25 * S, N, 1.25 * S)]
    out["percent"] = _g(sp, pr, 380)
    out["uni066A"] = out["percent"]
    out["uni066B"] = _g(sp, [slant(0, -130, 0.75 * S, 120, 0.95 * S)], S * 1.7, 70)
    out["uni066C"] = _g(sp, [slant(0, 290, 0.75 * S, 540, 0.95 * S)], S * 1.7, 70)
    c, r, w = 205, 205, S * 0.45
    star = []
    for k in range(4):
        a = math.pi * k / 4
        dx, dy = math.cos(a), math.sin(a)
        px, py = -dy * w / 2, dx * w / 2
        star.append(P((c - r * dx + px, 300 - r * dy + py), (c + r * dx + px, 300 + r * dy + py),
                      (c + r * dx - px, 300 + r * dy - py), (c - r * dx - px, 300 - r * dy - py)))
    out["asterisk"] = _g(sp, star, 2 * c, 50)
    return out


# ------------------------------------------------------------------ combining marks (zero width, anchor at 0,0)
def marks(sp):
    t = mark_t(sp)
    m = {}

    def fat(y):
        return P((-95, y), (95, y + 55), (95, y + 55 + t), (-95, y + t))
    m["uni064E"] = ([fat(0)], "top")
    m["uni0650"] = ([fat(-55 - t)], "bot")
    m["uni064B"] = ([fat(0), fat(t + 50)], "top")
    m["uni064D"] = ([fat(-55 - t), fat(-55 - 2 * t - 50)], "bot")
    L = max(120, 2 * t + 40)

    def damma(x):
        x0 = x - L / 2
        yb = 55
        return ring(x0, yb, L, L, t) + [R(x0, 0, x0 + t, yb + t), R(x0 - 55, 0, x0 + t, t)]
    m["uni064F"] = (damma(10), "top")
    m["uni064C"] = (damma(-L / 2 - 25) + damma(L / 2 + 50), "top")
    m["uni0652"] = (ring(-L / 2, 0, L, L, t), "top")
    g = max(50, round(t * 0.9))
    sw = 3 * t + 2 * g
    m["uni0651"] = ([R(-sw / 2, 0, sw / 2, t)] + [R(-sw / 2 + k * (t + g), 0, -sw / 2 + k * (t + g) + t, 115) for k in range(3)], "top")
    m["uni0670"] = ([R(-t / 2, 0, t / 2, 160)], "top")
    m["uni0654"] = (hamza(sp, 0, 0, 0.85), "top")
    m["uni0655"] = (shift(hamza(sp, 0, 0, 0.85), 0, -170), "bot")
    return m
