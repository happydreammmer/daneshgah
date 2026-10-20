"""Type specimen and font-vs-emblem picture for Daneshgah.

    python specimen.py ../fonts ..

writes, into the second folder:
    Daneshgah-specimen.html   self-contained specimen (fonts embedded)
    Daneshgah-specimen.png    the same page as an image (needs Microsoft Edge or Google Chrome)
    font-vs-emblem.png        the emblem's «دانشگاه» above the font (Bold) at the same scale,
                              and the font's outline laid over the emblem
Needs: fonttools, uharfbuzz, pillow.
"""
import base64, html, os, shutil, subprocess, sys, tempfile, time

ZWJ = "\u200d"
WEIGHTS = ("Light", "Regular", "Bold")

# letter, name, joins on the left?, (word with the letter at the start, in the middle, at the end)
LETTERS = [
    ("ا", "alef", False, ("اسب", "باران", "دریا")),
    ("ب", "be", True, ("باران", "صبح", "کتاب")),
    ("پ", "pe", True, ("پدر", "سپید", "چپ")),
    ("ت", "te", True, ("تهران", "ستاره", "دوست")),
    ("ث", "se", True, ("ثروت", "مثل", "میراث")),
    ("ج", "jim", True, ("جنگل", "انجمن", "کاج")),
    ("چ", "che", True, ("چراغ", "کوچه", "پیچ")),
    ("ح", "he", True, ("حرف", "محمد", "صبح")),
    ("خ", "khe", True, ("خورشید", "سخن", "کاخ")),
    ("د", "dal", False, ("دانش", "مادر", "سفید")),
    ("ذ", "zal", False, ("ذرت", "گذر", "کاغذ")),
    ("ر", "re", False, ("روز", "تهران", "شهر")),
    ("ز", "ze", False, ("زمین", "سبزه", "سبز")),
    ("ژ", "zhe", False, ("ژاله", "مژده", "دژ")),
    ("س", "sin", True, ("سلام", "آسمان", "درس")),
    ("ش", "shin", True, ("شب", "دانشگاه", "آتش")),
    ("ص", "sad", True, ("صبح", "قصه", "رقص")),
    ("ض", "zad", True, ("ضرب", "حضور", "حوض")),
    ("ط", "ta", True, ("طبیعت", "قطره", "خط")),
    ("ظ", "za", True, ("ظرف", "نظر", "حافظ")),
    ("ع", "eyn", True, ("عشق", "بعد", "شمع")),
    ("غ", "gheyn", True, ("غروب", "مغز", "باغ")),
    ("ف", "fe", True, ("فردا", "سفر", "برف")),
    ("ق", "qaf", True, ("قلم", "عقاب", "عشق")),
    ("ک", "kaf", True, ("کتاب", "مکتب", "بانک")),
    ("گ", "gaf", True, ("گل", "دانشگاه", "سنگ")),
    ("ل", "lam", True, ("لب", "گلستان", "گل")),
    ("م", "mim", True, ("ماه", "انجمن", "مردم")),
    ("ن", "nun", True, ("نان", "پنجره", "تهران")),
    ("و", "vav", False, ("وطن", "روز", "دو")),
    ("ه", "he", True, ("هوا", "شهر", "دانشگاه")),
    ("ی", "ye", True, ("یاد", "ایران", "شادی")),
]
EXTRA = "آ أ إ ء ئ ؤ ة ۀ ك ي ى"

TEXTS = [
    "دانشگاه تهران، نخستین دانشگاه نوین ایران، در سال ۱۳۱۳ بنیان گذاشته شد. از آن زمان، "
    "نسل‌های بسیاری از پژوهشگران، هنرمندان و دانشمندان در آن درس خوانده‌اند.",
    "صبح زود، ژاله روی گل‌های باغچه نشسته بود و باغبان پیر مثل هر روز، کنار حوض و زیر سایه‌ی درخت، "
    "با ذوق از جلوه‌ی ظریف طبیعت عکس می‌گرفت.",
    "باغ‌های سبز، کوه‌های بلند و دشت‌های گسترده؛ ایران سرزمینی است با طبیعتی گوناگون، "
    "از جنگل‌های شمال تا کویر مرکزی و ساحل‌های گرم جنوب.",
]

