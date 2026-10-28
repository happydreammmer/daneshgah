"""
Daneshgah (دانشگاه) — glyph design.

Rebuilt from pixel measurements of the «دانشگاه تهران» emblem lettering. In the emblem the
stroke is 9 px; at 1 stroke = 100 units the measured lines are:

    alef 655 · kaf arm (top) 533 · dal / ن tooth 411 · box (ه, ک) 322 · teeth (ش ت) 267-278
    tooth pitch 155 (100 tooth + 55 gap) · dots = stroke, 45 apart and 45 from the body
    ر: straight drop under the line, then a thin kick to the left (half a stroke); the font
       takes the drop down to the bowl line of ن, so ر ز ژ و end level with the bowls
    ن (final): a semicircle with the dot sitting in its mouth, level with the rim
    initial teeth sit flush with the end of the baseline (nothing sticks out past them)

Bold is the emblem's weight (stroke 100). Regular and Light thin the strokes inwards from the
same outer lines, so every weight shares one set of heights:

     650  A   alef, lam, tah stems                       (emblem 655)
              ک arm top = top of the گ dash, so ک and گ are the same height
              (gaf_top: Bold 650 · Regular 622 · Light 584)
     K        گ arm top = top of the dot over an initial tooth
              (Bold 565 · Regular 539 · Light 513; emblem 533-538)
     D        dal, initial teeth (ن ب ت ی …), top of the ش dots, ع loop
              (Bold 420 · Regular 407 · Light 394; emblem 411-416)
     320  B   boxes: ه (isolated / final) م ف ق, square kaf, ص ط loop, ح head   (emblem 322)
     275  T   medial teeth, س ش teeth, upturned tips, top of initial / medial ه   (emblem 267-278)
       0      baseline (the joining bar is 0 … S)
              S − T: lower storey of initial / medial ه (mirrors the upper one: −175 / −195 / −215)
    −320  DD  bowls: ن ق ص ض س ش (round), ی ل (square), tail of م, foot of ر ز ژ و
    −440  DJ  bowls of ج ح خ چ ع غ (deep and wide enough to hold the three dots of چ)

The emblem's square kaf (box + stem + arm) is kept only before ا and ل (کا گا کل گل), where the
box's left wall is the alef / lam; elsewhere the kaf is a stem with the arm reaching right.

Coordinates: each letter's *body* is drawn with x = 0 at its left end. Joining forms get the
run (the bar to the next letter) added on the left, and the body's right edge is where the
previous letter joins. Free sides get side bearings measured from the ink.
"""
import math
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
from shapely.affinity import translate, scale as sscale

A, B, T = 650, 320, 275
DD, DJ = -320, -440
N = 550                     # digit height
FORMS = ("isol", "init", "medi", "fina")


class Spec:
    def __init__(self, S):
        self.S = S                          # stroke (vertical and horizontal are equal: monoline)
        self.DOT = round(0.5 * S + 50)      # square dot: 100 / 90 / 80
        self.DG = round(0.15 * S + 30)      # gap between dots: 45 / 42 / 39
        self.DA = self.DG                   # body -> dots (the emblem uses the same gap)
        self.t = round(0.45 * S + 5)        # thin stroke (kick of ر, gaf dash, marks): 50 / 41 / 32
        self.SB = round(30 + 0.75 * (100 - S))      # side bearing: 30 / 45 / 60
        self.J = round(110 + 1.25 * (100 - S))      # joining run between letters: 110 / 135 / 160
        # the emblem's dot grid: dots of ش sit on the teeth and their top is the dal line; the
        # dot of ن sits on its tooth (dal line) and its top is the kaf line
        self.D = T + self.DA + self.DOT     # dal, initial teeth: 420 / 407 / 394
        self.K = self.D + self.DA + self.DOT    # kaf arm top: 565 / 539 / 513
        self.OV = 12                        # joins reach this far into the neighbour (no seams)
        self.N = N


# ------------------------------------------------------------------ primitives
def R(x0, y0, x1, y1):
    return box(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))


def P(*pts):
    return Polygon(pts)


def shift(shapes, dx=0, dy=0):
    return [translate(s, dx, dy) for s in shapes]


def mirror(shapes, cx):
    return [sscale(s, -1, 1, origin=(cx, 0)) for s in shapes]


