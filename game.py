"""
=============================================================================
FIRST ASSESSMENT - ROBOT PROGRAMMING COURSE (UC3M)
PROJECT: CLANCY VS PRINCE JAM ROLL (game.py)
-----------------------------------------------------------------------------
Theme: The Midnight Gospel Space Adventure (Episode 4: "Blinded by My End")
  - Player: Clancy Gilroy in Lilac Purple with Floppy Purple Wizard Hat
  - Weapon: Magical Heart Arrows from the show with trailing love sparkles
  - Antagonist: Prince Jam Roll (Episode 4 fleshy demon)
  - Obstacles: Cosmic Geode Asteroids
  - Collectibles: Pairs of Multiverse Shoes (Upper / Top-Down View)
  - Deep Space Progression: Background evolves into deeper space sectors
    every time you enter the Multiverse Simulator (every 20 levels)!
  - Full Rubric Compliance: Welcome screen waiting for keypress, 60 FPS clock,
    keyboard controls, scoring, difficulty scaling, 3 lives, and 800x600 size.
=============================================================================
"""

import sys
import math
import random
import io
import struct
import wave
import pygame

# ---------------------------------------------------------------------------
# 11. SCREEN SIZE (CONSISTENT SCREEN SIZE: 800 x 600)
# ---------------------------------------------------------------------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# ---------------------------------------------------------------------------
# COLOR PALETTE
# ---------------------------------------------------------------------------
# 10. Player Visible in Purple (Clancy Gilroy)
CLANCY_PURPLE       = (175, 80, 245)    # Clancy's lilac-purple skin
CLANCY_HAT_PURPLE   = (115, 35, 180)    # Floppy wizard hat
CLANCY_HAT_BAND     = (255, 110, 220)   # Magenta hat band
CLANCY_GLOW         = (225, 140, 255)   # Psychedelic highlight

# Heart Arrow Colors (Ep. 4 Love Barbarian / Trudy & Clancy)
ARROW_HEART_RED     = (255, 45, 115)    # Vibrant ruby-pink heart tip
ARROW_HEART_GLOW    = (255, 140, 190)   # Heart gleam
ARROW_SHAFT_GOLD    = (240, 190, 70)    # Mystic golden shaft
ARROW_FLETCH_PINK   = (255, 110, 180)   # Feathered fletching

# Prince Jam Roll Palette (Cartoon-Accurate to The Midnight Gospel Episode 4)
JAM_ROLL_SKIN       = (255, 145, 165)   # Fleshy cartoon peach / coral pink
JAM_ROLL_SHADOW     = (190, 85, 110)    # Deep rosy shadow / crease
JAM_ROLL_MOUTH      = (85, 12, 30)      # Dark maroon gullet
JAM_ROLL_EYE        = (255, 235, 50)    # Demonic yellow eyes
JAM_ROLL_HORN       = (95, 20, 40)      # Dark curved horns
JAM_ROLL_WING       = (240, 120, 145)   # Fleshy coral bat wing webbing

# Multiverse Simulator Colors
SIMULATOR_OUTER     = (140, 50, 180)    # Biomechanical casing
SIMULATOR_RIM       = (255, 120, 220)   # Iridescent rim
SIMULATOR_IRIS      = (255, 60, 140)    # Fleshy portal iris
SIMULATOR_CORE      = (0, 245, 255)     # Chromatic singularity core

# UI, Hazard & Item Colors
COLOR_CYAN          = (0, 245, 255)
COLOR_PINK          = (255, 60, 180)
COLOR_GOLD          = (255, 220, 50)
COLOR_ASTEROID      = (125, 85, 150)    # Cosmic geode asteroid
COLOR_ASTEROID_GLOW = (210, 130, 255)
COLOR_WHITE         = (255, 255, 255)
COLOR_BLACK         = (0, 0, 0)
COLOR_GRAY          = (160, 170, 190)

# Deep Space Progression Themes (Solid deep-space background changes every 20 levels)
DEEP_SPACE_THEMES = [
    # Cycle 0 (Levels 1-20): "Known Cosmos" - Classic Deep Cosmic Navy
    {
        "name": "KNOWN COSMOS",
        "bg": (10, 12, 24),
        "stars": [(240, 240, 255), (180, 210, 255), (255, 255, 255)]
    },
    # Cycle 1 (Levels 21-40): "Abyssal Violet Void" - Deep Indigo-Violet
    {
        "name": "ABYSSAL VIOLET VOID",
        "bg": (12, 6, 24),
        "stars": [(230, 200, 255), (170, 220, 255), (255, 180, 240)]
    },
    # Cycle 2 (Levels 41-60): "Midnight Teal Abyss" - Deep Cosmic Teal
    {
        "name": "MIDNIGHT TEAL ABYSS",
        "bg": (4, 14, 20),
        "stars": [(180, 255, 230), (220, 255, 255), (255, 240, 180)]
    },
    # Cycle 3 (Levels 61-80): "Crimson Singularity" - Deep Cosmic Plum
    {
        "name": "CRIMSON SINGULARITY",
        "bg": (18, 5, 14),
        "stars": [(255, 190, 210), (255, 220, 160), (255, 255, 255)]
    },
    # Cycle 4+ (Levels 81+): "Multiverse Event Horizon" - Deep Inky Void with Radiant Stars
    {
        "name": "EVENT HORIZON VOID",
        "bg": (3, 3, 8),
        "stars": [(255, 255, 255), (0, 245, 255), (255, 100, 200), (255, 230, 50)]
    }
]

# Game States
STATE_WELCOME       = "WELCOME"
STATE_PLAYING       = "PLAYING"
STATE_GAMEOVER      = "GAMEOVER"


# ---------------------------------------------------------------------------
# PROCEDURAL AUDIO SYNTHESIZER (NO EXTERNAL FILES REQUIRED)
# ---------------------------------------------------------------------------
class SoundManager:
    """Generates procedural retro synth sound effects in-memory."""
    def __init__(self):
        self.enabled = False
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            self.arrow_sound    = self._synth_sound(self._arrow_freq, duration=0.14, vol=0.22)
            self.jamroll_hit    = self._synth_sound(self._monster_freq, duration=0.20, vol=0.26)
            self.shoe_sound     = self._synth_sound(self._item_freq, duration=0.20, vol=0.25)
            self.hurt_sound     = self._synth_sound(self._hurt_freq, duration=0.22, vol=0.30)
            self.gameover_sound = self._synth_sound(self._gameover_freq, duration=0.45, vol=0.32)
            self.portal_sound   = self._synth_sound(self._portal_freq, duration=0.85, vol=0.28)
            self.enabled = True
        except Exception as e:
            print(f"[SoundManager] Audio initialization skipped: {e}")

    def _synth_sound(self, freq_func, duration=0.15, vol=0.2):
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            frames = bytearray()
            for i in range(n_samples):
                t = i / sample_rate
                freq = freq_func(t, duration)
                env = 1.0 - (i / n_samples)
                val = int(vol * 32767.0 * env * math.sin(2.0 * math.pi * freq * t))
                val = max(-32768, min(32767, val))
                frames.extend(struct.pack('<h', val))
            wav_file.writeframes(frames)
        buf.seek(0)
        return pygame.mixer.Sound(buf)

    @staticmethod
    def _arrow_freq(t, dur):
        # Magical bow twang into singing heart arrow whistle
        return 580 + (880 * math.sin((t / dur) * math.pi * 0.8))

    @staticmethod
    def _monster_freq(t, dur):
        return 220 - (120 * (t / dur)) + (random.random() * 30)

    @staticmethod
    def _item_freq(t, dur):
        # Sweet dual-tone shoe pickup chime
        return 659.25 if t < dur * 0.5 else 987.77

    @staticmethod
    def _hurt_freq(t, dur):
        return 260 - (170 * (t / dur))

    @staticmethod
    def _gameover_freq(t, dur):
        return 380 - (260 * (t / dur))

    @staticmethod
    def _portal_freq(t, dur):
        # Cosmic dimension warp whoosh
        phase = t / dur
        return 200 + 400 * math.sin(phase * math.pi * 3) + (100 * math.cos(phase * 12))

    def play(self, sound_name):
        if not self.enabled:
            return
        try:
            if sound_name in ("arrow", "laser"):
                self.arrow_sound.play()
            elif sound_name == "explosion":
                self.jamroll_hit.play()
            elif sound_name == "item":
                self.shoe_sound.play()
            elif sound_name == "hit":
                self.hurt_sound.play()
            elif sound_name == "gameover":
                self.gameover_sound.play()
            elif sound_name == "portal":
                self.portal_sound.play()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# PARTICLE EFFECTS (SPARKLES & HEART PARTICLES)