CSS = """
:root { --bg:#eef3f6; --ink:#12181d; --mut:#66717a; --acc:#0b9fd0; --card:#f8fbfc; --line:#d3dee5; }
* { box-sizing:border-box; }
html { background:var(--bg); }
body { margin:0; background:var(--bg); color:var(--ink); font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif; }
.wrap { max-width:1300px; margin:0 auto; padding:56px 40px 72px; }
.fa { direction:rtl; font-family:"DaneshgahBold"; }
.L { font-family:"DaneshgahLight"; } .R { font-family:"DaneshgahRegular"; } .B { font-family:"DaneshgahBold"; }
header { display:flex; justify-content:space-between; align-items:flex-start; gap:24px; flex-wrap:wrap; }
.brand { color:var(--acc); font-weight:800; font-size:26px; letter-spacing:.08em; }
.meta { color:var(--mut); font-weight:600; font-size:14px; margin-top:4px; }
.hero { font-size:190px; line-height:1.25; text-align:right; }
.rule { height:5px; background:var(--acc); margin:22px 0 36px; border-radius:2px; }
h2 { font-size:13px; letter-spacing:.14em; text-transform:uppercase; color:var(--mut); margin:56px 0 18px; display:flex; justify-content:space-between; gap:16px; }
h2 .fa { font-family:"DaneshgahRegular"; font-size:20px; letter-spacing:0; text-transform:none; color:var(--ink); }
.wline { display:grid; grid-template-columns:110px 1fr; align-items:center; border-top:1px solid var(--line); }
.wline .lab { color:var(--mut); font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:.08em; }
.wline .fa { font-size:76px; line-height:1.6; text-align:right; white-space:nowrap; overflow:hidden; }
.emblem img { width:100%; max-width:640px; height:auto; display:block; margin:0 auto; border-radius:8px; }
.emblem p { margin:10px auto 0; max-width:640px; color:var(--mut); font-size:13px; }
.grid { display:grid; grid-template-columns:repeat(4,1fr); gap:14px; direction:rtl; }
.card { background:var(--card); border:1px solid var(--line); border-radius:10px; padding:14px 16px 12px; direction:ltr; }
.card .top { display:flex; justify-content:space-between; align-items:baseline; color:var(--mut); font-size:12px; font-weight:700; letter-spacing:.06em; text-transform:uppercase; }
.card .big { font-family:"DaneshgahBold"; font-size:42px; color:var(--acc); line-height:1; direction:rtl; }
.forms { display:grid; grid-template-columns:repeat(4,1fr); direction:rtl; margin:10px 0 4px; text-align:center; }
.forms div { font-family:"DaneshgahBold"; font-size:44px; line-height:1.8; }
.forms span { display:block; font:600 9.5px/1 system-ui,sans-serif; color:var(--mut); letter-spacing:.06em; text-transform:uppercase; }
.forms .na { color:#bfcbd2; }
.words { display:grid; grid-template-columns:repeat(3,1fr); direction:rtl; text-align:center; border-top:1px solid var(--line); padding-top:6px; }
.words div { font-family:"DaneshgahRegular"; font-size:23px; line-height:2; }
.words span { display:block; font:600 9.5px/1 system-ui,sans-serif; color:var(--mut); letter-spacing:.06em; text-transform:uppercase; }
.row { display:flex; flex-wrap:wrap; gap:10px 34px; direction:rtl; font-size:64px; line-height:1.8; }
.panel { background:var(--card); border:1px solid var(--line); border-radius:10px; padding:16px 26px; }
.panel + .panel { margin-top:14px; }
.panel .lab { color:var(--mut); font-size:12px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; }
.wf div { display:grid; grid-template-columns:70px 1fr; align-items:baseline; }
.wf .fa { white-space:nowrap; overflow:hidden; text-align:right; line-height:1.8; }
.cols { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; }
.cols .panel { margin-top:0; }
.para { font-size:24px; line-height:2.2; text-align:right; margin:8px 0 4px; }
.heads > div { display:grid; grid-template-columns:110px 1fr; align-items:center; }
.heads .fa { font-size:58px; line-height:1.7; text-align:right; }
footer { margin-top:56px; color:var(--mut); font-size:13px; display:flex; justify-content:space-between; flex-wrap:wrap; gap:12px; border-top:1px solid var(--line); padding-top:16px; }
@media (max-width:1000px) { .grid { grid-template-columns:repeat(2,1fr); } .cols { grid-template-columns:1fr; } .hero { font-size:110px; } }
@media (max-width:560px) { .wrap { padding:32px 16px; } .grid { grid-template-columns:1fr; } .hero { font-size:76px; } .wline .fa { font-size:40px; } .row { font-size:44px; } }
"""