def ring(x, y, w, h, s):
    return [R(x, y, x + w, y + s), R(x, y + h - s, x + w, y + h), R(x, y, x + s, y + h), R(x + w - s, y, x + w, y + h)]


def disk(cx, cy, r):
    return Point(cx, cy).buffer(r, resolution=64)


def half_ring(cx, R_, s, top):
    """Lower half of a ring centred on (cx, 0), plus straight arms from 0 up to `top`."""
    ann = disk(cx, 0, R_).difference(disk(cx, 0, R_ - s)).intersection(R(cx - R_ - 1, -R_ - 1, cx + R_ + 1, 0))
    return [ann, R(cx - R_, 0, cx - R_ + s, top), R(cx + R_ - s, 0, cx + R_, top)]


def dots(sp, n, cx, y, above=True, row=False):
    """n square dots centred on cx. above: y = bottom of the lowest row; below: y = top of the
    highest row. Three dots: a pyramid (∴ above, ∵ below) or a row."""
    d, g = sp.DOT, sp.DG
    out = []

    def sq(x, yy):
        out.append(R(x - d / 2, yy, x + d / 2, yy + d))
    o = (d + g) / 2
    y1 = y if above else y - d
    if n == 1:
        sq(cx, y1)
    elif n == 2:
        sq(cx - o, y1); sq(cx + o, y1)
    elif n == 3 and row:
        sq(cx - 2 * o, y1); sq(cx, y1); sq(cx + 2 * o, y1)
    elif n == 3:
        sq(cx - o, y1); sq(cx + o, y1)
        sq(cx, y1 + d + g if above else y1 - d - g)
    return out


def dots_w(sp, n):
    return sp.DOT if n == 1 else 2 * sp.DOT + sp.DG


def dots_h(sp, n):
    return sp.DOT if n < 3 else 2 * sp.DOT + sp.DG


# ------------------------------------------------------------------ small marks (hamza, madda)
def mark_t(sp, k=1.0):
    return max(28, round(sp.t * k))


def hamza(sp, x, y, k=1.0):
    """Square hamza: a 'c' open to the right standing on a short tail that turns left.
    (x, y) = bottom centre. Returns shapes."""
    t = mark_t(sp, k)
    L = max(round(120 * k), 2 * t + round(40 * k))       # loop size, counter always open
    tail, foot = round(55 * k), round(55 * k)
    x0 = x - (L - foot) / 2
    yb = y + tail
    return [R(x0, y, x0 + t, yb + t), R(x0 - foot, y, x0 + t, y + t),     # tail + foot
            R(x0, yb + L - t, x0 + L, yb + L),                            # top arm
            R(x0, yb, x0 + t, yb + L),                                    # spine
            R(x0, yb, x0 + round(L * 0.85), yb + t)]                      # bottom arm


def hamza_h(sp, k=1.0):
    t = mark_t(sp, k)
    return round(55 * k) + max(round(120 * k), 2 * t + round(40 * k))


def madda(sp, cx, y):
    t = mark_t(sp)
    return [R(cx - 120, y, cx - 40, y + t),
            P((cx - 40, y), (cx + 40, y + 55), (cx + 40, y + 55 + t), (cx - 40, y + t)),
            R(cx + 40, y + 55, cx + 120, y + 55 + t)]


# ------------------------------------------------------------------ glyph + assembly
class Glyph:
    def __init__(self, shapes, adv, cx=None):
        self.shapes = shapes
        self.adv = adv
        self.cx = adv / 2 if cx is None else cx


def bounds(shapes):
    u = unary_union(shapes)
    return u.bounds


def assemble(sp, shapes, bw, form, cx=None, sbl=None, sbr=None, run=None):
    """Body x 0..bw. Joining left (init, medi): a run of length J leads to the next letter.
    Joining right (medi, fina): the body's right edge is the glyph's right edge.
    Free sides: side bearing measured from the ink."""
    S = sp.S
    jl = form in ("init", "medi")
    jr = form in ("medi", "fina")
    sbl = sp.SB if sbl is None else sbl
    sbr = sp.SB if sbr is None else sbr
    b = bounds(shapes) if shapes else (0, 0, bw, 0)
    if jl:
        xo = sp.J if run is None else run
        out = shift(shapes, xo) + [R(-sp.OV, 0, xo + S, S)]
    else:
        xo = sbl - b[0]
        out = shift(shapes, xo)
    if jr:
        adv = xo + bw
        out.append(R(adv - S, 0, adv + sp.OV, S))
    else:
        adv = xo + max(b[2], bw) + sbr
    return Glyph(out, adv, xo + (bw / 2 if cx is None else cx))


