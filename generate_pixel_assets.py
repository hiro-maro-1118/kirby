import os
import math
from PIL import Image, ImageDraw

os.makedirs("assets/sprites", exist_ok=True)

# 64x64 pixel grid scaled up to 256x256 for crisp high-definition pixel art
SIZE = 64
SCALE = 4

def create_frame():
    return Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))

def draw_pixels(img, pixel_dict):
    """pixel_dict: (x, y) -> (r, g, b, a)"""
    draw = ImageDraw.Draw(img)
    for (x, y), color in pixel_dict.items():
        if 0 <= x < SIZE and 0 <= y < SIZE:
            draw.point((x, y), fill=color)

def scale_and_save_webp(frames, filename, duration=180):
    scaled_frames = []
    for f in frames:
        scaled = f.resize((SIZE * SCALE, SIZE * SCALE), Image.NEAREST)
        scaled_frames.append(scaled)
    
    scaled_frames[0].save(
        filename,
        format="WEBP",
        save_all=True,
        append_images=scaled_frames[1:],
        duration=duration,
        loop=0,
        lossless=True,
        quality=100
    )
    print(f"Generated {filename}")

# --- Rich & Cute Color Palette ---
PINK_LIGHT = (255, 215, 235, 255)
PINK_BODY = (255, 145, 185, 255)
PINK_SHADOW = (235, 95, 145, 255)
PINK_DEEP = (195, 55, 110, 255)
OUTLINE = (45, 25, 40, 255)

RED_FEET = (235, 40, 80, 255)
RED_FEET_LIGHT = (255, 80, 120, 255)
RED_FEET_SHADOW = (175, 20, 60, 255)

WHITE = (255, 255, 255, 255)
BLACK = (25, 20, 30, 255)
CHEEK_COLOR = (255, 80, 140, 255)
CHEEK_LIGHT = (255, 140, 185, 255)

EYE_BLUE_TOP = (15, 30, 75, 255)
EYE_BLUE_MID = (30, 85, 185, 255)
EYE_BLUE_BOT = (75, 165, 245, 255)
EYE_BLUE_CYAN = (130, 215, 255, 255)

MOUTH_DARK = (160, 25, 60, 255)
MOUTH_TONGUE = (255, 120, 150, 255)

# --- Drawing Utilities ---

def fill_circle(px, cx, cy, radius, color):
    r_int = int(radius + 1)
    for y in range(int(cy - r_int), int(cy + r_int + 1)):
        for x in range(int(cx - r_int), int(cx + r_int + 1)):
            if (x - cx)**2 + (y - cy)**2 <= radius**2:
                px[(x, y)] = color

def fill_ellipse(px, cx, cy, rx, ry, color):
    rx_int = int(rx + 1)
    ry_int = int(ry + 1)
    for y in range(int(cy - ry_int), int(cy + ry_int + 1)):
        for x in range(int(cx - rx_int), int(cx + rx_int + 1)):
            if ((x - cx) / rx)**2 + ((y - cy) / ry)**2 <= 1.0:
                px[(x, y)] = color

def draw_shaded_body(px, cx, cy, radius=16, squash_x=0, squash_y=0):
    rx = radius + squash_x
    ry = radius + squash_y
    
    for y in range(int(cy - ry - 2), int(cy + ry + 3)):
        for x in range(int(cx - rx - 2), int(cx + rx + 3)):
            dx = (x - cx) / rx
            dy = (y - cy) / ry
            dist_sq = dx * dx + dy * dy
            
            if dist_sq <= 1.0:
                if dx < -0.25 and dy < -0.25 and dist_sq > 0.25:
                    px[(x, y)] = PINK_LIGHT
                elif dy > 0.4 or (dx > 0.45 and dy > 0.1):
                    if dist_sq > 0.85:
                        px[(x, y)] = PINK_DEEP
                    else:
                        px[(x, y)] = PINK_SHADOW
                else:
                    px[(x, y)] = PINK_BODY
            elif dist_sq <= 1.18:
                px[(x, y)] = OUTLINE

def draw_cute_eyes(px, cx, cy, eye_state='normal'):
    """
    Proportional, beautifully curved oval eyes (原作準拠の愛らしくスッキリした楕円の瞳)
    """
    if eye_state == 'blink':
        # Smooth arched closed eyes ^ ^
        for dx in range(-6, -2):
            arc = int((2.5 - abs(dx + 4)) * 0.8)
            px[(cx + dx, cy - 2 - arc)] = OUTLINE
            px[(cx + dx, cy - 1 - arc)] = OUTLINE
        for dx in range(2, 6):
            arc = int((2.5 - abs(dx - 4)) * 0.8)
            px[(cx + dx, cy - 2 - arc)] = OUTLINE
            px[(cx + dx, cy - 1 - arc)] = OUTLINE

    elif eye_state == 'happy':
        # Cheerful rainbow crescent eyes ^^
        for dx in range(-6, -1):
            arc = int(1.8 * (1.0 - ((dx + 3.5) / 2.5)**2))
            px[(cx + dx, cy - 1 - arc)] = OUTLINE
            px[(cx + dx, cy - arc)] = OUTLINE
        for dx in range(1, 6):
            arc = int(1.8 * (1.0 - ((dx - 3.5) / 2.5)**2))
            px[(cx + dx, cy - 1 - arc)] = OUTLINE
            px[(cx + dx, cy - arc)] = OUTLINE

    elif eye_state == 'sick':
        # Dizzy spiral eyes (Compact)
        for dx, dy in [(-5, -3), (-4, -4), (-3, -3), (-3, -2), (-4, -1), (-5, -2)]:
            px[(cx + dx, cy + dy)] = OUTLINE
        for dx, dy in [(5, -3), (4, -4), (3, -3), (3, -2), (4, -1), (5, -2)]:
            px[(cx + dx, cy + dy)] = OUTLINE

    else: # 'normal' or 'sparkle'
        # Perfectly Proportioned Oval Eyes (Faithful to Kirby proportions)
        eye_rx = 1.75
        eye_ry = 3.6
        
        # Left Eye Center: (cx - 4.5, cy - 2.5)
        # Right Eye Center: (cx + 4.5, cy - 2.5)
        for (ecx, is_left) in [(cx - 4.5, True), (cx + 4.5, False)]:
            ecy = cy - 2.5
            
            # 1. Draw Eye Outline & Iris (Oval)
            for y in range(int(ecy - eye_ry - 2), int(ecy + eye_ry + 3)):
                for x in range(int(ecx - eye_rx - 2), int(ecx + eye_rx + 3)):
                    ndx = (x - ecx) / eye_rx
                    ndy = (y - ecy) / eye_ry
                    dist = ndx * ndx + ndy * ndy
                    
                    if dist <= 1.0:
                        # Inner Iris with Smooth Gradient
                        if ndy < -0.1:
                            px[(x, y)] = EYE_BLUE_TOP
                        elif ndy < 0.35:
                            px[(x, y)] = EYE_BLUE_MID
                        elif ndy < 0.75:
                            px[(x, y)] = EYE_BLUE_BOT
                        else:
                            px[(x, y)] = EYE_BLUE_CYAN
                    elif dist <= 1.38:
                        # Smooth curved outline
                        px[(x, y)] = OUTLINE

            # 2. Main Top Highlight (Crisp oval shine)
            hl_x = ecx - (0.4 if is_left else 0.3)
            hl_y = ecy - 1.6
            fill_ellipse(px, hl_x, hl_y, 0.95, 1.45, WHITE)

            # 3. Bottom Secondary Sparkle (Subtle eye glint)
            gl_x = int(ecx + (0.5 if is_left else 0.5))
            gl_y = int(ecy + 1.8)
            px[(gl_x, gl_y)] = WHITE
            px[(gl_x - 1, gl_y)] = EYE_BLUE_CYAN