def b64(p):
    return base64.b64encode(open(p, "rb").read()).decode()


def esc(t):
    return html.escape(t)


# ------------------------------------------------------------------ HTML specimen
def specimen_html(fontdir, out, emblem_png=None):
    css = CSS
    for w in WEIGHTS:
        css += (f'@font-face {{ font-family:"Daneshgah{w}"; '
                f'src:url(data:font/woff2;base64,{b64(os.path.join(fontdir, f"Daneshgah-{w}.woff2"))}) format("woff2"); }}\n')
    H = [f"<!doctype html><html lang='fa'><head><meta charset='utf-8'>"
         f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
         f"<title>Daneshgah Specimen</title><style>{css}</style></head><body><div class='wrap'>"]
    H.append("<header><div><div class='brand'>DANESHGAH</div><div class='meta'>Light · Regular · Bold &nbsp;—&nbsp; v1.000 &nbsp;—&nbsp; MIT License</div>"
             "<div class='meta' style='font-weight:400;max-width:520px;margin-top:10px'>A geometric square-Kufic Persian display face, "
             "rebuilt from the lettering of the classic emblem of the University of Tehran.</div></div>"
             "<div class='fa hero'>دانشگاه</div></header><div class='rule'></div>")

    H.append("<h2><span>Weights</span><span class='fa'>وزن‌ها</span></h2>")
    for w in WEIGHTS:
        H.append(f"<div class='wline'><div class='lab'>{w}</div><div class='fa {w[0]}'>دانشگاه تهران ۱۳۱۳</div></div>")

    if emblem_png and os.path.exists(emblem_png):
        H.append("<h2><span>Font and emblem</span><span class='fa'>فونت و آرم</span></h2>")
        H.append(f"<div class='panel emblem'><img alt='The emblem lettering, the font, and the font laid over the emblem' "
                 f"src='data:image/png;base64,{b64(emblem_png)}'><p>Top: «دانشگاه» in the emblem. Middle: Daneshgah Bold at the same scale "
                 "(one stroke of the emblem = 100 units), on the same baseline. Bottom: the font's outline laid over the emblem.</p></div>")

    H.append("<h2><span>Letters · four forms · in words</span>"
             "<span class='fa'>حروف در جایگاه‌های گوناگون</span></h2><div class='grid'>")
    for ch, name, dual, words in LETTERS:
        cells = [(ch, "isolated"), (ch + ZWJ if dual else None, "initial"),
                 (ZWJ + ch + ZWJ if dual else None, "medial"), (ZWJ + ch, "final")]
        f = "".join(f"<div class='{'na' if t is None else ''}'>{esc(t) if t else '–'}<span>{lab}</span></div>" for t, lab in cells)
        wd = "".join(f"<div>{esc(x)}<span>{lab}</span></div>" for x, lab in zip(words, ("start", "middle", "end")))
        H.append(f"<div class='card'><div class='top'><span>{name}</span><span class='big'>{ch}</span></div>"
                 f"<div class='forms'>{f}</div><div class='words'>{wd}</div></div>")
    H.append("</div>")

    H.append("<h2><span>Additional letters · ligatures · marks</span><span class='fa'>حروف دیگر و نشانه‌ها</span></h2>")
    H.append(f"<div class='panel'><div class='lab'>Arabic and hamza forms</div><div class='row fa'>{esc(EXTRA)}</div></div>")
    H.append("<div class='panel'><div class='lab'>Lam-alef · the emblem's square kaf before ا and ل</div>"
             "<div class='row fa'>لا لآ لأ لإ &nbsp; کا گا کل گل &nbsp; سلام کلاس نگاه گلستان</div></div>")
    H.append("<div class='panel'><div class='lab'>Harakat</div><div class='row fa'>بَ  بِ  بُ  بً  بٍ  بٌ  بّ  بْ  &nbsp; حَتْماً  مُدَرِّس  کِتابِ دانِشْگاه</div></div>")

    H.append("<h2><span>Numerals &amp; punctuation</span><span class='fa'>رقم‌ها و علامت‌ها</span></h2>")
    H.append("<div class='panel'><div class='lab'>Persian digits</div><div class='row fa'>۰ ۱ ۲ ۳ ۴ ۵ ۶ ۷ ۸ ۹ &nbsp; ۱۳۱۳ &nbsp; ۱۴۰۵</div></div>")
    H.append("<div class='panel'><div class='lab'>Arabic-Indic &amp; Latin digits</div><div class='row fa' style='font-size:50px'>٠ ١ ٢ ٣ ٤ ٥ ٦ ٧ ٨ ٩ &nbsp; 0 1 2 3 4 5 6 7 8 9</div></div>")
    H.append("<div class='panel'><div class='lab'>Punctuation</div><div class='row fa'>، ؛ ؟ ! . : « » ( ) [ ] - – — ٪ ٫ ٬ * / + =</div></div>")

    H.append("<h2><span>Sizes</span><span class='fa'>اندازه‌ها</span></h2><div class='panel wf'>")
    for px in (96, 72, 54, 40, 30, 22, 16, 12):
        H.append(f"<div><span class='lab'>{px} px</span><div class='fa R' style='font-size:{px}px'>چگونه پژوهشگران ظرافت طبیعت را در عکس‌ها و یادداشت‌هایشان ثبت کردند</div></div>")
    H.append("</div>")

    H.append("<h2><span>Headlines</span><span class='fa'>تیترها</span></h2><div class='panel heads'>")
    for w, t in (("Bold", "دانشگاه تهران"), ("Regular", "باغ‌های سبز ایران"), ("Light", "شب‌های پرستاره")):
        H.append(f"<div><span class='lab'>{w}</span><div class='fa {w[0]}'>{esc(t)}</div></div>")
    H.append("</div>")

    H.append("<h2><span>Text · 24 px</span><span class='fa'>متن</span></h2><div class='cols'>")
    for w, t in zip(WEIGHTS, TEXTS):
        H.append(f"<div class='panel'><div class='lab'>{w}</div><p class='fa para {w[0]}'>{esc(t)}</p></div>")
    H.append("</div>")

    H.append("<footer><span>Daneshgah v1.000 · Light 300 · Regular 400 · Bold 700 · MIT License</span>"
             "<span>Glyphs: Persian &amp; Arabic letters with all contextual forms, lam-alef, square kaf ligatures, harakat, three digit sets, punctuation</span></footer>")
    H.append("</div></body></html>")
    open(out, "w", encoding="utf-8").write("\n".join(H))
    print("wrote", out)