# ------------------------------------------------------------------ shared parts
UP_TAIL = 300          # flat final tail: from the upturned tip to the start of the body


def tail(sp, x1):
    """Flat Kufic tail: baseline from 0 to x1 with the tip turned up at the left end."""
    S = sp.S
    return [R(0, 0, x1, S), R(0, 0, S, T)]


def sq_bowl(sp, w, depth, tip_top, tip_left=True):
    """Square bowl hanging under the baseline, x 0..w. The side opposite the tip drops from
    the baseline; the tip rises to tip_top."""
    S = sp.S
    sh = [R(0, depth, w, depth + S)]
    if tip_left:
        sh += [R(0, depth, S, tip_top), R(w - S, depth, w, S)]
    else:
        sh += [R(w - S, depth, w, tip_top), R(0, depth, S, S)]
    return sh


# ------------------------------------------------------------------ BEH / NOON / YEH
BEH_W = 520            # final / isolated beh: tip to tip


def beh_like(sp, form, nd=0, above=True, kind="beh"):
    S = sp.S
    if form in ("init", "medi"):
        # initial teeth stand tall on the dal line (the emblem's ن in «دانشگاه»), medial teeth
        # are short (the teeth line), for every letter of the family
        h = sp.D if form == "init" else T
        sh = [R(0, 0, S, h)]
        cx = S / 2
        if nd:
            sh += dots(sp, nd, cx, h + sp.DA, True) if above else dots(sp, nd, cx, -sp.DA, False)
        if kind == "hamza":
            sh += hamza(sp, cx + 10, h + sp.DA, 0.85)
        return assemble(sp, sh, S, form, cx)
    if kind == "noon":
        return noon_final(sp, form)
    if kind in ("yeh", "hamza"):
        return yeh_final(sp, form, nd, kind)
    # final and isolated alike: a flat tail between two upturned tips (in the final the join
    # comes in at the foot of the right tip); dots above ride on the tips' line, as on the teeth
    bw = BEH_W
    sh = tail(sp, bw) + [R(bw - S, 0, bw, T)]
    cx = bw / 2
    if nd:
        sh += dots(sp, nd, cx, T + sp.DA, True) if above else dots(sp, nd, cx, -sp.DA, False)
    return assemble(sp, sh, bw, form, cx)


NOON_R = 320


def noon_final(sp, form, nd=1):
    """The emblem's ن: a semicircle hanging from the baseline, its rim level with the top of the
    joining bar, so a join meets the right arm flush. The dot sits in the mouth, level with the rim."""
    S = sp.S
    Rn = NOON_R
    sh = half_ring(Rn, Rn, S, S)
    if nd:
        sh.append(R(Rn - sp.DOT / 2, S - sp.DOT, Rn + sp.DOT / 2, S))
    return assemble(sp, sh, 2 * Rn, form, Rn)


YEH_W = 520


def yeh_final(sp, form, nd, kind):
    """Final ی: the join drops on the right into a square bowl, whose tip rises on the left to
    the rim line. Isolated: a hooked head (⊏) rides on the right end."""
    S = sp.S
    bw = YEH_W
    sh = sq_bowl(sp, bw, DD, S, tip_left=True)
    top = S
    if form == "isol":
        hw = 220
        hx = bw - hw
        sh += [R(hx, 0, bw, S), R(hx, 0, hx + S, T), R(hx, T - S, bw, T)]
        top = T
    if nd:          # Arabic ي: two dots inside the bowl
        sh += dots(sp, nd, bw / 2, (DD + S) / 2 - sp.DOT / 2, True)
    if kind == "hamza":
        hx_ = bw - 115 if form == "isol" else bw / 2
        sh += hamza(sp, hx_, top + sp.DA, 0.85)
    return assemble(sp, sh, bw, form, bw / 2)


# ------------------------------------------------------------------ HAH family
HAH_W = 420
HAH_LIP = 80          # the lip hangs this far below the head's top bar (into the mouth)


def hah_head(sp, W):
    """Head of ح: top bar on the box line, spine on the right, a short lip at the left end."""
    S = sp.S
    return [R(0, B - S, W, B), R(W - S, 0, W, B), R(0, B - S - HAH_LIP, S, B)]


