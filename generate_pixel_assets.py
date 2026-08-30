import os
from PIL import Image, ImageDraw

os.makedirs("assets/sprites", exist_ok=True)

SCALE = 4  # 32x32 -> 128x128
SIZE = 32

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

# --- Helper Draw Routines ---
PINK = (255, 140, 180, 255)
PINK_SHADOW = (225, 95, 140, 255)
PINK_HIGHLIGHT = (255, 190, 215, 255)
RED_FEET = (235, 30, 75, 255)
RED_FEET_SHADOW = (180, 15, 50, 255)
BLACK = (20, 20, 25, 255)
WHITE = (255, 255, 255, 255)
CHEEK = (255, 80, 130, 255)
DIAPER_WHITE = (245, 245, 250, 255)
DIAPER_SHADOW = (195, 200, 215, 255)
DIAPER_PIN = (255, 215, 0, 255)

def draw_base_body(px, cx, cy, radius, bob=0, squash=0):
    """Draw circular Kirby body with outline and shading"""
    rx = int(radius + squash)
    ry = int(radius - squash)
    for y in range(cy - ry - 2, cy + ry + 3):
        for x in range(cx - rx - 2, cx + rx + 3):
            dx = (x - cx) / radius
            dy = (y - cy) / radius
            dist_sq = dx * dx + dy * dy
            if dist_sq <= 1.0:
                # Main body
                if dx < -0.3 and dy < -0.3:
                    px[(x, y)] = PINK_HIGHLIGHT
                elif dy > 0.4 or dx > 0.4:
                    px[(x, y)] = PINK_SHADOW
                else:
                    px[(x, y)] = PINK
            elif dist_sq <= 1.25:
                # Outline
                px[(x, y)] = BLACK

def draw_eyes_and_cheeks(px, cx, cy, blink=False, happy=False):
    if blink:
        # Closed smiling eyes
        for dx in [-3, -2, -1]:
            px[(cx + dx, cy - 1)] = BLACK
        for dx in [1, 2, 3]:
            px[(cx + dx, cy - 1)] = BLACK
    elif happy:
        # Happy arched eyes ^^
        px[(cx - 3, cy - 1)] = BLACK
        px[(cx - 2, cy - 2)] = BLACK
        px[(cx - 1, cy - 1)] = BLACK
        px[(cx + 1, cy - 1)] = BLACK
        px[(cx + 2, cy - 2)] = BLACK
        px[(cx + 3, cy - 1)] = BLACK
    else:
        # Standard Kirby oval eyes with highlight
        # Left eye
        px[(cx - 3, cy - 3)] = BLACK
        px[(cx - 2, cy - 3)] = BLACK
        px[(cx - 3, cy - 2)] = WHITE  # Highlight
        px[(cx - 2, cy - 2)] = BLACK
        px[(cx - 3, cy - 1)] = (30, 80, 180, 255) # Blue eye base
        px[(cx - 2, cy - 1)] = BLACK
        px[(cx - 3, cy)] = BLACK
        px[(cx - 2, cy)] = BLACK

        # Right eye
        px[(cx + 2, cy - 3)] = BLACK
        px[(cx + 3, cy - 3)] = BLACK
        px[(cx + 2, cy - 2)] = WHITE  # Highlight
        px[(cx + 3, cy - 2)] = BLACK
        px[(cx + 2, cy - 1)] = (30, 80, 180, 255)
        px[(cx + 3, cy - 1)] = BLACK
        px[(cx + 2, cy)] = BLACK
        px[(cx + 3, cy)] = BLACK

    # Cheeks
    px[(cx - 5, cy + 1)] = CHEEK
    px[(cx - 4, cy + 1)] = CHEEK
    px[(cx + 4, cy + 1)] = CHEEK
    px[(cx + 5, cy + 1)] = CHEEK

    # Small mouth
    if happy:
        px[(cx - 1, cy + 2)] = (200, 30, 50, 255)
        px[(cx, cy + 2)] = (240, 60, 80, 255)
        px[(cx + 1, cy + 2)] = (200, 30, 50, 255)
        px[(cx, cy + 3)] = BLACK
    else:
        px[(cx, cy + 2)] = BLACK

def draw_feet(px, cx, cy, f_offset=0):
    # Left foot
    for fx in range(cx - 8, cx - 3):
        for fy in range(cy + 6 + f_offset, cy + 10 + f_offset):
            px[(fx, fy)] = RED_FEET
    px[(cx - 9, cy + 8 + f_offset)] = BLACK
    px[(cx - 3, cy + 9 + f_offset)] = RED_FEET_SHADOW

    # Right foot
    for fx in range(cx + 3, cx + 8):
        for fy in range(cy + 6 - f_offset, cy + 10 - f_offset):
            px[(fx, fy)] = RED_FEET
    px[(cx + 8, cy + 8 - f_offset)] = BLACK
    px[(cx + 3, cy + 9 - f_offset)] = RED_FEET_SHADOW