# ------------------------------------------------------------------ PNG of the specimen page
def find_browser():
    for p in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
              "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
              r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"):
        if os.path.exists(p):
            return p
    for n in ("google-chrome", "chromium", "chromium-browser", "microsoft-edge"):
        if shutil.which(n):
            return shutil.which(n)
    return None


def specimen_png(html_path, out, width=1355):
    """Full-page screenshot of the specimen, the empty page bottom trimmed."""
    from PIL import Image
    browser = find_browser()
    if not browser:
        print("no Edge / Chrome found: skipped", out)
        return
    work = tempfile.mkdtemp()
    tmp = os.path.join(work, "shot.png")
    url = "file:///" + os.path.abspath(html_path).replace("\\", "/")
    subprocess.run([browser, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                    f"--user-data-dir={os.path.join(work, 'profile')}", f"--window-size={width},12000",
                    "--virtual-time-budget=8000", f"--screenshot={tmp}", url],
                   capture_output=True, timeout=180)
    for _ in range(120):                   # Edge hands the work to a background process: wait for it
        if os.path.exists(tmp) and os.path.getsize(tmp) > 0:
            time.sleep(1)
            break
        time.sleep(0.5)
    im = Image.open(tmp).convert("RGB")
    bg = im.getpixel((2, im.height - 2))
    px = im.load()
    y = im.height - 1
    while y > 0 and all(px[x, y] == bg for x in range(0, im.width, 4)):
        y -= 1
    im.crop((0, 0, im.width, min(im.height, y + 40))).save(out, optimize=True)
    print("wrote", out)


