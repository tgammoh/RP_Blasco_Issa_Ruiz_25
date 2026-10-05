"""
=============================================================================
FIRST ASSESSMENT - ROBOT PROGRAMMING COURSE (UC3M)
PROJECT: CYBER DEFENDER (game.py)
-----------------------------------------------------------------------------
A 2D arcade survival game built with Pygame following all assignment
specifications:
  - Welcome Screen waiting for keypress
  - Player controlled with Keyboard (Arrows / WASD / Spacebar)
  - Player visibly represented in PURPLE
  - Automatic enemies and obstacles
  - Collision detection (lives lost, enemy destroyed, items collected)
  - Live Score System & HUD
  - Increasing difficulty (faster enemies, higher spawn rates, smooth 60 FPS clock)
  - End Game Screen with Final Score and Play Again / Exit options
  - Fixed, consistent screen size (800 x 600)
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
# 11. SCREEN SIZE (CONSISTENT SCREEN SIZE)
# ---------------------------------------------------------------------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# ---------------------------------------------------------------------------
# COLOR PALETTE
# ---------------------------------------------------------------------------
# 10. PLAYER VISIBLE IN PURPLE
PLAYER_PURPLE       = (168, 50, 240)    # Primary purple
PLAYER_PURPLE_LIGHT = (215, 120, 255)   # Highlight purple
PLAYER_PURPLE_DARK  = (100, 20, 160)    # Shadow purple

# Environment & UI Colors
COLOR_BG_DARK       = (10, 12, 24)      # Deep cosmic navy
COLOR_CYAN          = (0, 240, 255)     # Lasers / Power items
COLOR_RED           = (255, 60, 90)     # Enemy drones
COLOR_ORANGE        = (255, 150, 40)    # Asteroids / Hazards
COLOR_GREEN         = (60, 255, 140)    # Energy cores / Success
COLOR_WHITE         = (255, 255, 255)
COLOR_GRAY          = (160, 170, 190)
COLOR_HUD_BG        = (15, 18, 35, 200)

# Game States
STATE_WELCOME   = "WELCOME"
STATE_PLAYING   = "PLAYING"
STATE_GAMEOVER  = "GAMEOVER"


# ---------------------------------------------------------------------------
# PROCEDURAL RETRO AUDIO (NO EXTERNAL AUDIO FILES REQUIRED)
# ---------------------------------------------------------------------------
class SoundManager:
    """Generates and plays in-memory synthesized 8-bit / retro sound effects."""
    def __init__(self):
        self.enabled = False
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            self.laser_sound = self._synth_sound(self._laser_freq, duration=0.10, vol=0.18)
            self.explosion_sound = self._synth_sound(self._explosion_freq, duration=0.22, vol=0.25)
            self.item_sound = self._synth_sound(self._item_freq, duration=0.15, vol=0.22)
            self.hit_sound = self._synth_sound(self._hit_freq, duration=0.20, vol=0.30)
            self.gameover_sound = self._synth_sound(self._gameover_freq, duration=0.45, vol=0.30)
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
                # Sine wave with simple envelope
                env = 1.0 - (i / n_samples)
                val = int(vol * 32767.0 * env * math.sin(2.0 * math.pi * freq * t))
                val = max(-32768, min(32767, val))
                frames.extend(struct.pack('<h', val))
            wav_file.writeframes(frames)
        buf.seek(0)
        return pygame.mixer.Sound(buf)

    @staticmethod
    def _laser_freq(t, dur):
        # High to low pitch sweep
        return 900 - (600 * (t / dur))

    @staticmethod
    def _explosion_freq(t, dur):
        # Low rumbling noise approximation
        return 140 - (80 * (t / dur)) + (random.random() * 40)

    @staticmethod
    def _item_freq(t, dur):
        # Rising chime
        return 523.25 if t < dur / 2 else 659.25

    @staticmethod
    def _hit_freq(t, dur):
        # Harsh drop
        return 280 - (180 * (t / dur))

    @staticmethod
    def _gameover_freq(t, dur):
        # Sad descending tone
        return 400 - (280 * (t / dur))

    def play(self, sound_name):
        if not self.enabled:
            return
        try:
            if sound_name == "laser":
                self.laser_sound.play()
            elif sound_name == "explosion":
                self.explosion_sound.play()
            elif sound_name == "item":
                self.item_sound.play()
            elif sound_name == "hit":
                self.hit_sound.play()
            elif sound_name == "gameover":
                self.gameover_sound.play()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# PARTICLE EFFECTS SYSTEM
# ---------------------------------------------------------------------------
class Particle:
    def __init__(self, x, y, color, size, vx, vy, life):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size = max(0, self.size * 0.94)

    def draw(self, surface):
        if self.life > 0 and self.size > 0.5:
            alpha = int(255 * (self.life / self.max_life))
            s = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (int(self.size), int(self.size)), int(self.size))
            surface.blit(s, (self.x - self.size, self.y - self.size))


# ---------------------------------------------------------------------------
# 3 & 10. PLAYER CLASS (CONTROLLED BY KEYBOARD & VISIBLE IN PURPLE)
# ---------------------------------------------------------------------------
class Player:
    """
    Represented visibly in PURPLE (Requirement 10).
    Controlled with Arrow keys, WASD, and Spacebar (Requirement 3).
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 44
        self.height = 44
        self.speed = 6.0
        self.lives = 3
        self.invincible_timer = 0
        self.shoot_cooldown = 0
        self.thruster_timer = 0

    def get_rect(self):
        # Slightly generous hitbox for fair gameplay
        return pygame.Rect(self.x - self.width / 2 + 6,
                           self.y - self.height / 2 + 6,
                           self.width - 12,
                           self.height - 12)

    def update(self, keys_pressed, particles):
        # Keyboard controls: Arrows or WASD
        dx, dy = 0, 0
        if keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]:
            dx -= 1
        if keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]:
            dx += 1
        if keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w]:
            dy -= 1
        if keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s]:
            dy += 1

        # Diagonal movement normalization
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        self.x += dx * self.speed
        self.y += dy * self.speed

        # Keep player within screen bounds
        half_w = self.width / 2
        half_h = self.height / 2
        self.x = max(half_w + 10, min(SCREEN_WIDTH - half_w - 10, self.x))
        self.y = max(half_h + 40, min(SCREEN_HEIGHT - half_h - 15, self.y))

        # Thruster particle trail
        self.thruster_timer += 1
        if self.thruster_timer % 2 == 0:
            particles.append(Particle(
                x=self.x + (random.random() - 0.5) * 10,
                y=self.y + half_h,
                color=PLAYER_PURPLE_LIGHT if random.random() > 0.4 else COLOR_CYAN,
                size=random.uniform(3, 5),
                vx=(random.random() - 0.5) * 1.5,
                vy=random.uniform(2, 4),
                life=random.randint(12, 18)
            ))

        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def shoot(self, lasers, sound_mgr):
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = 14  # Cooldown frames between shots
            # Dual laser bolts
            lasers.append(Laser(self.x - 12, self.y - 18))
            lasers.append(Laser(self.x + 12, self.y - 18))
            sound_mgr.play("laser")

    def draw(self, surface):
        # Flicker when recently damaged
        if self.invincible_timer > 0 and (self.invincible_timer // 4) % 2 == 0:
            return

        cx, cy = int(self.x), int(self.y)

        # Draw Futuristic Purple Robotic Craft
        # 1. Outer Purple Wings
        wing_points = [
            (cx, cy - 22),
            (cx + 22, cy + 18),
            (cx + 14, cy + 22),
            (cx, cy + 14),
            (cx - 14, cy + 22),
            (cx - 22, cy + 18)
        ]
        pygame.draw.polygon(surface, PLAYER_PURPLE_DARK, wing_points)
        pygame.draw.polygon(surface, PLAYER_PURPLE, wing_points, width=2)

        # 2. Main Purple Fuselage (Chassis)
        body_points = [
            (cx, cy - 24),
            (cx + 12, cy + 8),
            (cx, cy + 16),
            (cx - 12, cy + 8)
        ]
        pygame.draw.polygon(surface, PLAYER_PURPLE, body_points)

        # 3. Bright Purple / Cyan Energy Core
        pygame.draw.circle(surface, PLAYER_PURPLE_LIGHT, (cx, cy + 2), 7)
        pygame.draw.circle(surface, COLOR_WHITE, (cx, cy + 2), 3)

        # 4. Purple Cannon Barrels
        pygame.draw.rect(surface, PLAYER_PURPLE_LIGHT, (cx - 14, cy - 8, 3, 12))
        pygame.draw.rect(surface, PLAYER_PURPLE_LIGHT, (cx + 11, cy - 8, 3, 12))


# ---------------------------------------------------------------------------
# LASER PROJECTILE
# ---------------------------------------------------------------------------
class Laser:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 4
        self.height = 16
        self.speed = 12.0

    def update(self):
        self.y -= self.speed

    def get_rect(self):
        return pygame.Rect(self.x - self.width / 2, self.y - self.height, self.width, self.height)

    def draw(self, surface):
        rect = self.get_rect()
        pygame.draw.rect(surface, COLOR_CYAN, rect, border_radius=2)
        # Inner white beam
        inner_rect = pygame.Rect(rect.x + 1, rect.y + 2, rect.width - 2, rect.height - 4)
        pygame.draw.rect(surface, COLOR_WHITE, inner_rect, border_radius=1)


# ---------------------------------------------------------------------------
# 4. OBSTACLES & ENEMIES (MOVE AUTOMATICALLY)
# ---------------------------------------------------------------------------
class Enemy:
    """
    Rogue Combat Drone moving automatically downwards with sine-wave motion.
    Must be avoided or destroyed (Requirement 4).
    """
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.base_x = x
        self.speed = speed
        self.width = 36
        self.height = 36
        self.sine_phase = random.uniform(0, math.pi * 2)
        self.sine_amplitude = random.uniform(20, 50)
        self.color = COLOR_RED

    def update(self):
        self.y += self.speed
        self.sine_phase += 0.05
        self.x = self.base_x + math.sin(self.sine_phase) * self.sine_amplitude
        # Keep inside screen width
        self.x = max(20, min(SCREEN_WIDTH - 20, self.x))

    def get_rect(self):
        return pygame.Rect(self.x - self.width / 2, self.y - self.height / 2, self.width, self.height)

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        # Hexagonal Drone Body
        points = [
            (cx, cy - 16),
            (cx + 16, cy - 6),
            (cx + 12, cy + 14),
            (cx - 12, cy + 14),
            (cx - 16, cy - 6)
        ]
        pygame.draw.polygon(surface, (80, 15, 25), points)
        pygame.draw.polygon(surface, COLOR_RED, points, width=2)
        # Menacing eye
        pygame.draw.circle(surface, COLOR_RED, (cx, cy - 2), 5)
        pygame.draw.circle(surface, COLOR_WHITE, (cx, cy - 2), 2)


class Obstacle:
    """
    Hazardous Cosmic Asteroid falling automatically.
    Player must navigate around or destroy it (Requirement 4).
    """
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.radius = random.randint(16, 26)
        self.angle = 0
        self.rot_speed = random.uniform(-0.04, 0.04)
        # Generate jagged polygon vertices
        num_points = 8
        self.points = []
        for i in range(num_points):
            ang = (i / num_points) * math.pi * 2
            r = self.radius * random.uniform(0.75, 1.15)
            self.points.append((r * math.cos(ang), r * math.sin(ang)))

    def update(self):
        self.y += self.speed
        self.angle += self.rot_speed

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        rotated_points = []
        cos_a = math.cos(self.angle)
        sin_a = math.sin(self.angle)
        for px, py in self.points:
            rx = cx + (px * cos_a - py * sin_a)
            ry = cy + (px * sin_a + py * cos_a)
            rotated_points.append((rx, ry))

        pygame.draw.polygon(surface, (55, 35, 20), rotated_points)
        pygame.draw.polygon(surface, COLOR_ORANGE, rotated_points, width=2)


class EnergyCore:
    """
    Collectible Item (Requirement 6).
    Increases score by +50 points when collected.
    """
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.radius = 12
        self.pulse = 0.0

    def update(self):
        self.y += self.speed
        self.pulse += 0.08

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        r = self.radius + math.sin(self.pulse) * 3
        # Glowing green energy orb
        pygame.draw.circle(surface, (20, 80, 40), (cx, cy), int(r + 3))
        pygame.draw.circle(surface, COLOR_GREEN, (cx, cy), int(r))
        pygame.draw.circle(surface, COLOR_WHITE, (cx, cy), max(2, int(r * 0.4)))


# ---------------------------------------------------------------------------
# STARFIELD BACKGROUND
# ---------------------------------------------------------------------------
class Starfield:
    def __init__(self, count=90):
        self.stars = []
        for _ in range(count):
            self.stars.append([
                random.randint(0, SCREEN_WIDTH),
                random.randint(0, SCREEN_HEIGHT),
                random.uniform(0.6, 2.8),  # Speed / layer
                random.randint(1, 2)       # Size
            ])

    def update(self, speed_mult=1.0):
        for s in self.stars:
            s[1] += s[2] * speed_mult
            if s[1] > SCREEN_HEIGHT:
                s[1] = 0
                s[0] = random.randint(0, SCREEN_WIDTH)

    def draw(self, surface):
        for s in self.stars:
            brightness = int(100 + s[2] * 50)
            col = (brightness, brightness, min(255, brightness + 40))
            pygame.draw.rect(surface, col, (int(s[0]), int(s[1]), s[3], s[3]))


# ---------------------------------------------------------------------------
# MAIN GAME CONTROLLER CLASS
# ---------------------------------------------------------------------------
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Cyber Defender - Robot Programming UC3M (game.py)")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        # 9. CLOCK FOR SMOOTH FPS CONTROL
        self.clock = pygame.time.Clock()
        self.sound_mgr = SoundManager()

        # Fonts
        self.font_title = pygame.font.SysFont("consolas", 44, bold=True)
        self.font_heading = pygame.font.SysFont("consolas", 26, bold=True)
        self.font_body = pygame.font.SysFont("consolas", 18)
        self.font_hud = pygame.font.SysFont("consolas", 20, bold=True)

        self.starfield = Starfield()
        self.high_score = 0
        self.reset_game()
        self.state = STATE_WELCOME

    def reset_game(self):
        """Prepares a fresh session."""
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 90)
        self.lasers = []
        self.enemies = []
        self.obstacles = []
        self.items = []
        self.particles = []

        # 6 & 7. SCORE SYSTEM
        self.score = 0
        # 9. INCREASING DIFFICULTY
        self.level = 1
        self.difficulty_mult = 1.0

        # Spawning timers
        self.enemy_spawn_timer = 0
        self.obstacle_spawn_timer = 0
        self.item_spawn_timer = 0

    # -----------------------------------------------------------------------
    # 2. WELCOME SCREEN
    # -----------------------------------------------------------------------
    def draw_welcome_screen(self):
        self.screen.fill(COLOR_BG_DARK)
        self.starfield.draw(self.screen)

        # Title Banner
        title_surf = self.font_title.render("CYBER DEFENDER", True, PLAYER_PURPLE_LIGHT)
        self.screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 85))

        subtitle_surf = self.font_body.render("ROBOT PROGRAMMING ASSESSMENT - UC3M", True, COLOR_CYAN)
        self.screen.blit(subtitle_surf, (SCREEN_WIDTH // 2 - subtitle_surf.get_width() // 2, 140))

        # Decorative Purple Player Showcase
        center_x = SCREEN_WIDTH // 2
        center_y = 230
        pygame.draw.circle(self.screen, (35, 15, 60), (center_x, center_y), 50)
        pygame.draw.circle(self.screen, PLAYER_PURPLE, (center_x, center_y), 50, width=2)
        demo_player = Player(center_x, center_y + 4)
        demo_player.draw(self.screen)

        label_purple = self.font_body.render("PILOT: PURPLE DEFENDER UNIT", True, PLAYER_PURPLE_LIGHT)
        self.screen.blit(label_purple, (center_x - label_purple.get_width() // 2, center_y + 60))

        # Instructions Box
        box_rect = pygame.Rect(120, 320, 560, 160)
        pygame.draw.rect(self.screen, COLOR_HUD_BG, box_rect, border_radius=8)
        pygame.draw.rect(self.screen, PLAYER_PURPLE, box_rect, width=1, border_radius=8)

        instructions = [
            ("CONTROLS:", COLOR_CYAN),
            ("  [ARROW KEYS] or [W, A, S, D] -> Move Purple Ship", COLOR_WHITE),
            ("  [SPACEBAR]                   -> Fire Laser Cannons", COLOR_WHITE),
            ("MISSION OBJECTIVES:", COLOR_CYAN),
            ("  * Destroy Enemies (+100 pts)  * Dodge Asteroids (+10 pts)", COLOR_GRAY),
            ("  * Collect Energy Cores (+50 pts) * Survive & level up!", COLOR_GRAY)
        ]

        cur_y = 330
        for text, color in instructions:
            line_surf = self.font_body.render(text, True, color)
            self.screen.blit(line_surf, (140, cur_y))
            cur_y += 22

        # 2. Waiting for player to press a key message (pulsing effect)
        pulse = (pygame.time.get_ticks() // 400) % 2 == 0
        prompt_col = COLOR_WHITE if pulse else PLAYER_PURPLE_LIGHT
        prompt_surf = self.font_heading.render(">> PRESS ANY KEY TO START <<", True, prompt_col)
        self.screen.blit(prompt_surf, (SCREEN_WIDTH // 2 - prompt_surf.get_width() // 2, 515))

    # -----------------------------------------------------------------------
    # 8. END GAME SCREEN
    # -----------------------------------------------------------------------
    def draw_gameover_screen(self):
        # Translucent dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 10, 20, 215))
        self.screen.blit(overlay, (0, 0))

        # Game Over Title
        title_surf = self.font_title.render("SYSTEM COMPROMISED", True, COLOR_RED)
        self.screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 130))

        sub_surf = self.font_heading.render("GAME OVER", True, COLOR_WHITE)
        self.screen.blit(sub_surf, (SCREEN_WIDTH // 2 - sub_surf.get_width() // 2, 185))

        # Score Summary Box
        box_rect = pygame.Rect(200, 240, 400, 160)
        pygame.draw.rect(self.screen, COLOR_HUD_BG, box_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLOR_RED, box_rect, width=2, border_radius=8)

        score_text = self.font_heading.render(f"FINAL SCORE: {self.score}", True, COLOR_CYAN)
        high_text = self.font_body.render(f"BEST RECORD: {self.high_score}", True, COLOR_GREEN)
        level_text = self.font_body.render(f"DIFFICULTY LEVEL REACHED: {self.level}", True, COLOR_WHITE)

        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 265))
        self.screen.blit(high_text, (SCREEN_WIDTH // 2 - high_text.get_width() // 2, 310))
        self.screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 345))

        # Options to play again or exit
        play_again_surf = self.font_heading.render("PRESS [R] TO PLAY AGAIN", True, PLAYER_PURPLE_LIGHT)
        exit_surf = self.font_body.render("PRESS [Q] OR [ESC] TO EXIT", True, COLOR_GRAY)

        self.screen.blit(play_again_surf, (SCREEN_WIDTH // 2 - play_again_surf.get_width() // 2, 435))
        self.screen.blit(exit_surf, (SCREEN_WIDTH // 2 - exit_surf.get_width() // 2, 480))

    # -----------------------------------------------------------------------
    # 7. CURRENT SCORE & HUD DISPLAY
    # -----------------------------------------------------------------------
    def draw_hud(self):
        # Top HUD Bar
        hud_bar = pygame.Rect(0, 0, SCREEN_WIDTH, 42)
        pygame.draw.rect(self.screen, (12, 15, 30), hud_bar)
        pygame.draw.line(self.screen, PLAYER_PURPLE, (0, 42), (SCREEN_WIDTH, 42), 2)

        # Current Score
        score_surf = self.font_hud.render(f"SCORE: {self.score}", True, COLOR_CYAN)
        self.screen.blit(score_surf, (20, 10))

        # Difficulty / Level
        level_surf = self.font_hud.render(f"LEVEL: {self.level} ({self.difficulty_mult:.1f}x)", True, COLOR_GREEN)
        self.screen.blit(level_surf, (SCREEN_WIDTH // 2 - level_surf.get_width() // 2, 10))

        # Player Lives (Hearts)
        lives_label = self.font_hud.render("LIVES:", True, COLOR_WHITE)
        self.screen.blit(lives_label, (SCREEN_WIDTH - 180, 10))
        for i in range(3):
            lx = SCREEN_WIDTH - 95 + (i * 26)
            ly = 20
            color = PLAYER_PURPLE_LIGHT if i < self.player.lives else (60, 60, 80)
            # Draw heart shape
            pygame.draw.circle(self.screen, color, (lx - 4, ly - 2), 5)
            pygame.draw.circle(self.screen, color, (lx + 4, ly - 2), 5)
            pygame.draw.polygon(self.screen, color, [(lx - 8, ly - 1), (lx + 8, ly - 1), (lx, ly + 8)])

    # -----------------------------------------------------------------------
    # 9. DIFFICULTY SCALING ENGINE
    # -----------------------------------------------------------------------
    def update_difficulty(self):
        # Level up every 400 points
        new_level = 1 + (self.score // 400)
        if new_level != self.level:
            self.level = new_level
            # Increase enemy velocity and spawn rates
            self.difficulty_mult = 1.0 + (self.level - 1) * 0.18

    # -----------------------------------------------------------------------
    # EXPLOSION SPAWNER HELPER
    # -----------------------------------------------------------------------
    def spawn_explosion(self, x, y, color=COLOR_RED, count=18):
        for _ in range(count):
            ang = random.uniform(0, math.pi * 2)
            spd = random.uniform(1.5, 6.0)
            self.particles.append(Particle(
                x=x, y=y,
                color=color,
                size=random.uniform(2.5, 5.0),
                vx=math.cos(ang) * spd,
                vy=math.sin(ang) * spd,
                life=random.randint(18, 30)
            ))

    # -----------------------------------------------------------------------
    # GAMEPLAY LOOP
    # -----------------------------------------------------------------------
    def run(self):
        running = True
        while running:
            # 9. Smooth 60 FPS clock
            self.clock.tick(FPS)

            # ===============================================================
            # EVENT HANDLING
            # ===============================================================
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # 2. WELCOME SCREEN: Wait for any key
                elif self.state == STATE_WELCOME:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                        else:
                            self.reset_game()
                            self.state = STATE_PLAYING

                # 8. END GAME SCREEN: Options to play again or exit
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
                            self.player.shoot(self.lasers, self.sound_mgr)

            # ===============================================================
            # STATE UPDATES
            # ===============================================================
            if self.state == STATE_PLAYING:
                keys = pygame.key.get_pressed()
                # Continuous firing when holding Spacebar
                if keys[pygame.K_SPACE]:
                    self.player.shoot(self.lasers, self.sound_mgr)

                self.update_difficulty()
                self.starfield.update(speed_mult=self.difficulty_mult)
                self.player.update(keys, self.particles)

                # -----------------------------------------------------------
                # Spawning Entities (Automatic Movement)
                # -----------------------------------------------------------
                # Spawn Rogue Enemy Drones
                self.enemy_spawn_timer += 1
                enemy_threshold = max(35, int(75 / self.difficulty_mult))
                if self.enemy_spawn_timer >= enemy_threshold:
                    self.enemy_spawn_timer = 0
                    spawn_x = random.randint(40, SCREEN_WIDTH - 40)
                    enemy_spd = random.uniform(2.4, 4.0) * self.difficulty_mult
                    self.enemies.append(Enemy(spawn_x, -30, enemy_spd))

                # Spawn Hazardous Asteroids
                self.obstacle_spawn_timer += 1
                obstacle_threshold = max(45, int(95 / self.difficulty_mult))
                if self.obstacle_spawn_timer >= obstacle_threshold:
                    self.obstacle_spawn_timer = 0
                    spawn_x = random.randint(30, SCREEN_WIDTH - 30)
                    obs_spd = random.uniform(2.0, 3.8) * self.difficulty_mult
                    self.obstacles.append(Obstacle(spawn_x, -30, obs_spd))

                # Spawn Collectible Energy Cores
                self.item_spawn_timer += 1
                if self.item_spawn_timer >= 180:
                    self.item_spawn_timer = 0
                    spawn_x = random.randint(50, SCREEN_WIDTH - 50)
                    self.items.append(EnergyCore(spawn_x, -20, speed=2.5))

                # -----------------------------------------------------------
                # Update Lasers
                # -----------------------------------------------------------
                for laser in self.lasers[:]:
                    laser.update()
                    if laser.y < -20:
                        self.lasers.remove(laser)

                # -----------------------------------------------------------
                # Update Enemies & Check Out-of-bounds (Overcoming obstacles)
                # -----------------------------------------------------------
                for enemy in self.enemies[:]:
                    enemy.update()
                    # 6. Overcoming obstacles reward
                    if enemy.y > SCREEN_HEIGHT + 30:
                        self.enemies.remove(enemy)
                        self.score += 10

                for obs in self.obstacles[:]:
                    obs.update()
                    if obs.y > SCREEN_HEIGHT + 40:
                        self.obstacles.remove(obs)
                        self.score += 10

                for item in self.items[:]:
                    item.update()
                    if item.y > SCREEN_HEIGHT + 20:
                        self.items.remove(item)

                # -----------------------------------------------------------
                # 5. COLLISIONS DETECTION & SCORING
                # -----------------------------------------------------------
                player_rect = self.player.get_rect()

                # Laser vs Enemy Collisions (6. Destroying enemies: +100 pts)
                for laser in self.lasers[:]:
                    laser_rect = laser.get_rect()
                    hit = False
                    for enemy in self.enemies[:]:
                        if laser_rect.colliderect(enemy.get_rect()):
                            self.spawn_explosion(enemy.x, enemy.y, COLOR_RED, count=22)
                            self.enemies.remove(enemy)
                            self.score += 100
                            self.sound_mgr.play("explosion")
                            hit = True
                            break
                    if hit:
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                        continue

                    # Laser vs Asteroid Collisions
                    for obs in self.obstacles[:]:
                        if laser_rect.colliderect(obs.get_rect()):
                            self.spawn_explosion(obs.x, obs.y, COLOR_ORANGE, count=16)
                            self.obstacles.remove(obs)
                            self.score += 50
                            self.sound_mgr.play("explosion")
                            hit = True
                            break
                    if hit and laser in self.lasers:
                        self.lasers.remove(laser)

                # Player vs Collectible Items (6. Collecting items: +50 pts)
                for item in self.items[:]:
                    if player_rect.colliderect(item.get_rect()):
                        self.spawn_explosion(item.x, item.y, COLOR_GREEN, count=12)
                        self.items.remove(item)
                        self.score += 50
                        self.sound_mgr.play("item")

                # Player vs Enemy / Obstacle Collisions (5. Player loses life)
                if self.player.invincible_timer <= 0:
                    collided_hazard = None

                    # Check Enemies
                    for enemy in self.enemies[:]:
                        if player_rect.colliderect(enemy.get_rect()):
                            collided_hazard = (enemy.x, enemy.y, COLOR_RED)
                            self.enemies.remove(enemy)
                            break

                    # Check Asteroids
                    if not collided_hazard:
                        for obs in self.obstacles[:]:
                            if player_rect.colliderect(obs.get_rect()):
                                collided_hazard = (obs.x, obs.y, COLOR_ORANGE)
                                self.obstacles.remove(obs)
                                break

                    if collided_hazard:
                        hx, hy, hcol = collided_hazard
                        self.spawn_explosion(hx, hy, hcol, count=25)
                        self.spawn_explosion(self.player.x, self.player.y, PLAYER_PURPLE, count=20)
                        self.player.lives -= 1
                        self.player.invincible_timer = 90  # 1.5 seconds of invincibility
                        self.sound_mgr.play("hit")

                        # 5 & 8. Check End Game Condition
                        if self.player.lives <= 0:
                            if self.score > self.high_score:
                                self.high_score = self.score
                            self.sound_mgr.play("gameover")
                            self.state = STATE_GAMEOVER

                # Update particles
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
                self.screen.fill(COLOR_BG_DARK)
                self.starfield.draw(self.screen)

                # Draw Items
                for item in self.items:
                    item.draw(self.screen)

                # Draw Obstacles & Enemies
                for obs in self.obstacles:
                    obs.draw(self.screen)
                for enemy in self.enemies:
                    enemy.draw(self.screen)

                # Draw Lasers
                for laser in self.lasers:
                    laser.draw(self.screen)

                # Draw Particles
                for p in self.particles:
                    p.draw(self.screen)

                # 10. Draw Purple Player
                self.player.draw(self.screen)

                # 7. Draw Current Score HUD
                self.draw_hud()

            elif self.state == STATE_GAMEOVER:
                # Keep last active game scene in background
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
