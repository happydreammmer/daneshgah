"""Builds the Daneshgah fonts (Light, Regular, Bold) as TTF, OTF and WOFF2.

    python build.py ../fonts

Also writes the OpenType feature code of each weight (features-<weight>.fea) next to the fonts.
"""
import sys, os, unicodedata
import shapely
from shapely.ops import unary_union
from shapely.geometry import Polygon, MultiPolygon
from shapely.geometry.polygon import orient
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.ttLib import TTFont

import design as d
from design import Spec, Glyph, R, FORMS
import extras as ex

FAMILY = "Daneshgah"
FAMILY_FA = "دانشگاه"
VERSION = "1.000"
DESIGNER = "Hatef Mohammad Ali (Kouzehchi)"
COPYRIGHT = f"Copyright (c) 2026 {DESIGNER}"
LICENSE = ("This font is licensed under the MIT License: free to use, copy, modify, merge, publish, "
           "distribute, sublicense and sell, provided the copyright and permission notices are kept. "
           "The font is provided as is, without warranty of any kind.")
LICENSE_URL = "https://opensource.org/license/mit"


# (codepoint, glyph name, joining type, builder)
def letters():
    L = []
    def add(cp, name, jt, fn):
        L.append((cp, name, jt, fn))
    add(0x0628, "beh", "D", lambda sp, f: d.beh_like(sp, f, 1, False))
    add(0x067E, "peh", "D", lambda sp, f: d.beh_like(sp, f, 3, False))
    add(0x062A, "teh", "D", lambda sp, f: d.beh_like(sp, f, 2, True))
    add(0x062B, "theh", "D", lambda sp, f: d.beh_like(sp, f, 3, True))
    add(0x0646, "noon", "D", lambda sp, f: d.beh_like(sp, f, 1, True, "noon"))
    add(0x06CC, "yehFarsi", "D", lambda sp, f: d.beh_like(sp, f, 2 if f in ("init", "medi") else 0, False, "yeh"))
    add(0x064A, "yeh", "D", lambda sp, f: d.beh_like(sp, f, 2, False, "yeh"))
    add(0x0649, "alefMaksura", "D", lambda sp, f: d.beh_like(sp, f, 0, False, "yeh"))
    add(0x0626, "yehHamza", "D", lambda sp, f: d.beh_like(sp, f, 0, False, "hamza"))
    add(0x062C, "jeem", "D", lambda sp, f: d.hah_like(sp, f, 1, "below"))
    add(0x0686, "tcheh", "D", lambda sp, f: d.hah_like(sp, f, 3, "below"))
    add(0x062D, "hah", "D", lambda sp, f: d.hah_like(sp, f, 0))
    add(0x062E, "khah", "D", lambda sp, f: d.hah_like(sp, f, 1, "above"))
    add(0x062F, "dal", "R", lambda sp, f: d.dal(sp, f))
    add(0x0630, "thal", "R", lambda sp, f: d.dal(sp, f, 1))
    add(0x0631, "reh", "R", lambda sp, f: d.reh(sp, f))
    add(0x0632, "zain", "R", lambda sp, f: d.reh(sp, f, 1))
    add(0x0698, "jeh", "R", lambda sp, f: d.reh(sp, f, 3))
    add(0x0633, "seen", "D", lambda sp, f: d.seen(sp, f))
    add(0x0634, "sheen", "D", lambda sp, f: d.seen(sp, f, 3))
    add(0x0635, "sad", "D", lambda sp, f: d.sad(sp, f))
    add(0x0636, "dad", "D", lambda sp, f: d.sad(sp, f, 1))
    add(0x0637, "tah", "D", lambda sp, f: d.tah(sp, f))
    add(0x0638, "zah", "D", lambda sp, f: d.tah(sp, f, 1))
    add(0x0639, "ain", "D", lambda sp, f: d.ain_like(sp, f))
    add(0x063A, "ghain", "D", lambda sp, f: d.ain_like(sp, f, 1))
    add(0x0641, "feh", "D", lambda sp, f: d.feh_qaf(sp, f, 1))
    add(0x0642, "qaf", "D", lambda sp, f: d.feh_qaf(sp, f, 2, True))
    add(0x06A9, "keheh", "D", lambda sp, f: d.kaf(sp, f))
    add(0x06AF, "gaf", "D", lambda sp, f: d.kaf(sp, f, gaf=True))
    add(0x0643, "kaf", "D", lambda sp, f: d.kaf(sp, f, arabic=True))
    add(0x0644, "lam", "D", lambda sp, f: d.lam(sp, f))
    add(0x0645, "meem", "D", lambda sp, f: d.meem(sp, f))
    add(0x0647, "heh", "D", lambda sp, f: d.heh(sp, f))
    add(0x0629, "tehMarbuta", "R", lambda sp, f: d.heh(sp, f, 2))
    add(0x06C0, "hehYeh", "R", lambda sp, f: d.heh(sp, f, 0, True))
    add(0x0648, "waw", "R", lambda sp, f: d.waw(sp, f))
    add(0x0624, "wawHamza", "R", lambda sp, f: d.waw(sp, f, True))
    add(0x0627, "alef", "R", lambda sp, f: d.alef(sp, f))
    add(0x0622, "alefMadda", "R", lambda sp, f: d.alef(sp, f, "madda"))
    add(0x0623, "alefHamza", "R", lambda sp, f: d.alef(sp, f, "hamza_above"))
    add(0x0625, "alefHamzaBelow", "R", lambda sp, f: d.alef(sp, f, "hamza_below"))
    return L