HAH_TIP = 100          # the bowl's tip rises this far above the bowl floor
HAH_BW = 480           # final / isolated bowl: wider than the head, so the three dots of چ fit


def hah_bowl(sp, W):
    """Deep bowl of ج ح ع (final / isolated): left spine from the waist down, floor, short tip
    turned up at the right, under the head's spine."""
    S = sp.S
    return [R(0, DJ, S, S), R(0, DJ, W, DJ + S), R(W - S, DJ, W, DJ + S + HAH_TIP)]


def bowl_dots(sp, nd, W):
    """Dots inside the deep bowl: ج's dot in the middle of the counter; the three of چ hung one
    dot-gap under the waist and one dot-gap clear of the left spine, clear of the tip."""
    S = sp.S
    if nd == 1:
        return dots(sp, 1, W / 2, (DJ + S) / 2 - sp.DOT / 2, True)
    return dots(sp, 3, S + sp.DG + dots_w(sp, 3) / 2, -sp.DG, False)


def hah_like(sp, form, nd=0, where="below"):
    S = sp.S
    W = HAH_W
    if form in ("init", "medi"):
        sh = hah_head(sp, W) + [R(0, 0, W, S)]
        if nd:
            if where == "above":
                sh += dots(sp, nd, W / 2, B + sp.DA, True)
            else:
                sh += dots(sp, nd, W / 2, -sp.DA, False)
        return assemble(sp, sh, W, form, W / 2)
    # final / isolated: the head rides on a waist; the left spine runs down into a deep bowl
    # whose tip turns up at the right, under the head's spine
    BW = HAH_BW
    off = BW - W
    sh = shift(hah_head(sp, W), off) + [R(0, 0, BW, S)] + hah_bowl(sp, BW)
    cx = off + W / 2
    if nd:
        sh += dots(sp, nd, cx, B + sp.DA, True) if where == "above" else bowl_dots(sp, nd, BW)
    return assemble(sp, sh, BW, form, cx)


# ------------------------------------------------------------------ AIN family
# The ductus of ع: initial = a mouth opening to the right on the joining line; medial = a closed
# loop on the line; final = the loop over a bowl; isolated = the open mouth over a bowl (ε).
AIN_W = 340


def ain_open(sp):
    """Open head (initial / isolated): spine on the left, top arm on the box line ending in a
    horn up to the dal line; the line below is the joining bar / waist."""
    S, W = sp.S, AIN_W
    return [R(0, 0, S, B), R(0, B - S, W, B), R(W - S, B - S, W, sp.D)], W, sp.D


def ain_loop(sp):
    """Closed loop (medial / final) with a T-shaped counter (the mouth), as tall as the horn
    of the open head (the dal line). The outside is the counter grown by one stroke on every
    side: wide at the top, stepping in to a narrower neck over the line, so every stroke is
    one stroke wide. The crossbar of the T and the neck share the height left by the three
    strokes (Bold: 60 + 60)."""
    S = sp.S
    W, H = AIN_W, sp.D
    c = W / 2
    ch = round((H - 3 * S) / 2)             # height of the T's crossbar
    sw = round(0.4 * S + 30)                # width of the T's stem: 70 / 62 / 54
    ys = H - S - ch                         # bottom of the crossbar
    nh = sw / 2 + S                         # half width of the neck
    outer = R(0, ys - S, W, H).union(R(c - nh, 0, c + nh, ys - S))
    counter = R(S, ys, W - S, H - S).union(R(c - sw / 2, S, c + sw / 2, ys))
    return [outer.difference(counter)], W, H


def ain_like(sp, form, nd=0):
    S = sp.S
    open_ = form in ("init", "isol")
    head, W, top = ain_open(sp) if open_ else ain_loop(sp)
    x = 0
    if form in ("init", "medi"):
        sh = head + [R(0, 0, W, S)]
        bw = W
    else:
        # final / isolated: the line under the head runs on a step to the left (as in م) before
        # the tail drops into the bowl, whose tip turns up at the right
        x = MEEM_STEP
        bw = x + W
        sh = shift(head, x) + [R(0, 0, bw, S)] + hah_bowl(sp, HAH_BW)
    cx = x + W / 2
    if nd:
        # on the open head the dot sits on the arm, left of the horn; on the loop, above it
        sh += dots(sp, nd, cx - 40, B + sp.DA, True) if open_ else dots(sp, nd, cx, top + sp.DA, True)
    return assemble(sp, sh, bw, form, cx)