def draw_cheeks_and_mouth(px, cx, cy, mouth_type='smile'):
    # Cheeks (Smooth Blushing Oval)
    fill_ellipse(px, cx - 10.5, cy + 2.0, 2.8, 1.8, CHEEK_COLOR)
    px[(int(cx - 10.5), int(cy + 1.5))] = CHEEK_LIGHT
    
    fill_ellipse(px, cx + 10.5, cy + 2.0, 2.8, 1.8, CHEEK_COLOR)
    px[(int(cx + 10.5), int(cy + 1.5))] = CHEEK_LIGHT

    # Mouth
    if mouth_type == 'smile':
        # Rounded open smile :3
        fill_ellipse(px, cx, cy + 3.8, 2.2, 1.6, MOUTH_TONGUE)
        for a in range(0, 181, 30):
            rad = math.radians(a)
            mx = int(cx + 2.4 * math.cos(rad))
            my = int(cy + 3.8 + 1.8 * math.sin(rad))
            px[(mx, my)] = OUTLINE

    elif mouth_type == 'open':
        # Cheerful open mouth with tongue
        fill_ellipse(px, cx, cy + 4.8, 2.6, 2.2, MOUTH_DARK)
        fill_ellipse(px, cx, cy + 5.6, 1.8, 1.2, MOUTH_TONGUE)
        for a in range(0, 360, 30):
            rad = math.radians(a)
            px[(int(cx + 2.8 * math.cos(rad)), int(cy + 4.8 + 2.4 * math.sin(rad)))] = OUTLINE

    elif mouth_type == 'eating':
        fill_ellipse(px, cx, cy + 4.5, 3.5, 2.0, MOUTH_DARK)
        fill_ellipse(px, cx, cy + 5.2, 2.0, 1.2, MOUTH_TONGUE)
        px[(cx - 4, cy + 4)] = OUTLINE
        px[(cx + 4, cy + 4)] = OUTLINE

    elif mouth_type == 'inhale':
        fill_circle(px, cx, cy + 4.5, 8.5, MOUTH_DARK)
        fill_circle(px, cx, cy + 6.5, 5.5, (100, 10, 40, 255))
        for a in range(0, 360, 15):
            rad = math.radians(a)
            px[(int(cx + 9.0 * math.cos(rad)), int(cy + 4.5 + 9.0 * math.sin(rad)))] = OUTLINE

def draw_feet(px, cx, cy, f_left_offset=(0,0), f_right_offset=(0,0)):
    # Left foot
    lx, ly = cx - 10 + f_left_offset[0], cy + 13 + f_left_offset[1]
    for y in range(int(ly - 4), int(ly + 6)):
        for x in range(int(lx - 7), int(lx + 8)):
            dist = (x - lx)**2 / 38.0 + (y - ly)**2 / 18.0
            if dist <= 1.0:
                if y < ly: px[(x, y)] = RED_FEET_LIGHT
                elif y > ly + 2: px[(x, y)] = RED_FEET_SHADOW
                else: px[(x, y)] = RED_FEET
            elif dist <= 1.25:
                px[(x, y)] = OUTLINE

    # Right foot
    rx, ry = cx + 10 + f_right_offset[0], cy + 13 + f_right_offset[1]
    for y in range(int(ry - 4), int(ry + 6)):
        for x in range(int(rx - 7), int(rx + 8)):
            dist = (x - rx)**2 / 38.0 + (y - ry)**2 / 18.0
            if dist <= 1.0:
                if y < ry: px[(x, y)] = RED_FEET_LIGHT
                elif y > ry + 2: px[(x, y)] = RED_FEET_SHADOW
                else: px[(x, y)] = RED_FEET
            elif dist <= 1.25:
                px[(x, y)] = OUTLINE

def draw_hands(px, cx, cy, hand_pose='normal', bounce=0):
    if hand_pose == 'cheer':
        fill_circle(px, cx - 15, cy - 5 + bounce, 4.5, PINK_BODY)
        px[(cx - 15, cy - 7 + bounce)] = PINK_LIGHT
        for a in range(0, 360, 20):
            rad = math.radians(a)
            px[(int(cx - 15 + 5 * math.cos(rad)), int(cy - 5 + bounce + 5 * math.sin(rad)))] = OUTLINE

        fill_circle(px, cx + 15, cy - 5 - bounce, 4.5, PINK_BODY)
        px[(cx + 15, cy - 7 - bounce)] = PINK_LIGHT
        for a in range(0, 360, 20):
            rad = math.radians(a)
            px[(int(cx + 15 + 5 * math.cos(rad)), int(cy - 5 - bounce + 5 * math.sin(rad)))] = OUTLINE
    else:
        fill_circle(px, cx - 15, cy + 3 + bounce, 4.5, PINK_BODY)
        px[(cx - 15, cy + 1 + bounce)] = PINK_LIGHT
        for a in range(0, 360, 20):
            rad = math.radians(a)
            px[(int(cx - 15 + 5 * math.cos(rad)), int(cy + 3 + bounce + 5 * math.sin(rad)))] = OUTLINE

        fill_circle(px, cx + 15, cy + 3 - bounce, 4.5, PINK_BODY)
        px[(cx + 15, cy + 1 - bounce)] = PINK_LIGHT
        for a in range(0, 360, 20):
            rad = math.radians(a)
            px[(int(cx + 15 + 5 * math.cos(rad)), int(cy + 3 - bounce + 5 * math.sin(rad)))] = OUTLINE


# ==========================================
# 1. おむつカービィ (Baby Kirby)
# ==========================================
def generate_baby_kirby():
    frames = []
    for f in range(4):
        img = create_frame()
        px = {}
        cx, cy = 32, 34
        bob = -1 if f in [1, 3] else 1
        crawl = 2 if f % 2 == 0 else -2
        blink = (f == 2)
        
        draw_feet(px, cx, cy + bob, (-3 + crawl, 1), (3 - crawl, 1))
        draw_shaded_body(px, cx, cy + bob, radius=14)

        # Diaper
        for y in range(cy + 4 + bob, cy + 16 + bob):
            for x in range(cx - 13, cx + 14):
                if (x - cx)**2 + (y - (cy + bob))**2 <= 14**2:
                    if y >= cy + 6 + bob:
                        px[(x, y)] = (255, 255, 255, 255)
                        if y >= cy + 13 + bob or abs(x - cx) >= 11:
                            px[(x, y)] = (215, 225, 240, 255)
        for x in range(cx - 12, cx + 13):
            if (x - cx)**2 + (cy + 6 + bob - (cy + bob))**2 <= 14**2:
                px[(x, cy + 6 + bob)] = (180, 195, 220, 255)

        # Diaper Star Pin
        pin_x, pin_y = cx - 6, cy + 9 + bob
        fill_circle(px, pin_x, pin_y, 2.5, (255, 220, 40, 255))
        px[(pin_x, pin_y)] = (255, 255, 180, 255)

        # Big Cute Rounded Eyes
        draw_cute_eyes(px, cx, cy - 2 + bob, 'blink' if blink else 'normal')
        
        # Pacifier
        pac_y = cy + 4 + bob
        fill_circle(px, cx, pac_y, 4, (255, 210, 50, 255))
        fill_circle(px, cx, pac_y, 2, (255, 140, 20, 255))
        px[(cx, pac_y + 3)] = (255, 240, 100, 255)

        # Cheeks
        fill_ellipse(px, cx - 10, cy + bob + 1, 2.5, 1.8, CHEEK_COLOR)
        fill_ellipse(px, cx + 10, cy + bob + 1, 2.5, 1.8, CHEEK_COLOR)

        # Baby crawl hands
        fill_circle(px, cx - 11, cy + 10 + bob, 3.5, PINK_BODY)
        fill_circle(px, cx + 11, cy + 10 + bob, 3.5, PINK_BODY)

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/pet_baby.webp", 200)


# ==========================================
# 2. 普通カービィ (Normal Kirby)
# ==========================================
def generate_normal_kirby():
    frames = []
    for f in range(4):
        img = create_frame()
        px = {}
        cx, cy = 32, 32
        bob = -2 if f in [1, 2] else 0
        blink = (f == 3)
        happy = (f == 2)
        
        draw_feet(px, cx, cy + bob, (-1 if f==1 else 0, bob), (1 if f==2 else 0, bob))
        draw_shaded_body(px, cx, cy + bob, radius=16)
        draw_hands(px, cx, cy + bob, 'cheer' if happy else 'normal', bounce=1 if f%2==1 else 0)
        draw_cute_eyes(px, cx, cy + bob, 'blink' if blink else ('happy' if happy else 'normal'))
        draw_cheeks_and_mouth(px, cx, cy + bob, 'open' if happy else 'smile')

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/pet_normal.webp", 180)