ALEFS = [("alef", None), ("alefMadda", "madda"), ("alefHamza", "hamza_above"), ("alefHamzaBelow", "hamza_below")]
KAFS = [("keheh", False), ("gaf", True), ("kaf", False)]


def build_glyphs(sp):
    G = {}
    cmap = {}
    joining = {}
    for cp, name, jt, fn in letters():
        forms = FORMS if jt == "D" else ("isol", "fina")
        for f in forms:
            G[name if f == "isol" else f"{name}.{f}"] = fn(sp, f)
        cmap[cp] = name
        joining[name] = jt
    # lam-alef ligatures
    for an, var in ALEFS:
        G[f"lam_{an}"] = d.lamalef(sp, "isol", var)
        G[f"lam_{an}.fina"] = d.lamalef(sp, "fina", var)
    # kaf-alef / gaf-alef (the emblem's گا): the alef is the left wall of the kaf's box
    for kn, gaf in KAFS:
        G[f"{kn}_alef"] = d.kaf_alef(sp, "isol", gaf)
        G[f"{kn}_alef.fina"] = d.kaf_alef(sp, "fina", gaf)
        for f in FORMS:
            G[f"{kn}_lam" + ("" if f == "isol" else f".{f}")] = d.kaf_lam(sp, f, gaf)
    # hamza, tatweel
    hz = d.hamza(sp, 0, 0, 1.4)
    x0 = min(s.bounds[0] for s in hz)
    w = max(s.bounds[2] for s in hz) - x0
    G["hamza"] = ex._g(sp, d.shift(hz, -x0, 40), w)
    cmap[0x0621] = "hamza"
    G["tatweel"] = Glyph([R(-sp.OV, 0, 240 + sp.OV, sp.S)], 240)
    cmap[0x0640] = "tatweel"
    # digits
    for n in range(10):
        G[f"uni{0x06F0 + n:04X}"] = ex.fa_digit(sp, n)
        cmap[0x06F0 + n] = f"uni{0x06F0 + n:04X}"
        ln = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"][n]
        G[ln] = ex.la_digit(sp, n)
        cmap[0x30 + n] = ln
        an = f"uni{0x0660 + n:04X}"
        if n in (4, 5, 6):
            G[an] = ex.ar_digit(sp, n)
            cmap[0x0660 + n] = an
        else:
            cmap[0x0660 + n] = f"uni{0x06F0 + n:04X}"
    # punctuation
    P = ex.punct(sp)
    uni = {"period": 0x2E, "colon": 0x3A, "comma": 0x2C, "semicolon": 0x3B, "uni060C": 0x060C, "uni061B": 0x061B,
           "exclam": 0x21, "question": 0x3F, "uni061F": 0x061F, "hyphen": 0x2D, "endash": 0x2013, "emdash": 0x2014,
           "underscore": 0x5F, "slash": 0x2F, "backslash": 0x5C, "parenleft": 0x28, "parenright": 0x29,
           "bracketleft": 0x5B, "bracketright": 0x5D, "plus": 0x2B, "equal": 0x3D, "less": 0x3C, "greater": 0x3E,
           "guillemotleft": 0xAB, "guillemotright": 0xBB, "quotesingle": 0x27, "quotedbl": 0x22, "ellipsis": 0x2026,
           "percent": 0x25, "uni066B": 0x066B, "uni066C": 0x066C, "asterisk": 0x2A}
    for k, v in P.items():
        if k not in uni:
            continue
        G[k] = v
        cmap[uni[k]] = k
    cmap[0x066A] = "percent"
    cmap[0x066D] = "asterisk"
    cmap[0x2010] = "hyphen"
    # spaces & controls
    G["space"] = Glyph([], 300)
    cmap[0x20] = "space"; cmap[0xA0] = "space"
    for cp in (0x200C, 0x200D, 0x200E, 0x200F):
        G[f"uni{cp:04X}"] = Glyph([], 0)
        cmap[cp] = f"uni{cp:04X}"
    # marks
    M = ex.marks(sp)
    for k, (sh, pos) in M.items():
        G[k] = Glyph(sh, 0, 0)
        G[k].markpos = pos
        cmap[int(k[3:], 16)] = k
    # presentation forms (for apps without shaping)
    for cp in list(range(0xFB50, 0xFDFF)) + list(range(0xFE70, 0xFEFF)):
        dec = unicodedata.decomposition(chr(cp)).split()
        if not dec or not dec[0].startswith("<"):
            continue
        tag = dec[0][1:-1]
        bases = [int(x, 16) for x in dec[1:]]
        if tag not in ("isolated", "initial", "medial", "final"):
            continue
        sfx = {"isolated": "", "initial": ".init", "medial": ".medi", "final": ".fina"}[tag]
        if len(bases) == 1 and bases[0] in cmap and cmap[bases[0]] in joining:
            g = cmap[bases[0]] + sfx
        elif len(bases) == 2 and bases[0] == 0x0644 and bases[1] in cmap:
            an = cmap[bases[1]]
            g = f"lam_{an}" + (".fina" if tag == "final" else "")
        else:
            continue
        if g in G:
            cmap[cp] = g
    return G, cmap, joining