# ------------------------------------------------------------------ DAL / REH / WAW
DAL_W, DAL_ARM = 255, 200


def dal(sp, form, nd=0):
    """⊐: a stem on the right with a short head arm and a longer foot, both to the left."""
    S = sp.S
    bw = DAL_W
    D = sp.D
    sh = [R(0, 0, bw, S), R(bw - S, 0, bw, D), R(bw - DAL_ARM, D - S, bw, D)]
    cx = bw - DAL_ARM / 2
    if nd:
        sh += dots(sp, nd, cx, D + sp.DA, True)
    return assemble(sp, sh, bw, form, cx)


REH_KICK = 80


def reh(sp, form, nd=0):
    """ر: an upright from the top of the line straight down under it, ending in a thin kick left.
    No bar of its own to the right: in the final form the previous letter's joining run reaches it."""
    S = sp.S
    k = REH_KICK
    bw = k + S
    sh = [R(k, DD, bw, S), R(0, DD, bw, DD + sp.t)]
    cx = k + S / 2
    if nd:
        sh += dots(sp, nd, cx, S + sp.DA, True)
    return assemble(sp, sh, bw, form, cx)


BOX = 320


def waw(sp, form, hamza_above=False):
    """و: the ه box, its right wall running on down to the foot line and turning left in a
    thin kick under the box (the ر's drop and kick)."""
    S = sp.S
    W = BOX
    k = 60
    bw = k + W
    sh = ring(k, 0, W, B, S) + [R(bw - S, DD, bw, S), R(0, DD, bw, DD + sp.t)]
    if hamza_above:
        sh += hamza(sp, k + W / 2, B + sp.DA, 0.85)
    return assemble(sp, sh, bw, form, k + W / 2)


# ------------------------------------------------------------------ SEEN / SAD / TAH
SEEN_W = 410            # three teeth on the emblem's pitch of 155


def teeth3(sp, x0):
    S = sp.S
    xs = [x0, x0 + (SEEN_W - S) / 2, x0 + SEEN_W - S]
    return [R(x, 0, x + S, T) for x in xs], xs


def seen(sp, form, nd=0):
    S = sp.S
    if form in ("init", "medi"):
        sh, xs = teeth3(sp, 0)
        bw = SEEN_W
        sh.append(R(0, 0, bw, S))
    else:
        # final / isolated, as ص: the first tooth stands on the right arm of the ن bowl, which
        # hangs below the line to the left
        x0 = 2 * NOON_R - S
        sh, xs = teeth3(sp, x0)
        bw = x0 + SEEN_W
        sh.append(R(x0, 0, bw, S))
        sh += half_ring(NOON_R, NOON_R, S, S)
    cx = xs[1] + S / 2
    if nd:
        # as in the emblem: the dots of ش sit on the two right-hand teeth, the third dot above
        # the gap between them
        sh += dots(sp, nd, (xs[1] + S + xs[2]) / 2, T + sp.DA, True)
    return assemble(sp, sh, bw, form, cx)


LOOP_W = 410            # loop of ص ض ط ظ: B tall, as wide as the three teeth of س


def sad(sp, form, nd=0):
    S = sp.S
    # final / isolated: the small tooth stands on the right arm of the ن bowl, which hangs
    # below the line to the left
    x = 0 if form in ("init", "medi") else 2 * NOON_R - S
    sh = [R(x, 0, x + S, T)]                 # the small tooth that follows the loop
    lx = x + 155
    sh += ring(lx, 0, LOOP_W, B, S)
    bw = lx + LOOP_W
    sh.append(R(x, 0, bw, S))
    if x:
        sh += half_ring(NOON_R, NOON_R, S, S)
    cx = lx + LOOP_W / 2
    if nd:
        sh += dots(sp, nd, cx, B + sp.DA, True)
    return assemble(sp, sh, bw, form, cx)


TAH_STEM = 110          # the stem rises from the loop's top, leaving a shoulder on the left