# ------------------------------------------------------------------ font vs emblem
class Shaped:
    """The shaped text as polygons, one list of contours per glyph (font units, baseline at 0,
    left end of the advance at 0)."""

    def __init__(self, fontpath, text):
        import uharfbuzz as hb
        from fontTools.ttLib import TTFont
        from fontTools.pens.recordingPen import DecomposingRecordingPen
        tt = TTFont(fontpath)
        gs, order = tt.getGlyphSet(), tt.getGlyphOrder()
        font = hb.Font(hb.Face(hb.Blob.from_file_path(fontpath)))
        buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties(); buf.direction = "rtl"
        hb.shape(font, buf, {})
        self.glyphs, x = [], 0
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            pen = DecomposingRecordingPen(gs)
            gs[order[info.codepoint]].draw(pen)
            cur, contours = [], []
            for op, args in pen.value:
                if op == "moveTo":
                    cur = [args[0]]
                elif op in ("lineTo", "qCurveTo", "curveTo"):
                    cur += list(args)          # the outlines are straight lines; curves are finely segmented
                elif op in ("closePath", "endPath") and cur:
                    contours.append([(x + pos.x_offset + px, pos.y_offset + py) for px, py in cur])
                    cur = []
            self.glyphs.append(contours)
            x += pos.x_advance
        xs = [p[0] for g in self.glyphs for c in g for p in c]
        self.lo, self.hi = min(xs), max(xs)

    def mask(self, size, x0, base, sc, ss=4):
        """Filled mask, supersampled ss times, (x0, base) = where font x = 0, y = 0 lands. Each
        glyph is filled even-odd on its own (its counters stay open), then the glyphs are
        combined: joined letters overlap, and the overlap must stay ink."""
        from PIL import Image, ImageDraw, ImageChops
        W, H = size[0] * ss, size[1] * ss
        m = Image.new("1", (W, H), 0)
        for contours in self.glyphs:
            g = Image.new("1", (W, H), 0)
            for c in contours:
                t = Image.new("1", (W, H), 0)
                ImageDraw.Draw(t).polygon([((x0 + x * sc) * ss, (base - y * sc) * ss) for x, y in c], fill=1)
                g = ImageChops.logical_xor(g, t)
            m = ImageChops.logical_or(m, g)
        return m.convert("L").resize(size, Image.LANCZOS)