# ------------------------------------------------------------------ outlines
def polys(g):
    if not g.shapes:
        return []
    u = unary_union([s.buffer(0) for s in g.shapes])
    u = shapely.set_precision(u, 1.0)
    u = u.buffer(0)
    geoms = list(u.geoms) if hasattr(u, "geoms") else [u]
    return [p for p in geoms if isinstance(p, Polygon) and p.area > 4]


def clean(coords):
    pts = [(int(round(x)), int(round(y))) for x, y in coords[:-1]]
    out = []
    for p in pts:
        if not out or out[-1] != p:
            out.append(p)
    if len(out) > 1 and out[0] == out[-1]:
        out.pop()
    # drop collinear points
    changed = True
    while changed and len(out) > 3:
        changed = False
        for i in range(len(out)):
            a, b, c = out[i - 1], out[i], out[(i + 1) % len(out)]
            if (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0]) == 0:
                out.pop(i); changed = True; break
    return out


def draw(pen, ps, sign):
    rings = []
    for p in ps:
        p = orient(p, sign=sign)
        for ring_ in [p.exterior] + list(p.interiors):
            pts = clean(list(ring_.coords))
            if len(pts) >= 3:
                rings.append(pts)
    if len(rings) == 1 and len(rings[0]) == 4:
        # a glyph that is one plain rectangle (alef, tatweel, ۱, ...): PDF renderers such as
        # pdfium (Chrome, Edge) fill such a path as a pixel-snapped rect without anti-aliasing,
        # so it sticks out by up to a pixel next to its anti-aliased neighbours. A midpoint on
        # one edge keeps it a normal path.
        a, b = rings[0][0], rings[0][1]
        rings[0].insert(1, ((a[0] + b[0]) // 2, (a[1] + b[1]) // 2))
    for pts in rings:
        pen.moveTo(pts[0])
        for q in pts[1:]:
            pen.lineTo(q)
        pen.closePath()


# ------------------------------------------------------------------ kerning
FOOTED = ("reh", "zain", "jeh", "waw", "wawHamza")
TUCK_PUNCT = ("period", "comma", "uni060C", "uni061B", "uni061F", "exclam", "question", "colon",
              "ellipsis", "guillemotleft", "guillemotright", "parenleft", "parenright")


def body(ps, sp):
    """The letter without its dots and small marks (hamza, madda)."""
    lim = 2.6 * sp.DOT
    out = [p for p in ps if not (p.bounds[2] - p.bounds[0] <= lim and p.bounds[3] - p.bounds[1] <= lim)]
    return out or ps


def foot_kerning(G, P, joining, sp):
    """For every letter ending in a foot (reh family, waw) and every glyph that can follow it,
    slide the follower right over the foot, as if the foot were not there:
      - above the baseline, the follower's body keeps the regular gap (2 x side bearing)
        from the upright of ر / head of و; dots and marks are left out of this measure,
      - nothing comes closer than CLEAR anywhere (dots below, bowls, the follower's own foot),
      - the foot never sticks out past the follower's left edge.
    The feet are drawn so that an alef after ر ends exactly where the foot ends (design.reh) and
    a letter after و begins exactly where its foot ends (design.waw); the same rule gives the
    same picture in every weight."""
    from shapely.geometry import MultiPolygon as MP
    from shapely.geometry import box as bx
    from shapely.affinity import translate as tr
    left = [n + sfx for n in FOOTED for sfx in ("", ".fina")]
    followers = []
    for n, j in joining.items():
        followers.append(n)
        if j == "D":
            followers.append(n + ".init")
    followers += [k for k in G if k.startswith("lam_") and not k.endswith(".fina")]
    followers += [k for k in TUCK_PUNCT if k in G]
    up = bx(-5000, -20, 5000, 5000)
    pairs = []
    for a in left:
        A = MP(P[a]).buffer(0)
        edge = MP(body(P[a], sp)).buffer(0).intersection(up).bounds[0]
        foot_end = A.bounds[0]
        for b in followers:
            if not P.get(b):
                continue
            Bg = MP(P[b]).buffer(0)
            Bup = MP(body(P[b], sp)).buffer(0).intersection(up)
            if Bup.is_empty:
                continue
            adv_b = round(G[b].adv)
            CLEAR = 2 * sp.SB
            def ok(k):
                Bs = tr(Bg, -adv_b + k, 0)
                return Bs.distance(A) >= CLEAR and Bs.bounds[0] <= foot_end + 0.5
            kmax = k = int(edge - 2 * sp.SB - (Bup.bounds[2] - adv_b))
            while k > 0 and not ok(k):
                k -= 4
            while 0 < k < kmax and ok(k + 1):
                k += 1
            if k >= 20:
                pairs.append((a, b, -k))
    return pairs


# Letters whose left end (towards the next letter) is a tooth, and letters whose right end
# (where the previous letter joins) is a tooth.
TOOTH_END = ["beh", "peh", "teh", "theh", "noon", "yehFarsi", "yeh", "alefMaksura", "yehHamza",
             "seen", "sheen", "sad", "dad"]
TOOTH_START = ["beh", "peh", "teh", "theh", "noon", "yehFarsi", "yeh", "alefMaksura", "yehHamza", "seen", "sheen"]
TOOTH_START_FINA = ["beh", "peh", "teh", "theh", "seen", "sheen"]


def is_dot(p, sp):
    """Dots and small marks (hamza, madda): no separate piece of a letter body is this small."""
    lim = max(1.75 * sp.DOT, 180)
    w, h = p.bounds[2] - p.bounds[0], p.bounds[3] - p.bounds[1]
    return w <= lim and h <= lim


KAF_NAMES = ("keheh.", "gaf.", "kaf.", "keheh_alef.fina", "gaf_alef.fina", "kaf_alef.fina",
             "keheh_lam.", "gaf_lam.", "kaf_lam.")


def join_kerning(G, P, joining, sp):
    """Every joined pair (a letter that joins left, then one that joins right):
      - tooth after tooth (ن ش, ب ی, س ت ...): the run closes so the two teeth stand on the same
        pitch as the three teeth of س, as in the emblem's نش;
      - dots of one letter keep two dot-gaps from the dots of the next (so ب ی never reads as پ)
        and one dot-gap plus a little from its strokes; where they would come closer the run
        opens up just enough."""
    from shapely.geometry import MultiPolygon as MP
    from shapely.geometry import box as bx
    from shapely.affinity import translate as tr
    band = bx(-5000, -2, 5000, sp.S + 2)
    comb = (d.SEEN_W - 3 * sp.S) / 2          # gap between the teeth of س
    CLD, CLB = 2 * sp.DG, sp.DG + 10
    names = list(G)
    lefts = [n for n in names if n.endswith((".init", ".medi")) and P.get(n)]
    lefts += [n for n in names if n.startswith("lam_") and False]
    rights = [n for n in names if n.endswith((".medi", ".fina")) and P.get(n)]
    t_end = {n + f for n in TOOTH_END for f in (".init", ".medi")}
    t_start = {n + ".medi" for n in TOOTH_START} | {n + ".fina" for n in TOOTH_START_FINA}

    def split(n):
        polys = [p.difference(band) for p in P[n]]
        polys = [g for p in polys for g in (p.geoms if hasattr(p, "geoms") else [p]) if not g.is_empty]
        dts = [p for p in P[n] if is_dot(p, sp)]
        bod = [p for p in polys if not any(p.equals(q) or p.within(q.buffer(0.5)) for q in dts)]
        return (MP(bod).buffer(0) if bod else None), (MP(dts).buffer(0) if dts else None), dts, bod
    parts = {n: split(n) for n in set(lefts) | set(rights)}
    bands = {n: MP(P[n]).buffer(0).intersection(band) for n in set(lefts) | set(rights)}
    right_half = bx(0, -5000, 5000, 5000)
    pairs, loose = [], []
    for a in lefts:
        Ab, Ad, Al, Ap = parts[a]
        for bn in rights:
            Bb, Bd, Bl, Bp = parts[bn]
            if Ad is None and Bd is None and not (a in t_end and bn in t_start) and not bn.startswith(KAF_NAMES):
                continue
            adv_b = round(G[bn].adv)
            def ok(k):
                dx = -adv_b + k
                if Ab is not None and Bb is not None and tr(Bb, dx, 0).distance(Ab) < comb - 0.5:
                    return False
                # the joining bar of the second letter may run under the first one only where
                # the first one has its own bar (else a stub would stick out)
                if k > 0 and tr(bands[bn], dx, 0).intersection(right_half).difference(bands[a]).area > 20:
                    return False
                for p in Al:
                    for q in Bl:
                        q = tr(q, dx, 0)
                        same_row = p.bounds[1] < q.bounds[3] and q.bounds[1] < p.bounds[3]
                        if same_row and q.distance(p) < CLD:      # side by side: keep clusters apart
                            return False
                        if q.distance(p) < CLB:
                            return False
                # a dot and a stroke of the other letter: one dot-gap and a little; two dot-gaps when
                # they stand side by side on the same row (else the dot reads as part of the stroke)
                for dl, bl, sign in ((Al, Bp, 1), (Bl, Ap, -1)):
                    for p in dl:
                        p = tr(p, dx, 0) if sign < 0 else p
                        for q in bl:
                            q = tr(q, dx, 0) if sign > 0 else q
                            same_row = p.bounds[1] < q.bounds[3] and q.bounds[1] < p.bounds[3]
                            dd = q.distance(p)
                            if dd < CLB or (same_row and dd < CLD):
                                return False
                return True
            if bn.startswith(KAF_NAMES):
                # kaf / gaf: the arm may reach over the end of the previous letter, as the emblem's
                # گ reaches over the undotted tooth of ش; the stem keeps the س tooth gap
                # ... but never past the previous letter's own right end (what comes before it is unknown)
                k = int(min(sp.J + d.KAF_REACH, G[a].adv - comb))
            elif a in t_end and bn in t_start:
                k = int(sp.J - comb)
            else:
                k = 0
            while k > -400 and not ok(k):
                k -= 5
            if k > 0:
                pairs.append((a, bn, -k))
            elif k < 0:
                # opening up must not break the bar: the first letter gets a longer run instead
                loose.append((a, bn, -k))
    return pairs, loose


def long_run(g, L, sp):
    """The same joining letter with its run (on the left) made L units longer."""
    sh = d.shift(g.shapes, L) + [R(-sp.OV, 0, L + sp.OV, sp.S)]
    return Glyph(sh, g.adv + L, g.cx + L)


# ------------------------------------------------------------------ features
def features(G, joining, marknames, anchors, kerns=(), loose=()):
    D = [n for n, j in joining.items() if j == "D"]
    Rj = [n for n, j in joining.items() if j == "R"]
    fea = ["languagesystem DFLT dflt;", "languagesystem arab dflt;", "languagesystem arab FAR;", ""]
    def single(tag, names, sfx):
        names = [n for n in names if n + sfx in G]
        fea.append(f"feature {tag} {{")
        fea.append(f"  sub [{' '.join(names)}] by [{' '.join(n + sfx for n in names)}];")
        fea.append(f"}} {tag};")
    single("init", D, ".init")
    single("medi", D, ".medi")
    single("fina", D + Rj, ".fina")
    fea.append("feature rlig {")
    for an, _ in ALEFS:
        fea.append(f"  sub lam.init {an}.fina by lam_{an};")
        fea.append(f"  sub lam.medi {an}.fina by lam_{an}.fina;")
    fea.append("} rlig;")
    # kaf + alef (the emblem's گا) in rlig too, so that calt below already sees the ligature
    fea.append("feature rlig {")
    fea.append("  lookupflag IgnoreMarks;")
    for kn, _ in KAFS:
        fea.append(f"  sub {kn}.init alef.fina by {kn}_alef;")
        fea.append(f"  sub {kn}.medi alef.fina by {kn}_alef.fina;")
        fea.append(f"  sub {kn}.init lam.fina by {kn}_lam;")
        fea.append(f"  sub {kn}.init lam.medi by {kn}_lam.init;")
        fea.append(f"  sub {kn}.medi lam.fina by {kn}_lam.fina;")
        fea.append(f"  sub {kn}.medi lam.medi by {kn}_lam.medi;")
    fea.append("} rlig;")
    if loose:
        # pairs that need more room than the run gives: the first letter takes a longer run
        fea.append("feature calt {")
        fea.append("  lookupflag IgnoreMarks;")
        for a, b, L in loose:
            fea.append(f"  sub {a}' {b} by {a}.w{L};")
        fea.append("} calt;")
    top = [m for m in marknames if G[m].markpos == "top"]
    bot = [m for m in marknames if G[m].markpos == "bot"]
    bases = [n for n in G if n not in marknames and n != ".notdef"]
    fea.append(f"markClass [{' '.join(top)}] <anchor 0 0> @TOP;")
    fea.append(f"markClass [{' '.join(bot)}] <anchor 0 0> @BOT;")
    fea.append("feature mark {")
    for n in bases:
        if not G[n].shapes:
            continue
        (tx, ty), (bx, by) = anchors[n]
        fea.append(f"  pos base {n} <anchor {tx} {ty}> mark @TOP <anchor {bx} {by}> mark @BOT;")
    fea.append("} mark;")
    if kerns:
        fea.append("feature kern {")
        fea.append("  lookupflag IgnoreMarks;")
        for a, b, v in kerns:
            # RTL: shift the footed letter (and everything before it) left, so the next letter closes in
            fea.append(f"  pos {a} {b} <{v} 0 {v} 0>;")
        fea.append("} kern;")
    fea.append("feature mkmk {")
    for m in top:
        fea.append(f"  pos mark {m} <anchor 0 {anchors[m][0][1]}> mark @TOP;")
    for m in bot:
        fea.append(f"  pos mark {m} <anchor 0 {anchors[m][1][1]}> mark @BOT;")
    fea.append("} mkmk;")
    fea.append("table GDEF {")
    fea.append(f"  GlyphClassDef [{' '.join(bases)}], , [{' '.join(marknames)}], ;")
    fea.append("} GDEF;")
    return "\n".join(fea)


# ------------------------------------------------------------------ build
STYLE_FA = {"Light": "نازک", "Regular": "معمولی", "Bold": "ضخیم"}


def build(S, style, weight, outdir):
    sp = Spec(S)
    G, cmap, joining = build_glyphs(sp)
    G[".notdef"] = Glyph([R(50, 0, 450, 600), ], 500)
    G[".notdef"].hole = True
    P = {n: polys(G[n]) for n in G}
    jk, loose = join_kerning(G, P, joining, sp)
    kerns = foot_kerning(G, P, joining, sp) + jk
    # longer-run variants for the loose pairs; a variant's right side is its letter's, so it
    # takes the same kerning as the second glyph of a pair
    variants = {}
    for a, b, L in loose:
        v = f"{a}.w{L}"
        if v not in G:
            G[v] = long_run(G[a], L, sp)
            P[v] = polys(G[v])
            variants.setdefault(a, []).append(v)
    kerns += [(x, v, k) for x, y, k in kerns for v in variants.get(y, ())]
    order = [".notdef"] + [n for n in G if n != ".notdef"]
    P = {n: P.get(n) or polys(G[n]) for n in order}
    # .notdef box with hole
    P[".notdef"] = [Polygon([(50, 0), (450, 0), (450, 600), (50, 600)], [[(100, 50), (400, 50), (400, 550), (100, 550)]])]
    marknames = [n for n in G if hasattr(G[n], "markpos")]
    anchors = {}
    ymax_all, ymin_all = 0, 0
    for n in order:
        if not P[n]:
            anchors[n] = ((0, 0), (0, 0)); continue
        b = MultiPolygon(P[n]).bounds
        ymin_all, ymax_all = min(ymin_all, b[1]), max(ymax_all, b[3])
        cx = int(round(G[n].cx))
        if n in marknames:
            anchors[n] = ((0, int(b[3] + 45)), (0, int(b[1] - 45)))
        else:
            anchors[n] = ((cx, int(max(b[3], d.T) + 75)), (cx, int(min(b[1], 0) - 75)))
    asc = int(ymax_all + 230)    # room for marks
    desc = int(ymin_all - 120)
    adv = {n: int(round(G[n].adv)) for n in order}
    fea = features(G, joining, marknames, anchors, kerns, loose)
    # Style linking: Regular and Bold make the family "Daneshgah" (so Ctrl+B switches between
    # them); Light is the Regular of its own family "Daneshgah Light".
    linked = style in ("Regular", "Bold")
    names = {
        "familyName": FAMILY if linked else f"{FAMILY} {style}",
        "styleName": "Bold" if style == "Bold" else "Regular",
        "typographicFamily": FAMILY, "typographicSubfamily": style,
        "uniqueFontIdentifier": f"{FAMILY}-{style};{VERSION}",
        "fullName": f"{FAMILY} {style}", "psName": f"{FAMILY}-{style}",
        "version": f"Version {VERSION}",
        "copyright": COPYRIGHT,
        "designer": DESIGNER,
        "description": ("Daneshgah is a geometric square-Kufic Persian display typeface, rebuilt from the "
                        "lettering of the classic University of Tehran emblem."),
        "licenseDescription": LICENSE,
        "licenseInfoURL": LICENSE_URL,
        "sampleText": "دانشگاه تهران ۱۳۱۳",
    }
    outs = []
    for flavor in ("ttf", "otf"):
        fb = FontBuilder(1000, isTTF=(flavor == "ttf"))
        fb.setupGlyphOrder(order)
        fb.setupCharacterMap(cmap)
        if flavor == "ttf":
            glyphs = {}
            for n in order:
                pen = TTGlyphPen(None)
                draw(pen, P[n], -1.0)
                glyphs[n] = pen.glyph()
            fb.setupGlyf(glyphs)
        else:
            cs = {}
            for n in order:
                pen = T2CharStringPen(adv[n], None)
                draw(pen, P[n], 1.0)
                cs[n] = pen.getCharString()
            fb.setupCFF(f"{FAMILY}-{style}", {"FullName": f"{FAMILY} {style}", "FamilyName": FAMILY,
                                               "Weight": style, "Notice": COPYRIGHT}, cs, {})
        lsb = {}
        for n in order:
            lsb[n] = int(MultiPolygon(P[n]).bounds[0]) if P[n] else 0
        fb.setupHorizontalMetrics({n: (adv[n], lsb[n]) for n in order})
        fb.setupHorizontalHeader(ascent=asc, descent=desc, lineGap=0)
        fb.setupNameTable(names)
        nt = fb.font["name"]
        nt.setName(FAMILY_FA if linked else f"{FAMILY_FA} {STYLE_FA[style]}", 1, 3, 1, 0x0429)
        nt.setName(f"{FAMILY_FA} {STYLE_FA[style]}", 4, 3, 1, 0x0429)
        nt.setName(FAMILY_FA, 16, 3, 1, 0x0429)
        nt.setName(STYLE_FA[style], 17, 3, 1, 0x0429)
        fsSel = 0x20 if style == "Bold" else 0x40
        fb.setupOS2(sTypoAscender=asc, sTypoDescender=desc, sTypoLineGap=0,
                    usWinAscent=asc, usWinDescent=-desc, usWeightClass=weight,
                    fsType=0,                              # installable: no embedding restrictions
                    fsSelection=fsSel | 0x80, achVendID="NONE",
                    ulUnicodeRange1=(1 << 0) | (1 << 13), ulCodePageRange1=(1 << 0) | (1 << 6),
                    sxHeight=d.T, sCapHeight=d.A, version=4)
        fb.setupPost()
        from fontTools.misc.timeTools import timestampNow
        fb.setupHead(unitsPerEm=1000, fontRevision=float(VERSION), macStyle=1 if style == "Bold" else 0, created=timestampNow(), modified=timestampNow())
        addOpenTypeFeaturesFromString(fb.font, fea)
        fb.font["OS/2"].recalcAvgCharWidth(fb.font)
        path = os.path.join(outdir, f"{FAMILY}-{style}.{flavor}")
        fb.save(path)
        outs.append(path)
        if flavor == "ttf":
            f = TTFont(path)
            f.flavor = "woff2"
            wp = os.path.join(outdir, f"{FAMILY}-{style}.woff2")
            f.save(wp)
            outs.append(wp)
    open(os.path.join(outdir, f"features-{style}.fea"), "w", encoding="utf-8").write(fea)
    return outs, len(order)


WEIGHTS = ((60, "Light", 300), (80, "Regular", 400), (100, "Bold", 700))      # Bold = the emblem

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "../fonts"
    os.makedirs(out, exist_ok=True)
    for S, style, w in WEIGHTS:
        o, n = build(S, style, w, out)
        print(style, n, "glyphs:", ", ".join(os.path.basename(p) for p in o))
