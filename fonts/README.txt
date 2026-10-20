Daneshgah (دانشگاه) — Persian display typeface · version 1.000
==============================================================

A geometric square-Kufic Persian face rebuilt from the lettering «دانشگاه تهران» of the
classic emblem of the University of Tehran: monoline strokes, a flat joining baseline,
square teeth and square dots.

Weights: Light (300), Regular (400), Bold (700). Bold matches the emblem's weight.

Free and open source under the MIT License (see ../LICENSE).
Copyright (c) 2026 Hatef Mohammad Ali (Kouzehchi).

Files
  Daneshgah-Light / -Regular / -Bold .ttf    install these on Windows, macOS, Linux
  Daneshgah-Light / -Regular / -Bold .otf    PostScript (CFF) version, for design apps
  Daneshgah-Light / -Regular / -Bold .woff2  for websites
  ../Daneshgah-specimen.html / .png          type specimen
  ../font-vs-emblem.png                      the emblem's lettering and the font at the same scale
  ../source/                                 Python sources that generate the fonts

Install
  Windows : right-click the .ttf files > Install (or "Install for all users")
  macOS   : double-click the .ttf file > Install Font
  Linux   : copy the .ttf files to ~/.local/share/fonts and run fc-cache -f
  Install either the .ttf or the .otf set, not both.
  In apps the family appears as "Daneshgah" (Regular plus Bold, so Ctrl+B switches between
  them) and "Daneshgah Light". Apps that understand typographic families group all three
  under "Daneshgah". The Persian family name is دانشگاه (نازک · معمولی · ضخیم).

Web use
  @font-face { font-family: "Daneshgah"; font-weight: 300; src: url(Daneshgah-Light.woff2) format("woff2"); }
  @font-face { font-family: "Daneshgah"; font-weight: 400; src: url(Daneshgah-Regular.woff2) format("woff2"); }
  @font-face { font-family: "Daneshgah"; font-weight: 700; src: url(Daneshgah-Bold.woff2) format("woff2"); }

Design notes
  Every measure comes from the emblem: its stroke (9 px) is 100 units. Bold has the emblem's
  stroke; Regular (80) and Light (60) thin the strokes inwards from the same outer lines, so
  all weights share one set of heights (units of 1000; Bold / Regular / Light where they differ)
     650              alef, lam and tah stems
     565 / 539 / 513  kaf and gaf arm; top of the dot over an initial tooth
     550              digits
     420 / 407 / 394  د ذ; the tall initial tooth (ب پ ت ث ن ی ئ); horn and loop of ع غ;
                      top of the dots of ش
     320              boxes ه ک ف ق م, loop of ص ض ط ظ, head of ج ح خ چ
     275              medial teeth, teeth of س ش, upturned tips of the tails
       0              baseline (joining line)
    −220 / −240 / −260  foot of ر ز ژ و, hanging box of م, lower storey of medial ه
    −320              bowl of ن ق ص ض س ش ی, tail of م
    −440              bowl of ج ح خ چ ع غ

  Teeth: the emblem's pitch, 100 tooth + 55 gap in Bold. Two teeth in a row (نش in «دانشگاه»)
  keep that pitch.
  Dots: square, the size of the stroke, one dot-gap apart and from the body, as in the emblem.
  The dots of ش sit on its two right-hand teeth, as in the emblem.
  Kaf: the emblem's square kaf (box + stem + arm) is used only before ا and ل, where the box's
  left wall is the alef / lam (کا گا کل گل). Elsewhere the kaf is a stem with the arm reaching
  right; where there is room the arm reaches over the end of the previous letter, as the
  emblem's گ reaches over ش.
  Joins: where the dots of two joined letters would come too close, the joining stroke between
  them grows longer (calt); the baseline is never broken. After ر ز ژ و ؤ the next letter tucks
  in over the foot (kern).
  The emblem's alef in «دا» floats slightly above the baseline; the font keeps it on the line.

Version history
  1.000  First public release.

Character set
  - Full Persian alphabet + Arabic ي ك ى ة ء أ إ آ ؤ ئ ۀ
  - Isolated / initial / medial / final forms (OpenType init, medi, fina)
  - Lam-alef ligatures لا لآ لأ لإ and the square kaf before alef and lam کا گا کل گل (rlig)
  - Longer joins between letters whose dots would crowd (calt)
  - Kerning after footed letters ر ز ژ و ؤ, between teeth, and for the reaching kaf arm (kern)
  - Harakat with mark positioning: ـَ ـِ ـُ ـً ـٍ ـٌ ـّ ـْ ـٰ
  - Persian digits ۰–۹, Arabic-Indic ٠–٩, Latin digits 0–9 (square style)
  - Persian punctuation ، ؛ ؟ « » ٪ ٫ ٬ and basic ASCII punctuation
  - ZWNJ (نیم‌فاصله) and ZWJ, kashida ـ
  - Arabic presentation-form code points for apps without text shaping
  Latin letters are not included; apps fall back to another font for them.

Rebuild from source
  pip install fonttools shapely brotli uharfbuzz pillow
  cd source
  python build.py ../fonts
  python specimen.py ../fonts ..
  build.py writes the fonts (and features-*.fea, the OpenType feature code, next to them).
  specimen.py writes Daneshgah-specimen.html / .png and font-vs-emblem.png; the specimen PNG
  needs Google Chrome or Microsoft Edge.

Daneshgah is an independent typeface inspired by the emblem's lettering. It is not
affiliated with or endorsed by the University of Tehran.
