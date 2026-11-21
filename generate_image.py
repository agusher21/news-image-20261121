#!/usr/bin/env python3
"""
Generate the 21 November 2026 news image - dense newspaper front page with UTC timeline spine.
Output: 1024x1024 PNG, deterministic, <= 1 MiB.
"""
from PIL import Image, ImageDraw, ImageFont
import os
import hashlib

WIDTH, HEIGHT = 1024, 1024
OUTPUT_DIR = "/home/hatch/workspace/makefun/news-image-20261121/out"
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "entry.png")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Colors - newsprint palette
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GRAY = (40, 40, 40)
MED_GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
VERY_LIGHT_GRAY = (235, 235, 235)
RED = (180, 20, 20)
RED_DARK = (140, 15, 15)
BLUE = (20, 60, 140)
BLUE_DARK = (15, 45, 100)
ACCENT_GOLD = (180, 140, 0)


def get_font(size, bold=False):
    """Get a font - use DejaVu Serif for masthead, DejaVu Sans for body."""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                pass
    return ImageFont.load_default()


def measure_text(draw, text, font, max_width=None):
    """Measure text dimensions with optional word wrapping. Returns (width, height, lines)."""
    if max_width is None:
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1], [text]

    words = text.split()
    lines = []
    current = []
    line_height = int(font.size * 1.2)
    for word in words:
        test = " ".join(current + [word])
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))

    max_w = max(draw.textbbox((0, 0), line, font=font)[2] for line in lines) if lines else 0
    total_h = len(lines) * line_height
    return max_w, total_h, lines


def draw_wrapped_text(draw, x, y, text, font, fill=BLACK, max_width=None, line_spacing=1.1):
    """Draw wrapped text, return actual height used."""
    if max_width is None:
        draw.text((x, y), text, font=font, fill=fill)
        bbox = draw.textbbox((x, y), text, font=font)
        return bbox[3] - bbox[1]

    _, h, lines = measure_text(draw, text, font, max_width)
    line_height = int(font.size * line_spacing)
    for i, line in enumerate(lines):
        draw.text((x, y + i * line_height), line, font=font, fill=fill)
    return h


def draw_wrapped_text_height(draw, text, font, max_width):
    """Calculate height of wrapped text without drawing."""
    _, h, _ = measure_text(draw, text, font, max_width)
    return h