def clean_emblem(emb):
    """Clear everything in the crop that is not «دانشگاه»: the pieces of «تهران» that reach
    down into it and the ring of the emblem (the dark shapes touching the crop's border)."""
    from PIL import Image, ImageDraw, ImageFilter
    W, H = emb.size
    bg = sorted(emb.tobytes())[int(W * H * 0.9)]          # the light ground
    mark = emb.point(lambda v: 255 if v < 150 else 0)     # dark = ink
    for x in range(0, W, 2):
        for y in (0, H - 1):
            if mark.getpixel((x, y)) == 255:
                ImageDraw.floodfill(mark, (x, y), 128)
    for y in range(0, H, 2):
        for x in (0, W - 1):
            if mark.getpixel((x, y)) == 255:
                ImageDraw.floodfill(mark, (x, y), 128)
    gone = mark.point(lambda v: 255 if v == 128 else 0).filter(ImageFilter.MaxFilter(9))
    emb = Image.composite(Image.new("L", emb.size, bg), emb, gone)
    return emb.point(lambda v: bg if v > 185 else v)      # faint ornament lines of the emblem


def font_vs_emblem(fontdir, emblem_jpg, out, k=6):
    """Three rows at one scale (1 emblem stroke = 9 px = 100 units): the emblem's «دانشگاه»,
    Daneshgah Bold, and the Bold outline laid over the emblem. Same baseline; the font is
    centred on the emblem's lettering."""
    from PIL import Image, ImageOps, ImageChops, ImageFilter
    box = (170, 206, 378, 290)                 # «دانشگاه» in the emblem (px)
    base_y = 279.5                             # emblem baseline (bottom of the joining bar)
    ink = (189, 359)                           # left edge of its ه, right edge of its د
    W, H = (box[2] - box[0]) * k, (box[3] - box[1]) * k
    crop = Image.open(emblem_jpg).convert("L").crop(box).resize((W, H), Image.LANCZOS)
    emb = ImageOps.autocontrast(ImageOps.invert(crop), cutoff=1)          # dark letters on light
    emb = clean_emblem(emb)
    emb = Image.eval(emb, lambda v: int(70 + v * (255 - 70) / 255))       # soft grey, as a print
    sc = 0.09 * k
    sh = Shaped(os.path.join(fontdir, "Daneshgah-Bold.ttf"), "دانشگاه")
    mid = ((ink[0] + ink[1]) / 2 - box[0]) * k
    x0 = mid - (sh.lo + sh.hi) / 2 * sc
    base = (base_y - box[1]) * k
    m = sh.mask((W, H), x0, base, sc)
    font_row = ImageOps.invert(m).convert("RGB")
    edge = ImageChops.subtract(m, m.filter(ImageFilter.MinFilter(7)))     # the outline, ~3 px wide
    over = Image.composite(Image.new("RGB", (W, H), (214, 40, 40)), Image.merge("RGB", [emb] * 3), edge)
    gap = 10
    sheet = Image.new("RGB", (W, 3 * H + 2 * gap), (255, 255, 255))
    sheet.paste(Image.merge("RGB", [emb] * 3), (0, 0))
    sheet.paste(font_row, (0, H + gap))
    sheet.paste(over, (0, 2 * (H + gap)))
    sheet.save(out, optimize=True)
    print("wrote", out)


def main(fontdir, outdir):
    emblem = os.path.join(outdir, "original-emblem.jpg")
    fve = os.path.join(outdir, "font-vs-emblem.png")
    font_vs_emblem(fontdir, emblem, fve)
    page = os.path.join(outdir, "Daneshgah-specimen.html")
    specimen_html(fontdir, page, fve)
    specimen_png(page, os.path.join(outdir, "Daneshgah-specimen.png"))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "../fonts", sys.argv[2] if len(sys.argv) > 2 else "..")
