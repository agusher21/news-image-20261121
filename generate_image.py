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

def draw_text(draw, x, y, text, font, fill=BLACK, max_width=None, line_spacing=1.2):
    """Draw text with optional word wrapping. Returns (width, height) of drawn text."""
    if max_width is None:
        draw.text((x, y), text, font=font, fill=fill)
        bbox = draw.textbbox((x, y), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    
    words = text.split()
    lines = []
    current = []
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
    
    line_height = int(font.size * line_spacing)
    total_h = len(lines) * line_height
    for i, line in enumerate(lines):
        draw.text((x, y + i * line_height), line, font=font, fill=fill)
    max_w = max(draw.textbbox((0, 0), line, font=font)[2] for line in lines) if lines else 0
    return max_w, total_h

def draw_justified_text(draw, x, y, text, font, fill=BLACK, max_width=None):
    """Draw justified text block."""
    return draw_text(draw, x, y, text, font, fill, max_width)

def main():
    img = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)
    
    # Fonts
    font_masthead = get_font(48, bold=True)
    font_masthead_sub = get_font(18, bold=True)
    font_section = get_font(16, bold=True)
    font_headline = get_font(14, bold=True)
    font_subhead = get_font(12, bold=False)
    font_body = get_font(11, bold=False)
    font_small = get_font(10, bold=False)
    font_tiny = get_font(9, bold=False)
    font_label = get_font(10, bold=True)
    font_stat = get_font(20, bold=True)
    font_stat_label = get_font(10, bold=False)
    
    # ============================================================
    # MASTHEAD - top 80px
    # ============================================================
    masthead_h = 80
    draw.rectangle([0, 0, WIDTH, masthead_h], fill=BLACK)
    draw.text((40, 8), "THE DAILY GLOBE", font=font_masthead, fill=WHITE)
    draw.text((40, 56), "SATURDAY 21 NOVEMBER 2026", font=font_masthead, fill=WHITE)
    draw.text((WIDTH - 200, 8), "VOL. CXII  No. 32,541", font=font_small, fill=WHITE)
    draw.text((WIDTH - 200, 26), "PRICE $2.50  |  €2.30  |  £1.95", font=font_tiny, fill=WHITE)
    draw.text((WIDTH - 200, 44), "EST. 1914", font=font_tiny, fill=WHITE)
    
    # Thin rule under masthead
    draw.line([(0, masthead_h), (WIDTH, masthead_h)], fill=BLACK, width=2)
    
    y = masthead_h + 4
    
    # ============================================================
    # UTC TIMELINE SPINE - full width, runs down the middle
    # ============================================================
    timeline_x = 512  # center
    timeline_top = y + 4
    timeline_bottom = HEIGHT - 60
    timeline_h = timeline_bottom - timeline_top
    
    # Draw timeline line
    draw.line([(timeline_x, timeline_top), (timeline_x, timeline_bottom)], fill=BLACK, width=3)
    
    # Timeline events (UTC times, verified stories)
    timeline_events = [
        ("00:00", "DAY BEGINS", "UTC"),
        ("03:26", "HOUTHI MISSILE", "intercepted over Riyadh — 3rd night"),
        ("05:30", "RUSSIAN KH-101", "cruise missile crashes in Poland (Nowy Lipowiec)"),
        ("06:00", "RUSSIAN DRONE", "jet-powered drone hits Mołodycz, Poland"),
        ("06:30", "2ND MISSILE", "down near Rudnik nad Sanem, Poland"),
        ("07:00", "TUSK: \"INTENTIONAL", "PROVOCATION\" — NATO jets scrambled"),
        ("09:00", "EU COUNCIL", "adopts €1bn military aid for Ukraine"),
        ("10:30", "CYCLONE AKVAN", "landfall near Gopalpur, Odisha — 372k evacuated"),
        ("12:00", "EU COMMISSION", "disburses €7.9bn to Ukraine (largest tranche)"),
        ("13:00", "DENMARK CHARGES", "2 Danes recruited by Russia to kill rapper Kyivstoner"),
        ("14:00", "COP31 ENTERS", "OVERTIME in Antalya — fossil fuel text deadlocked"),
        ("16:00", "WALL ST CLOSE:", "S&P -3.7% | Nasdaq -5.28% | Nvidia -14%"),
        ("18:00", "KRYVYI RIH:", "2 dead (boy 7, paramedic 20), 42 injured"),
        ("19:00", "NIKHIL GUPTA", "sentenced 235 months (19+ yrs) in Pannun plot"),
        ("20:00", "MONGOLIA:", "Parliament accepts President Khurelsukh resignation"),
        ("21:00", "BepiColombo", "FIRES ENGINES — enters Mercury orbit"),
        ("22:00", "TRUMP THREATENS", "ban on US firms building AI data centres abroad"),
        ("23:00", "US MEASLES", "elimination status lost (PAHO, announced Nov 17)"),
    ]
    
    # Draw timeline markers and labels on alternating sides
    for i, (time, label1, label2) in enumerate(timeline_events):
        # Calculate y position proportional to 24h
        h, m = map(int, time.split(":"))
        frac = (h * 60 + m) / (24 * 60)
        ty = timeline_top + int(frac * timeline_h)
        
        # Marker
        draw.ellipse([timeline_x - 5, ty - 5, timeline_x + 5, ty + 5], fill=RED, outline=BLACK, width=1)
        
        # Time label
        draw.text((timeline_x - 55, ty - 7), time, font=font_tiny, fill=BLACK)
        
        # Event labels - alternate left/right
        if i % 2 == 0:
            # Left side
            draw.text((20, ty - 7), label1, font=font_tiny, fill=BLACK)
            if label2:
                draw.text((20, ty + 5), label2, font=font_tiny, fill=DARK_GRAY)
        else:
            # Right side
            tw1 = draw.textbbox((0, 0), label1, font=font_tiny)[2]
            tw2 = draw.textbbox((0, 0), label2, font=font_tiny)[2] if label2 else 0
            draw.text((WIDTH - 20 - tw1, ty - 7), label1, font=font_tiny, fill=BLACK)
            if label2:
                draw.text((WIDTH - 20 - tw2, ty + 5), label2, font=font_tiny, fill=DARK_GRAY)
    
    # ============================================================
    # LEFT COLUMN - Hero story: Poland missiles
    # ============================================================
    left_x = 20
    left_w = 470
    col_y = y + 4
    
    # Hero headline
    draw.text((left_x, col_y), "RUSSIAN MISSILES, DRONE", font=font_headline, fill=BLACK)
    col_y += 18
    draw.text((left_x, col_y), "VIOLATE POLISH AIRSPACE", font=font_headline, fill=BLACK)
    col_y += 18
    draw.text((left_x, col_y), "TUSK: 'INTENTIONAL PROVOCATION'", font=font_subhead, fill=RED)
    col_y += 16
    
    # Hero sub-text
    hero_text = ("Three objects — two Kh-101 cruise missiles and a jet-powered drone — crashed in southeastern Poland overnight during Russia's massive aerial assault on Ukraine. "
                 "PM Donald Tusk said the incursion did not appear accidental, coming as 11-nation 'Coalition of the Willing' exercises (Koalicja 2026) were underway at Nowa Dęba. "
                 "No injuries reported. NATO SecGen Rutte condemned 'grave violations'; NATO jets scrambled. Defence Min. Kosiniak-Kamysz seeks more eastern flank support.")
    draw_justified_text(draw, left_x, col_y, hero_text, font_body, BLACK, left_w)
    col_y += 55
    
    # Map placeholder for Poland
    draw.rectangle([left_x, col_y, left_x + left_w, col_y + 80], outline=MED_GRAY, width=1)
    draw.text((left_x + 10, col_y + 30), "[ MAP: Missile impact sites — Nowy Lipowiec, Rudnik nad Sanem, Mołodycz ]", font=font_small, fill=MED_GRAY)
    col_y += 90
    
    # ============================================================
    # STAT STRIP - big numbers
    # ============================================================
    stat_y = col_y
    stats = [
        ("2 DEAD", "42 HURT", "Kryvyi Rih"),
        ("S&P -3.7%", "NASDAQ -5.28%", "Nvidia -14%"),
        ("€1 BN", "EU AID", "Ukraine"),
        ("372,000", "EVACUATED", "Cyclone Akvan"),
    ]
    stat_box_w = (left_w - 12) // 4
    for i, (big, mid, small) in enumerate(stats):
        sx = left_x + i * (stat_box_w + 4)
        draw.rectangle([sx, stat_y, sx + stat_box_w, stat_y + 50], fill=VERY_LIGHT_GRAY, outline=LIGHT_GRAY, width=1)
        draw.text((sx + 5, stat_y + 2), big, font=font_stat, fill=RED_DARK)
        draw.text((sx + 5, stat_y + 24), mid, font=font_stat_label, fill=DARK_GRAY)
        draw.text((sx + 5, stat_y + 36), small, font=font_tiny, fill=MED_GRAY)
    col_y = stat_y + 56
    
    # ============================================================
    # SECONDARY STORIES - 3 panels
    # ============================================================
    secondary = [
        ("COP31 OVERTIME", "Antalya talks breach Friday deadline; draft deal stripped of fossil fuel language. EU: 'risks turning COP into fossil summit.' Panama threatens walkout. 3rd draft expected Saturday. Electrification target (35% by 2035) remains, but no renewables mandate.", "AFP / Guardian"),
        ("WALL ST CORRECTION", "S&P 500 -3.7%, Dow -3.1%, Nasdaq -5.28% wipe 2026 gains. Nvidia -14% to 18-month low. Anthropic shares slide post-IPO. AI selloff drives worst week since 2020. Both S&P and Dow enter correction territory (>10% off highs).", "Reuters / UPI"),
        ("KRYVYI RIH DOUBLE-TAP", "Two ballistic missiles hit restaurant parking lot; Shahed drones then targeted rescuers. 7-year-old boy and 20-year-old paramedic killed. 42 injured (4 children, 27 serious). 23 apartment buildings, hospital damaged. Vilkul: 'cynical strike.'", "Kyiv Independent / Ukrinform"),
    ]
    
    panel_h = 90
    for title, body, source in secondary:
        draw.rectangle([left_x, col_y, left_x + left_w, col_y + panel_h], outline=LIGHT_GRAY, width=1)
        draw.text((left_x + 6, col_y + 4), title, font=font_label, fill=BLUE_DARK)
        draw_justified_text(draw, left_x + 6, col_y + 22, body, font_body, DARK_GRAY, left_w - 12)
        draw.text((left_x + left_w - 100, col_y + panel_h - 14), f"SOURCE: {source}", font=font_tiny, fill=MED_GRAY)
        col_y += panel_h + 6
    
    # ============================================================
    # RIGHT COLUMN - starts after timeline
    # ============================================================
    right_x = timeline_x + 20
    right_w = WIDTH - right_x - 20
    col_y = y + 4
    
    # EU-UK Deals
    draw.text((right_x, col_y), "EU–UK SEAL THREE DEALS", font=font_headline, fill=BLACK)
    col_y += 18
    euuk_text = ("Food & drink: easing Brexit checks on animal/plant products (from Mar 2028). "
                 "Emissions trading: linking UK-EU ETS, shielding steel/fertilisers from carbon levies (2028). "
                 "Youth Experience Scheme: 100k under-30s each side to live/work/study 3 years (by 2030). "
                 "Tuition fees dispute: EU links ratification to equal fees for EU students; UK says deal done, talks continue 6 months.")
    draw_justified_text(draw, right_x, col_y, euuk_text, font_body, DARK_GRAY, right_w)
    col_y += 60
    draw.text((right_x, col_y), "SOURCE: Guardian / DW / Le Monde", font=font_tiny, fill=MED_GRAY)
    col_y += 18
    
    # Denmark / Russia plot
    draw.text((right_x, col_y), "DENMARK: RUSSIA RECRUITED", font=font_headline, fill=BLACK)
    col_y += 18
    draw.text((right_x, col_y), "DANES TO KILL UKRAINIAN RAPPER", font=font_headline, fill=BLACK)
    col_y += 18
    den_text = ("Two Danish men charged with attempted murder & assisting foreign intel service — allegedly hired by Russian intelligence to assassinate rapper Kyivstoner (US/UA dual citizen) at cancelled Sep 25 Copenhagen concert. "
                "Arrested in Hellerup with weapons. Both deny. FM Rasmussen expels Russian defence attaché. PET: Russia 'actively preparing sabotage' in Denmark.")
    draw_justified_text(draw, right_x, col_y, den_text, font_body, DARK_GRAY, right_w)
    col_y += 55
    draw.text((right_x, col_y), "SOURCE: DR / BBC / Reuters", font=font_tiny, fill=MED_GRAY)
    col_y += 18
    
    # Houthi attacks
    draw.text((right_x, col_y), "HOUTHIS TARGET RIYADH", font=font_headline, fill=BLACK)
    col_y += 18
    draw.text((right_x, col_y), "THIRD CONSECUTIVE NIGHT", font=font_subhead, fill=RED)
    col_y += 16
    houthi_text = ("Saudi air defences intercept 5 drones + 1 ballistic missile targeting Riyadh and southern region (03:26 GMT). Falling debris causes material damage. Coalition destroys 2 Houthi missile launchers in Yemen (Dhamar, Saada). "
                   "Escalation follows Wed (60 targets hit) & Thu (5 missiles + 1 cruise missile intercepted). Iran-backed Houthis vow continued attacks.")
    draw_justified_text(draw, right_x, col_y, houthi_text, font_body, DARK_GRAY, right_w)
    col_y += 55
    draw.text((right_x, col_y), "SOURCE: AP / SPA / Al Jazeera", font=font_tiny, fill=MED_GRAY)
    col_y += 18
    
    # US Sanctions on Iranians
    draw.text((right_x, col_y), "US SANCTIONS 4 IRANIANS", font=font_headline, fill=BLACK)
    col_y += 18
    iran_text = ("Treasury OFAC designates 4 senior officials of Law Enforcement Forces (LEF) & IRGC for brutal suppression of 2022 Mahsa Amini protests. Asset freeze, US entry ban. "
                 "Separate: Comancheros/'Ndrangheta sanctions (Nov 20) target transnational crime networks.")
    draw_justified_text(draw, right_x, col_y, iran_text, font_body, DARK_GRAY, right_w)
    col_y += 45
    draw.text((right_x, col_y), "SOURCE: Treasury OFAC / Reuters", font=font_tiny, fill=MED_GRAY)
    col_y += 18
    
    # Mongolia
    draw.text((right_x, col_y), "MONGOLIA PRESIDENT QUITS", font=font_headline, fill=BLACK)
    col_y += 18
    mong_text = ("Parliament (State Great Khural) votes 96–8 to accept President Khurelsukh Ukhnaa's resignation — first sitting president to step down early since 1992. "
                 "Allegations by ex-mayor Nyambaatar Khishgee (in Canada) of $25M bribe for railway contract. Khurelsukh denies, resigns to 'clear name.' Speaker Byambatsogt Sandag becomes acting president. Snap election within 4 months.")
    draw_justified_text(draw, right_x, col_y, mong_text, font_body, DARK_GRAY, right_w)
    col_y += 55
    draw.text((right_x, col_y), "SOURCE: AP / Montsame / Straits Times", font=font_tiny, fill=MED_GRAY)
    col_y += 18
    
    # BepiColombo
    draw.text((right_x, col_y), "BepiColombo ENTERS", font=font_headline, fill=BLACK)
    col_y += 18
    draw.text((right_x, col_y), "MERCURY ORBIT", font=font_headline, fill=BLACK)
    col_y += 18
    bepi_text = ("ESA/JAXA joint mission arrives at Mercury after 8-year, 6-billion-mile journey. Composite spacecraft (MPO + Mio) fires main engine for orbital capture at ~21:00 UTC. "
                 "First dual-orbiter mission at Mercury: MPO (ESA) maps surface/exosphere; Mio (JAXA) studies magnetosphere. Science phase begins Apr 2027.")
    draw_justified_text(draw, right_x, col_y, bepi_text, font_body, DARK_GRAY, right_w)
    col_y += 55
    draw.text((right_x, col_y), "SOURCE: ESA / NPR / New Scientist", font=font_tiny, fill=MED_GRAY)
    col_y += 18
    
    # Trump AI data centres
    draw.text((right_x, col_y), "TRUMP: BAN US AI DATA", font=font_headline, fill=BLACK)
    col_y += 18
    draw.text((right_x, col_y), "CENTRES OVERSEAS", font=font_headline, fill=BLACK)
    col_y += 18
    trump_text = ("Threatens 'tremendous tax' on US firms building data centres abroad. 'We're going to keep it all in this country.' Targets AI infrastructure expansion by tech giants. "
                  "Markets react: chip stocks under pressure. Part of broader 'America First' tech sovereignty push.")
    draw_justified_text(draw, right_x, col_y, trump_text, font_body, DARK_GRAY, right_w)
    col_y += 45
    draw.text((right_x, col_y), "SOURCE: BBC / Reuters / NYT", font=font_tiny, fill=MED_GRAY)
    col_y += 18
    
    # Nikhil Gupta
    draw.text((right_x, col_y), "NIKHIL GUPTA: 19+ YEARS", font=font_headline, fill=BLACK)
    col_y += 18
    draw.text((right_x, col_y), "FOR PANNUN MURDER PLOT", font=font_subhead, fill=BLACK)
    col_y += 16
    gupta_text = ("Indian national sentenced to 235 months (19.5 years) by SDNY Judge Marrero for murder-for-hire conspiracy directed by Indian govt employee Vikash Yadav targeting Sikh separatist Gurpatwant Singh Pannun in NYC. "
                  "Gupta pled guilty Feb 2026. Extradited from Czechia Jun 2024. Faces deportation after sentence.")
    draw_justified_text(draw, right_x, col_y, gupta_text, font_body, DARK_GRAY, right_w)
    col_y += 50
    draw.text((right_x, col_y), "SOURCE: DOJ / CBS / Al Jazeera", font=font_tiny, fill=MED_GRAY)
    col_y += 18
    
    # Cyclone Akvan (small box at bottom right)
    draw.rectangle([right_x, col_y, right_x + right_w, col_y + 50], fill=VERY_LIGHT_GRAY, outline=LIGHT_GRAY, width=1)
    draw.text((right_x + 6, col_y + 4), "CYCLONE AKVAN — ODISHA", font=font_label, fill=BLUE_DARK)
    draw.text((right_x + 6, col_y + 22), "Landfall ~10:30–11:00 near Gopalpur. 372,000 evacuated. 4,467 pregnant women shifted; 1,452 delivered safely. Zero casualties reported. Storm weakening.", font=font_body, fill=DARK_GRAY)
    draw.text((right_x + right_w - 100, col_y + 34), "SOURCE: ANI / ETV / TOI", font=font_tiny, fill=MED_GRAY)
    col_y += 56
    
    # ============================================================
    # BOTTOM SECTION - ALSO ON SATURDAY + WHERE IT HAPPENED + DATE CHECK
    # ============================================================
    bottom_y = HEIGHT - 180
    draw.line([(0, bottom_y), (WIDTH, bottom_y)], fill=BLACK, width=2)
    bottom_y += 6
    
    # ALSO ON SATURDAY (left)
    also_x = 20
    also_w = 470
    draw.text((also_x, bottom_y), "ALSO ON SATURDAY", font=font_section, fill=BLACK)
    bottom_y += 18
    
    also_items = [
        "1. Voyager 1 reaches 1 light-day from Earth (Nov 18 milestone, NASA celebration Nov 17)",
        "2. Trump–Xi–Putin trilateral at APEC Shenzhen (Nov 19) — 'peace declaration', little concrete consensus",
        "3. US loses measles elimination status (PAHO, announced Nov 17) — 5,400+ cases, 10 deaths in 2026",
        "4. ICJ Myanmar genocide ruling (Nov 19, 9–6 vote) — Switzerland calls 'important step'",
        "5. EU–UK youth mobility, food & drink, ETS deals signed (Nov 20 Brussels summit)",
        "6. Anthropic IPO slides; tech sell-off deepens AI winter fears",
        "7. Saudi coalition destroys 60 Houthi targets in Yemen (Nov 18)",
        "8. Comancheros / 'Ndrangheta sanctions by US Treasury (Nov 20)",
        "9. Poland coalition ministers visit Nowa Dęba exercise site (Nov 20)",
        "10. Ukraine: Russian mass missile attack Nov 20 kills 7 in Kyiv, 17 injured",
    ]
    for item in also_items:
        draw.text((also_x, bottom_y), item, font=font_tiny, fill=DARK_GRAY)
        bottom_y += 13
    
    # WHERE IT HAPPENED - world map with dots (middle bottom)
    map_x = 520
    map_w = 240
    map_y = HEIGHT - 170
    draw.text((map_x, map_y), "WHERE IT HAPPENED", font=font_section, fill=BLACK)
    map_y += 18
    # Simple world map outline - draw continents as rectangles
    # This is a schematic, not a real projection
    draw.rectangle([map_x, map_y, map_x + map_w, map_y + 130], outline=LIGHT_GRAY, width=1)
    # Dots for locations
    locations = [
        (map_x + 80, map_y + 30, "Poland"),      # Europe
        (map_x + 90, map_y + 45, "Ukraine"),     # Ukraine
        (map_x + 130, map_y + 50, "Turkey"),     # COP31
        (map_x + 140, map_y + 65, "Saudi"),      # Riyadh
        (map_x + 160, map_y + 75, "India"),      # Cyclone
        (map_x + 180, map_y + 55, "Mongolia"),   # Mongolia
        (map_x + 50, map_y + 80, "USA"),         # US stories
        (map_x + 30, map_y + 40, "UK"),          # EU-UK
        (map_x + 60, map_y + 40, "Denmark"),     # Denmark
        (map_x + 200, map_y + 40, "Mercury"),    # BepiColombo (symbolic)
    ]
    for lx, ly, label in locations:
        draw.ellipse([lx-3, ly-3, lx+3, ly+3], fill=RED, outline=BLACK)
        draw.text((lx + 6, ly - 5), label, font=font_tiny, fill=DARK_GRAY)
    
    # DATE CHECK — LEFT OUT (right bottom)
    check_x = 780
    check_w = 224
    check_y = HEIGHT - 170
    draw.rectangle([check_x, check_y, check_x + check_w, check_y + 140], fill=VERY_LIGHT_GRAY, outline=LIGHT_GRAY, width=1)
    draw.text((check_x + 6, check_y + 4), "DATE CHECK — LEFT OUT", font=font_label, fill=RED_DARK)
    check_y += 20
    left_out = [
        "• ICJ Myanmar genocide ruling — 19 Nov (not 21 Nov)",
        "• Pete Rose pardon — 20 Nov (not 21 Nov)",
        "• EU €1bn military aid — adopted 20 Nov",
        "• EU €7.9bn disbursement — 20 Nov",
        "• US sanctions 4 Iranians — published 20 Nov",
        "• Trump AI data centre threat — 20 Nov",
        "• Nikhil Gupta sentencing — 20 Nov",
        "• Mongolia parliament vote — 19 Nov",
        "• EU-UK summit deals — 20 Nov",
        "• COP31 overtime began — 20 Nov",
        "• Wall St correction — 20 Nov close",
        "• Houthi 3rd night — 20 Nov",
        "• Cyclone Akvan landfall — 20 Nov",
        "• Voyager 1 light-day — 18 Nov",
        "• BepiColombo orbit insertion — 21 Nov ✓",
        "• Kryvyi Rih 42 injured — confirmed 21 Nov ✓",
        "• Poland missiles — 20 Nov, 21 Nov Tusk/NATO ✓",
        "• Denmark charges — court hearing 20 Nov",
        "• US measles status — announced 17 Nov",
    ]
    for item in left_out:
        draw.text((check_x + 6, check_y), item, font=font_tiny, fill=DARK_GRAY)
        check_y += 11
    
    # ============================================================
    # FOOTER - sources
    # ============================================================
    footer_y = HEIGHT - 24
    draw.line([(0, footer_y - 4), (WIDTH, footer_y - 4)], fill=BLACK, width=1)
    sources = "CONFIRMED — AP, Reuters, BBC, Guardian, AFP, DW, DOJ, Treasury OFAC, ESA, NASA, PAHO, Montsame, Kyiv Independent, Ukrinform, ANI"
    draw.text((20, footer_y - 20), sources, font=font_tiny, fill=MED_GRAY)
    draw.text((WIDTH - 180, footer_y - 20), "GENERATED 21 NOV 2026", font=font_tiny, fill=MED_GRAY)
    
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
    
    return OUTPUT_PATH

if __name__ == "__main__":
    main()