# ==========================================
# 3. ファイアカービィ (Fire Kirby)
# ==========================================
def generate_fire_kirby():
    frames = []
    flame_colors = [(255, 60, 20, 255), (255, 140, 20, 255), (255, 230, 40, 255), (255, 255, 180, 255)]
    for f in range(4):
        img = create_frame()
        px = {}
        cx, cy = 32, 34
        bob = -1 if f in [1, 2] else 0
        
        draw_feet(px, cx, cy + bob)
        draw_shaded_body(px, cx, cy + bob, radius=16)
        draw_hands(px, cx, cy + bob, 'cheer', bounce=1)
        draw_cute_eyes(px, cx, cy + bob, 'sparkle')
        draw_cheeks_and_mouth(px, cx, cy + bob, 'open')

        # Gold Crown Band
        for y in range(cy - 16 + bob, cy - 11 + bob):
            for x in range(cx - 13, cx + 14):
                if (x - cx)**2 <= 14**2:
                    px[(x, y)] = (255, 215, 0, 255)
        fill_circle(px, cx, cy - 13 + bob, 2.5, (230, 20, 40, 255))
        px[(cx, cy - 14 + bob)] = WHITE

        # Dynamic Roaring Flames
        for fy in range(cy - 30 + bob, cy - 15 + bob):
            h_ratio = (cy - 15 + bob - fy) / 15.0
            max_w = int(14 * (1.0 - h_ratio * 0.7))
            for fx in range(cx - max_w, cx + max_w + 1):
                wave = int(math.sin(fy * 0.5 + f * 1.5) * 3)
                if abs(fx - cx + wave) <= max_w:
                    dist = (abs(fx - cx) / max(1, max_w)) + (h_ratio * 0.5)
                    if dist < 0.35: px[(fx, fy)] = flame_colors[3]
                    elif dist < 0.65: px[(fx, fy)] = flame_colors[2]
                    elif dist < 0.95: px[(fx, fy)] = flame_colors[1]
                    else: px[(fx, fy)] = flame_colors[0]

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/pet_fire.webp", 150)


# ==========================================
# 4. ソードカービィ (Sword Kirby)
# ==========================================
def generate_sword_kirby():
    frames = []
    for f in range(4):
        img = create_frame()
        px = {}
        cx, cy = 30, 34
        bob = -1 if f in [1, 2] else 0
        blink = (f == 3)
        
        draw_feet(px, cx, cy + bob)
        draw_shaded_body(px, cx, cy + bob, radius=16)
        draw_cute_eyes(px, cx, cy + bob, 'blink' if blink else 'normal')
        draw_cheeks_and_mouth(px, cx, cy + bob, 'smile')

        # Green Knight Cap
        cap_green = (40, 160, 50, 255)
        cap_dark = (25, 105, 30, 255)
        cap_light = (75, 205, 80, 255)
        
        for y in range(cy - 26 + bob, cy - 10 + bob):
            for x in range(cx - 14, cx + 15):
                dist_top = cy - 10 + bob - y
                target_cx = cx + int(dist_top * 0.7)
                w = max(2, int(15 - dist_top * 0.6))
                if abs(x - target_cx) <= w:
                    if y == cy - 11 + bob or x == cx - 14: px[(x, y)] = cap_dark
                    elif y <= cy - 22 + bob or x == target_cx - w + 1: px[(x, y)] = cap_light
                    else: px[(x, y)] = cap_green
        
        # Yellow pompom
        fill_circle(px, cx + 16, cy - 22 + bob + (f % 2), 3, (255, 225, 50, 255))

        # Silver Sword in Hand
        sword_base_x = cx + 18
        sword_base_y = cy + 2 + bob
        fill_circle(px, cx + 16, cy + 2 + bob, 4.5, PINK_BODY)
        for gy in range(sword_base_y - 3, sword_base_y + 4):
            px[(sword_base_x, gy)] = (255, 215, 0, 255)
        for i in range(1, 15):
            bx = sword_base_x + i
            by = sword_base_y - i
            px[(bx, by)] = WHITE
            px[(bx - 1, by)] = (210, 230, 255, 255)
            px[(bx, by + 1)] = (150, 180, 210, 255)

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/pet_sword.webp", 180)


# ==========================================
# 5. スパークカービィ (Spark Kirby)
# ==========================================
def generate_spark_kirby():
    frames = []
    for f in range(4):
        img = create_frame()
        px = {}
        cx, cy = 32, 34
        bob = -1 if f in [1, 2] else 0
        
        draw_feet(px, cx, cy + bob)
        draw_shaded_body(px, cx, cy + bob, radius=16)
        draw_hands(px, cx, cy + bob, 'cheer', bounce=2)
        draw_cute_eyes(px, cx, cy + bob, 'sparkle')
        draw_cheeks_and_mouth(px, cx, cy + bob, 'open')

        # Electric Plasma Crown
        for y in range(cy - 24 + bob, cy - 11 + bob):
            for x in range(cx - 14, cx + 15):
                dx = abs(x - cx)
                spike_h = 13 if dx <= 4 else (10 if dx <= 9 else 7)
                if cy - 11 + bob - y <= spike_h:
                    px[(x, y)] = (255, 220, 30, 255)
                    if (x + y + f) % 3 == 0: px[(x, y)] = (255, 255, 180, 255)
        fill_circle(px, cx, cy - 15 + bob, 3, (0, 220, 255, 255))
        px[(cx, cy - 15 + bob)] = WHITE

        # Electric Bolts
        bolt_offsets = [
            [(cx - 18, cy - 15), (cx - 14, cy - 22), (cx - 10, cy - 18)],
            [(cx + 18, cy - 15), (cx + 14, cy - 22), (cx + 10, cy - 18)]
        ]
        for bolt in bolt_offsets:
            shift = (f * 2) % 3
            for i in range(len(bolt) - 1):
                p1, p2 = bolt[i], bolt[i+1]
                px[(p1[0], p1[1] + bob + shift)] = WHITE
                px[(p2[0], p2[1] + bob - shift)] = (80, 230, 255, 255)

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/pet_spark.webp", 140)


# ==========================================
# 6. アイスカービィ (Ice Kirby)
# ==========================================
def generate_ice_kirby():
    frames = []
    for f in range(4):
        img = create_frame()
        px = {}
        cx, cy = 32, 34
        bob = -1 if f in [1, 2] else 0
        blink = (f == 2)
        
        draw_feet(px, cx, cy + bob)
        draw_shaded_body(px, cx, cy + bob, radius=16)
        draw_hands(px, cx, cy + bob, 'cheer', bounce=1)
        draw_cute_eyes(px, cx, cy + bob, 'blink' if blink else 'normal')
        draw_cheeks_and_mouth(px, cx, cy + bob, 'smile')

        # Crystal Ice Tiara
        ice_cyan_light = (220, 250, 255, 255)
        ice_cyan_mid = (120, 215, 255, 255)
        ice_cyan_deep = (30, 140, 230, 255)
        
        for y in range(cy - 26 + bob, cy - 11 + bob):
            for x in range(cx - 14, cx + 15):
                dx = abs(x - cx)
                spike = 15 if dx <= 2 else (12 if dx <= 7 else (8 if dx <= 12 else 0))
                if cy - 11 + bob - y <= spike:
                    px[(x, y)] = ice_cyan_light if x % 2 == 0 else ice_cyan_mid

        # Snowflake Particles
        snow_anim = (f * 5) % 30
        for sx, sy in [(cx - 16, cy - 15 + snow_anim), (cx + 18, cy - 10 + ((snow_anim + 15) % 30))]:
            if 0 <= sx < SIZE and 0 <= sy < SIZE:
                px[(sx, sy)] = WHITE
                px[(sx + 1, sy)] = ice_cyan_light

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/pet_ice.webp", 180)


