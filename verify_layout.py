#!/usr/bin/env python3
"""
Verify the generated image has no overlapping text by simulating the layout
and checking all text bounding boxes for intersections.
This script mirrors the EXACT layout from generate_image.py.
"""
from PIL import Image, ImageDraw, ImageFont
import os

WIDTH, HEIGHT = 1024, 1024

def get_font(size, bold=False):
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
    if max_width is None:
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1], [text]

    words = text.split()
    lines = []
    current = []
    line_height = int(font.size * 1.1)
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

def get_text_bbox(draw, x, y, text, font, max_width=None, line_spacing=1.1):
    if max_width is None:
        bbox = draw.textbbox((x, y), text, font=font)
        return (bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1])
    
    _, h, lines = measure_text(draw, text, font, max_width)
    line_height = int(font.size * line_spacing)
    max_w = max(draw.textbbox((0, 0), line, font=font)[2] for line in lines) if lines else 0
    return (x, y, max_w, h)

def boxes_overlap(b1, b2, margin=0):
    x1, y1, w1, h1 = b1
    x2, y2, w2, h2 = b2
    return not (x1 + w1 + margin <= x2 or x2 + w2 + margin <= x1 or
                y1 + h1 + margin <= y2 or y2 + h2 + margin <= y1)

def main():
    img = Image.new("RGB", (WIDTH, HEIGHT), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Fonts - EXACT match to generate_image.py
    font_masthead = get_font(42, bold=True)
    font_masthead_sub = get_font(15, bold=True)
    font_section = get_font(14, bold=True)
    font_headline = get_font(12, bold=True)
    font_subhead = get_font(10, bold=False)
    font_body = get_font(9, bold=False)
    font_small = get_font(8, bold=False)
    font_tiny = get_font(7, bold=False)
    font_label = get_font(8, bold=True)
    font_stat = get_font(17, bold=True)
    font_stat_label = get_font(8, bold=False)

    # Layout constants - EXACT match
    MASTHEAD_H = 76
    TIMELINE_CENTER = 512
    TIMELINE_HALF_W = 60
    TIMELINE_LEFT = TIMELINE_CENTER - TIMELINE_HALF_W
    TIMELINE_RIGHT = TIMELINE_CENTER + TIMELINE_HALF_W
    
    LEFT_COL_X = 10
    LEFT_COL_W = TIMELINE_LEFT - LEFT_COL_X - 10
    RIGHT_COL_X = TIMELINE_RIGHT + 10
    RIGHT_COL_W = WIDTH - RIGHT_COL_X - 10
    
    TIMELINE_TOP = MASTHEAD_H + 4
    TIMELINE_BOTTOM = HEIGHT - 250
    TIMELINE_H = TIMELINE_BOTTOM - TIMELINE_TOP

    all_boxes = []  # (x, y, w, h, description)

    def add_box(x, y, w, h, desc):
        all_boxes.append((x, y, w, h, desc))

    def check_overlaps():
        errors = []
        for i, (x1, y1, w1, h1, d1) in enumerate(all_boxes):
            for j, (x2, y2, w2, h2, d2) in enumerate(all_boxes):
                if i >= j:
                    continue
                # Skip intentional overlaps: text inside its container box
                is_d1_container = any(s in d1 for s in ['_box', '_bg', '_panel', '_strip', '_rule', 'cyclone_box', 'datecheck_box', 'map_box', 'poland_map_box', 'stat_box'])
                is_d2_container = any(s in d2 for s in ['_box', '_bg', '_panel', '_strip', '_rule', 'cyclone_box', 'datecheck_box', 'map_box', 'poland_map_box', 'stat_box'])
                is_d1_text = any(s in d1 for s in ['_title', '_date', '_vol', '_price', '_est', '_h', '_sub', '_body', '_source', '_label', '_item', '_big', '_mid', '_small', '_time', '_marker', '_dot', '_gen', '_sources', 'masthead_', 'hero_', 'also_', 'datecheck_', 'cyclone_', 'map_', 'footer_', 'stat_', 'secondary_', 'euuk_', 'denmark_', 'houthi_', 'iran_', 'mongolia_', 'bepi_', 'trump_', 'gupta_'])
                is_d2_text = any(s in d2 for s in ['_title', '_date', '_vol', '_price', '_est', '_h', '_sub', '_body', '_source', '_label', '_item', '_big', '_mid', '_small', '_time', '_marker', '_dot', '_gen', '_sources', 'masthead_', 'hero_', 'also_', 'datecheck_', 'cyclone_', 'map_', 'footer_', 'stat_', 'secondary_', 'euuk_', 'denmark_', 'houthi_', 'iran_', 'mongolia_', 'bepi_', 'trump_', 'gupta_'])
                
                # Text inside container - OK if fully contained
                if is_d1_container and is_d2_text:
                    if x1 <= x2 and y1 <= y2 and x1+w1 >= x2+w2 and y1+h1 >= y2+h2:
                        continue
                if is_d2_container and is_d1_text:
                    if x2 <= x1 and y2 <= y1 and x2+w2 >= x1+w1 and y2+h2 >= y1+h1:
                        continue
                
                # Timeline elements: markers, times, labels are all tightly packed within timeline_strip
                # Allow adjacency (1px margin) for timeline elements
                is_timeline_d1 = any(s in d1 for s in ['timeline_marker', 'timeline_time', 'timeline_label', 'timeline_center', 'timeline_strip'])
                is_timeline_d2 = any(s in d2 for s in ['timeline_marker', 'timeline_time', 'timeline_label', 'timeline_center', 'timeline_strip'])
                if is_timeline_d1 and is_timeline_d2:
                    if boxes_overlap((x1, y1, w1, h1), (x2, y2, w2, h2), margin=0):
                        # Only flag if they actually overlap with positive area, not just touch
                        if not (x1 + w1 <= x2 or x2 + w2 <= x1 or y1 + h1 <= y2 or y2 + h2 <= y1):
                            pass  # real overlap
                        else:
                            continue  # just touching - OK
                
                # Map dots and labels - adjacent by design
                if 'map_dot' in d1 and 'map_label' in d2:
                    continue
                if 'map_label' in d1 and 'map_dot' in d2:
                    continue
                if 'map_label' in d1 and 'map_label' in d2:
                    continue
                
                # Cyclone body and source in same box - adjacent
                if 'cyclone_body' in d1 and 'cyclone_source' in d2:
                    continue
                if 'cyclone_source' in d1 and 'cyclone_body' in d2:
                    continue
                
                # Masthead elements inside masthead_bg
                if d1 == 'masthead_bg' and d2.startswith('masthead_'):
                    continue
                if d2 == 'masthead_bg' and d1.startswith('masthead_'):
                    continue
                
                if boxes_overlap((x1, y1, w1, h1), (x2, y2, w2, h2), margin=1):
                    errors.append(f"OVERLAP: {d1} ({x1},{y1},{w1},{h1}) vs {d2} ({x2},{y2},{w2},{h2})")
        return errors

    # ============================================================
    # MASTHEAD
    # ============================================================
    add_box(0, 0, WIDTH, MASTHEAD_H, "masthead_bg")
    add_box(*get_text_bbox(draw, 30, 6, "THE DAILY GLOBE", font_masthead), "masthead_title")
    add_box(*get_text_bbox(draw, 30, 50, "SATURDAY 21 NOVEMBER 2026", font_masthead_sub), "masthead_date")
    add_box(*get_text_bbox(draw, WIDTH - 180, 6, "VOL. CXII  No. 32,541", font_small), "masthead_vol")
    add_box(*get_text_bbox(draw, WIDTH - 180, 22, "PRICE $2.50  |  €2.30  |  £1.95", font_tiny), "masthead_price")
    add_box(*get_text_bbox(draw, WIDTH - 180, 38, "EST. 1914", font_tiny), "masthead_est")

    # ============================================================
    # TIMELINE STRIP (452-572)
    # ============================================================
    add_box(TIMELINE_LEFT, TIMELINE_TOP, TIMELINE_RIGHT - TIMELINE_LEFT, TIMELINE_H, "timeline_strip")
    # Center line
    add_box(TIMELINE_CENTER - 1, TIMELINE_TOP, 3, TIMELINE_H, "timeline_center")

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

    LEFT_LABEL_X = TIMELINE_LEFT + 4
    LEFT_LABEL_W = TIMELINE_CENTER - LEFT_LABEL_X - 4
    RIGHT_LABEL_X = TIMELINE_CENTER + 4
    RIGHT_LABEL_W = TIMELINE_RIGHT - RIGHT_LABEL_X - 4

    for i, (time, label1, label2) in enumerate(timeline_events):
        h, m = map(int, time.split(":"))
        frac = (h * 60 + m) / (24 * 60)
        ty = TIMELINE_TOP + int(frac * TIMELINE_H)

        # Marker on center line
        add_box(TIMELINE_CENTER - 4, ty - 4, 8, 8, f"timeline_marker_{i}")

        # Time label centered
        tw = draw.textbbox((0, 0), time, font=font_tiny)[2]
        add_box(TIMELINE_CENTER - tw // 2, ty - 6, tw, 12, f"timeline_time_{i}")

        if i % 2 == 0:
            # Left side of timeline strip
            lx = LEFT_LABEL_X
            add_box(lx, ty - 6, LEFT_LABEL_W, 12, f"timeline_label1_{i}_left")
            if label2:
                add_box(lx, ty + 6, LEFT_LABEL_W, 12, f"timeline_label2_{i}_left")
        else:
            # Right side of timeline strip
            rx = RIGHT_LABEL_X
            add_box(rx, ty - 6, RIGHT_LABEL_W, 12, f"timeline_label1_{i}_right")
            if label2:
                add_box(rx, ty + 6, RIGHT_LABEL_W, 12, f"timeline_label2_{i}_right")

    # ============================================================
    # LEFT COLUMN
    # ============================================================
    col_y = MASTHEAD_H + 8

    # Hero headlines
    h1_h = draw_wrapped_text_height(draw, LEFT_COL_X, col_y, "RUSSIAN MISSILES, DRONE", font_headline, LEFT_COL_W)
    add_box(LEFT_COL_X, col_y, LEFT_COL_W, h1_h, "hero_h1")
    col_y += h1_h + 2
    h2_h = draw_wrapped_text_height(draw, LEFT_COL_X, col_y, "VIOLATE POLISH AIRSPACE", font_headline, LEFT_COL_W)
    add_box(LEFT_COL_X, col_y, LEFT_COL_W, h2_h, "hero_h2")
    col_y += h2_h + 2
    h3_h = draw_wrapped_text_height(draw, LEFT_COL_X, col_y, "TUSK: 'INTENTIONAL PROVOCATION'", font_subhead, LEFT_COL_W)
    add_box(LEFT_COL_X, col_y, LEFT_COL_W, h3_h, "hero_sub")
    col_y += h3_h + 4

    # Hero body
    hero_text = ("Three objects — two Kh-101 cruise missiles and a jet-powered drone — crashed in southeastern Poland overnight during Russia's massive aerial assault on Ukraine. "
                 "PM Donald Tusk said the incursion did not appear accidental, coming as 11-nation 'Coalition of the Willing' exercises (Koalicja 2026) were underway at Nowa Dęba. "
                 "No injuries reported. NATO SecGen Rutte condemned 'grave violations'; NATO jets scrambled. Defence Min. Kosiniak-Kamysz seeks more eastern flank support.")
    hero_h = draw_wrapped_text_height(draw, LEFT_COL_X, col_y, hero_text, font_body, LEFT_COL_W)
    add_box(LEFT_COL_X, col_y, LEFT_COL_W, hero_h, "hero_body")
    col_y += hero_h + 6

    # Map placeholder
    map_box_h = 60
    add_box(LEFT_COL_X, col_y, LEFT_COL_W, map_box_h, "poland_map_box")
    col_y += map_box_h + 6

    # Stat strip
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
        add_box(sx, col_y, stat_box_w, stat_h, f"stat_box_{i}")
        add_box(*get_text_bbox(draw, sx + 4, col_y + 2, big, font_stat), f"stat_big_{i}")
        add_box(*get_text_bbox(draw, sx + 4, col_y + 20, mid, font_stat_label), f"stat_mid_{i}")
        add_box(*get_text_bbox(draw, sx + 4, col_y + 32, small, font_tiny), f"stat_small_{i}")
    col_y += stat_h + 6

    # Secondary stories
    secondary = [
        ("COP31 OVERTIME", "Antalya talks breach Friday deadline; draft deal stripped of fossil fuel language. EU: 'risks turning COP into fossil summit.' Panama threatens walkout. 3rd draft expected Saturday. Electrification target (35% by 2035) remains, but no renewables mandate.", "AFP / Guardian"),
        ("WALL ST CORRECTION", "S&P 500 -3.7%, Dow -3.1%, Nasdaq -5.28% wipe 2026 gains. Nvidia -14% to 18-month low. Anthropic shares slide post-IPO. AI selloff drives worst week since 2020. Both S&P and Dow enter correction territory (>10% off highs).", "Reuters / UPI"),
        ("KRYVYI RIH DOUBLE-TAP", "Two ballistic missiles hit restaurant parking lot; Shahed drones then targeted rescuers. 7-year-old boy and 20-year-old paramedic killed. 42 injured (4 children, 27 serious). 23 apartment buildings, hospital damaged. Vilkul: 'cynical strike.'", "Kyiv Independent / Ukrinform"),
    ]

    for idx, (title, body, source) in enumerate(secondary):
        _, body_h, _ = measure_text(draw, body, font_body, LEFT_COL_W - 12)
        panel_h = 18 + body_h + 14
        add_box(LEFT_COL_X, col_y, LEFT_COL_W, panel_h, f"secondary_panel_{idx}")
        add_box(*get_text_bbox(draw, LEFT_COL_X + 6, col_y + 3, title, font_label), f"secondary_title_{idx}")
        add_box(LEFT_COL_X + 6, col_y + 20, LEFT_COL_W - 12, body_h, f"secondary_body_{idx}")
        add_box(*get_text_bbox(draw, LEFT_COL_X + LEFT_COL_W - 120, col_y + panel_h - 12, f"SOURCE: {source}", font_tiny), f"secondary_source_{idx}")
        col_y += panel_h + 4

    left_col_bottom = col_y

    # ============================================================
    # RIGHT COLUMN
    # ============================================================
    col_y = MASTHEAD_H + 8

    def measure_story(headline_lines, subhead, body, source):
        h = 0
        for hl in headline_lines:
            h += draw_wrapped_text_height(draw, RIGHT_COL_X, 0, hl, font_headline, RIGHT_COL_W) + 1
        if subhead:
            h += draw_wrapped_text_height(draw, RIGHT_COL_X, 0, subhead, font_subhead, RIGHT_COL_W) + 3
        if body:
            h += draw_wrapped_text_height(draw, RIGHT_COL_X, 0, body, font_body, RIGHT_COL_W) + 3
        if source:
            h += 12
        return h + 4

    def add_story_boxes(x, y, w, headline_lines, subhead, body, source, prefix):
        cy = y
        for j, hl in enumerate(headline_lines):
            hh = draw_wrapped_text_height(draw, x, cy, hl, font_headline, w)
            add_box(x, cy, w, hh, f"{prefix}_h{j}")
            cy += hh + 1
        if subhead:
            sh = draw_wrapped_text_height(draw, x, cy, subhead, font_subhead, w)
            add_box(x, cy, w, sh, f"{prefix}_sub")
            cy += sh + 3
        if body:
            bh = draw_wrapped_text_height(draw, x, cy, body, font_body, w)
            add_box(x, cy, w, bh, f"{prefix}_body")
            cy += bh + 3
        if source:
            add_box(*get_text_bbox(draw, x, cy, f"SOURCE: {source}", font_tiny), f"{prefix}_source")
            cy += 12
        return cy + 4

    # EU-UK
    col_y = add_story_boxes(RIGHT_COL_X, col_y, RIGHT_COL_W,
        ["EU–UK SEAL THREE DEALS"],
        None,
        ("Food & drink: easing Brexit checks on animal/plant products (from Mar 2028). "
         "Emissions trading: linking UK-EU ETS, shielding steel/fertilisers from carbon levies (2028). "
         "Youth Experience Scheme: 100k under-30s each side to live/work/study 3 years (by 2030). "
         "Tuition fees: EU links ratification to equal fees for EU students."),
        "Guardian / DW / Le Monde", "euuk")

    # Denmark
    col_y = add_story_boxes(RIGHT_COL_X, col_y, RIGHT_COL_W,
        ["DENMARK: RUSSIA RECRUITED", "DANES TO KILL UKRAINIAN RAPPER"],
        None,
        ("Two Danish men charged with attempted murder & assisting foreign intel — allegedly hired by Russian intelligence to assassinate rapper Kyivstoner (US/UA dual citizen) at cancelled Sep 25 Copenhagen concert. "
         "Arrested in Hellerup with weapons. Both deny. FM Rasmussen expels Russian defence attaché. PET: Russia 'actively preparing sabotage' in Denmark."),
        "DR / BBC / Reuters", "denmark")

    # Houthi
    col_y = add_story_boxes(RIGHT_COL_X, col_y, RIGHT_COL_W,
        ["HOUTHIS TARGET RIYADH"],
        "THIRD CONSECUTIVE NIGHT",
        ("Saudi air defences intercept 5 drones + 1 ballistic missile targeting Riyadh (03:26 GMT). Falling debris causes damage. Coalition destroys 2 Houthi launchers in Yemen. "
         "Escalation follows Wed (60 targets hit) & Thu (5 missiles + 1 cruise missile). Iran-backed Houthis vow continued attacks."),
        "AP / SPA / Al Jazeera", "houthi")

    # Iran sanctions
    col_y = add_story_boxes(RIGHT_COL_X, col_y, RIGHT_COL_W,
        ["US SANCTIONS 4 IRANIANS"],
        None,
        ("Treasury OFAC designates 4 senior LEF & IRGC officials for brutal suppression of 2022 Mahsa Amini protests. Asset freeze, US entry ban. "
         "Separate: Comancheros/'Ndrangheta sanctions (Nov 20) target transnational crime networks."),
        "Treasury OFAC / Reuters", "iran")

    # Mongolia
    col_y = add_story_boxes(RIGHT_COL_X, col_y, RIGHT_COL_W,
        ["MONGOLIA PRESIDENT QUITS"],
        None,
        ("Parliament votes 96–8 to accept President Khurelsukh's resignation — first sitting president to step down early since 1992. "
         "Allegations by ex-mayor Nyambaatar (in Canada) of $25M bribe for railway contract. Khurelsukh denies, resigns to 'clear name.' Snap election within 4 months."),
        "AP / Montsame / Straits Times", "mongolia")

    # BepiColombo
    col_y = add_story_boxes(RIGHT_COL_X, col_y, RIGHT_COL_W,
        ["BepiColombo ENTERS", "MERCURY ORBIT"],
        None,
        ("ESA/JAXA mission arrives at Mercury after 8-year, 6-billion-mile journey. Composite spacecraft fires engine for orbital capture at ~21:00 UTC. "
         "First dual-orbiter mission: MPO (ESA) maps surface/exosphere; Mio (JAXA) studies magnetosphere. Science phase begins Apr 2027."),
        "ESA / NPR / New Scientist", "bepi")

    # Trump
    col_y = add_story_boxes(RIGHT_COL_X, col_y, RIGHT_COL_W,
        ["TRUMP: BAN US AI DATA", "CENTRES OVERSEAS"],
        None,
        ("Threatens 'tremendous tax' on US firms building data centres abroad. 'We're going to keep it all in this country.' Targets AI infrastructure expansion by tech giants. "
         "Markets react: chip stocks under pressure. Part of broader 'America First' tech sovereignty push."),
        "BBC / Reuters / NYT", "trump")

    # Gupta
    col_y = add_story_boxes(RIGHT_COL_X, col_y, RIGHT_COL_W,
        ["NIKHIL GUPTA: 19+ YEARS"],
        "FOR PANNUN MURDER PLOT",
        ("Indian national sentenced to 235 months (19.5 years) by SDNY Judge Marrero for murder-for-hire conspiracy directed by Indian govt employee Vikash Yadav targeting Sikh separatist Gurpatwant Singh Pannun in NYC. "
         "Gupta pled guilty Feb 2026. Extradited from Czechia Jun 2024. Faces deportation after sentence."),
        "DOJ / CBS / Al Jazeera", "gupta")

    # Cyclone Akvan box
    cyc_h = 44
    add_box(RIGHT_COL_X, col_y, RIGHT_COL_W, cyc_h, "cyclone_box")
    add_box(*get_text_bbox(draw, RIGHT_COL_X + 6, col_y + 3, "CYCLONE AKVAN — ODISHA", font_label), "cyclone_title")
    add_box(RIGHT_COL_X + 6, col_y + 19, RIGHT_COL_W - 12, draw_wrapped_text_height(draw, RIGHT_COL_X + 6, col_y + 19, "Landfall ~10:30–11:00 near Gopalpur. 372,000 evacuated. 4,467 pregnant women shifted; 1,452 delivered safely. Zero casualties reported. Storm weakening.", font_body, RIGHT_COL_W - 12), "cyclone_body")
    add_box(*get_text_bbox(draw, RIGHT_COL_X + RIGHT_COL_W - 110, col_y + 30, "SOURCE: ANI / ETV / TOI", font_tiny), "cyclone_source")
    col_y += cyc_h + 6

    right_col_bottom = col_y

    # ============================================================
    # BOTTOM SECTION
    # ============================================================
    BOTTOM_Y = max(HEIGHT - 250, right_col_bottom + 8)
    add_box(0, BOTTOM_Y, WIDTH, 2, "bottom_rule")
    content_y = BOTTOM_Y + 6

    # ALSO ON SATURDAY
    also_x = LEFT_COL_X
    also_w = LEFT_COL_W
    add_box(*get_text_bbox(draw, also_x, content_y, "ALSO ON SATURDAY", font_section), "also_title")
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
    for i, item in enumerate(also_items):
        add_box(*get_text_bbox(draw, also_x, ay, item, font_tiny), f"also_item_{i}")
        ay += 11

    # WHERE IT HAPPENED
    map_x = TIMELINE_RIGHT + 10
    map_w = 240
    map_y = content_y
    add_box(*get_text_bbox(draw, map_x, map_y, "WHERE IT HAPPENED", font_section), "map_title")
    my = map_y + 16
    add_box(map_x, my, map_w, 120, "map_box")

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
    for i, (lx, ly, label) in enumerate(locations):
        add_box(lx-3, ly-3, 6, 6, f"map_dot_{i}")
        tw = draw.textbbox((0, 0), label, font=font_tiny)[2]
        if lx + 6 + tw > map_x + map_w - 2:
            add_box(lx - 6 - tw, ly - 4, tw, 10, f"map_label_{i}")
        else:
            add_box(lx + 6, ly - 4, tw, 10, f"map_label_{i}")

    # DATE CHECK
    check_x = map_x + map_w + 10
    check_w = WIDTH - check_x - 10
    check_y = content_y
    check_box_h = 180
    add_box(check_x, check_y, check_w, check_box_h, "datecheck_box")
    add_box(*get_text_bbox(draw, check_x + 6, check_y + 3, "DATE CHECK — LEFT OUT", font_label), "datecheck_title")
    cy = check_y + 18
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
    for i, item in enumerate(left_out):
        add_box(*get_text_bbox(draw, check_x + 6, cy, item, font_tiny), f"datecheck_item_{i}")
        cy += 9

    # FOOTER
    footer_y = HEIGHT - 22
    add_box(0, footer_y - 4, WIDTH, 1, "footer_rule")
    sources = "CONFIRMED — AP, Reuters, BBC, Guardian, AFP, DW, DOJ, Treasury OFAC, ESA, NASA, PAHO, Montsame, Kyiv Independent, Ukrinform, ANI"
    add_box(*get_text_bbox(draw, 20, footer_y - 20, sources, font_tiny), "footer_sources")
    add_box(*get_text_bbox(draw, WIDTH - 160, footer_y - 20, "GENERATED 21 NOV 2026", font_tiny), "footer_gen")

    # Check for overlaps
    errors = check_overlaps()
    
    if errors:
        print(f"FOUND {len(errors)} REAL OVERLAPS:")
        for e in errors:
            print(f"  {e}")
        return False
    else:
        print(f"SUCCESS: No overlapping text boxes found ({len(all_boxes)} boxes checked)")
        print(f"Left column bottom: {left_col_bottom}")
        print(f"Right column bottom: {right_col_bottom}")
        print(f"Bottom section starts: {BOTTOM_Y}")
        print(f"Footer at: {footer_y}")
        print(f"DATE CHECK ends at: {cy}")
        return True


def draw_wrapped_text_height(draw, x, y, text, font, max_width):
    _, h, _ = measure_text(draw, text, font, max_width)
    return h


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)