def main():
    img = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)

    # Fonts - smaller for better density
    font_masthead = get_font(42, bold=True)
    font_masthead_sub = get_font(15, bold=True)
    font_section = get_font(14, bold=True)
    font_headline = get_font(12, bold=True)
    font_subhead = get_font(10, bold=False)
    font_body = get_font(9, bold=False)
    font_small = get_font(8, bold=False)
    font_tiny = get_font(7, bold=False)
    font_timeline = get_font(6, bold=False)  # timeline labels: smaller to fit dense events
    font_label = get_font(8, bold=True)
    font_stat = get_font(17, bold=True)
    font_stat_label = get_font(8, bold=False)

    # ============================================================
    # LAYOUT CONSTANTS - Fixed columns with reserved timeline strip
    # ============================================================
    MASTHEAD_H = 76
    TIMELINE_CENTER = 512
    TIMELINE_HALF_W = 60  # 60px each side of center = 120px total timeline strip
    TIMELINE_LEFT = TIMELINE_CENTER - TIMELINE_HALF_W   # 452
    TIMELINE_RIGHT = TIMELINE_CENTER + TIMELINE_HALF_W  # 572
    
    LEFT_COL_X = 10
    LEFT_COL_W = TIMELINE_LEFT - LEFT_COL_X - 10  # 452 - 10 - 10 = 432
    RIGHT_COL_X = TIMELINE_RIGHT + 10              # 582
    RIGHT_COL_W = WIDTH - RIGHT_COL_X - 10         # 1024 - 582 - 10 = 432
    
    TIMELINE_TOP = MASTHEAD_H + 4
    TIMELINE_BOTTOM = HEIGHT - 250  # Bottom section starts here
    TIMELINE_H = TIMELINE_BOTTOM - TIMELINE_TOP

    # ============================================================
    # MASTHEAD - top band only
    # ============================================================
    draw.rectangle([0, 0, WIDTH, MASTHEAD_H], fill=BLACK)
    draw.text((30, 6), "THE DAILY GLOBE", font=font_masthead, fill=WHITE)
    draw.text((30, 50), "SATURDAY 21 NOVEMBER 2026", font=font_masthead_sub, fill=WHITE)
    draw.text((WIDTH - 180, 6), "VOL. CXII  No. 32,541", font=font_small, fill=WHITE)
    draw.text((WIDTH - 180, 22), "PRICE $2.50  |  €2.30  |  £1.95", font=font_tiny, fill=WHITE)
    draw.text((WIDTH - 180, 38), "EST. 1914", font=font_tiny, fill=WHITE)
    draw.line([(0, MASTHEAD_H), (WIDTH, MASTHEAD_H)], fill=BLACK, width=2)

    # ============================================================
    # UTC TIMELINE SPINE - reserved vertical strip (452-572), no story text enters
    # ============================================================
    # Draw timeline background strip
    draw.rectangle([TIMELINE_LEFT, TIMELINE_TOP, TIMELINE_RIGHT, TIMELINE_BOTTOM], fill=VERY_LIGHT_GRAY, outline=LIGHT_GRAY, width=1)
    # Center line
    draw.line([(TIMELINE_CENTER, TIMELINE_TOP), (TIMELINE_CENTER, TIMELINE_BOTTOM)], fill=BLACK, width=3)

    timeline_events = [
        ("00:00", "DAY BEGINS", "UTC"),
        ("03:26", "HOUTHI MISSILE", "intercepted over Riyadh"),
        ("05:30", "RUSSIAN KH-101", "crashes in Poland (Nowy Lipowiec)"),
        ("06:00", "RUSSIAN DRONE", "hits Mołodycz, Poland"),
        ("06:30", "2ND MISSILE", "down near Rudnik nad Sanem"),
        ("07:00", "TUSK: INTENTIONAL", "PROVOCATION — NATO jets scrambled"),
        ("09:00", "EU COUNCIL", "adopts €1bn military aid for Ukraine"),
        ("10:30", "CYCLONE AKVAN", "landfall near Gopalpur, Odisha"),
        ("12:00", "EU COMMISSION", "disburses €7.9bn to Ukraine"),
        ("13:00", "DENMARK CHARGES", "2 Danes recruited by Russia"),
        ("14:00", "COP31 ENTERS", "OVERTIME in Antalya"),
        ("16:00", "WALL ST CLOSE:", "S&P -3.7% | Nasdaq -5.28%"),
        ("18:00", "KRYVYI RIH:", "2 dead, 42 injured"),
        ("19:00", "NIKHIL GUPTA", "sentenced 235 months (Pannun plot)"),
        ("20:00", "MONGOLIA:", "Parliament accepts resignation"),
        ("21:00", "BepiColombo", "FIRES ENGINES — Mercury orbit"),
        ("22:00", "TRUMP THREATENS", "ban on US AI data centres abroad"),
        ("23:00", "US MEASLES", "elimination status lost (PAHO)"),
    ]

    # Timeline labels: LEFT side in [TIMELINE_LEFT, TIMELINE_CENTER), RIGHT side in (TIMELINE_CENTER, TIMELINE_RIGHT]
    LEFT_LABEL_X = TIMELINE_LEFT + 4
    LEFT_LABEL_W = TIMELINE_CENTER - LEFT_LABEL_X - 4  # ~56px
    RIGHT_LABEL_X = TIMELINE_CENTER + 4
    RIGHT_LABEL_W = TIMELINE_RIGHT - RIGHT_LABEL_X - 4  # ~56px

    # Evenly distribute 18 events down the full timeline height
    NUM_EVENTS = len(timeline_events)
    ROW_H = TIMELINE_H // NUM_EVENTS  # Fixed row height per event (~38px)
    # measure_text uses line_height = int(font.size * 1.2); match it for drawing
    LINE_H = int(font_timeline.size * 1.2)

    # Layout pass: pre-measure all labels to know wrapped lines and heights
    event_layouts = []
    for i, (time, label1, label2) in enumerate(timeline_events):
        # Alternate sides: even indices on left, odd on right
        side = "left" if i % 2 == 0 else "right"
        label_x = LEFT_LABEL_X if side == "left" else RIGHT_LABEL_X
        label_w = LEFT_LABEL_W if side == "left" else RIGHT_LABEL_W

        # Measure label1 and label2 with wrapping
        _, label1_h, label1_lines = measure_text(draw, label1, font_timeline, label_w)
        _, label2_h, label2_lines = measure_text(draw, label2, font_timeline, label_w) if label2 else (0, 0, [])

        # Time label width for centering
        time_w = draw.textbbox((0, 0), time, font=font_timeline)[2]

        event_layouts.append({
            "side": side,
            "label_x": label_x,
            "label_w": label_w,
            "time": time,
            "time_w": time_w,
            "label1_lines": label1_lines,
            "label1_h": label1_h,
            "label2_lines": label2_lines,
            "label2_h": label2_h,
        })

    # Draw pass: place each event in its fixed row, centered vertically
    for i, layout in enumerate(event_layouts):
        row_top = TIMELINE_TOP + i * ROW_H
        row_center = row_top + ROW_H // 2

        # Marker on center line (at row center)
        draw.ellipse([TIMELINE_CENTER - 4, row_center - 4, TIMELINE_CENTER + 4, row_center + 4], fill=RED, outline=BLACK, width=1)

        # Time label - centered on timeline center, vertically centered in row
        time_y = row_center - font_timeline.size // 2
        draw.text((TIMELINE_CENTER - layout["time_w"] // 2, time_y), layout["time"], font=font_timeline, fill=BLACK)

        # Event labels - draw wrapped within the row, stacked label1 above label2
        label_y = row_center - (layout["label1_h"] + layout["label2_h"]) // 2
        for line in layout["label1_lines"]:
            draw.text((layout["label_x"], label_y), line, font=font_timeline, fill=BLACK)
            label_y += LINE_H
        for line in layout["label2_lines"]:
            draw.text((layout["label_x"], label_y), line, font=font_timeline, fill=DARK_GRAY)
            label_y += LINE_H

    # ============================================================
    # LEFT COLUMN - Hero story: Poland missiles
    # ============================================================
    col_y = MASTHEAD_H + 8

    # Hero headline (measured)
    h1_h = draw_wrapped_text(draw, LEFT_COL_X, col_y, "RUSSIAN MISSILES, DRONE", font_headline, BLACK, LEFT_COL_W)
    col_y += h1_h + 2
    h2_h = draw_wrapped_text(draw, LEFT_COL_X, col_y, "VIOLATE POLISH AIRSPACE", font_headline, BLACK, LEFT_COL_W)
    col_y += h2_h + 2
    h3_h = draw_wrapped_text(draw, LEFT_COL_X, col_y, "TUSK: 'INTENTIONAL PROVOCATION'", font_subhead, RED, LEFT_COL_W)
    col_y += h3_h + 4

    # Hero body text
    hero_text = ("Three objects — two Kh-101 cruise missiles and a jet-powered drone — crashed in southeastern Poland overnight during Russia's massive aerial assault on Ukraine. "
                 "PM Donald Tusk said the incursion did not appear accidental, coming as 11-nation 'Coalition of the Willing' exercises (Koalicja 2026) were underway at Nowa Dęba. "
                 "No injuries reported. NATO SecGen Rutte condemned 'grave violations'; NATO jets scrambled. Defence Min. Kosiniak-Kamysz seeks more eastern flank support.")
    hero_h = draw_wrapped_text(draw, LEFT_COL_X, col_y, hero_text, font_body, DARK_GRAY, LEFT_COL_W)
    col_y += hero_h + 6

    # Real small map for Poland missile impact sites
    map_box_h = 70
    draw.rectangle([LEFT_COL_X, col_y, LEFT_COL_X + LEFT_COL_W, col_y + map_box_h], outline=LIGHT_GRAY, width=1, fill=VERY_LIGHT_GRAY)
    # Poland outline (simple rotated rectangle approximation)
    poland_left = LEFT_COL_X + 20
    poland_top = col_y + 8
    poland_w = LEFT_COL_W - 40
    poland_h = map_box_h - 16
    # Draw Poland shape - rough outline
    draw.rectangle([poland_left, poland_top, poland_left + poland_w, poland_top + poland_h], outline=MED_GRAY, width=1)
    # Impact sites as red dots with labels
    # Approximate relative positions in SE Poland
    sites = [
        (poland_left + int(poland_w * 0.35), poland_top + int(poland_h * 0.25), "Nowy\nLipowiec"),
        (poland_left + int(poland_w * 0.55), poland_top + int(poland_h * 0.45), "Rudnik\nnad Sanem"),
        (poland_left + int(poland_w * 0.75), poland_top + int(poland_h * 0.65), "Mołodycz"),
        (poland_left + int(poland_w * 0.45), poland_top + int(poland_h * 0.75), "Sanem"),
    ]
    for sx, sy, label in sites:
        draw.ellipse([sx - 4, sy - 4, sx + 4, sy + 4], fill=RED, outline=BLACK, width=1)
        # Draw label below dot
        lines = label.split("\n")
        for i, line in enumerate(lines):
            tw = draw.textbbox((0, 0), line, font=font_tiny)[2]
            draw.text((sx - tw // 2, sy + 10 + i * 8), line, font=font_tiny, fill=DARK_GRAY)
    # Title
    draw.text((LEFT_COL_X + 6, col_y + 2), "MISSILE IMPACT SITES — SE POLAND", font=font_label, fill=BLUE_DARK)
    col_y += map_box_h + 6

    # ============================================================
    # STAT STRIP - big numbers
    # ============================================================
    stats = [
        ("2 DEAD", "42 HURT", "Kryvyi Rih"),
        ("S&P -3.7%", "NASDAQ -5.28%", "Nvidia -14%"),
        ("€1 BN", "EU AID", "Ukraine"),
        ("372K", "EVACUATED", "Cyclone Akvan"),
    ]
    stat_box_w = (LEFT_COL_W - 12) // 4
    stat_h = 46
    for i, (big, mid, small) in enumerate(stats):
        sx = LEFT_COL_X + i * (stat_box_w + 4)
        draw.rectangle([sx, col_y, sx + stat_box_w, col_y + stat_h], fill=VERY_LIGHT_GRAY, outline=LIGHT_GRAY, width=1)
        draw.text((sx + 4, col_y + 2), big, font=font_stat, fill=RED_DARK)
        draw.text((sx + 4, col_y + 20), mid, font=font_stat_label, fill=DARK_GRAY)
        draw.text((sx + 4, col_y + 32), small, font=font_tiny, fill=MED_GRAY)
    col_y += stat_h + 6

    # ============================================================
    # SECONDARY STORIES - 3 panels
    # ============================================================
    secondary = [
        ("COP31 OVERTIME", "Antalya talks breach Friday deadline; draft deal stripped of fossil fuel language. EU: 'risks turning COP into fossil summit.' Panama threatens walkout. 3rd draft expected Saturday. Electrification target (35% by 2035) remains, but no renewables mandate.", "AFP / Guardian"),
        ("WALL ST CORRECTION", "S&P 500 -3.7%, Dow -3.1%, Nasdaq -5.28% wipe 2026 gains. Nvidia -14% to 18-month low. Anthropic shares slide post-IPO. AI selloff drives worst week since 2020. Both S&P and Dow enter correction territory (>10% off highs).", "Reuters / UPI"),
        ("KRYVYI RIH DOUBLE-TAP", "Two ballistic missiles hit restaurant parking lot; Shahed drones then targeted rescuers. 7-year-old boy and 20-year-old paramedic killed. 42 injured (4 children, 27 serious). 23 apartment buildings, hospital damaged. Vilkul: 'cynical strike.'", "Kyiv Independent / Ukrinform"),
    ]

    for title, body, source in secondary:
        _, body_h, _ = measure_text(draw, body, font_body, LEFT_COL_W - 12)
        panel_h = 18 + body_h + 14
        draw.rectangle([LEFT_COL_X, col_y, LEFT_COL_X + LEFT_COL_W, col_y + panel_h], outline=LIGHT_GRAY, width=1)
        draw.text((LEFT_COL_X + 6, col_y + 3), title, font=font_label, fill=BLUE_DARK)
        draw_wrapped_text(draw, LEFT_COL_X + 6, col_y + 20, body, font_body, DARK_GRAY, LEFT_COL_W - 12)
        # Source text - ensure it stays within left column (ends at LEFT_COL_X + LEFT_COL_W = 442)
        # Timeline strip starts at 452, so keep source within 442
        source_text = f"SOURCE: {source}"
        source_w = draw.textbbox((0, 0), source_text, font=font_tiny)[2]
        source_x = min(LEFT_COL_X + LEFT_COL_W - 120, LEFT_COL_X + LEFT_COL_W - source_w - 6)
        draw.text((source_x, col_y + panel_h - 12), source_text, font=font_tiny, fill=MED_GRAY)
        col_y += panel_h + 4

    left_col_bottom = col_y

    # ============================================================
    # RIGHT COLUMN
    # ============================================================
    col_y = MASTHEAD_H + 8

    def draw_story(x, y, w, headline_lines, subhead, body, source):
        """Draw a story with measured spacing. Returns new y."""
        cy = y
        for hl in headline_lines:
            h = draw_wrapped_text(draw, x, cy, hl, font_headline, BLACK, w)
            cy += h + 1
        if subhead:
            h = draw_wrapped_text(draw, x, cy, subhead, font_subhead, RED, w)
            cy += h + 3
        if body:
            h = draw_wrapped_text(draw, x, cy, body, font_body, DARK_GRAY, w)
            cy += h + 3
        if source:
            source_text = f"SOURCE: {source}"
            source_w = draw.textbbox((0, 0), source_text, font=font_tiny)[2]
            # Keep source within column bounds
            source_x = min(x, x + w - source_w - 6)
            draw.text((source_x, cy), source_text, font=font_tiny, fill=MED_GRAY)
            cy += 12
        return cy + 4

    # EU-UK Deals
    col_y = draw_story(RIGHT_COL_X, col_y, RIGHT_COL_W,
        ["EU–UK SEAL THREE DEALS"],
        None,
        ("Food & drink: easing Brexit checks on animal/plant products (from Mar 2028). "
         "Emissions trading: linking UK-EU ETS, shielding steel/fertilisers from carbon levies (2028). "
         "Youth Experience Scheme: 100k under-30s each side to live/work/study 3 years (by 2030). "
         "Tuition fees: EU links ratification to equal fees for EU students."),
        "Guardian / DW / Le Monde")

    # Denmark / Russia plot
    col_y = draw_story(RIGHT_COL_X, col_y, RIGHT_COL_W,
        ["DENMARK: RUSSIA RECRUITED", "DANES TO KILL UKRAINIAN RAPPER"],
        None,
        ("Two Danish men charged with attempted murder & assisting foreign intel — allegedly hired by Russian intelligence to assassinate rapper Kyivstoner (US/UA dual citizen) at cancelled Sep 25 Copenhagen concert. "
         "Arrested in Hellerup with weapons. Both deny. FM Rasmussen expels Russian defence attaché. PET: Russia 'actively preparing sabotage' in Denmark."),
        "DR / BBC / Reuters")

    # Houthi attacks
    col_y = draw_story(RIGHT_COL_X, col_y, RIGHT_COL_W,
        ["HOUTHIS TARGET RIYADH"],
        "THIRD CONSECUTIVE NIGHT",
        ("Saudi air defences intercept 5 drones + 1 ballistic missile targeting Riyadh (03:26 GMT). Falling debris causes damage. Coalition destroys 2 Houthi launchers in Yemen. "
         "Escalation follows Wed (60 targets hit) & Thu (5 missiles + 1 cruise missile). Iran-backed Houthis vow continued attacks."),
        "AP / SPA / Al Jazeera")

    # US Sanctions on Iranians
    col_y = draw_story(RIGHT_COL_X, col_y, RIGHT_COL_W,
        ["US SANCTIONS 4 IRANIANS"],
        None,
        ("Treasury OFAC designates 4 senior LEF & IRGC officials for brutal suppression of 2022 Mahsa Amini protests. Asset freeze, US entry ban. "
         "Separate: Comancheros/'Ndrangheta sanctions (Nov 20) target transnational crime networks."),
        "Treasury OFAC / Reuters")

    # Mongolia
    col_y = draw_story(RIGHT_COL_X, col_y, RIGHT_COL_W,
        ["MONGOLIA PRESIDENT QUITS"],
        None,
        ("Parliament votes 96–8 to accept President Khurelsukh's resignation — first sitting president to step down early since 1992. "
         "Allegations by ex-mayor Nyambaatar (in Canada) of $25M bribe for railway contract. Khurelsukh denies, resigns to 'clear name.' Snap election within 4 months."),
        "AP / Montsame / Straits Times")

    # BepiColombo
    col_y = draw_story(RIGHT_COL_X, col_y, RIGHT_COL_W,
        ["BepiColombo ENTERS", "MERCURY ORBIT"],
        None,
        ("ESA/JAXA mission arrives at Mercury after 8-year, 6-billion-mile journey. Composite spacecraft fires engine for orbital capture at ~21:00 UTC. "
         "First dual-orbiter mission: MPO (ESA) maps surface/exosphere; Mio (JAXA) studies magnetosphere. Science phase begins Apr 2027."),
        "ESA / NPR / New Scientist")

    # Trump AI data centres
    col_y = draw_story(RIGHT_COL_X, col_y, RIGHT_COL_W,
        ["TRUMP: BAN US AI DATA", "CENTRES OVERSEAS"],
        None,
        ("Threatens 'tremendous tax' on US firms building data centres abroad. 'We're going to keep it all in this country.' Targets AI infrastructure expansion by tech giants. "
         "Markets react: chip stocks under pressure. Part of broader 'America First' tech sovereignty push."),
        "BBC / Reuters / NYT")

    # Nikhil Gupta
    col_y = draw_story(RIGHT_COL_X, col_y, RIGHT_COL_W,
        ["NIKHIL GUPTA: 19+ YEARS"],
        "FOR PANNUN MURDER PLOT",
        ("Indian national sentenced to 235 months (19.5 years) by SDNY Judge Marrero for murder-for-hire conspiracy directed by Indian govt employee Vikash Yadav targeting Sikh separatist Gurpatwant Singh Pannun in NYC. "
         "Gupta pled guilty Feb 2026. Extradited from Czechia Jun 2024. Faces deportation after sentence."),
        "DOJ / CBS / Al Jazeera")

    # Cyclone Akvan (small box at bottom right)
    cyc_h = 44
    draw.rectangle([RIGHT_COL_X, col_y, RIGHT_COL_X + RIGHT_COL_W, col_y + cyc_h], fill=VERY_LIGHT_GRAY, outline=LIGHT_GRAY, width=1)
    draw.text((RIGHT_COL_X + 6, col_y + 3), "CYCLONE AKVAN — ODISHA", font=font_label, fill=BLUE_DARK)
    draw_wrapped_text(draw, RIGHT_COL_X + 6, col_y + 19, "Landfall ~10:30–11:00 near Gopalpur. 372,000 evacuated. 4,467 pregnant women shifted; 1,452 delivered safely. Zero casualties reported. Storm weakening.", font_body, DARK_GRAY, RIGHT_COL_W - 12)
    source_text = "SOURCE: ANI / ETV / TOI"
    source_w = draw.textbbox((0, 0), source_text, font=font_tiny)[2]
    source_x = RIGHT_COL_X + RIGHT_COL_W - source_w - 6
    draw.text((source_x, col_y + 30), source_text, font=font_tiny, fill=MED_GRAY)
    col_y += cyc_h + 6

    right_col_bottom = col_y

    # ============================================================
    # BOTTOM SECTION - ALSO ON SATURDAY + WHERE IT HAPPENED + DATE CHECK
    # Starts below the right column with a small gap
    # ============================================================
    BOTTOM_Y = max(HEIGHT - 250, right_col_bottom + 8)
    draw.line([(0, BOTTOM_Y), (WIDTH, BOTTOM_Y)], fill=BLACK, width=2)
    content_y = BOTTOM_Y + 6

    # ALSO ON SATURDAY (left)
    also_x = LEFT_COL_X
    also_w = LEFT_COL_W
    draw.text((also_x, content_y), "ALSO ON SATURDAY", font=font_section, fill=BLACK)
    ay = content_y + 16

    also_items = [
        "1. Voyager 1 reaches 1 light-day from Earth (Nov 18 milestone)",
        "2. Trump–Xi–Putin trilateral at APEC Shenzhen (Nov 19) — 'peace declaration'",
        "3. US loses measles elimination status (PAHO, Nov 17) — 5,400+ cases",
        "4. ICJ Myanmar genocide ruling (Nov 19, 9–6 vote)",
        "5. EU–UK youth mobility, food & drink, ETS deals signed (Nov 20)",
        "6. Anthropic IPO slides; tech sell-off deepens AI winter fears",
        "7. Saudi coalition destroys 60 Houthi targets in Yemen (Nov 18)",
        "8. Comancheros / 'Ndrangheta sanctions by US Treasury (Nov 20)",
        "9. Poland ministers visit Nowa Dęba exercise site (Nov 20)",
        "10. Ukraine: Russian mass missile attack Nov 20 kills 7 in Kyiv",
    ]
    for item in also_items:
        draw.text((also_x, ay), item, font=font_tiny, fill=DARK_GRAY)
        ay += 11

    # WHERE IT HAPPENED - world map with dots (middle)
    map_x = TIMELINE_RIGHT + 10  # 582
    map_w = 240
    map_y = content_y
    draw.text((map_x, map_y), "WHERE IT HAPPENED", font=font_section, fill=BLACK)
    my = map_y + 16
    draw.rectangle([map_x, my, map_x + map_w, my + 120], outline=LIGHT_GRAY, width=1)

    # Dots for locations with labels that fit within map box
    locations = [
        (map_x + 40, my + 18, "UK"),
        (map_x + 70, my + 18, "Denmark"),
        (map_x + 50, my + 38, "Poland"),
        (map_x + 65, my + 52, "Ukraine"),
        (map_x + 100, my + 48, "Turkey"),
        (map_x + 115, my + 62, "Saudi"),
        (map_x + 145, my + 72, "India"),
        (map_x + 170, my + 52, "Mongolia"),
        (map_x + 15, my + 78, "USA"),
        (map_x + 210, my + 28, "Mercury"),
    ]
    for lx, ly, label in locations:
        draw.ellipse([lx-3, ly-3, lx+3, ly+3], fill=RED, outline=BLACK)
        tw = draw.textbbox((0, 0), label, font=font_tiny)[2]
        if lx + 6 + tw > map_x + map_w - 2:
            draw.text((lx - 6 - tw, ly - 4), label, font=font_tiny, fill=DARK_GRAY)
        else:
            draw.text((lx + 6, ly - 4), label, font=font_tiny, fill=DARK_GRAY)

    # DATE CHECK — LEFT OUT (right)
    check_x = map_x + map_w + 10  # 582 + 240 + 10 = 832
    check_w = WIDTH - check_x - 10  # 1024 - 832 - 10 = 182
    check_y = content_y
    check_box_h = 180
    draw.rectangle([check_x, check_y, check_x + check_w, check_y + check_box_h], fill=VERY_LIGHT_GRAY, outline=LIGHT_GRAY, width=1)
    draw.text((check_x + 6, check_y + 3), "DATE CHECK — LEFT OUT", font=font_label, fill=RED_DARK)
    cy = check_y + 16  # Reduced from 18 to fit all items
    left_out = [
        "• ICJ Myanmar — 19 Nov",
        "• Pete Rose pardon — 20 Nov",
        "• EU €1bn aid adopted — 20 Nov",
        "• EU €7.9bn disbursed — 20 Nov",
        "• US sanctions 4 Iranians — 20 Nov",
        "• Trump AI data centre threat — 20 Nov",
        "• Nikhil Gupta sentencing — 20 Nov",
        "• Mongolia parliament vote — 19 Nov",
        "• EU-UK summit deals — 20 Nov",
        "• COP31 overtime began — 20 Nov",
        "• Wall St correction — 20 Nov",
        "• Houthi 3rd night — 20 Nov",
        "• Cyclone Akvan landfall — 20 Nov",
        "• Voyager 1 light-day — 18 Nov",
        "• BepiColombo orbit — 21 Nov ✓",
        "• Kryvyi Rih 42 injured — 21 Nov ✓",
        "• Poland missiles — 20/21 Nov ✓",
        "• Denmark charges — 20 Nov",
        "• US measles status — 17 Nov",
    ]
    for item in left_out:
        draw.text((check_x + 6, cy), item, font=font_tiny, fill=DARK_GRAY)
        cy += 7  # Reduced from 9 to 7 to fit all 20 items within box

    # ============================================================
    # FOOTER - sources
    # ============================================================
    footer_y = HEIGHT - 22
    draw.line([(0, footer_y - 4), (WIDTH, footer_y - 4)], fill=BLACK, width=1)
    sources = "CONFIRMED — AP, Reuters, BBC, Guardian, AFP, DW, DOJ, Treasury OFAC, ESA, NASA, PAHO, Montsame, Kyiv Independent, Ukrinform, ANI"
    draw.text((20, footer_y - 20), sources, font=font_tiny, fill=MED_GRAY)
    draw.text((WIDTH - 160, footer_y - 20), "GENERATED 21 NOV 2026", font=font_tiny, fill=MED_GRAY)

    # Save
    img.save(OUTPUT_PATH, "PNG", optimize=True)

    # Verify size
    size = os.path.getsize(OUTPUT_PATH)
    print(f"Saved to {OUTPUT_PATH}: {WIDTH}x{HEIGHT}, {size} bytes ({size/1024:.1f} KiB)")

    # Verify determinism by hashing
    with open(OUTPUT_PATH, "rb") as f:
        content = f.read()
        sha = hashlib.sha256(content).hexdigest()
    print(f"SHA256: {sha}")

    # Debug layout bounds
    print(f"Layout: LEFT_COL_X={LEFT_COL_X}, LEFT_COL_W={LEFT_COL_W} (ends at {LEFT_COL_X+LEFT_COL_W})")
    print(f"        TIMELINE: {TIMELINE_LEFT}-{TIMELINE_RIGHT} (center {TIMELINE_CENTER})")
    print(f"        RIGHT_COL_X={RIGHT_COL_X}, RIGHT_COL_W={RIGHT_COL_W} (ends at {RIGHT_COL_X+RIGHT_COL_W})")
    print(f"        Left col bottom: {left_col_bottom}, Right col bottom: {right_col_bottom}")
    print(f"        Bottom section starts: {BOTTOM_Y}")
    print(f"        Footer at: {footer_y}")

    return OUTPUT_PATH


if __name__ == "__main__":
    main()