# ==========================================
# 7. ウィザード/ドクターカービィ (Wizard Kirby)
# ==========================================
def generate_wizard_kirby():
    frames = []
    for f in range(4):
        img = create_frame()
        px = {}
        cx, cy = 32, 34
        bob = -1 if f in [1, 2] else 0
        
        draw_feet(px, cx, cy + bob)
        draw_shaded_body(px, cx, cy + bob, radius=16)
        draw_cute_eyes(px, cx, cy + bob, 'sparkle')
        draw_cheeks_and_mouth(px, cx, cy + bob, 'smile')

        # Round Glasses
        for a in range(0, 360, 20):
            rad = math.radians(a)
            px[(int(cx - 4.5 + 3.6 * math.cos(rad)), int(cy - 2 + bob + 3.6 * math.sin(rad)))] = (110, 80, 50, 255)
            px[(int(cx + 4.5 + 3.6 * math.cos(rad)), int(cy - 2 + bob + 3.6 * math.sin(rad)))] = (110, 80, 50, 255)
        px[(cx - 1, cy - 2 + bob)] = (180, 140, 60, 255)
        px[(cx, cy - 2 + bob)] = (180, 140, 60, 255)
        px[(cx + 1, cy - 2 + bob)] = (180, 140, 60, 255)

        # Wizard Hat
        hat_purple = (110, 45, 185, 255)
        for y in range(cy - 28 + bob, cy - 14 + bob):
            h_dist = cy - 14 + bob - y
            cone_w = max(1, int(14 - h_dist * 0.9))
            for x in range(cx - cone_w, cx + cone_w + 1):
                px[(x, y)] = hat_purple
        fill_circle(px, cx, cy - 20 + bob, 2.5, (255, 225, 40, 255))

        # Magic Wand
        wand_x, wand_y = cx + 16, cy + 2 + bob
        fill_circle(px, wand_x, wand_y, 4.5, PINK_BODY)
        for i in range(1, 12): px[(wand_x + i//2, wand_y - i)] = (180, 120, 60, 255)
        fill_circle(px, wand_x + 6, wand_y - 12, 3.5, (255, 230, 50, 255))
        px[(wand_x + 6, wand_y - 12)] = WHITE

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/pet_wizard.webp", 180)


# ==========================================
# 8. バーニングソード (Burning Sword Kirby)
# ==========================================
def generate_burning_sword():
    frames = []
    for f in range(4):
        img = create_frame()
        px = {}
        cx, cy = 28, 34
        bob = -1 if f in [1, 2] else 0
        
        draw_feet(px, cx, cy + bob)
        draw_shaded_body(px, cx, cy + bob, radius=16)
        draw_cute_eyes(px, cx, cy + bob, 'sparkle')
        draw_cheeks_and_mouth(px, cx, cy + bob, 'open')

        # Flaming Knight Helmet
        for y in range(cy - 16 + bob, cy - 10 + bob):
            for x in range(cx - 14, cx + 15):
                if (x - cx)**2 <= 14**2: px[(x, y)] = (255, 200, 20, 255)
        fill_circle(px, cx, cy - 13 + bob, 3, (240, 30, 40, 255))
        px[(cx, cy - 14 + bob)] = WHITE

        # Flame Crest
        for y in range(cy - 30 + bob, cy - 15 + bob):
            h_ratio = (cy - 15 + bob - y) / 15.0
            flame_w = int(14 * (1.0 - h_ratio * 0.5))
            for x in range(cx - flame_w, cx + flame_w + 1):
                dist = abs(x - cx) / max(1, flame_w)
                if dist < 0.35: px[(x, y)] = (255, 255, 200, 255)
                elif dist < 0.7: px[(x, y)] = (255, 180, 20, 255)
                else: px[(x, y)] = (220, 30, 10, 255)

        # Huge Flaming Greatsword
        sw_x, sw_y = cx + 18, cy + 2 + bob
        fill_circle(px, sw_x, sw_y, 4.5, PINK_BODY)
        for i in range(1, 20):
            bx = sw_x + int(i * 0.8)
            by = sw_y - i
            px[(bx, by)] = (255, 255, 240, 255)
            px[(bx - 1, by)] = (255, 230, 80, 255)
            px[(bx + 1, by)] = (255, 120, 20, 255)
            px[(bx + 2, by)] = (255, 50, 10, 255)

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/pet_burning_sword.webp", 150)


# ==========================================
# 9. スパークブレード/カッター (Spark Cutter Kirby)
# ==========================================
def generate_spark_cutter():
    frames = []
    for f in range(4):
        img = create_frame()
        px = {}
        cx, cy = 30, 34
        bob = -1 if f in [1, 2] else 0
        
        draw_feet(px, cx, cy + bob)
        draw_shaded_body(px, cx, cy + bob, radius=16)
        draw_cute_eyes(px, cx, cy + bob, 'sparkle')
        draw_cheeks_and_mouth(px, cx, cy + bob, 'open')

        # Visor & Gold Helmet
        for x in range(cx - 10, cx + 11):
            for y in range(cy - 6 + bob, cy - 2 + bob): px[(x, y)] = (0, 220, 255, 220)
        for x in range(cx - 14, cx + 15):
            px[(x, cy - 12 + bob)] = (255, 215, 0, 255)

        # Boomerang Cutter
        for a in range(-60, 61, 6):
            rad = math.radians(a + (f * 5))
            bl_x = int(cx + 18 * math.cos(rad))
            bl_y = int(cy - 18 + bob + 10 * math.sin(rad))
            px[(bl_x, bl_y)] = WHITE
            px[(bl_x + 1, bl_y)] = (0, 230, 255, 255)

        # Hand blade
        sw_x, sw_y = cx + 17, cy + 2 + bob
        fill_circle(px, sw_x, sw_y, 4.5, PINK_BODY)
        for i in range(1, 16):
            px[(sw_x + i, sw_y - i)] = WHITE
            px[(sw_x + i + 1, sw_y - i)] = (0, 240, 255, 255)

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/pet_spark_cutter.webp", 150)


# ==========================================
# 10. フロストスパーク (Frost Spark Kirby)
# ==========================================
def generate_frost_spark():
    frames = []
    for f in range(4):
        img = create_frame()
        px = {}
        cx, cy = 32, 34
        bob = -1 if f in [1, 2] else 0
        
        draw_feet(px, cx, cy + bob)
        draw_shaded_body(px, cx, cy + bob, radius=16)
        draw_cute_eyes(px, cx, cy + bob, 'sparkle')
        draw_cheeks_and_mouth(px, cx, cy + bob, 'open')

        # Aurora Crystal Master Tiara
        for y in range(cy - 28 + bob, cy - 11 + bob):
            for x in range(cx - 15, cx + 16):
                dx = abs(x - cx)
                spike = 17 if dx <= 3 else (13 if dx <= 8 else 8)
                if cy - 11 + bob - y <= spike:
                    hue = (x + y + f * 2) % 4
                    if hue == 0: px[(x, y)] = (180, 245, 255, 255)
                    elif hue == 1: px[(x, y)] = (255, 255, 150, 255)
                    elif hue == 2: px[(x, y)] = (255, 170, 240, 255)
                    else: px[(x, y)] = WHITE

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/pet_frost_spark.webp", 150)


# ==========================================
# 11. スターレジェンド (Star Legend Kirby - Ultimate)
# ==========================================
def generate_star_legend():
    frames = []
    for f in range(4):
        img = create_frame()
        px = {}
        cx, cy = 28, 34
        bob = -1 if f in [1, 2] else 0
        
        draw_feet(px, cx, cy + bob)
        draw_shaded_body(px, cx, cy + bob, radius=16)
        draw_cute_eyes(px, cx, cy + bob, 'sparkle')
        draw_cheeks_and_mouth(px, cx, cy + bob, 'open')

        # Rainbow Star Crown
        for y in range(cy - 26 + bob, cy - 12 + bob):
            for x in range(cx - 15, cx + 16):
                dx = abs(x - cx)
                spike = 14 if dx in [0, 1, 2, 7, 8, 13, 14] else 9
                if cy - 12 + bob - y <= spike:
                    px[(x, y)] = (255, 215, 0, 255)
                    if (x + y) % 3 == 0: px[(x, y)] = (255, 255, 180, 255)
        fill_circle(px, cx, cy - 22 + bob, 3, (255, 60, 120, 255))
        px[(cx, cy - 22 + bob)] = WHITE

        # Legendary Star Rod (スターロッド)
        rod_x, rod_y = cx + 18, cy + 2 + bob
        fill_circle(px, rod_x, rod_y, 4.5, PINK_BODY)
        for i in range(1, 18):
            rx = rod_x + int(i * 0.4)
            ry = rod_y - i
            color = (255, 50, 80, 255) if (i // 3) % 2 == 0 else WHITE
            px[(rx, ry)] = color
        
        star_tip_x, star_tip_y = rod_x + 8, rod_y - 20
        fill_circle(px, star_tip_x, star_tip_y, 5, (255, 225, 30, 255))
        fill_circle(px, star_tip_x, star_tip_y, 2.5, WHITE)

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/pet_star_legend.webp", 150)


# ==========================================
# 12. もぐもぐ食べるカービィ (Eating Kirby)
# ==========================================
def generate_eating_kirby():
    frames = []
    for f in range(4):
        img = create_frame()
        px = {}
        cx, cy = 32, 34
        bob = -1 if f % 2 == 1 else 1
        squash = 2 if f % 2 == 0 else -1
        
        draw_feet(px, cx, cy + bob)
        draw_shaded_body(px, cx, cy + bob, radius=16, squash_x=squash, squash_y=-squash)
        draw_hands(px, cx, cy + bob, 'normal')
        draw_cute_eyes(px, cx, cy + bob, 'happy')
        draw_cheeks_and_mouth(px, cx, cy + bob, 'eating')

        if f in [1, 3]:
            px[(cx - 10, cy + 8 + bob)] = (255, 215, 0, 255)
            px[(cx + 11, cy + 7 + bob)] = (255, 180, 50, 255)

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/pet_eating.webp", 160)


# ==========================================
# 13. すいこみカービィ (Inhale Kirby)
# ==========================================
def generate_inhale_kirby():
    frames = []
    for f in range(4):
        img = create_frame()
        px = {}
        cx, cy = 34, 32
        
        draw_feet(px, cx - 2, cy + 2)
        draw_shaded_body(px, cx, cy, radius=18)
        draw_cute_eyes(px, cx, cy - 2, 'normal')
        draw_cheeks_and_mouth(px, cx, cy, 'inhale')
        
        fill_circle(px, cx - 18, cy + 6, 4, PINK_BODY)
        fill_circle(px, cx + 18, cy + 6, 4, PINK_BODY)

        # Inhale Wind Vortex
        v_offset = f * 3
        for r in range(12, 28, 4):
            arc_a = (v_offset * 15 + r * 10) % 360
            rad = math.radians(arc_a)
            wx = int(cx + r * math.cos(rad))
            wy = int(cy + 4 + (r * 0.6) * math.sin(rad))
            if 0 <= wx < SIZE and 0 <= wy < SIZE:
                px[(wx, wy)] = (240, 250, 255, 220)

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/pet_inhale.webp", 140)


# ==========================================
# 14. 病気カービィ (Sick Kirby)
# ==========================================
def generate_sick_kirby():
    frames = []
    for f in range(4):
        img = create_frame()
        px = {}
        cx, cy = 32, 36
        bob = 1 if f % 2 == 1 else 0
        
        draw_feet(px, cx, cy + bob)
        draw_shaded_body(px, cx, cy + bob, radius=16)
        draw_cute_eyes(px, cx, cy + bob, 'sick')
        
        for x in range(cx - 3, cx + 4):
            px[(x, cy + 4 + bob - abs(x - cx)//2)] = OUTLINE
        
        # Ice pack on head
        bag_y = cy - 16 + bob
        fill_circle(px, cx, bag_y, 6, (160, 220, 255, 255))
        fill_circle(px, cx, bag_y - 6, 2.5, (255, 215, 0, 255))

        if f in [1, 3]:
            fill_circle(px, cx + 13, cy - 4 + bob, 2, (100, 200, 255, 255))

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/pet_sick.webp", 200)


# ==========================================
# 15. おばけカービィ (Ghost Kirby)
# ==========================================
def generate_ghost_kirby():
    frames = []
    GHOST_WHITE = (230, 240, 255, 220)
    GHOST_SHADOW = (175, 195, 230, 220)
    GHOST_LIGHT = (255, 255, 255, 240)
    
    for f in range(4):
        img = create_frame()
        px = {}
        cx, cy = 32, 28
        float_y = int(math.sin(f * (math.pi / 2)) * 3)
        
        for y in range(cy - 14 + float_y, cy + 18 + float_y):
            for x in range(cx - 15, cx + 16):
                if y <= cy + 6 + float_y:
                    dist_sq = (x - cx)**2 / (15.0**2) + (y - (cy + float_y))**2 / (14.0**2)
                    if dist_sq <= 1.0:
                        px[(x, y)] = GHOST_WHITE
                        if x < cx - 4 and y < cy + float_y - 4: px[(x, y)] = GHOST_LIGHT
                    elif dist_sq <= 1.15:
                        px[(x, y)] = (80, 100, 140, 220)
                else:
                    wave = int(math.sin((y - cy) * 0.6 + f * 1.5) * 4)
                    tail_w = max(1, 14 - (y - (cy + 6 + float_y)))
                    if abs(x - cx + wave) <= tail_w:
                        px[(x, y)] = GHOST_SHADOW

        # Rounded Glowing Eyes
        fill_ellipse(px, cx - 5, cy - 1 + float_y, 2.5, 3.5, (30, 70, 150, 255))
        fill_ellipse(px, cx + 5, cy - 1 + float_y, 2.5, 3.5, (30, 70, 150, 255))
        px[(cx - 5, cy - 2 + float_y)] = WHITE
        px[(cx + 5, cy - 2 + float_y)] = WHITE
        fill_circle(px, cx, cy + 4 + float_y, 2.0, (30, 70, 150, 255))

        # Angel Halo
        halo_y = cy - 18 + float_y
        for x in range(cx - 10, cx + 11):
            px[(x, halo_y)] = (255, 230, 80, 255)
            px[(x, halo_y + 1)] = (255, 200, 40, 255)

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/pet_ghost.webp", 180)


# ==========================================
# 16. うんち (Poop)
# ==========================================
def generate_poop():
    frames = []
    POOP_BROWN = (190, 110, 40, 255)
    POOP_LIGHT = (225, 145, 60, 255)
    POOP_DARK = (130, 70, 20, 255)
    
    for f in range(2):
        img = create_frame()
        px = {}
        cx, cy = 32, 36
        bob = -1 if f == 1 else 0
        
        # 3-tier Soft Serve Poop Shape
        for y in range(cy + 4 + bob, cy + 14 + bob):
            for x in range(cx - 14, cx + 15):
                if (x - cx)**2 / 196.0 + (y - (cy + 9 + bob))**2 / 25.0 <= 1.0:
                    px[(x, y)] = POOP_LIGHT if y < cy + 8 + bob and x < cx else (POOP_DARK if y > cy + 10 + bob else POOP_BROWN)
        
        for y in range(cy - 4 + bob, cy + 6 + bob):
            for x in range(cx - 10, cx + 11):
                if (x - cx)**2 / 100.0 + (y - (cy + 1 + bob))**2 / 25.0 <= 1.0:
                    px[(x, y)] = POOP_LIGHT if y < cy and x < cx else (POOP_DARK if y > cy + 3 + bob else POOP_BROWN)

        for y in range(cy - 12 + bob, cy - 2 + bob):
            for x in range(cx - 6, cx + 7):
                if (x - cx)**2 / 36.0 + (y - (cy - 7 + bob))**2 / 20.0 <= 1.0:
                    px[(x, y)] = POOP_LIGHT if y < cy - 8 + bob else POOP_BROWN
        px[(cx + 2, cy - 13 + bob)] = POOP_LIGHT

        px[(cx - 14, cy - 8 + bob)] = (255, 230, 100, 255)
        px[(cx + 15, cy - 4 - bob)] = (255, 230, 100, 255)

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/poop.webp", 250)


# ==========================================
# 17. 敵キャラ：ワドルディ (Waddle Dee - Ultra Cute HD)
# ==========================================
def generate_waddle_dee():
    frames = []
    WD_ORANGE = (255, 140, 40, 255)
    WD_ORANGE_LIGHT = (255, 185, 90, 255)
    WD_ORANGE_SHADOW = (220, 95, 25, 255)
    WD_ORANGE_DEEP = (180, 65, 15, 255)
    WD_FACE = (255, 230, 195, 255)
    WD_FACE_LIGHT = (255, 245, 225, 255)
    WD_FACE_SHADOW = (240, 200, 160, 255)
    WD_FEET = (255, 205, 25, 255)
    WD_FEET_LIGHT = (255, 230, 80, 255)
    WD_FEET_SHADOW = (200, 145, 0, 255)
    
    for f in range(4):
        img = create_frame()
        px = {}
        cx, cy = 32, 34
        bob = -1 if f in [1, 2] else 0
        blink = (f == 2)
        
        # Yellow Feet (Chubby rounded ovals)
        for (fx, fy, is_l) in [(cx - 10, cy + 13 + bob, True), (cx + 10, cy + 13 + bob, False)]:
            for y in range(fy - 4, fy + 6):
                for x in range(fx - 7, fx + 8):
                    dist = (x - fx)**2 / 40.0 + (y - fy)**2 / 18.0
                    if dist <= 1.0:
                        if y < fy: px[(x, y)] = WD_FEET_LIGHT
                        elif y > fy + 2: px[(x, y)] = WD_FEET_SHADOW
                        else: px[(x, y)] = WD_FEET
                    elif dist <= 1.25:
                        px[(x, y)] = OUTLINE

        # Round Orange Body
        for y in range(cy - 18 + bob, cy + 17 + bob):
            for x in range(cx - 18, cx + 19):
                dx = (x - cx) / 16.0
                dy = (y - (cy + bob)) / 16.0
                dist_sq = dx * dx + dy * dy
                if dist_sq <= 1.0:
                    if dx < -0.25 and dy < -0.25 and dist_sq > 0.25: px[(x, y)] = WD_ORANGE_LIGHT
                    elif dy > 0.4: px[(x, y)] = WD_ORANGE_DEEP if dist_sq > 0.85 else WD_ORANGE_SHADOW
                    else: px[(x, y)] = WD_ORANGE
                elif dist_sq <= 1.18:
                    px[(x, y)] = OUTLINE

        # Heart-shaped Cream Face (Smooth round curve)
        for y in range(cy - 11 + bob, cy + 12 + bob):
            for x in range(cx - 12, cx + 13):
                dist = (x - cx)**2 / 130.0 + (y - (cy + bob + 0.5))**2 / 85.0
                if dist <= 1.0:
                    if y < cy + bob - 4: px[(x, y)] = WD_FACE_LIGHT
                    elif y > cy + bob + 6: px[(x, y)] = WD_FACE_SHADOW
                    else: px[(x, y)] = WD_FACE

        # Beautiful Rounded Eyes (Oval)
        if blink:
            for dx in range(-6, -1):
                px[(cx + dx, cy - 2 + bob)] = OUTLINE
            for dx in range(2, 7):
                px[(cx + dx, cy - 2 + bob)] = OUTLINE
        else:
            for (ecx, is_left) in [(cx - 4.5, True), (cx + 4.5, False)]:
                ecy = cy - 2.0 + bob
                fill_ellipse(px, ecx, ecy, 2.2, 4.2, (25, 35, 75, 255))
                # Outline
                for a in range(0, 360, 30):
                    rad = math.radians(a)
                    px[(int(ecx + 2.5 * math.cos(rad)), int(ecy + 4.5 * math.sin(rad)))] = OUTLINE
                # Top White Shine
                fill_ellipse(px, ecx - 0.4, ecy - 1.8, 1.2, 1.8, WHITE)
                # Bottom Blue Glow
                px[(int(ecx + 0.5), int(ecy + 2.0))] = (80, 160, 255, 255)

        # Cheeks (Cute Pink Ovals)
        fill_ellipse(px, cx - 8.5, cy + 2.5 + bob, 2.2, 1.5, (255, 100, 130, 255))
        fill_ellipse(px, cx + 8.5, cy + 2.5 + bob, 2.2, 1.5, (255, 100, 130, 255))

        # Little Hands
        fill_circle(px, cx - 15, cy + 4 + bob, 4.0, WD_ORANGE)
        px[(cx - 15, cy + 2 + bob)] = WD_ORANGE_LIGHT
        for a in range(0, 360, 30):
            rad = math.radians(a)
            px[(int(cx - 15 + 4.2 * math.cos(rad)), int(cy + 4 + bob + 4.2 * math.sin(rad)))] = OUTLINE

        fill_circle(px, cx + 15, cy + 4 + bob, 4.0, WD_ORANGE)
        px[(cx + 15, cy + 2 + bob)] = WD_ORANGE_LIGHT
        for a in range(0, 360, 30):
            rad = math.radians(a)
            px[(int(cx + 15 + 4.2 * math.cos(rad)), int(cy + 4 + bob + 4.2 * math.sin(rad)))] = OUTLINE

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/enemy_waddle_dee.webp", 180)


# ==========================================
# 18. 敵キャラ：デデデ大王 (King Dedede - Rich HD)
# ==========================================
def generate_king_dedede():
    frames = []
    for f in range(4):
        img = create_frame()
        px = {}
        cx, cy = 32, 34
        bob = -1 if f in [1, 2] else 0
        
        # Big Feet
        for fx in [cx - 11, cx + 11]:
            fill_ellipse(px, fx, cy + 17 + bob, 7.0, 3.5, (255, 200, 20, 255))
            fill_ellipse(px, fx, cy + 16 + bob, 6.0, 2.0, (255, 230, 80, 255))

        # Royal Red Robe
        for y in range(cy - 12 + bob, cy + 17 + bob):
            for x in range(cx - 19, cx + 20):
                if (x - cx)**2 / 340.0 + (y - (cy + 2 + bob))**2 / 210.0 <= 1.0:
                    px[(x, y)] = (215, 30, 40, 255)
                    if x < cx - 8: px[(x, y)] = (245, 60, 70, 255)
                    elif x > cx + 8: px[(x, y)] = (170, 15, 25, 255)

        # White Fur Trim on Robe
        for x in range(cx - 18, cx + 19):
            px[(x, cy + 13 + bob)] = WHITE
            px[(x, cy + 14 + bob)] = (220, 230, 245, 255)

        # Yellow Belly
        fill_ellipse(px, cx, cy + 3 + bob, 9.0, 9.0, (255, 230, 140, 255))
        fill_ellipse(px, cx, cy + 2 + bob, 8.0, 8.0, (255, 245, 180, 255))

        # Blue Penguin Face
        fill_ellipse(px, cx, cy - 9 + bob, 12.0, 10.0, (40, 110, 215, 255))
        fill_ellipse(px, cx - 3, cy - 11 + bob, 7.0, 5.0, (75, 145, 245, 255))

        # Yellow Beak (Smooth 3D shape)
        fill_ellipse(px, cx, cy - 3 + bob, 9.0, 4.5, (255, 195, 20, 255))
        fill_ellipse(px, cx, cy - 4 + bob, 7.5, 3.0, (255, 230, 70, 255))
        for x in range(cx - 8, cx + 9):
            px[(x, cy - 2 + bob)] = (210, 130, 10, 255)

        # Expressive Eyes
        for ecx in [cx - 4.5, cx + 4.5]:
            fill_ellipse(px, ecx, cy - 10 + bob, 2.2, 3.5, WHITE)
            fill_ellipse(px, ecx + (0.5 if ecx>cx else -0.5), cy - 10 + bob, 1.2, 2.2, BLACK)
            px[(int(ecx), cy - 11 + bob)] = WHITE

        # Royal Crown & Knit Hat
        for y in range(cy - 26 + bob, cy - 15 + bob):
            for x in range(cx - 12, cx + 13):
                if abs(x - cx) <= 12 - (cy - 15 + bob - y):
                    px[(x, y)] = (215, 30, 40, 255)
        fill_circle(px, cx, cy - 26 + bob, 4.0, (255, 220, 40, 255))
        px[(cx, cy - 27 + bob)] = WHITE

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/enemy_king_dedede.webp", 180)


# ==========================================
# 19. 敵キャラ：ゴルドー (Gordo - Spiky HD)
# ==========================================
def generate_gordo():
    frames = []
    for f in range(4):
        img = create_frame()
        px = {}
        cx, cy = 32, 32
        
        # 8 Massive Spikes with 3D Shading
        for a in range(0, 360, 45):
            rad = math.radians(a + (f * 8))
            for dist in range(12, 27):
                sx = int(cx + dist * math.cos(rad))
                sy = int(cy + dist * math.sin(rad))
                if 0 <= sx < SIZE and 0 <= sy < SIZE:
                    px[(sx, sy)] = (210, 220, 240, 255) if dist > 22 else (110, 120, 145, 255)

        # Core Iron Sphere with Sphere Shading
        for y in range(cy - 15, cy + 16):
            for x in range(cx - 15, cx + 16):
                dx = (x - cx) / 14.0
                dy = (y - cy) / 14.0
                dist_sq = dx*dx + dy*dy
                if dist_sq <= 1.0:
                    if dx < -0.3 and dy < -0.3: px[(x, y)] = (150, 165, 195, 255)
                    elif dx < 0 and dy < 0: px[(x, y)] = (95, 105, 130, 255)
                    elif dy > 0.4: px[(x, y)] = (40, 45, 60, 255)
                    else: px[(x, y)] = (65, 75, 95, 255)
                elif dist_sq <= 1.15:
                    px[(x, y)] = OUTLINE

        # Giant Staring Oval Eyes
        p_offset = 1 if f in [1, 2] else -1
        for (ecx, is_left) in [(cx - 5.5, True), (cx + 5.5, False)]:
            fill_ellipse(px, ecx, cy - 1, 3.2, 5.0, WHITE)
            fill_ellipse(px, ecx + p_offset * 0.8, cy - 1, 1.8, 3.0, BLACK)
            px[(int(ecx + p_offset * 0.8), cy - 2)] = WHITE

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/enemy_gordo.webp", 180)


# ==========================================
# 20. 敵キャラ：ブロントバート (Bronto Burt - Cute Fluttering HD)
# ==========================================
def generate_bronto_burt():
    frames = []
    for f in range(4):
        img = create_frame()
        px = {}
        cx, cy = 32, 32
        bob = -2 if f in [1, 3] else 2
        
        # Feathered Wings Fluttering
        wing_y = cy - 6 + bob + (-5 if f in [0, 2] else 5)
        for (wx, is_left) in [(cx - 16, True), (cx + 16, False)]:
            fill_ellipse(px, wx, wing_y, 8.0, 5.0, WHITE)
            fill_ellipse(px, wx + (-1 if is_left else 1), wing_y, 6.0, 3.5, (235, 245, 255, 255))

        # Round Pinkish-Purple Body
        for y in range(cy - 14 + bob, cy + 15 + bob):
            for x in range(cx - 14, cx + 15):
                dx = (x - cx) / 13.0
                dy = (y - (cy + bob)) / 13.0
                dist_sq = dx*dx + dy*dy
                if dist_sq <= 1.0:
                    if dx < -0.25 and dy < -0.25: px[(x, y)] = (255, 140, 185, 255)
                    elif dy > 0.4: px[(x, y)] = (185, 40, 95, 255)
                    else: px[(x, y)] = (235, 75, 130, 255)
                elif dist_sq <= 1.18:
                    px[(x, y)] = OUTLINE

        # Fierce Angry Slanted Eyes (キリッと怒った鋭いツリ目)
        for (ecx, is_left) in [(cx - 5.5, True), (cx + 5.5, False)]:
            ecy = cy - 2.0 + bob
            sgn = -1 if is_left else 1
            
            # Slanted oval white eye & black pupil
            for dy in range(-4, 5):
                for dx in range(-4, 5):
                    # Rotate coordinates for slanted eye angle
                    angle = math.radians(-sgn * 25)
                    u = (dx * math.cos(angle) - dy * math.sin(angle))
                    v = (dx * math.sin(angle) + dy * math.cos(angle))
                    
                    dist = (u / 2.6)**2 + (v / 3.8)**2
                    if dist <= 1.0:
                        # Slanted brow cutoff
                        if v < -0.7 and u * sgn > -0.8:
                            px[(int(ecx + dx), int(ecy + dy))] = OUTLINE
                        else:
                            px[(int(ecx + dx), int(ecy + dy))] = WHITE
                            # Sharp dark pupil glaring inward
                            p_dx = dx - sgn * 0.5
                            p_dy = dy + 0.2
                            if (p_dx / 1.5)**2 + (p_dy / 2.2)**2 <= 1.0:
                                px[(int(ecx + dx), int(ecy + dy))] = (20, 15, 35, 255)
                                if abs(dx - sgn * 0.2) < 0.8 and dy == 0:
                                    px[(int(ecx + dx), int(ecy + dy))] = WHITE
                    elif dist <= 1.35:
                        px[(int(ecx + dx), int(ecy + dy))] = OUTLINE

            # Sharp Angry Brow Over Eyelid
            for i in range(-4, 5):
                bx = int(ecx + i)
                by = int(ecy - 3 - sgn * i * 0.6)
                px[(bx, by)] = OUTLINE
                px[(bx, by + 1)] = OUTLINE

        # Angry Determined Mouth (キリッとしたへの字口)
        for mx in range(cx - 3, cx + 4):
            my = cy + 5 + bob + abs(mx - cx) // 2
            px[(mx, my)] = OUTLINE
            px[(mx, my - 1)] = (175, 20, 55, 255)
        
        # Little feet
        fill_ellipse(px, cx - 4, cy + 12 + bob, 2.5, 1.5, (255, 200, 40, 255))
        fill_ellipse(px, cx + 4, cy + 12 + bob, 2.5, 1.5, (255, 200, 40, 255))

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/enemy_bronto_burt.webp", 150)


# ==========================================
# 21. 敵キャラ追加：メタナイト (Meta Knight - Ultra Cool HD)
# ==========================================
def draw_meta_knight_bat_wings(px, cx, cy, bob, f):
    """
    Ultra-detailed, realistic bat wings (リアルで迫力あるコウモリ/悪魔の翼)
    Features:
      - Articulated upper arm bone with golden elbow/wrist talon
      - 3 radiating finger bones (struts) forming sharp wing tips
      - Scalloped (crescent cutout) leathery membrane with smooth purple gradient
      - Dynamic flapping animation (4 frames)
    """
    WING_OUTLINE = (20, 10, 45, 255)
    WING_DARK = (45, 18, 85, 255)
    WING_MID = (70, 32, 125, 255)
    WING_LIGHT = (105, 52, 175, 255)
    WING_BONE_LIGHT = (145, 80, 220, 255)
    WING_TALON = (255, 215, 40, 255)
    WING_TALON_LIGHT = (255, 255, 180, 255)

    flap_offsets = [-3, 0, 3, 0]
    flap = flap_offsets[f % 4]

    def point_in_triangle(pt, v1, v2, v3):
        def sign(p1, p2, p3):
            return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
        d1 = sign(pt, v1, v2)
        d2 = sign(pt, v2, v3)
        d3 = sign(pt, v3, v1)
        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
        return not (has_neg and has_pos)

    def draw_thick_line(px, p1, p2, color, thickness=1):
        x1, y1 = p1
        x2, y2 = p2
        dist = max(1, int(math.hypot(x2 - x1, y2 - y1) * 2))
        for i in range(dist + 1):
            t = i / dist
            x = int(x1 + t * (x2 - x1))
            y = int(y1 + t * (y2 - y1))
            for tx in range(-thickness, thickness + 1):
                for ty in range(-thickness, thickness + 1):
                    if tx*tx + ty*ty <= thickness*thickness:
                        px[(x + tx, y + ty)] = color

    for is_left in [True, False]:
        sgn = -1 if is_left else 1

        # Key Anchors
        root = (cx + sgn * 6, cy - 2 + bob)
        joint = (cx + sgn * 22, cy - 15 + bob + flap)
        tip1 = (cx + sgn * 29, cy - 4 + bob + int(flap * 1.3))
        tip2 = (cx + sgn * 25, cy + 8 + bob + int(flap * 0.8))
        tip3 = (cx + sgn * 15, cy + 14 + bob + int(flap * 0.4))

        # 1. Fill Membrane Polygons
        triangles = [
            (root, joint, tip1),
            (root, tip1, tip2),
            (root, tip2, tip3)
        ]

        min_x = min(root[0], joint[0], tip1[0], tip2[0], tip3[0]) - 2
        max_x = max(root[0], joint[0], tip1[0], tip2[0], tip3[0]) + 2
        min_y = min(root[1], joint[1], tip1[1], tip2[1], tip3[1]) - 2
        max_y = max(root[1], joint[1], tip1[1], tip2[1], tip3[1]) + 2

        # Scallop cutout circles (centers placed to carve inner curves)
        # Cutout 1: between tip1 and tip2
        c1_x = (tip1[0] + tip2[0]) / 2 - sgn * 2.5
        c1_y = (tip1[1] + tip2[1]) / 2 - 1.5
        r1_sq = (math.hypot(tip1[0] - tip2[0], tip1[1] - tip2[1]) * 0.44)**2

        # Cutout 2: between tip2 and tip3
        c2_x = (tip2[0] + tip3[0]) / 2 - sgn * 2.0
        c2_y = (tip2[1] + tip3[1]) / 2 - 1.0
        r2_sq = (math.hypot(tip2[0] - tip3[0], tip2[1] - tip3[1]) * 0.44)**2

        # Cutout 3: between tip3 and root
        c3_x = (tip3[0] + root[0]) / 2 - sgn * 1.5
        c3_y = (tip3[1] + root[1]) / 2 + 1.0
        r3_sq = (math.hypot(tip3[0] - root[0], tip3[1] - root[1]) * 0.44)**2

        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                pt = (x, y)
                # Check if in any triangle
                in_membrane = any(point_in_triangle(pt, v1, v2, v3) for v1, v2, v3 in triangles)
                if in_membrane:
                    # Check if inside scalloped cutouts
                    in_cut1 = (x - c1_x)**2 + (y - c1_y)**2 < r1_sq
                    in_cut2 = (x - c2_x)**2 + (y - c2_y)**2 < r2_sq
                    in_cut3 = (x - c3_x)**2 + (y - c3_y)**2 < r3_sq

                    if not (in_cut1 or in_cut2 or in_cut3):
                        # Gradient shading based on height & depth
                        rel_y = (y - min_y) / max(1, (max_y - min_y))
                        dist_root = math.hypot(x - root[0], y - root[1])
                        
                        if rel_y < 0.25:
                            px[(x, y)] = WING_LIGHT
                        elif rel_y < 0.65 and dist_root > 6:
                            px[(x, y)] = WING_MID
                        else:
                            px[(x, y)] = WING_DARK

        # 2. Draw Skeletal Arm & Strut Bones (Thick lines with highlights)
        # Main Upper Arm
        draw_thick_line(px, root, joint, WING_MID, thickness=1)
        draw_thick_line(px, (root[0], root[1]-1), (joint[0], joint[1]-1), WING_BONE_LIGHT, thickness=0)

        # Finger Struts
        draw_thick_line(px, joint, tip1, WING_MID, thickness=1)
        draw_thick_line(px, joint, tip2, WING_MID, thickness=1)
        draw_thick_line(px, root, tip3, WING_DARK, thickness=1)

        # Bone Highlights
        draw_thick_line(px, (joint[0] - sgn, joint[1] - 1), (tip1[0] - sgn, tip1[1] - 1), WING_BONE_LIGHT, thickness=0)
        draw_thick_line(px, (joint[0] - sgn, joint[1]), (tip2[0] - sgn, tip2[1]), WING_BONE_LIGHT, thickness=0)

        # 3. Outer Edge Outline
        for y in range(min_y - 1, max_y + 2):
            for x in range(min_x - 1, max_x + 2):
                if (x, y) in px and px[(x, y)] in [WING_DARK, WING_MID, WING_LIGHT, WING_BONE_LIGHT]:
                    # Check if neighbor is empty
                    for nx, ny in [(x+1,y), (x-1,y), (x,y+1), (x,y-1)]:
                        if (nx, ny) not in px:
                            px[(nx, ny)] = WING_OUTLINE

        # 4. Golden Talons on Wing Joints & Tips
        # Elbow/Wrist Upper Talon
        fill_circle(px, joint[0], joint[1], 1.8, WING_TALON)
        px[(joint[0], joint[1] - 1)] = WING_TALON_LIGHT
        px[(joint[0] + sgn * 2, joint[1] - 2)] = WING_TALON
        px[(joint[0] + sgn * 3, joint[1] - 3)] = WING_TALON_LIGHT

        # Sharp claw tips
        px[tip1] = WING_TALON
        px[(tip1[0] + sgn, tip1[1])] = WING_TALON_LIGHT
        px[tip2] = WING_TALON
        px[tip3] = WING_TALON


def generate_meta_knight():
    frames = []
    MK_NAVY = (35, 45, 95, 255)
    MK_NAVY_LIGHT = (55, 70, 135, 255)
    MK_NAVY_DARK = (20, 25, 60, 255)
    
    MASK_SILVER = (200, 210, 225, 255)
    MASK_LIGHT = (245, 250, 255, 255)
    MASK_SHADOW = (130, 145, 170, 255)
    MASK_DARK = (75, 85, 105, 255)
    
    for f in range(4):
        img = create_frame()
        px = {}
        cx, cy = 32, 34
        bob = -1 if f in [1, 2] else 0
        eye_glow = (255, 240, 50, 255) if f % 2 == 0 else (255, 210, 20, 255)
        
        # 1. Realistic Dimensional Bat Wings Flapping in Background
        draw_meta_knight_bat_wings(px, cx, cy, bob, f)

        # 2. Shoulder Pauldrons (White/Silver with Gold Trim)
        fill_ellipse(px, cx - 15, cy - 6 + bob, 4.5, 4.0, MASK_SILVER)
        fill_ellipse(px, cx - 15, cy - 7 + bob, 3.5, 2.5, MASK_LIGHT)
        for a in range(0, 360, 30):
            rad = math.radians(a)
            px[(int(cx - 15 + 4.5 * math.cos(rad)), int(cy - 6 + bob + 4.0 * math.sin(rad)))] = (255, 215, 0, 255)

        fill_ellipse(px, cx + 15, cy - 6 + bob, 4.5, 4.0, MASK_SILVER)
        fill_ellipse(px, cx + 15, cy - 7 + bob, 3.5, 2.5, MASK_LIGHT)
        for a in range(0, 360, 30):
            rad = math.radians(a)
            px[(int(cx + 15 + 4.5 * math.cos(rad)), int(cy - 6 + bob + 4.0 * math.sin(rad)))] = (255, 215, 0, 255)

        # 3. Navy Blue Feet
        for fx in [cx - 10, cx + 10]:
            fill_ellipse(px, fx, cy + 14 + bob, 6.0, 3.5, (120, 40, 160, 255))
            fill_ellipse(px, fx, cy + 13 + bob, 5.0, 2.0, (160, 70, 205, 255))

        # 4. Round Navy Body
        for y in range(cy - 16 + bob, cy + 15 + bob):
            for x in range(cx - 16, cx + 17):
                dx = (x - cx) / 15.0
                dy = (y - (cy + bob)) / 15.0
                dist_sq = dx*dx + dy*dy
                if dist_sq <= 1.0:
                    if dx < -0.25 and dy < -0.25: px[(x, y)] = MK_NAVY_LIGHT
                    elif dy > 0.4: px[(x, y)] = MK_NAVY_DARK
                    else: px[(x, y)] = MK_NAVY
                elif dist_sq <= 1.18:
                    px[(x, y)] = OUTLINE

        # 5. Silver Mask (Faceplate)
        for y in range(cy - 13 + bob, cy + 9 + bob):
            for x in range(cx - 13, cx + 14):
                dx = (x - cx) / 12.5
                dy = (y - (cy - 2 + bob)) / 10.0
                dist_sq = dx*dx + dy*dy
                if dist_sq <= 1.0:
                    if dx < -0.2 and dy < -0.2: px[(x, y)] = MASK_LIGHT
                    elif dx > 0.3 or dy > 0.4: px[(x, y)] = MASK_SHADOW
                    else: px[(x, y)] = MASK_SILVER
                elif dist_sq <= 1.18:
                    px[(x, y)] = MASK_DARK

        # Mask T-Slit / Visor Cutouts & Glowing Yellow Eyes
        # Slit line
        for y in range(cy - 8 + bob, cy + 7 + bob):
            px[(cx, y)] = MASK_DARK
        for x in range(cx - 10, cx + 11):
            px[(x, cy - 2 + bob)] = MASK_DARK

        # Glowing Yellow Eyes (Piercing Angled Eyes)
        for (ecx, is_left) in [(cx - 5.5, True), (cx + 5.5, False)]:
            ecy = cy - 2.0 + bob
            # Slanted oval eye
            for dx in range(-4, 4):
                for dy in range(-2, 3):
                    if is_left:
                        if abs(dx + dy * 0.5) <= 2.5 and abs(dy) <= 1.8:
                            px[(int(ecx + dx), int(ecy + dy))] = eye_glow
                    else:
                        if abs(dx - dy * 0.5) <= 2.5 and abs(dy) <= 1.8:
                            px[(int(ecx + dx), int(ecy + dy))] = eye_glow
            px[(int(ecx), int(ecy - 1))] = WHITE

        # 6. Legendary Golden Sword Galaxia in Hand!
        sw_x = cx + 17
        sw_y = cy + 4 + bob
        fill_circle(px, sw_x, sw_y, 4.0, MK_NAVY) # Hand
        
        # Golden Spiked Hilt
        for gy in range(sw_y - 4, sw_y + 5):
            px[(sw_x + 1, gy)] = (255, 215, 0, 255)
            px[(sw_x + 2, gy)] = (255, 180, 0, 255)
        # Ruby Gem on Hilt
        px[(sw_x + 1, sw_y)] = (255, 40, 80, 255)
        
        # Jagged Golden Blade (Galaxia)
        for i in range(1, 18):
            bx = sw_x + int(i * 0.6)
            by = sw_y - i
            px[(bx, by)] = (255, 255, 200, 255) # Core
            px[(bx + 1, by)] = (255, 215, 0, 255) # Edge
            # Lightning spikes on Galaxia blade
            if i in [5, 6, 11, 12]:
                px[(bx + 2, by)] = (255, 215, 0, 255)
                px[(bx - 1, by)] = (255, 215, 0, 255)

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/enemy_meta_knight.webp", 160)


# ==========================================
# Run all generator functions
# ==========================================
if __name__ == "__main__":
    print("Starting generation of 64x64 HD cute rounded pixel art sprites...")
    generate_baby_kirby()
    generate_normal_kirby()
    generate_fire_kirby()
    generate_sword_kirby()
    generate_spark_kirby()
    generate_ice_kirby()
    generate_wizard_kirby()
    generate_burning_sword()
    generate_spark_cutter()
    generate_frost_spark()
    generate_star_legend()
    generate_eating_kirby()
    generate_inhale_kirby()
    generate_sick_kirby()
    generate_ghost_kirby()
    generate_poop()
    generate_waddle_dee()
    generate_king_dedede()
    generate_gordo()
    generate_bronto_burt()
    generate_meta_knight()
    print("All 21 HD sprites generated successfully!")