def draw_hands(px, cx, cy, h_up=False):
    if h_up:
        # Hands cheering up
        for hx in range(cx - 9, cx - 6):
            for hy in range(cy - 4, cy):
                px[(hx, hy)] = PINK
        for hx in range(cx + 6, cx + 9):
            for hy in range(cy - 4, cy):
                px[(hx, hy)] = PINK
        px[(cx - 10, cy - 2)] = BLACK
        px[(cx + 9, cy - 2)] = BLACK
    else:
        # Hands resting at side
        for hx in range(cx - 9, cx - 6):
            for hy in range(cy + 1, cy + 4):
                px[(hx, hy)] = PINK
        for hx in range(cx + 6, cx + 9):
            for hy in range(cy + 1, cy + 4):
                px[(hx, hy)] = PINK

# 1. おむつカービィ (Baby Kirby)
def generate_baby_kirby():
    frames = []
    for frame_idx in range(4):
        img = create_frame()
        px = {}
        cx, cy = 16, 17
        bob = 1 if frame_idx in [1, 3] else 0
        blink = (frame_idx == 2)
        
        # Small baby body
        draw_base_body(px, cx, cy + bob, radius=6.5, bob=bob)
        
        # Diaper (おむつ)
        for dy in range(cy + 2 + bob, cy + 7 + bob):
            for dx in range(cx - 6, cx + 7):
                if (dx - cx)**2 + (dy - (cy + bob))**2 <= 6.8**2:
                    if dy >= cy + 3 + bob:
                        px[(dx, dy)] = DIAPER_WHITE
                        if dy == cy + 6 + bob:
                            px[(dx, dy)] = DIAPER_SHADOW
        # Diaper pin / badge
        px[(cx - 3, cy + 4 + bob)] = DIAPER_PIN
        px[(cx - 2, cy + 4 + bob)] = (255, 165, 0, 255)

        # Baby eyes (bigger/rounder)
        if blink:
            for dx in [-2, -1]: px[(cx + dx, cy - 1 + bob)] = BLACK
            for dx in [1, 2]: px[(cx + dx, cy - 1 + bob)] = BLACK
        else:
            px[(cx - 2, cy - 2 + bob)] = WHITE
            px[(cx - 2, cy - 1 + bob)] = BLACK
            px[(cx - 2, cy + bob)] = (50, 100, 220, 255)
            px[(cx + 2, cy - 2 + bob)] = WHITE
            px[(cx + 2, cy - 1 + bob)] = BLACK
            px[(cx + 2, cy + bob)] = (50, 100, 220, 255)
        
        # Pacifier (おしゃぶり) or baby cheeks
        px[(cx - 4, cy + 1 + bob)] = CHEEK
        px[(cx + 4, cy + 1 + bob)] = CHEEK
        # Yellow pacifier ring
        px[(cx - 1, cy + 1 + bob)] = (255, 230, 50, 255)
        px[(cx, cy + 1 + bob)] = (255, 200, 0, 255)
        px[(cx + 1, cy + 1 + bob)] = (255, 230, 50, 255)
        px[(cx, cy + 2 + bob)] = (255, 140, 0, 255)

        # Tiny baby feet crawling
        f_crawl = 1 if frame_idx in [1, 2] else -1
        px[(cx - 5 + f_crawl, cy + 7 + bob)] = RED_FEET
        px[(cx + 5 - f_crawl, cy + 7 + bob)] = RED_FEET

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/pet_baby.webp", 200)

# 2. 普通カービィ (Normal Kirby)
def generate_normal_kirby():
    frames = []
    for frame_idx in range(4):
        img = create_frame()
        px = {}
        cx, cy = 16, 16
        bob = -1 if frame_idx in [1, 2] else 0
        blink = (frame_idx == 3)
        squash = 1 if frame_idx == 0 else 0

        draw_feet(px, cx, cy + bob, f_offset=bob)
        draw_base_body(px, cx, cy + bob, radius=7.5, squash=squash)
        draw_hands(px, cx, cy + bob, h_up=(frame_idx == 2))
        draw_eyes_and_cheeks(px, cx, cy + bob, blink=blink, happy=(frame_idx == 2))

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/pet_normal.webp", 180)