def tah(sp, form, nd=0):
    S = sp.S
    W = LOOP_W
    sh = ring(0, 0, W, B, S) + [R(TAH_STEM, B - S, TAH_STEM + S, A)]
    cx = (TAH_STEM + S + W) / 2
    if nd:
        sh += dots(sp, nd, cx, B + sp.DA, True)
    return assemble(sp, sh, W, form, W / 2)


# ------------------------------------------------------------------ FEH / QAF
def feh_qaf(sp, form, nd=1, qaf=False):
    S = sp.S
    if form in ("init", "medi"):
        sh = ring(0, 0, BOX, B, S)
        bw, lx = BOX, 0
    elif not qaf:
        lx = UP_TAIL
        bw = lx + BOX
        sh = ring(lx, 0, BOX, B, S) + tail(sp, bw)
    else:
        # the box rides on the right half of the ن bowl
        bw = 2 * NOON_R
        lx = bw - BOX
        sh = ring(lx, 0, BOX, B, S) + half_ring(NOON_R, NOON_R, S, S)
    cx = lx + BOX / 2
    sh += dots(sp, nd, cx, B + sp.DA, True)
    return assemble(sp, sh, bw, form, cx)


# ------------------------------------------------------------------ KAF / GAF
KAF_REACH = 230         # arm reach right of the stem
GAF_DASH = (35, 185)    # dash of گ, measured from the stem's right edge; its top is on the alef line


def stem_arm(sp, x, gaf):
    """The kaf's stem (left edge at x) with the flat arm reaching right from its top. گ: the arm
    on the kaf line and the dash one dot-gap above it (a little less in Bold, so the dash stays
    under the alef line). ک: no dash, so the arm rises to the top of the گ's dash and both
    letters are the same height."""
    S, K = sp.S, sp.K
    top = K if gaf else gaf_top(sp)
    sh = [R(x, 0, x + S, top), R(x, top - S, x + S + KAF_REACH, top)]
    if gaf:
        y0 = gaf_top(sp) - sp.t
        sh.append(R(x + S + GAF_DASH[0], y0, x + S + GAF_DASH[1], y0 + sp.t))
    return sh


def gaf_top(sp):
    """Top of the گ's dash = top of the ک's arm: 650 / 622 / 584."""
    return sp.K + min(sp.DA, A - sp.t - sp.K) + sp.t


def kaf(sp, form, gaf=False, arabic=False):
    """ک گ: a stem with the arm reaching right. Initial: the stem stands on the end of the run.
    Medial / final: the joining bar comes in under the arm (the arm may then slide over the
    previous letter, see build.join_kerning). Final / isolated: the base runs on to the left
    into an upturned tip, as in ب."""
    S = sp.S
    x = 0 if form in ("init", "medi") else UP_TAIL
    if arabic and x:
        # ك: the tail is long enough for its hamza to keep a dot-gap from the tip and the stem
        hz = [s.bounds for s in hamza(sp, 0, 0, 0.85)]
        x = max(x, S + 2 * sp.DA + max(b[2] for b in hz) - min(b[0] for b in hz))
    sh = stem_arm(sp, x, gaf)
    if form in ("medi", "fina"):
        bw = x + S + KAF_REACH
        sh.append(R(x, 0, bw, S))
    else:
        bw = x + S
    if x:
        sh += tail(sp, x + S)
    if arabic and x:
        sh += hamza(sp, (S + x) / 2, S + sp.DA, 0.85)
    return assemble(sp, sh, bw, form, x + (S + KAF_REACH) / 2)


def kaf_box(sp, form, gaf=False, lam_tail=False):
    """The emblem's square kaf, used only before ا and ل (کا گا کل گل): the box (3x3) sits
    before the stem and its left wall rises to the alef line as the ا / ل. Before a final ل the
    left wall runs on down into the ل's bowl."""
    S = sp.S
    bowl, lw = lam_bowl(sp) if lam_tail else ([], S)
    x = lw - S
    bw = x + BOX + KAF_REACH
    sh = shift(ring(0, 0, BOX, B, S) + stem_arm(sp, BOX - S, gaf) + [R(0, 0, S, A)], x) + bowl
    if form in ("medi", "fina"):
        sh.append(R(x + BOX - S, 0, bw, S))
    return assemble(sp, sh, bw, form, x + BOX / 2)


def kaf_alef(sp, form, gaf=False):
    """کا / گا (isolated / final)."""
    return kaf_box(sp, form, gaf)