# ---------------------------------------------------------------------------
class Particle:
    def __init__(self, x, y, color, size, vx, vy, life, is_heart=False):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.is_heart = is_heart

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        if not self.is_heart:
            self.size = max(0, self.size * 0.94)

    def draw(self, surface):
        if self.life <= 0 or self.size <= 0.5:
            return
        alpha = int(255 * (self.life / self.max_life))
        s_size = int(self.size * 3)
        s = pygame.Surface((s_size * 2, s_size * 2), pygame.SRCALPHA)

        if self.is_heart:
            # Draw tiny floating heart
            hx, hy = s_size, s_size
            r = max(2, int(self.size))
            c = (*self.color, alpha)
            pygame.draw.circle(s, c, (hx - r // 2, hy - r // 2), r // 2 + 1)
            pygame.draw.circle(s, c, (hx + r // 2, hy - r // 2), r // 2 + 1)
            pts = [(hx - r - 1, hy - r // 3), (hx + r + 1, hy - r // 3), (hx, hy + r)]
            pygame.draw.polygon(s, c, pts)
        else:
            pygame.draw.circle(s, (*self.color, alpha), (s_size, s_size), int(self.size))

        surface.blit(s, (self.x - s_size, self.y - s_size))


# ---------------------------------------------------------------------------
# 3 & 10. CLANCY GILROY PLAYER (VISIBLE IN PURPLE)
# ---------------------------------------------------------------------------
class Player:
    """
    Clancy Gilroy from The Midnight Gospel:
    - Visible in signature LILAC PURPLE (Requirement 10).
    - Floppy purple wizard hat with light purple brim, bent tip, and star.
    - Armed with magical Heart Arrows from Episode 4 (Requirement 3).
    - Controlled with Arrow keys or WASD, shoots with Spacebar.
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 6.0
        self.lives = 3
        self.invincible_timer = 0
        self.shoot_cooldown = 0
        self.float_timer = 0
        self.shoes_collected = 0

    def get_rect(self):
        return pygame.Rect(self.x - 16, self.y - 12, 32, 42)

    def update(self, keys_pressed, particles):
        # 3. Keyboard control
        dx, dy = 0, 0
        if keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]:
            dx -= 1
        if keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]:
            dx += 1
        if keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w]:
            dy -= 1
        if keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s]:
            dy += 1

        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        self.x += dx * self.speed
        self.y += dy * self.speed

        # Keep Clancy on screen
        self.x = max(30, min(SCREEN_WIDTH - 30, self.x))
        self.y = max(45, min(SCREEN_HEIGHT - 35, self.y))

        # Cosmic magic aura sparks & heart dust
        self.float_timer += 1
        if self.float_timer % 2 == 0:
            colors = [CLANCY_GLOW, COLOR_PINK, COLOR_CYAN, ARROW_HEART_GLOW]
            particles.append(Particle(
                x=self.x + (random.random() - 0.5) * 14,
                y=self.y + 24,
                color=random.choice(colors),
                size=random.uniform(3, 5),
                vx=(random.random() - 0.5) * 1.5,
                vy=random.uniform(2, 4),
                life=random.randint(14, 20),
                is_heart=(random.random() < 0.25)
            ))

        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def shoot(self, arrows, sound_mgr):
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = 13
            # Shoot twin Heart Arrows from Episode 4
            arrows.append(HeartArrow(self.x - 12, self.y - 24))
            arrows.append(HeartArrow(self.x + 12, self.y - 24))
            sound_mgr.play("arrow")

    def draw(self, surface):
        if self.invincible_timer > 0 and (self.invincible_timer // 4) % 2 == 0:
            return

        cx, cy = int(self.x), int(self.y)
        hover_y = cy + int(math.sin(self.float_timer * 0.1) * 3)

        # Purple Robe
        robe = [
            (cx - 14, hover_y + 8),
            (cx + 14, hover_y + 8),
            (cx + 16, hover_y + 24),
            (cx, hover_y + 20),
            (cx - 16, hover_y + 24)
        ]
        pygame.draw.polygon(surface, (135, 50, 200), robe)
        pygame.draw.polygon(surface, CLANCY_PURPLE, robe, width=2)

        # Purple Head
        pygame.draw.circle(surface, CLANCY_PURPLE, (cx, hover_y), 14)

        # Floppy Purple Wizard Hat
        # Brim
        pygame.draw.ellipse(surface, CLANCY_HAT_PURPLE, (cx - 24, hover_y - 8, 48, 12))
        pygame.draw.ellipse(surface, CLANCY_GLOW, (cx - 24, hover_y - 8, 48, 12), width=1)

        # Floppy Cone
        hat_cone = [
            (cx - 15, hover_y - 4),
            (cx + 15, hover_y - 4),
            (cx + 6, hover_y - 20),
            (cx - 8, hover_y - 34),
            (cx - 14, hover_y - 28),
            (cx - 6, hover_y - 14)
        ]
        pygame.draw.polygon(surface, CLANCY_HAT_PURPLE, hat_cone)
        pygame.draw.polygon(surface, (190, 80, 255), hat_cone, width=1)

        # Magenta Hat Band & Star
        pygame.draw.ellipse(surface, CLANCY_HAT_BAND, (cx - 14, hover_y - 7, 28, 7))
        pygame.draw.circle(surface, COLOR_GOLD, (cx - 8, hover_y - 34), 3)

        # Face: Round Cartoon Eyes
        pygame.draw.circle(surface, COLOR_WHITE, (cx - 5, hover_y + 1), 4)
        pygame.draw.circle(surface, COLOR_WHITE, (cx + 5, hover_y + 1), 4)
        pygame.draw.circle(surface, COLOR_BLACK, (cx - 5, hover_y + 1), 2)
        pygame.draw.circle(surface, COLOR_BLACK, (cx + 5, hover_y + 1), 2)
        # Smile
        pygame.draw.arc(surface, (90, 20, 130), (cx - 4, hover_y + 4, 8, 5), math.pi, math.pi * 2, 2)


# ---------------------------------------------------------------------------
# HEART ARROWS (EPISODE 4: THE LOVE BARBARIAN WEAPON)
# ---------------------------------------------------------------------------
class HeartArrow:
    """
    Magical Heart Arrow from The Midnight Gospel Episode 4 ("Blinded by My End"):
    - Fired by Clancy and Trudy the Love Barbarian.
    - Sharp ruby-pink heart arrowhead with gleaming highlights.
    - Golden mystic wooden shaft with pink feathered fletching.
    - Leaves a trail of mini heart motes and glowing love dust!
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 13.0
        self.sparkle_timer = 0

    def update(self, particles=None):
        self.y -= self.speed
        self.sparkle_timer += 1
        if particles is not None and self.sparkle_timer % 2 == 0:
            particles.append(Particle(
                x=self.x + (random.random() - 0.5) * 6,
                y=self.y + 14,
                color=random.choice([ARROW_HEART_RED, ARROW_HEART_GLOW, COLOR_GOLD, (255, 180, 220)]),
                size=random.uniform(2.5, 4.5),
                vx=(random.random() - 0.5) * 1.2,
                vy=random.uniform(1.5, 3.5),
                life=random.randint(10, 16),
                is_heart=(random.random() < 0.4)
            ))

    def get_rect(self):
        return pygame.Rect(self.x - 7, self.y - 14, 14, 28)

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)

        # 1. Golden Arrow Shaft
        pygame.draw.line(surface, ARROW_SHAFT_GOLD, (cx, cy - 6), (cx, cy + 14), 3)
        pygame.draw.line(surface, COLOR_WHITE, (cx, cy - 4), (cx, cy + 12), 1)

        # 2. Feathered Fletching (Wings at base)
        fletch_left = [(cx, cy + 12), (cx - 5, cy + 17), (cx - 1, cy + 15)]
        fletch_right = [(cx, cy + 12), (cx + 5, cy + 17), (cx + 1, cy + 15)]
        pygame.draw.polygon(surface, ARROW_FLETCH_PINK, fletch_left)
        pygame.draw.polygon(surface, ARROW_FLETCH_PINK, fletch_right)
        pygame.draw.polygon(surface, COLOR_WHITE, fletch_left, width=1)
        pygame.draw.polygon(surface, COLOR_WHITE, fletch_right, width=1)

        # 3. Heart Arrowhead (Iconic pointed love heart pointing UP)
        hx, hy = cx, cy - 10
        hr = 5  # Radius of heart lobes

        # Glow halo behind heart
        halo_surf = pygame.Surface((28, 28), pygame.SRCALPHA)
        pygame.draw.circle(halo_surf, (255, 80, 150, 70), (14, 14), 13)
        surface.blit(halo_surf, (hx - 14, hy - 14))

        # Left & right lobes of heart
        pygame.draw.circle(surface, ARROW_HEART_RED, (hx - hr + 1, hy - 2), hr)
        pygame.draw.circle(surface, ARROW_HEART_RED, (hx + hr - 1, hy - 2), hr)

        # Lower triangular point of heart
        heart_pts = [
            (hx - hr * 2 + 1, hy - 1),
            (hx + hr * 2 - 1, hy - 1),
            (hx, hy - 12)  # Sharp arrow tip pointing UP!
        ]
        pygame.draw.polygon(surface, ARROW_HEART_RED, heart_pts)

        # Inner bright gleam
        pygame.draw.circle(surface, ARROW_HEART_GLOW, (hx - 2, hy - 3), 2)
        pygame.draw.circle(surface, COLOR_WHITE, (hx - 2, hy - 3), 1)
        pygame.draw.line(surface, COLOR_WHITE, (hx, hy - 2), (hx, hy - 10), 1)


# ---------------------------------------------------------------------------
# 4. ANTAGONIST ENEMY: PRINCE JAM ROLL (ACCURATE EPISODE 4 DESIGN)
# ---------------------------------------------------------------------------
class PrinceJamRoll:
    """
    Prince Jam Roll:
    - Modeled accurately after the demon antagonist in The Midnight Gospel (Ep. 4).
    - Fleshy rounded crimson body with his signature gluteal cheeks.
    - Large consuming toothy mouth with sharp fangs and dark gullet.
    - Demonic curved horns, flapping bat wings, and mischievous yellow eyes.
    - Moves automatically with sweeping sine-wave swoops toward Clancy (Requirement 4).
    """
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.base_x = x
        self.speed = speed
        self.width = 48
        self.height = 44
        self.sine_phase = random.uniform(0, math.pi * 2)
        self.sine_amplitude = random.uniform(25, 55)
        self.wing_anim = random.uniform(0, math.pi * 2)

    def update(self):
        self.y += self.speed
        self.sine_phase += 0.055
        self.x = self.base_x + math.sin(self.sine_phase) * self.sine_amplitude
        self.x = max(25, min(SCREEN_WIDTH - 25, self.x))
        self.wing_anim += 0.20

    def get_rect(self):
        return pygame.Rect(self.x - 22, self.y - 18, 44, 40)

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        wing_flap = math.sin(self.wing_anim) * 9

        # 1. Demon Bat Wings with Webbed Struts
        # Left Wing
        left_wing = [
            (cx - 12, cy - 2),
            (cx - 32, cy - 14 + wing_flap),
            (cx - 26, cy + 4),
            (cx - 15, cy + 10)
        ]
        pygame.draw.polygon(surface, JAM_ROLL_SHADOW, left_wing)
        pygame.draw.polygon(surface, JAM_ROLL_SKIN, left_wing, width=2)
        # Wing bone line
        pygame.draw.line(surface, JAM_ROLL_HORN, (cx - 12, cy - 2), (cx - 32, cy - 14 + wing_flap), 2)

        # Right Wing
        right_wing = [
            (cx + 12, cy - 2),
            (cx + 32, cy - 14 + wing_flap),
            (cx + 24, cy + 4),
            (cx + 15, cy + 10)
        ]
        pygame.draw.polygon(surface, JAM_ROLL_SHADOW, right_wing)
        pygame.draw.polygon(surface, JAM_ROLL_SKIN, right_wing, width=2)
        # Wing bone line
        pygame.draw.line(surface, JAM_ROLL_HORN, (cx + 12, cy - 2), (cx + 32, cy - 14 + wing_flap), 2)

        # 2. Dangling Little Imp Claws / Legs
        leg_sway = math.cos(self.wing_anim) * 2
        pygame.draw.line(surface, JAM_ROLL_SHADOW, (cx - 8, cy + 14), (cx - 10 + leg_sway, cy + 22), 3)
        pygame.draw.line(surface, JAM_ROLL_SHADOW, (cx + 8, cy + 14), (cx + 10 - leg_sway, cy + 22), 3)

        # 3. Demonic Horns (Curved on top)
        horn_left = [(cx - 12, cy - 10), (cx - 18, cy - 25), (cx - 6, cy - 14)]
        horn_right = [(cx + 12, cy - 10), (cx + 18, cy - 25), (cx + 6, cy - 14)]
        pygame.draw.polygon(surface, JAM_ROLL_HORN, horn_left)
        pygame.draw.polygon(surface, JAM_ROLL_HORN, horn_right)

        # 4. Prince Jam Roll's Signature Rounded Cheeks
        pygame.draw.circle(surface, JAM_ROLL_SKIN, (cx - 11, cy - 5), 14)
        pygame.draw.circle(surface, JAM_ROLL_SKIN, (cx + 11, cy - 5), 14)
        # Central defining crease
        pygame.draw.line(surface, JAM_ROLL_SHADOW, (cx, cy - 19), (cx, cy - 2), 2)

        # 5. Gaping Toothy Consuming Mouth
        mouth_rect = (cx - 15, cy - 2, 30, 20)
        pygame.draw.ellipse(surface, JAM_ROLL_MOUTH, mouth_rect)
        pygame.draw.ellipse(surface, (100, 10, 25), mouth_rect, width=2)

        # Sharp White Jagged Teeth
        # Top teeth
        pygame.draw.polygon(surface, COLOR_WHITE, [(cx - 11, cy + 1), (cx - 8, cy + 6), (cx - 5, cy + 1)])
        pygame.draw.polygon(surface, COLOR_WHITE, [(cx - 5, cy + 1), (cx - 2, cy + 7), (cx + 1, cy + 1)])
        pygame.draw.polygon(surface, COLOR_WHITE, [(cx + 1, cy + 1), (cx + 4, cy + 6), (cx + 7, cy + 1)])
        pygame.draw.polygon(surface, COLOR_WHITE, [(cx + 7, cy + 1), (cx + 10, cy + 6), (cx + 13, cy + 1)])
        # Bottom teeth
        pygame.draw.polygon(surface, COLOR_WHITE, [(cx - 8, cy + 15), (cx - 5, cy + 9), (cx - 2, cy + 15)])
        pygame.draw.polygon(surface, COLOR_WHITE, [(cx - 2, cy + 15), (cx + 1, cy + 9), (cx + 4, cy + 15)])
        pygame.draw.polygon(surface, COLOR_WHITE, [(cx + 4, cy + 15), (cx + 7, cy + 9), (cx + 10, cy + 15)])

        # 6. Evil Yellow Eyes with Menacing Slit Pupils
        pygame.draw.circle(surface, JAM_ROLL_EYE, (cx - 9, cy - 11), 5)
        pygame.draw.circle(surface, JAM_ROLL_EYE, (cx + 9, cy - 11), 5)
        pygame.draw.ellipse(surface, COLOR_BLACK, (cx - 10, cy - 13, 2, 5))
        pygame.draw.ellipse(surface, COLOR_BLACK, (cx + 8, cy - 13, 2, 5))


# ---------------------------------------------------------------------------
# 4. COSMIC GEODE ASTEROID (PSYCHEDELIC CRYSTAL HAZARD)
# ---------------------------------------------------------------------------
class CosmicAsteroid:
    """
    Cosmic crystalline geode tumbling through deep space (Requirement 4).
    """
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.radius = random.randint(18, 28)
        self.angle = 0.0
        self.rot_speed = random.uniform(-0.04, 0.04)

        # Jagged crystalline points
        self.points = []
        num_pts = 9
        for i in range(num_pts):
            ang = (i / num_pts) * math.pi * 2
            r = self.radius * random.uniform(0.78, 1.22)
            self.points.append((r * math.cos(ang), r * math.sin(ang)))

    def update(self):
        self.y += self.speed
        self.angle += self.rot_speed

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        cos_a = math.cos(self.angle)
        sin_a = math.sin(self.angle)
        pts = []
        for px, py in self.points:
            rx = cx + (px * cos_a - py * sin_a)
            ry = cy + (px * sin_a + py * cos_a)
            pts.append((rx, ry))

        pygame.draw.polygon(surface, (55, 30, 70), pts)
        pygame.draw.polygon(surface, COLOR_ASTEROID_GLOW, pts, width=2)
        pygame.draw.circle(surface, (180, 90, 240), (cx, cy), max(3, int(self.radius * 0.35)))
        pygame.draw.circle(surface, COLOR_WHITE, (cx, cy), max(1, int(self.radius * 0.15)))


# ---------------------------------------------------------------------------
# 6. THE MULTIVERSE SHOES - PAIRS FROM UPPER / TOP-DOWN VIEW
# ---------------------------------------------------------------------------
class MultiverseShoePair:
    """
    A matching pair of Multiverse Shoes from The Midnight Gospel!
    Rendered strictly from an UPPER (TOP-DOWN / BIRD'S-EYE) VIEW:
    - Displays Left and Right sneakers side-by-side as a complete pair.
    - Detailed top-down anatomy: rubber toe caps, tongue, criss-cross laces,
      collar opening showing inner sock lining, and rubber outsole rim.
    - Collecting a pair grants +50 points and saves a pair to Clancy's Shoe Rack!
    """
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.pulse = 0.0
        # Vibrant sneaker colors matching the psychedelic show palette
        self.shoe_color = random.choice([
            (255, 50, 130),   # Neon Hot Pink
            (0, 230, 255),    # Cyber Cyan
            (255, 205, 40),   # Golden Sun
            (160, 60, 255),   # Royal Violet
            (40, 240, 140),   # Neon Jade
            (255, 110, 40)    # Electric Coral
        ])

    def update(self):
        self.y += self.speed
        self.pulse += 0.09

    def get_rect(self):
        return pygame.Rect(self.x - 22, self.y - 18, 44, 36)

    def _draw_single_shoe_topdown(self, surface, cx, cy, is_right, bob):
        """Draws one sneaker viewed from straight above (top-down view)."""
        w = 8.5   # half width of shoe body
        h = 15.0  # half length of shoe

        # Anatomical curve offset: inner arch curves slightly inwards
        arch_dir = -1.0 if is_right else 1.0

        # 1. White Rubber Outsole Border (top-down perimeter)
        outsole_pts = [
            (cx - w, cy - h * 0.5 + bob),          # Outer top curve
            (cx - w * 0.7, cy - h + bob),          # Toe curve left
            (cx, cy - h - 1.5 + bob),              # Toe tip center
            (cx + w * 0.7, cy - h + bob),          # Toe curve right
            (cx + w, cy - h * 0.5 + bob),          # Inner top curve
            (cx + w * (0.9 + arch_dir * 0.15), cy + bob), # Arch waist
            (cx + w * 0.85, cy + h * 0.7 + bob),  # Heel right
            (cx, cy + h + bob),                    # Heel center
            (cx - w * 0.85, cy + h * 0.7 + bob),  # Heel left
            (cx - w * (0.9 - arch_dir * 0.15), cy + bob)  # Outer waist
        ]
        pygame.draw.polygon(surface, (245, 245, 255), outsole_pts)
        pygame.draw.polygon(surface, (160, 170, 190), outsole_pts, width=1)

        # 2. Main Sneaker Upper Canvas
        inner_pts = [
            (cx - (w - 1.5), cy - h * 0.5 + bob),
            (cx - (w - 1.5) * 0.7, cy - (h - 1.5) + bob),
            (cx, cy - h + bob),
            (cx + (w - 1.5) * 0.7, cy - (h - 1.5) + bob),
            (cx + (w - 1.5), cy - h * 0.5 + bob),
            (cx + (w - 1.5) * (0.9 + arch_dir * 0.15), cy + bob),
            (cx + (w - 1.5) * 0.85, cy + (h - 1.5) * 0.7 + bob),
            (cx, cy + (h - 1.5) + bob),
            (cx - (w - 1.5) * 0.85, cy + (h - 1.5) * 0.7 + bob),
            (cx - (w - 1.5) * (0.9 - arch_dir * 0.15), cy + bob)
        ]
        pygame.draw.polygon(surface, self.shoe_color, inner_pts)

        # 3. White Rubber Toe Cap (Upper curve)
        toe_cap_pts = [
            (cx - w * 0.75, cy - h * 0.45 + bob),
            (cx - w * 0.6, cy - h + bob),
            (cx, cy - h - 1.0 + bob),
            (cx + w * 0.6, cy - h + bob),
            (cx + w * 0.75, cy - h * 0.45 + bob)
        ]
        pygame.draw.polygon(surface, COLOR_WHITE, toe_cap_pts)
        pygame.draw.polygon(surface, (200, 200, 215), toe_cap_pts, width=1)

        # 4. Ankle Collar / Foot Opening (dark oval at heel)
        collar_rect = pygame.Rect(cx - 4.5, cy + h * 0.15 + bob, 9, 10)
        pygame.draw.ellipse(surface, (25, 20, 35), collar_rect)
        pygame.draw.ellipse(surface, COLOR_WHITE, collar_rect, width=1)
        # Inner footbed logo dot
        pygame.draw.circle(surface, COLOR_GOLD, (int(cx), int(cy + h * 0.45 + bob)), 2)

        # 5. Shoe Tongue & Criss-Cross Shoelaces (Top-Down)
        tongue_rect = pygame.Rect(cx - 3.5, cy - h * 0.4 + bob, 7, 9)
        pygame.draw.rect(surface, (240, 240, 250), tongue_rect, border_radius=2)

        # Criss-cross lace lines
        for i in range(3):
            ly = cy - h * 0.35 + (i * 3.2) + bob
            pygame.draw.line(surface, COLOR_WHITE, (cx - 4, ly), (cx + 4, ly + 1.8), 2)
            pygame.draw.line(surface, COLOR_WHITE, (cx + 4, ly), (cx - 4, ly + 1.8), 2)

        # Tied Shoelace Bow loops
        bow_y = cy - h * 0.42 + bob
        pygame.draw.ellipse(surface, COLOR_WHITE, (cx - 5.5, bow_y - 2, 5, 4), width=1)
        pygame.draw.ellipse(surface, COLOR_WHITE, (cx + 0.5, bow_y - 2, 5, 4), width=1)

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        bob = math.sin(self.pulse) * 3

        # Glowing Multiverse Aura
        sparkle_r = 26 + math.sin(self.pulse) * 3
        aura = pygame.Surface((sparkle_r * 2, sparkle_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(aura, (*self.shoe_color, 45), (sparkle_r, sparkle_r), sparkle_r)
        pygame.draw.circle(aura, (255, 255, 255, 30), (sparkle_r, sparkle_r), sparkle_r - 6)
        surface.blit(aura, (cx - sparkle_r, cy - sparkle_r + bob))

        # Draw Left Shoe (top-down view)
        self._draw_single_shoe_topdown(surface, cx - 11, cy, is_right=False, bob=bob)

        # Draw Right Shoe (top-down view)
        self._draw_single_shoe_topdown(surface, cx + 11, cy, is_right=True, bob=bob)

        # Sparkle motes around the pair
        for angle in [0.3, 2.1, 4.2]:
            sx = cx + math.cos(self.pulse * 1.5 + angle) * 20
            sy = cy + math.sin(self.pulse * 1.5 + angle) * 14 + bob
            pygame.draw.circle(surface, COLOR_WHITE, (int(sx), int(sy)), 2)


# ---------------------------------------------------------------------------
# DEEP-SPACE PROGRESSION STARFIELD BACKGROUND
# ---------------------------------------------------------------------------
class Starfield:
    """
    Clean deep space starfield that evolves to represent deeper space
    every time you enter the Multiverse Simulator (every 20 levels):
      - Smooth parallax scrolling stars across 3 depth layers.
      - Dynamic sector background hues (Navy -> Abyssal Violet -> Midnight Teal -> Crimson Singularity -> Event Horizon).
      - Subtle cosmic nebula bands that stay clean, crisp, and high-contrast!
    """
    def __init__(self, count=120):
        self.cycle_index = 0
        self.stars = []
        for _ in range(count):
            self.stars.append([
                random.randint(0, SCREEN_WIDTH),
                random.randint(0, SCREEN_HEIGHT),
                random.uniform(0.6, 2.8),  # Speed / layer
                random.randint(1, 2),      # Size
                random.randint(0, 2)       # Color tint index
            ])
        self.ambient_scroll = 0.0

    def set_cycle(self, cycle):
        self.cycle_index = min(len(DEEP_SPACE_THEMES) - 1, max(0, cycle))

    def update(self, speed_mult=1.0):
        self.ambient_scroll += 0.4 * speed_mult
        for s in self.stars:
            s[1] += s[2] * speed_mult
            if s[1] > SCREEN_HEIGHT:
                s[1] = 0
                s[0] = random.randint(0, SCREEN_WIDTH)

    def draw(self, surface):
        theme = DEEP_SPACE_THEMES[self.cycle_index]
        # Clean solid deep-space background
        surface.fill(theme["bg"])

        # Stars with cycle-specific starlight tints (clean parallax starfield)
        star_palette = theme["stars"]
        for s in self.stars:
            base_col = star_palette[s[4] % len(star_palette)]
            brightness = min(1.0, 0.45 + (s[2] / 2.8) * 0.55)
            col = (
                int(base_col[0] * brightness),
                int(base_col[1] * brightness),
                int(base_col[2] * brightness)
            )
            pygame.draw.rect(surface, col, (int(s[0]), int(s[1]), s[3], s[3]))


# ---------------------------------------------------------------------------
# MULTIVERSE SIMULATOR LEVEL TRANSITION CONTROLLER & ANIMATOR (EVERY 20 LEVELS)
# ---------------------------------------------------------------------------
class MultiverseSimulatorTransition:
    """
    The iconic Multiverse Simulator Portal from The Midnight Gospel:
    - Biomechanical/organic portal machine with pulsating iris and swirling dimension vortex.
    - Plays every 20 levels (e.g. Level 20, 40, 60...) as Clancy ascends to deeper space!
    """
    def __init__(self):
        self.active = False
        self.timer = 0
        self.max_duration = 175  # ~3 seconds at 60 FPS
        self.portal_y = -120     # Enters smoothly from top
        self.vortex_angle = 0.0
        self.from_level = 20
        self.to_level = 21
        self.sector_name = "ABYSSAL VOID"

    def start(self, from_level, to_level):
        self.active = True
        self.timer = 0
        self.portal_y = -120
        self.vortex_angle = 0.0
        self.from_level = from_level
        self.to_level = to_level

        cycle_idx = min(len(DEEP_SPACE_THEMES) - 1, (to_level - 1) // 20)
        self.sector_name = DEEP_SPACE_THEMES[cycle_idx]["name"]

    def update(self, player, particles):
        if not self.active:
            return False

        self.timer += 1
        self.vortex_angle += 0.12

        # 1. Simulator descends into view at top
        target_portal_y = 135
        self.portal_y += (target_portal_y - self.portal_y) * 0.08

        # 2. Clancy is magnetically drawn upwards into the simulator portal funnel
        portal_cx = SCREEN_WIDTH // 2
        portal_cy = self.portal_y

        if self.timer > 30:
            # Smoothly glide Clancy into the portal iris
            player.x += (portal_cx - player.x) * 0.08
            player.y += (portal_cy - player.y) * 0.08

            # Swirling dimension warp sparks around Clancy
            for _ in range(3):
                ang = random.uniform(0, math.pi * 2)
                dist = random.uniform(10, 60)
                particles.append(Particle(
                    x=portal_cx + math.cos(ang) * dist,
                    y=portal_cy + math.sin(ang) * dist,
                    color=random.choice([COLOR_CYAN, COLOR_PINK, COLOR_GOLD, CLANCY_GLOW, ARROW_HEART_RED]),
                    size=random.uniform(3, 6),
                    vx=-math.cos(ang) * 3,
                    vy=-math.sin(ang) * 3,
                    life=random.randint(12, 22),
                    is_heart=(random.random() < 0.3)
                ))

        # Transition finished
        if self.timer >= self.max_duration:
            self.active = False
            # Reposition player at base for the new deep space sector
            player.x = SCREEN_WIDTH // 2
            player.y = SCREEN_HEIGHT - 90
            player.invincible_timer = 90
            return True  # 20-level warp complete!

        return False

    def draw(self, surface, player):
        if not self.active:
            return

        cx = SCREEN_WIDTH // 2
        cy = int(self.portal_y)

        # 1. Outer Biomechanical Housing & Pipes
        pygame.draw.circle(surface, (25, 15, 40), (cx, cy), 95)
        pygame.draw.circle(surface, SIMULATOR_OUTER, (cx, cy), 95, width=6)
        pygame.draw.circle(surface, SIMULATOR_RIM, (cx, cy), 85, width=4)

        # Biomechanical connector bolts
        for i in range(8):
            ang = (i / 8) * math.pi * 2
            bx = cx + math.cos(ang) * 90
            by = cy + math.sin(ang) * 90
            pygame.draw.circle(surface, COLOR_GOLD, (int(bx), int(by)), 5)
            pygame.draw.circle(surface, COLOR_WHITE, (int(bx), int(by)), 2)

        # 2. Organic Pulsating Portal Iris (The Meat / Simulator Funnel)
        iris_pulse = 68 + math.sin(self.timer * 0.15) * 6
        pygame.draw.circle(surface, SIMULATOR_IRIS, (cx, cy), int(iris_pulse))
        pygame.draw.circle(surface, (180, 30, 90), (cx, cy), int(iris_pulse), width=3)

        # 3. Swirling Dimension Vortex Rays
        num_rays = 12
        for i in range(num_rays):
            ang = self.vortex_angle + (i / num_rays) * math.pi * 2
            color = COLOR_CYAN if i % 2 == 0 else COLOR_PINK
            rx1 = cx + math.cos(ang) * 12
            ry1 = cy + math.sin(ang) * 12
            rx2 = cx + math.cos(ang + 0.6) * (iris_pulse - 4)
            ry2 = cy + math.sin(ang + 0.6) * (iris_pulse - 4)
            pygame.draw.line(surface, color, (rx1, ry1), (rx2, ry2), 3)

        # Glowing Singularity Core
        pygame.draw.circle(surface, COLOR_WHITE, (cx, cy), 14)
        pygame.draw.circle(surface, SIMULATOR_CORE, (cx, cy), 10)

        # 4. Draw Clancy ascending into the simulator funnel
        player.draw(surface)

        # 5. Warp Speed Lines & Dimension Announcement HUD
        if self.timer > 40:
            flash_alpha = min(180, int((self.timer - 40) * 3))
            if self.timer > self.max_duration - 25:
                flash_alpha = int(255 * ((self.max_duration - self.timer) / 25))

            warp_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            warp_surf.fill((10, 8, 20, flash_alpha))
            surface.blit(warp_surf, (0, 0))

            # Banner Announcements
            font_title = pygame.font.SysFont("consolas", 31, bold=True)
            font_sub = pygame.font.SysFont("consolas", 20, bold=True)
            font_stat = pygame.font.SysFont("consolas", 16, bold=True)

            t1 = font_title.render("🌌 MULTIVERSE SIMULATOR ASCENSION 🌌", True, COLOR_CYAN)
            t2 = font_sub.render(f"WARPING TO DEEPER SPACE: {self.sector_name} (LEVEL {self.to_level})", True, COLOR_PINK)
            t3 = font_stat.render(f"SIMULATION ACCELERATING • 20 LEVELS COMPLETED!", True, COLOR_GOLD)

            surface.blit(t1, (SCREEN_WIDTH // 2 - t1.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
            surface.blit(t2, (SCREEN_WIDTH // 2 - t2.get_width() // 2, SCREEN_HEIGHT // 2 + 8))
            surface.blit(t3, (SCREEN_WIDTH // 2 - t3.get_width() // 2, SCREEN_HEIGHT // 2 + 44))


# ---------------------------------------------------------------------------
# MAIN GAME CONTROLLER CLASS
# ---------------------------------------------------------------------------
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("The Midnight Gospel: Clancy vs Prince Jam Roll (game.py)")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        # 9. Clock for smooth 60 FPS control
        self.clock = pygame.time.Clock()
        self.sound_mgr = SoundManager()

        # Fonts
        self.font_title = pygame.font.SysFont("consolas", 36, bold=True)
        self.font_heading = pygame.font.SysFont("consolas", 22, bold=True)
        self.font_body = pygame.font.SysFont("consolas", 17)
        self.font_hud = pygame.font.SysFont("consolas", 19, bold=True)

        self.starfield = Starfield()
        self.simulator = MultiverseSimulatorTransition()
        self.high_score = 0
        self.reset_game()
        self.state = STATE_WELCOME

    def reset_game(self):
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 90)
        self.arrows = []
        self.enemies = []
        self.obstacles = []
        self.items = []
        self.particles = []

        # 6 & 7. Score
        self.score = 0
        # 9. Difficulty scaling
        self.level = 1
        self.last_transition_cycle = 0
        self.difficulty_mult = 1.0
        self.starfield.set_cycle(0)

        # Spawning timers
        self.enemy_spawn_timer = 0
        self.obstacle_spawn_timer = 0
        self.item_spawn_timer = 0

    # -----------------------------------------------------------------------
    # 2. WELCOME SCREEN
    # -----------------------------------------------------------------------
    def draw_welcome_screen(self):
        self.starfield.draw(self.screen)

        # Title Banner
        title_surf = self.font_title.render("THE MIDNIGHT GOSPEL", True, COLOR_PINK)
        sub_surf = self.font_heading.render("CLANCY VS PRINCE JAM ROLL (EPISODE 4)", True, COLOR_CYAN)
        self.screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 45))
        self.screen.blit(sub_surf, (SCREEN_WIDTH // 2 - sub_surf.get_width() // 2, 88))

        # Clancy Pilot Showcase in Purple with Heart Arrow & Shoes
        center_x = SCREEN_WIDTH // 2
        center_y = 175
        pygame.draw.circle(self.screen, (35, 15, 60), (center_x, center_y), 45)
        pygame.draw.circle(self.screen, CLANCY_PURPLE, (center_x, center_y), 45, width=2)
        demo_clancy = Player(center_x, center_y + 2)
        demo_clancy.draw(self.screen)

        clancy_lbl = self.font_body.render("PILOT: CLANCY GILROY • SHOOTING HEART ARROWS", True, CLANCY_GLOW)
        self.screen.blit(clancy_lbl, (center_x - clancy_lbl.get_width() // 2, center_y + 52))

        # Instructions Box
        box_rect = pygame.Rect(75, 260, 650, 220)
        pygame.draw.rect(self.screen, (15, 18, 35, 230), box_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLOR_PINK, box_rect, width=2, border_radius=10)

        instructions = [
            ("CONTROLS:", COLOR_CYAN),
            ("  [ARROW KEYS] or [W, A, S, D] -> Move Clancy across Deep Space", COLOR_WHITE),
            ("  [SPACEBAR]                   -> Cast Magical Heart Arrows (Ep. 4)", ARROW_HEART_GLOW),
            ("MISSION OBJECTIVES:", COLOR_CYAN),
            ("  * Defeat Prince Jam Roll (+100 pts) * Dodge Asteroids (+10 pts)", COLOR_WHITE),
            ("  * Collect Pairs of Multiverse Shoes (+50 pts) for Clancy's Rack!", COLOR_GOLD),
            ("  * Enter Multiverse Simulator every 20 levels to Warp to Deeper Space!", COLOR_CYAN)
        ]

        cur_y = 272
        for text, color in instructions:
            line_surf = self.font_body.render(text, True, color)
            self.screen.blit(line_surf, (95, cur_y))
            cur_y += 24

        # 2. Pulsing key press prompt
        pulse = (pygame.time.get_ticks() // 380) % 2 == 0
        prompt_col = COLOR_GOLD if pulse else COLOR_WHITE
        prompt_surf = self.font_heading.render(">> PRESS ANY KEY TO ENTER SIMULATION <<", True, prompt_col)
        self.screen.blit(prompt_surf, (SCREEN_WIDTH // 2 - prompt_surf.get_width() // 2, 510))

    # -----------------------------------------------------------------------
    # 8. END GAME SCREEN
    # -----------------------------------------------------------------------
    def draw_gameover_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 12, 24, 230))
        self.screen.blit(overlay, (0, 0))

        title_surf = self.font_title.render("SIMULATOR SHUTDOWN!", True, JAM_ROLL_SKIN)
        sub_surf = self.font_heading.render("PRINCE JAM ROLL PREVAILED!", True, COLOR_WHITE)
        self.screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 110))
        self.screen.blit(sub_surf, (SCREEN_WIDTH // 2 - sub_surf.get_width() // 2, 160))

        box_rect = pygame.Rect(170, 210, 460, 205)
        pygame.draw.rect(self.screen, (18, 20, 40), box_rect, border_radius=10)
        pygame.draw.rect(self.screen, JAM_ROLL_SKIN, box_rect, width=2, border_radius=10)

        sector_idx = min(len(DEEP_SPACE_THEMES) - 1, (self.level - 1) // 20)
        sector_name = DEEP_SPACE_THEMES[sector_idx]["name"]

        score_text = self.font_heading.render(f"FINAL SCORE: {self.score}", True, COLOR_CYAN)
        shoes_text = self.font_body.render(f"SHOES SAVED TO RACK: {self.player.shoes_collected} PAIRS", True, COLOR_GOLD)
        high_text = self.font_body.render(f"BEST RECORD: {self.high_score}", True, COLOR_WHITE)
        lvl_text = self.font_body.render(f"SECTOR REACHED: {sector_name} (LVL {self.level})", True, CLANCY_GLOW)

        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 235))
        self.screen.blit(shoes_text, (SCREEN_WIDTH // 2 - shoes_text.get_width() // 2, 275))
        self.screen.blit(high_text, (SCREEN_WIDTH // 2 - high_text.get_width() // 2, 312))
        self.screen.blit(lvl_text, (SCREEN_WIDTH // 2 - lvl_text.get_width() // 2, 350))

        # Replay / Exit Options
        play_again = self.font_heading.render("PRESS [R] TO RESPAWN IN SIMULATOR", True, COLOR_PINK)
        exit_prompt = self.font_body.render("PRESS [Q] OR [ESC] TO EXIT", True, COLOR_GRAY)
        self.screen.blit(play_again, (SCREEN_WIDTH // 2 - play_again.get_width() // 2, 440))
        self.screen.blit(exit_prompt, (SCREEN_WIDTH // 2 - exit_prompt.get_width() // 2, 485))

    # -----------------------------------------------------------------------
    # 7. CURRENT SCORE & HUD DISPLAY
    # -----------------------------------------------------------------------
    def draw_hud(self):
        hud_bar = pygame.Rect(0, 0, SCREEN_WIDTH, 44)
        pygame.draw.rect(self.screen, (12, 15, 30), hud_bar)
        pygame.draw.line(self.screen, CLANCY_PURPLE, (0, 44), (SCREEN_WIDTH, 44), 2)

        # Score
        score_surf = self.font_hud.render(f"SCORE: {self.score}", True, COLOR_CYAN)
        self.screen.blit(score_surf, (15, 11))

        # Dimension / Level & Deep Space Sector
        sector_idx = min(len(DEEP_SPACE_THEMES) - 1, (self.level - 1) // 20)
        lvl_surf = self.font_hud.render(f"LVL {self.level} ({DEEP_SPACE_THEMES[sector_idx]['name'][:10]}.. {self.difficulty_mult:.1f}x)", True, COLOR_GOLD)
        self.screen.blit(lvl_surf, (180, 11))

        # Shoes Collected Counter (Pairs)
        shoes_surf = self.font_hud.render(f"👟 SHOES: {self.player.shoes_collected}", True, COLOR_PINK)
        self.screen.blit(shoes_surf, (440, 11))

        # Clancy Lives (Illustrated Purple Wizard Hats)
        lbl_lives = self.font_hud.render("LIVES:", True, COLOR_WHITE)
        self.screen.blit(lbl_lives, (SCREEN_WIDTH - 180, 11))

        for i in range(3):
            hx = SCREEN_WIDTH - 105 + (i * 26)
            hy = 20
            color = CLANCY_PURPLE if i < self.player.lives else (55, 30, 80)
            pygame.draw.ellipse(self.screen, color, (hx - 8, hy + 2, 16, 6))
            pygame.draw.polygon(self.screen, color, [(hx - 5, hy + 3), (hx + 5, hy + 3), (hx, hy - 8)])

    # -----------------------------------------------------------------------
    # 9. DIFFICULTY & 20-LEVEL DEEP-SPACE SIMULATOR TRANSITION ENGINE
    # -----------------------------------------------------------------------
    def update_difficulty_and_transitions(self):
        """
        Updates Level & Difficulty scaling every 400 pts,
        and triggers the Multiverse Simulator Transition every 20 levels!
        """
        new_level = 1 + (self.score // 400)
        if new_level != self.level:
            old_level = self.level
            self.level = new_level
            self.difficulty_mult = 1.0 + (self.level - 1) * 0.18

            # Check if crossing a 20-level simulator milestone (e.g. Level 20, 40, 60...)
            current_cycle = (self.level - 1) // 20
            if current_cycle > self.last_transition_cycle and not self.simulator.active:
                self.last_transition_cycle = current_cycle
                self.starfield.set_cycle(current_cycle)
                self.simulator.start(old_level, self.level)
                self.sound_mgr.play("portal")

    def spawn_splat(self, x, y, color=JAM_ROLL_SKIN, count=20, is_heart=False):
        for _ in range(count):
            ang = random.uniform(0, math.pi * 2)
            spd = random.uniform(1.8, 6.0)
            self.particles.append(Particle(
                x=x, y=y,
                color=color,
                size=random.uniform(2.5, 5.5),
                vx=math.cos(ang) * spd,
                vy=math.sin(ang) * spd,
                life=random.randint(18, 30),
                is_heart=is_heart
            ))

    # -----------------------------------------------------------------------
    # MAIN LOOP
    # -----------------------------------------------------------------------
    def run(self):
        running = True
        while running:
            # 9. Smooth 60 FPS clock control
            self.clock.tick(FPS)

            # ===============================================================
            # EVENT HANDLING
            # ===============================================================
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # 2. WELCOME SCREEN KEYPRESS
                elif self.state == STATE_WELCOME:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                        else:
                            self.reset_game()
                            self.state = STATE_PLAYING

                # 8. GAMEOVER SCREEN OPTIONS
                elif self.state == STATE_GAMEOVER:
                    if event.type == pygame.KEYDOWN:
                        if event.key in (pygame.K_r, pygame.K_SPACE):
                            self.reset_game()
                            self.state = STATE_PLAYING
                        elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                            running = False

                # PLAYING STATE: Single-shot triggers
                elif self.state == STATE_PLAYING:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.state = STATE_GAMEOVER
                        elif event.key == pygame.K_SPACE:
                            if not self.simulator.active:
                                self.player.shoot(self.arrows, self.sound_mgr)

            # ===============================================================
            # GAMEPLAY UPDATES
            # ===============================================================
            if self.state == STATE_PLAYING:
                # Update deep space starfield background
                self.starfield.update(speed_mult=self.difficulty_mult)

                # Check if currently in Simulator Transition sequence (every 20 levels)
                if self.simulator.active:
                    done = self.simulator.update(self.player, self.particles)
                    if done:
                        # Clear lingering hazards for clean entry into new cycle
                        self.enemies.clear()
                        self.obstacles.clear()
                else:
                    # Normal Playing Controls & Mechanics
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_SPACE]:
                        self.player.shoot(self.arrows, self.sound_mgr)

                    self.player.update(keys, self.particles)
                    self.update_difficulty_and_transitions()

                    # -------------------------------------------------------
                    # 4. Spawning Enemies & Obstacles (Automatic Movement)
                    # -------------------------------------------------------
                    # Spawn Prince Jam Roll
                    self.enemy_spawn_timer += 1
                    enemy_thresh = max(32, int(70 / self.difficulty_mult))
                    if self.enemy_spawn_timer >= enemy_thresh:
                        self.enemy_spawn_timer = 0
                        spawn_x = random.randint(40, SCREEN_WIDTH - 40)
                        spd = random.uniform(2.5, 4.2) * self.difficulty_mult
                        self.enemies.append(PrinceJamRoll(spawn_x, -35, spd))

                    # Spawn Cosmic Geode Asteroids
                    self.obstacle_spawn_timer += 1
                    obs_thresh = max(42, int(90 / self.difficulty_mult))
                    if self.obstacle_spawn_timer >= obs_thresh:
                        self.obstacle_spawn_timer = 0
                        spawn_x = random.randint(35, SCREEN_WIDTH - 35)
                        spd = random.uniform(2.0, 3.6) * self.difficulty_mult
                        self.obstacles.append(CosmicAsteroid(spawn_x, -35, spd))

                    # Spawn Multiverse Shoes (Pairs Viewed from Above)
                    self.item_spawn_timer += 1
                    if self.item_spawn_timer >= 170:
                        self.item_spawn_timer = 0
                        spawn_x = random.randint(50, SCREEN_WIDTH - 50)
                        self.items.append(MultiverseShoePair(spawn_x, -25, speed=2.4))

                # -----------------------------------------------------------
                # Update Heart Arrows & Entities
                # -----------------------------------------------------------
                for arrow in self.arrows[:]:
                    arrow.update(self.particles)
                    if arrow.y < -25:
                        self.arrows.remove(arrow)

                for enemy in self.enemies[:]:
                    enemy.update()
                    # 6. Overcoming obstacles reward (+10 pts)
                    if enemy.y > SCREEN_HEIGHT + 35:
                        self.enemies.remove(enemy)
                        self.score += 10
                        self.update_difficulty_and_transitions()

                for obs in self.obstacles[:]:
                    obs.update()
                    if obs.y > SCREEN_HEIGHT + 40:
                        self.obstacles.remove(obs)
                        self.score += 10
                        self.update_difficulty_and_transitions()

                for item in self.items[:]:
                    item.update()
                    if item.y > SCREEN_HEIGHT + 25:
                        self.items.remove(item)

                # -----------------------------------------------------------
                # 5. COLLISIONS & SCORING
                # -----------------------------------------------------------
                if not self.simulator.active:
                    player_rect = self.player.get_rect()

                    # Heart Arrows vs Prince Jam Roll Collisions (+100 pts)
                    for arrow in self.arrows[:]:
                        arrow_rect = arrow.get_rect()
                        hit = False
                        for enemy in self.enemies[:]:
                            if arrow_rect.colliderect(enemy.get_rect()):
                                self.spawn_splat(enemy.x, enemy.y, JAM_ROLL_SKIN, count=24)
                                self.spawn_splat(enemy.x, enemy.y, ARROW_HEART_RED, count=12, is_heart=True)
                                self.enemies.remove(enemy)
                                self.score += 100
                                self.sound_mgr.play("explosion")
                                self.update_difficulty_and_transitions()
                                hit = True
                                break
                        if hit:
                            if arrow in self.arrows:
                                self.arrows.remove(arrow)
                            continue

                        # Heart Arrows vs Asteroid Collisions (+50 pts)
                        for obs in self.obstacles[:]:
                            if arrow_rect.colliderect(obs.get_rect()):
                                self.spawn_splat(obs.x, obs.y, COLOR_ASTEROID_GLOW, count=18)
                                self.spawn_splat(obs.x, obs.y, ARROW_HEART_RED, count=8, is_heart=True)
                                self.obstacles.remove(obs)
                                self.score += 50
                                self.sound_mgr.play("explosion")
                                self.update_difficulty_and_transitions()
                                hit = True
                                break
                        if hit and arrow in self.arrows:
                            self.arrows.remove(arrow)

                    # Player vs Multiverse Shoes (+50 pts & Shoe Rack Pairs)
                    for item in self.items[:]:
                        if player_rect.colliderect(item.get_rect()):
                            self.spawn_splat(item.x, item.y, item.shoe_color, count=20)
                            self.spawn_splat(item.x, item.y, COLOR_GOLD, count=10, is_heart=True)
                            self.items.remove(item)
                            self.score += 50
                            self.player.shoes_collected += 1
                            self.sound_mgr.play("item")
                            self.update_difficulty_and_transitions()

                    # Player vs Hazard Collisions (5. Lose life)
                    if self.player.invincible_timer <= 0:
                        collided_hazard = None

                        # Check Prince Jam Roll
                        for enemy in self.enemies[:]:
                            if player_rect.colliderect(enemy.get_rect()):
                                collided_hazard = (enemy.x, enemy.y, JAM_ROLL_SKIN)
                                self.enemies.remove(enemy)
                                break

                        # Check Asteroids
                        if not collided_hazard:
                            for obs in self.obstacles[:]:
                                if player_rect.colliderect(obs.get_rect()):
                                    collided_hazard = (obs.x, obs.y, COLOR_ASTEROID_GLOW)
                                    self.obstacles.remove(obs)
                                    break

                        if collided_hazard:
                            hx, hy, hcol = collided_hazard
                            self.spawn_splat(hx, hy, hcol, count=25)
                            self.spawn_splat(self.player.x, self.player.y, CLANCY_PURPLE, count=20)
                            self.player.lives -= 1
                            self.player.invincible_timer = 90
                            self.sound_mgr.play("hit")

                            if self.player.lives <= 0:
                                if self.score > self.high_score:
                                    self.high_score = self.score
                                self.sound_mgr.play("gameover")
                                self.state = STATE_GAMEOVER

                # Particles
                for p in self.particles[:]:
                    p.update()
                    if p.life <= 0:
                        self.particles.remove(p)

            # ===============================================================
            # RENDERING
            # ===============================================================
            if self.state == STATE_WELCOME:
                self.draw_welcome_screen()

            elif self.state == STATE_PLAYING:
                # 1. Deep Space Starfield Background
                self.starfield.draw(self.screen)

                # 2. Draw Multiverse Shoes (Pairs)
                for item in self.items:
                    item.draw(self.screen)

                # 3. Draw Asteroids
                for obs in self.obstacles:
                    obs.draw(self.screen)

                # 4. Draw Prince Jam Roll
                for enemy in self.enemies:
                    enemy.draw(self.screen)

                # 5. Draw Heart Arrows
                for arrow in self.arrows:
                    arrow.draw(self.screen)

                # 6. Draw Particles
                for p in self.particles:
                    p.draw(self.screen)

                # 7. Simulator Transition Portal OR Normal Player
                if self.simulator.active:
                    self.simulator.draw(self.screen, self.player)
                else:
                    # 10. Draw Purple Player (Clancy Gilroy)
                    self.player.draw(self.screen)

                # 8. Draw Current Score HUD
                self.draw_hud()

            elif self.state == STATE_GAMEOVER:
                self.draw_gameover_screen()

            pygame.display.flip()

        pygame.quit()
        sys.exit()


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    game = Game()
    game.run()