# 3. 単能力：ファイア (Fire Kirby)
def generate_fire_kirby():
    frames = []
    for frame_idx in range(4):
        img = create_frame()
        px = {}
        cx, cy = 16, 17
        bob = -1 if frame_idx in [1, 2] else 0
        
        draw_feet(px, cx, cy + bob)
        draw_base_body(px, cx, cy + bob, radius=7.5)
        draw_hands(px, cx, cy + bob)
        draw_eyes_and_cheeks(px, cx, cy + bob, happy=True)

        # Fire crown / Flaming headgear
        flame_colors = [(255, 50, 0, 255), (255, 140, 0, 255), (255, 230, 0, 255)]
        shift = frame_idx % 2
        for fy in range(cy - 12 + bob, cy - 6 + bob):
            for fx in range(cx - 5, cx + 6):
                dist = abs(fx - cx) + abs(fy - (cy - 10 + bob))
                if dist <= 4 + shift:
                    c = flame_colors[(fy + fx + frame_idx) % len(flame_colors)]
                    px[(fx, fy)] = c
        # Crown base
        for fx in range(cx - 6, cx + 7):
            px[(fx, cy - 6 + bob)] = (180, 30, 0, 255)
            px[(fx, cy - 7 + bob)] = (255, 100, 0, 255)

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/pet_fire.webp", 160)