def kaf_lam(sp, form, gaf=False):
    """کل / گل in all four forms (initial / medial: the ل goes on joining to the left)."""
    return kaf_box(sp, form, gaf, lam_tail=form in ("isol", "fina"))


# ------------------------------------------------------------------ LAM / LAM-ALEF
def lam_bowl(sp):
    """The bowl of the final / isolated ل: the square bowl of ی, hanging under the baseline to
    the bowl line, its tip rising on the left to the top of the line. Its right wall
    (x w-S..w) is where the stem goes up. Returns (shapes, w)."""
    return sq_bowl(sp, YEH_W, DD, sp.S, tip_left=True), YEH_W


def lam(sp, form):
    """Initial / medial: a stem to the alef line. Final / isolated: the stem runs on down into
    a bowl under the baseline, as deep as the ن."""
    S = sp.S
    if form in ("init", "medi"):
        return assemble(sp, [R(0, 0, S, A)], S, form)
    sh, bw = lam_bowl(sp)
    sh = sh + [R(bw - S, 0, bw, A)]
    return assemble(sp, sh, bw, form, bw - S / 2)


def lamalef(sp, form, var=None):
    """لا: two stems on one baseline, the lam on the right, the alef on the left."""
    S = sp.S
    W = 2 * S + sp.J
    top = A
    sh = []
    if var == "madda":
        top = A - sp.DA - 55 - mark_t(sp)
        sh += madda(sp, S / 2, top + sp.DA)
    elif var == "hamza_above":
        top = A - hamza_h(sp, 0.85) - sp.DA
        sh += hamza(sp, S / 2 + 10, top + sp.DA, 0.85)
    elif var == "hamza_below":
        sh += hamza(sp, S / 2 + 10, -sp.DA - hamza_h(sp, 0.85), 0.85)
    sh += [R(0, 0, S, top), R(W - S, 0, W, A), R(0, 0, W, S)]
    return assemble(sp, sh, W, form)


# ------------------------------------------------------------------ MEEM
MEEM_STEP = 170         # final / isolated: tail's left edge to the box's left edge


def meem(sp, form):
    """The 3x3 box sits on the baseline in every form (its floor is the joining bar).
    Final / isolated: the base runs on to the left and drops into a tail."""
    S = sp.S
    if form in ("init", "medi"):
        return assemble(sp, ring(0, 0, BOX, B, S), BOX, form)
    # the base runs on a little to the left of the box before it drops into the tail
    e = MEEM_STEP
    sh = ring(e, 0, BOX, B, S) + [R(0, 0, e + S, S), R(0, DD, S, S)]
    return assemble(sp, sh, e + BOX, form, e + BOX / 2)


# ------------------------------------------------------------------ HEH / TEH MARBUTA
HEH_W, HEH_TOP = 280, T     # initial / medial ه: width, and top of the upper storey (teeth line)


def heh(sp, form, nd=0, hamza_above=False):
    """Initial / medial: the emblem's two-storey box straddling the baseline, two equal
    counters, smaller than the box. Final / isolated: the 3x3 box."""
    S = sp.S
    if form in ("init", "medi"):
        bw = HEH_W
        lo = S - HEH_TOP                    # the lower storey mirrors the upper one
        sh = ring(0, lo, bw, HEH_TOP - lo, S) + [R(0, 0, bw, S)]
    else:
        bw = BOX
        sh = ring(0, 0, BOX, B, S)
    if nd:
        sh += dots(sp, nd, BOX / 2, B + sp.DA, True)
    if hamza_above:
        sh += hamza(sp, BOX / 2 + 10, B + sp.DA, 0.85)
    return assemble(sp, sh, bw, form)


# ------------------------------------------------------------------ ALEF
def alef(sp, form, var=None):
    S = sp.S
    sh = []
    top = A
    cx = S / 2
    if var == "madda":
        top = A - sp.DA - 55 - mark_t(sp)
        sh += madda(sp, cx, top + sp.DA)
    elif var == "hamza_above":
        top = A - hamza_h(sp, 0.85) - sp.DA
        sh += hamza(sp, cx + 10, top + sp.DA, 0.85)
    elif var == "hamza_below":
        sh += hamza(sp, cx + 10, -sp.DA - hamza_h(sp, 0.85), 0.85)
    sh.append(R(0, 0, S, top))
    return assemble(sp, sh, S, form, cx)