# 4. 単能力：ソード (Sword Kirby)
def generate_sword_kirby():
    frames = []
    for frame_idx in range(4):
        img = create_frame()
        px = {}
        cx, cy = 16, 16
        bob = -1 if frame_idx in [1, 2] else 0

        draw_feet(px, cx, cy + bob)
        draw_base_body(px, cx, cy + bob, radius=7.5)
        draw_eyes_and_cheeks(px, cx, cy + bob)

        # Green Link-style Cap
        for cy_cap in range(cy - 11 + bob, cy - 5 + bob):
            for cx_cap in range(cx - 6, cx + 7):
                if cx_cap <= cx + (cy - 5 + bob - cy_cap) * 2 - 2:
                    px[(cx_cap, cy_cap)] = (34, 139, 34, 255)
                    if cy_cap == cy - 6 + bob:
                        px[(cx_cap, cy_cap)] = (0, 100, 0, 255)
        # Cap tip drooping right
        px[(cx + 7, cy - 6 + bob + frame_idx % 2)] = (50, 180, 50, 255)
        px[(cx + 8, cy - 5 + bob + frame_idx % 2)] = (50, 180, 50, 255)
        px[(cx + 9, cy - 4 + bob + frame_idx % 2)] = (255, 215, 0, 255) # Yellow pompom

        # Sword in hand
        sw_y = cy - 2 + bob
        # Blade
        for i in range(7):
            px[(cx + 8 + i//2, sw_y - i)] = (220, 230, 255, 255)
            px[(cx + 9 + i//2, sw_y - i)] = (180, 200, 230, 255)
        # Hilt
        px[(cx + 7, sw_y + 1)] = (255, 215, 0, 255)
        px[(cx + 8, sw_y + 1)] = (160, 82, 45, 255)
        px[(cx + 9, sw_y + 1)] = (255, 215, 0, 255)

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/pet_sword.webp", 180)

# 5. 単能力：スパーク (Spark Kirby)
def generate_spark_kirby():
    frames = []
    for frame_idx in range(4):
        img = create_frame()
        px = {}
        cx, cy = 16, 16
        bob = -1 if frame_idx in [1, 2] else 0

        draw_feet(px, cx, cy + bob)
        draw_base_body(px, cx, cy + bob, radius=7.5)
        draw_hands(px, cx, cy + bob, h_up=True)
        draw_eyes_and_cheeks(px, cx, cy + bob, happy=True)

        # Plasma / Electric Hat with glowing lightning sparks
        for hx in range(cx - 5, cx + 6):
            px[(hx, cy - 7 + bob)] = (255, 215, 0, 255)
            px[(hx, cy - 8 + bob)] = (255, 255, 100, 255)
        
        # Electric bolts shooting out
        shift = frame_idx * 2
        sparks = [
            (cx - 8, cy - 10 + bob + (shift%3)),
            (cx - 6, cy - 12 + bob),
            (cx + 6, cy - 12 + bob),
            (cx + 8, cy - 9 + bob - (shift%3)),
            (cx - 10, cy + bob),
            (cx + 10, cy + bob)
        ]
        for sx, sy in sparks:
            if 0 <= sx < SIZE and 0 <= sy < SIZE:
                px[(sx, sy)] = (255, 255, 255, 255)
                px[(sx+1, sy)] = (100, 240, 255, 255)

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/pet_spark.webp", 150)

# 6. 単能力：アイス (Ice Kirby)
def generate_ice_kirby():
    frames = []
    for frame_idx in range(4):
        img = create_frame()
        px = {}
        cx, cy = 16, 16
        bob = -1 if frame_idx in [1, 2] else 0

        draw_feet(px, cx, cy + bob)
        draw_base_body(px, cx, cy + bob, radius=7.5)
        draw_hands(px, cx, cy + bob)
        draw_eyes_and_cheeks(px, cx, cy + bob)

        # Ice Crown / Frost Spikes
        ice_light = (200, 240, 255, 255)
        ice_deep = (0, 160, 240, 255)
        for cy_crown in range(cy - 12 + bob, cy - 6 + bob):
            for cx_crown in range(cx - 5, cx + 6):
                if (cx_crown - cx) % 3 == 0 or cy_crown == cy - 7 + bob:
                    px[(cx_crown, cy_crown)] = ice_light
                elif abs(cx_crown - cx) <= 4:
                    px[(cx_crown, cy_crown)] = ice_deep
        
        # Snowflake particles
        sf_y = (cy - 4 + frame_idx * 2) % SIZE
        px[(cx - 8, sf_y)] = (240, 255, 255, 255)
        px[(cx + 8, (sf_y + 5) % SIZE)] = (240, 255, 255, 255)

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/pet_ice.webp", 180)

# 7. 単能力：ドクター/ウィザード (Wizard Kirby)
def generate_wizard_kirby():
    frames = []
    for frame_idx in range(4):
        img = create_frame()
        px = {}
        cx, cy = 16, 16
        bob = -1 if frame_idx in [1, 2] else 0

        draw_feet(px, cx, cy + bob)
        draw_base_body(px, cx, cy + bob, radius=7.5)
        
        # Big intellectual glasses (めがね)
        draw_eyes_and_cheeks(px, cx, cy + bob)
        # Glasses frames
        px[(cx - 4, cy - 2 + bob)] = (100, 100, 100, 255)
        px[(cx - 1, cy - 2 + bob)] = (100, 100, 100, 255)
        px[(cx + 1, cy - 2 + bob)] = (100, 100, 100, 255)
        px[(cx + 4, cy - 2 + bob)] = (100, 100, 100, 255)
        px[(cx, cy - 2 + bob)] = (150, 150, 150, 255) # Bridge

        # Wizard hat with stars
        for hy in range(cy - 14 + bob, cy - 6 + bob):
            h_width = (cy - 6 + bob - hy)
            for hx in range(cx - h_width, cx + h_width + 1):
                px[(hx, hy)] = (100, 50, 180, 255)
        # Brim
        for hx in range(cx - 7, cx + 8):
            px[(hx, cy - 6 + bob)] = (70, 30, 140, 255)
        # Yellow Star on hat
        px[(cx, cy - 10 + bob)] = (255, 230, 50, 255)

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/pet_wizard.webp", 180)

# 8. 複合能力：バーニングソード (Burning Sword Kirby)
def generate_burning_sword():
    frames = []
    for frame_idx in range(4):
        img = create_frame()
        px = {}
        cx, cy = 16, 16
        bob = -1 if frame_idx in [1, 2] else 0

        draw_feet(px, cx, cy + bob)
        draw_base_body(px, cx, cy + bob, radius=7.5)
        draw_eyes_and_cheeks(px, cx, cy + bob, happy=True)

        # Flaming Knight Helm
        for fy in range(cy - 13 + bob, cy - 6 + bob):
            for fx in range(cx - 6, cx + 7):
                if abs(fx - cx) <= (cy - 6 + bob - fy):
                    px[(fx, fy)] = (255, 69, 0, 255) if (fx+fy+frame_idx)%2==0 else (255, 200, 0, 255)
        # Gold crown base
        for fx in range(cx - 7, cx + 8):
            px[(fx, cy - 6 + bob)] = (255, 215, 0, 255)

        # Huge Flaming Greatsword!
        sw_y = cy - 4 + bob
        for i in range(10):
            fx = cx + 7 + i//2
            fy = sw_y - i
            px[(fx, fy)] = (255, 255, 200, 255) # Core
            px[(fx+1, fy)] = (255, 100, 0, 255) # Fire aura
            px[(fx-1, fy)] = (255, 50, 0, 255)
        px[(cx + 6, sw_y + 1)] = (255, 215, 0, 255)

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/pet_burning_sword.webp", 150)

# 9. 複合能力：スパークブレード (Spark Blade Kirby)
def generate_spark_cutter():
    frames = []
    for frame_idx in range(4):
        img = create_frame()
        px = {}
        cx, cy = 16, 16
        bob = -1 if frame_idx in [1, 2] else 0

        draw_feet(px, cx, cy + bob)
        draw_base_body(px, cx, cy + bob, radius=7.5)
        draw_eyes_and_cheeks(px, cx, cy + bob, happy=True)

        # Emerald & Lightning Cap
        for cy_cap in range(cy - 12 + bob, cy - 6 + bob):
            for cx_cap in range(cx - 6, cx + 7):
                px[(cx_cap, cy_cap)] = (0, 200, 100, 255)
        # Lightning Crest
        px[(cx, cy - 9 + bob)] = (255, 255, 100, 255)

        # Dual Plasma Blades
        for i in range(8):
            px[(cx + 7 + i//2, cy - 2 - i + bob)] = (100, 255, 255, 255)
            px[(cx - 7 - i//2, cy - 2 - i + bob)] = (100, 255, 255, 255)

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/pet_spark_cutter.webp", 150)

# 10. 複合能力：フロストボム (Frost Bomb / Spark Kirby)
def generate_frost_spark():
    frames = []
    for frame_idx in range(4):
        img = create_frame()
        px = {}
        cx, cy = 16, 16
        bob = -1 if frame_idx in [1, 2] else 0

        draw_feet(px, cx, cy + bob)
        draw_base_body(px, cx, cy + bob, radius=7.5)
        draw_eyes_and_cheeks(px, cx, cy + bob, happy=True)

        # Cyan / Blue Ice & Plasma Crown
        for cy_crown in range(cy - 13 + bob, cy - 6 + bob):
            for cx_crown in range(cx - 6, cx + 7):
                if (cx_crown + cy_crown + frame_idx) % 2 == 0:
                    px[(cx_crown, cy_crown)] = (0, 255, 255, 255)
                else:
                    px[(cx_crown, cy_crown)] = (200, 255, 255, 255)

        # Orbiting Ice Crystal Bombs
        angle_offsets = [0, 90, 180, 270]
        for a in angle_offsets:
            ox = int(cx + 10 * ((frame_idx + a/90) % 2 * 2 - 1))
            oy = int(cy + 6 * ((frame_idx + 1 + a/90) % 2 * 2 - 1))
            if 0 <= ox < SIZE and 0 <= oy < SIZE:
                px[(ox, oy)] = (0, 220, 255, 255)
                px[(ox+1, oy)] = (255, 255, 255, 255)

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/pet_frost_spark.webp", 150)

# 11. 究極形態：スターロッド・レジェンド (Star Legend Kirby)
def generate_star_legend():
    frames = []
    for frame_idx in range(4):
        img = create_frame()
        px = {}
        cx, cy = 16, 16
        bob = -1 if frame_idx in [1, 2] else 0

        draw_feet(px, cx, cy + bob)
        # Golden Rainbow Aura Kirby!
        aura_colors = [(255, 215, 0, 255), (255, 180, 220, 255), (100, 240, 255, 255), (255, 255, 255, 255)]
        draw_base_body(px, cx, cy + bob, radius=7.5)
        draw_hands(px, cx, cy + bob, h_up=True)
        draw_eyes_and_cheeks(px, cx, cy + bob, happy=True)

        # Radiant Star Tiara
        px[(cx, cy - 10 + bob)] = (255, 255, 255, 255)
        px[(cx-1, cy - 9 + bob)] = (255, 215, 0, 255)
        px[(cx, cy - 9 + bob)] = (255, 215, 0, 255)
        px[(cx+1, cy - 9 + bob)] = (255, 215, 0, 255)
        for fx in range(cx - 6, cx + 7):
            px[(fx, cy - 7 + bob)] = (255, 215, 0, 255)

        # Star Rod in hand
        # Wand handle
        for i in range(8):
            px[(cx + 8, cy + 4 - i + bob)] = (255, 50, 80, 255) if i % 2 == 0 else (255, 255, 255, 255)
        # Glowing Star on top
        star_y = cy - 5 + bob
        px[(cx + 8, star_y - 2)] = (255, 255, 255, 255)
        for sx in range(cx + 6, cx + 11):
            px[(sx, star_y - 1)] = (255, 230, 50, 255)
        px[(cx + 7, star_y)] = (255, 215, 0, 255)
        px[(cx + 8, star_y)] = (255, 255, 255, 255)
        px[(cx + 9, star_y)] = (255, 215, 0, 255)
        px[(cx + 7, star_y + 1)] = (255, 200, 0, 255)
        px[(cx + 9, star_y + 1)] = (255, 200, 0, 255)

        # Twinkling sparkles around
        sparkle_pos = [(cx - 9, cy - 6 + frame_idx), (cx + 10, cy - 8 - frame_idx), (cx - 7, cy + 7 - frame_idx)]
        for sx, sy in sparkle_pos:
            if 0 <= sx < SIZE and 0 <= sy < SIZE:
                px[(sx, sy)] = (255, 255, 150, 255)

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/pet_star_legend.webp", 140)

# --- 敵キャラクター (Monsters) ---
def generate_waddle_dee():
    frames = []
    for frame_idx in range(4):
        img = create_frame()
        px = {}
        cx, cy = 16, 17
        bob = 1 if frame_idx in [1, 3] else 0
        
        # Feet (Yellow)
        for fx in range(cx - 7, cx - 2):
            for fy in range(cy + 6 + bob, cy + 9 + bob):
                px[(fx, fy)] = (255, 215, 0, 255)
        for fx in range(cx + 2, cx + 7):
            for fy in range(cy + 6 + bob, cy + 9 + bob):
                px[(fx, fy)] = (255, 215, 0, 255)

        # Orange Body
        for y in range(cy - 6 + bob, cy + 7 + bob):
            for x in range(cx - 7, cx + 8):
                if (x - cx)**2 + (y - (cy + bob))**2 <= 6.8**2:
                    px[(x, y)] = (240, 110, 30, 255)
        
        # Tan face mask
        for y in range(cy - 4 + bob, cy + 4 + bob):
            for x in range(cx - 5, cx + 6):
                if (x - cx)**2 / 5.0**2 + (y - (cy + bob))**2 / 4.0**2 <= 1.0:
                    px[(x, y)] = (255, 230, 190, 255)

        # Eyes & Cheeks
        px[(cx - 2, cy - 1 + bob)] = BLACK
        px[(cx - 2, cy + bob)] = (50, 100, 200, 255)
        px[(cx + 2, cy - 1 + bob)] = BLACK
        px[(cx + 2, cy + bob)] = (50, 100, 200, 255)
        px[(cx - 4, cy + 1 + bob)] = (255, 120, 100, 255)
        px[(cx + 4, cy + 1 + bob)] = (255, 120, 100, 255)

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/enemy_waddle_dee.webp", 200)

def generate_bronto_burt():
    frames = []
    for frame_idx in range(4):
        img = create_frame()
        px = {}
        cx, cy = 16, 16
        wing_y = -3 if frame_idx in [0, 2] else 1
        
        # Wings
        for wx in range(cx - 10, cx - 5):
            for wy in range(cy + wing_y - 2, cy + wing_y + 3):
                px[(wx, wy)] = (255, 255, 255, 255)
        for wx in range(cx + 5, cx + 10):
            for wy in range(cy + wing_y - 2, cy + wing_y + 3):
                px[(wx, wy)] = (255, 255, 255, 255)

        # Purple body
        for y in range(cy - 6, cy + 7):
            for x in range(cx - 6, cx + 7):
                if (x - cx)**2 + (y - cy)**2 <= 6**2:
                    px[(x, y)] = (180, 50, 180, 255)

        # Big round eyes
        px[(cx - 2, cy - 1)] = WHITE
        px[(cx - 2, cy)] = BLACK
        px[(cx + 2, cy - 1)] = WHITE
        px[(cx + 2, cy)] = BLACK

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/enemy_bronto_burt.webp", 150)

def generate_gordo():
    frames = []
    for frame_idx in range(4):
        img = create_frame()
        px = {}
        cx, cy = 16, 16

        # Spikes (8 directions)
        spikes = [(0, -9), (0, 9), (-9, 0), (9, 0), (-6, -6), (6, -6), (-6, 6), (6, 6)]
        for sx, sy in spikes:
            px[(cx + sx, cy + sy)] = (180, 190, 200, 255)
            px[(cx + sx//2, cy + sy//2)] = (120, 130, 140, 255)

        # Dark iron sphere
        for y in range(cy - 6, cy + 7):
            for x in range(cx - 6, cx + 7):
                if (x - cx)**2 + (y - cy)**2 <= 6**2:
                    px[(x, y)] = (60, 65, 75, 255) if (x-cx< -1 and y-cy< -1) else (30, 35, 45, 255)

        # Glowing yellow unblinking eyes
        px[(cx - 2, cy - 1)] = (255, 230, 0, 255)
        px[(cx - 2, cy)] = BLACK
        px[(cx + 2, cy - 1)] = (255, 230, 0, 255)
        px[(cx + 2, cy)] = BLACK

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/enemy_gordo.webp", 200)

def generate_dedede():
    frames = []
    for frame_idx in range(4):
        img = create_frame()
        px = {}
        cx, cy = 16, 16
        bob = -1 if frame_idx in [1, 2] else 0

        # Big Blue Body / Yellow Beak / Red Robe
        # Yellow feet
        for fx in range(cx - 8, cx - 2):
            for fy in range(cy + 8 + bob, cy + 12 + bob):
                px[(fx, fy)] = (255, 200, 0, 255)
        for fx in range(cx + 2, cx + 8):
            for fy in range(cy + 8 + bob, cy + 12 + bob):
                px[(fx, fy)] = (255, 200, 0, 255)

        # Red King's Robe
        for y in range(cy - 6 + bob, cy + 9 + bob):
            for x in range(cx - 9, cx + 10):
                if (x - cx)**2 / 9.0**2 + (y - (cy + bob))**2 / 8.0**2 <= 1.0:
                    px[(x, y)] = (220, 20, 40, 255)
        # White fluff trim
        for fx in range(cx - 8, cx + 9):
            px[(fx, cy + 7 + bob)] = (255, 255, 255, 255)

        # Blue Penguin Face
        for y in range(cy - 6 + bob, cy + 2 + bob):
            for x in range(cx - 6, cx + 7):
                if (x - cx)**2 + (y - (cy - 2 + bob))**2 <= 5.5**2:
                    px[(x, y)] = (30, 120, 220, 255)

        # Yellow Beak
        for x in range(cx - 3, cx + 4):
            px[(x, cy + 1 + bob)] = (255, 215, 0, 255)
            px[(x, cy + 2 + bob)] = (240, 160, 0, 255)

        # Eyes
        px[(cx - 2, cy - 3 + bob)] = WHITE
        px[(cx - 2, cy - 2 + bob)] = BLACK
        px[(cx + 2, cy - 3 + bob)] = WHITE
        px[(cx + 2, cy - 2 + bob)] = BLACK

        # Royal Crown Hat
        for hx in range(cx - 5, cx + 6):
            px[(hx, cy - 7 + bob)] = (255, 215, 0, 255)
            px[(hx, cy - 8 + bob)] = (220, 20, 40, 255)
        px[(cx, cy - 9 + bob)] = (255, 255, 255, 255)

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/enemy_king_dedede.webp", 180)

# --- 特殊アクション：すいこみ・食べる・進化・うんち・病気・ゴースト ---
def generate_poop():
    frames = []
    for frame_idx in range(4):
        img = create_frame()
        px = {}
        cx, cy = 16, 20
        # Cute brown pixel poop with eyes
        BROWN = (139, 69, 19, 255)
        BROWN_LIGHT = (180, 100, 30, 255)
        
        # Base swirl
        for y in range(cy, cy + 6):
            for x in range(cx - 5, cx + 6):
                if (x - cx)**2 / 5.0**2 + (y - (cy + 2))**2 / 3.0**2 <= 1.0:
                    px[(x, y)] = BROWN
        # Mid swirl
        for y in range(cy - 4, cy + 1):
            for x in range(cx - 4, cx + 5):
                if (x - cx)**2 / 4.0**2 + (y - (cy - 1))**2 / 2.5**2 <= 1.0:
                    px[(x, y)] = BROWN_LIGHT
        # Top peak
        px[(cx, cy - 6 + (1 if frame_idx%2==0 else 0))] = BROWN
        px[(cx + 1, cy - 5)] = BROWN
        px[(cx - 1, cy - 5)] = BROWN
        
        # Cute face
        px[(cx - 2, cy)] = BLACK
        px[(cx + 2, cy)] = BLACK
        px[(cx - 3, cy + 1)] = (255, 120, 120, 255)
        px[(cx + 3, cy + 1)] = (255, 120, 120, 255)

        # Stink steam particle
        sy = cy - 8 - (frame_idx * 2) % 6
        px[(cx - 3, sy)] = (150, 180, 100, 200)
        px[(cx + 3, sy - 1)] = (150, 180, 100, 200)

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/poop.webp", 200)

def generate_sick_kirby():
    frames = []
    for frame_idx in range(4):
        img = create_frame()
        px = {}
        cx, cy = 16, 17
        bob = 1 if frame_idx in [1, 3] else 0

        # Pale / sickly pink body
        PALE_PINK = (245, 180, 195, 255)
        PALE_SHADOW = (210, 140, 160, 255)
        for y in range(cy - 7 + bob, cy + 8 + bob):
            for x in range(cx - 7, cx + 8):
                if (x - cx)**2 + (y - (cy + bob))**2 <= 7.0**2:
                    px[(x, y)] = PALE_PINK if y < cy + bob else PALE_SHADOW

        # Pale feet
        px[(cx - 5, cy + 7 + bob)] = (200, 100, 120, 255)
        px[(cx + 5, cy + 7 + bob)] = (200, 100, 120, 255)

        # Sick dizzy swirl eyes (@ @)
        if frame_idx % 2 == 0:
            px[(cx - 3, cy - 1 + bob)] = BLACK
            px[(cx - 2, cy - 2 + bob)] = BLACK
            px[(cx - 1, cy - 1 + bob)] = BLACK
            px[(cx - 2, cy + bob)] = BLACK
            px[(cx + 1, cy - 1 + bob)] = BLACK
            px[(cx + 2, cy - 2 + bob)] = BLACK
            px[(cx + 3, cy - 1 + bob)] = BLACK
            px[(cx + 2, cy + bob)] = BLACK
        else:
            px[(cx - 3, cy - 2 + bob)] = BLACK
            px[(cx - 1, cy + bob)] = BLACK
            px[(cx + 1, cy - 2 + bob)] = BLACK
            px[(cx + 3, cy + bob)] = BLACK

        # Forehead ice pack / bandage (ひえぴた / 氷のう)
        for bx in range(cx - 4, cx + 5):
            for by in range(cy - 10 + bob, cy - 6 + bob):
                px[(bx, by)] = (100, 200, 255, 255)
        px[(cx, cy - 11 + bob)] = (255, 255, 255, 255) # Ice bag tie

        # Blue face gradient (青ざめ)
        px[(cx - 4, cy + bob)] = (120, 160, 220, 200)
        px[(cx + 4, cy + bob)] = (120, 160, 220, 200)

        # Wavy sick mouth ~
        px[(cx - 1, cy + 2 + bob)] = BLACK
        px[(cx, cy + 3 + bob)] = BLACK
        px[(cx + 1, cy + 2 + bob)] = BLACK

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/pet_sick.webp", 250)

def generate_ghost_kirby():
    frames = []
    for frame_idx in range(4):
        img = create_frame()
        px = {}
        cx, cy = 16, 15
        float_y = -1 if frame_idx in [1, 2] else 1

        # Ghostly transparent white-blue body with tail
        GHOST_WHITE = (235, 245, 255, 220)
        GHOST_SHADOW = (180, 210, 240, 200)
        for y in range(cy - 7 + float_y, cy + 6 + float_y):
            for x in range(cx - 7, cx + 8):
                if (x - cx)**2 + (y - (cy + float_y))**2 <= 7.0**2:
                    px[(x, y)] = GHOST_WHITE
        
        # Ghost tail ripples
        tail_shift = frame_idx % 2
        for tx in range(cx - 5, cx + 6):
            if (tx + tail_shift) % 2 == 0:
                px[(tx, cy + 7 + float_y)] = GHOST_SHADOW
                px[(tx, cy + 8 + float_y)] = GHOST_SHADOW

        # Triangle headband (死冠・三角頭巾)
        for ty in range(cy - 12 + float_y, cy - 6 + float_y):
            t_w = (cy - 6 + float_y - ty) // 2
            for tx in range(cx - t_w, cx + t_w + 1):
                px[(tx, ty)] = WHITE
        px[(cx, cy - 10 + float_y)] = (255, 50, 50, 255) # Red dot

        # Empty black ghost eyes
        px[(cx - 3, cy - 2 + float_y)] = BLACK
        px[(cx - 3, cy - 1 + float_y)] = BLACK
        px[(cx + 3, cy - 2 + float_y)] = BLACK
        px[(cx + 3, cy - 1 + float_y)] = BLACK

        # Round open 'o' mouth
        px[(cx, cy + 2 + float_y)] = BLACK
        px[(cx, cy + 3 + float_y)] = BLACK

        # Will-o-wisp / Ghost fire (ひとだま)
        w_x = cx + 9 + (frame_idx % 2)
        w_y = cy - 4 - float_y
        px[(w_x, w_y)] = (100, 220, 255, 240)
        px[(w_x, w_y - 1)] = (200, 255, 255, 240)

        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/pet_ghost.webp", 200)

def generate_action_sprites():
    # すいこみ (Inhale)
    frames = []
    for frame_idx in range(4):
        img = create_frame()
        px = {}
        cx, cy = 16, 16
        mouth_size = 4 + frame_idx % 2 * 2
        draw_feet(px, cx, cy)
        draw_base_body(px, cx, cy, radius=8)
        # Giant open mouth
        for my in range(cy - mouth_size//2, cy + mouth_size//2 + 2):
            for mx in range(cx - 2, cx + 8):
                px[(mx, my)] = (120, 10, 30, 255)
        # Swirling wind lines into mouth
        for wx in range(cx + 8, cx + 15):
            wy = cy + (wx + frame_idx * 3) % 5 - 2
            if 0 <= wy < SIZE:
                px[(wx, wy)] = (255, 255, 255, 220)
        draw_eyes_and_cheeks(px, cx - 2, cy - 1)
        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/pet_inhale.webp", 120)

    # もぐもぐ (Eating)
    frames = []
    for frame_idx in range(4):
        img = create_frame()
        px = {}
        cx, cy = 16, 16
        chew = 1 if frame_idx % 2 == 1 else -1
        draw_feet(px, cx, cy)
        draw_base_body(px, cx, cy, radius=7.5, squash=chew)
        draw_hands(px, cx, cy, h_up=True)
        draw_eyes_and_cheeks(px, cx, cy, happy=True)
        # Chewing cheeks puffed out
        px[(cx - 6, cy + 2)] = CHEEK
        px[(cx + 6, cy + 2)] = CHEEK
        # Crumbs
        if frame_idx % 2 == 1:
            px[(cx + 4, cy + 4)] = (255, 200, 50, 255)
            px[(cx - 4, cy + 4)] = (255, 100, 50, 255)
        draw_pixels(img, px)
        frames.append(img)
    scale_and_save_webp(frames, "assets/sprites/pet_eating.webp", 140)

if __name__ == "__main__":
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
    generate_waddle_dee()
    generate_bronto_burt()
    generate_gordo()
    generate_dedede()
    generate_action_sprites()
    generate_poop()
    generate_sick_kirby()
    generate_ghost_kirby()
    print("All WebP sprites generated successfully!")
