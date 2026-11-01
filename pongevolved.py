import math
import random
import sys
import pygame

# Initialize Pygame
pygame.init()
pygame.font.init()

# Screen Dimensions (Portrait Mode matching your mobile design)
WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong Evolved - Desktop Edition")
clock = pygame.time.Clock()

# Fonts
FONT_SM = pygame.font.SysFont("Courier", 14, bold=True)
FONT_MD = pygame.font.SysFont("Courier", 18, bold=True)
FONT_LG = pygame.font.SysFont("Courier", 28, bold=True)
FONT_XL = pygame.font.SysFont("Courier", 42, bold=True)


class PongGamePygame:

    def __init__(self):
        self.state = "MENU"
        self.frame_count = 0
        self.countdown_frames = 0

        # Snow particles
        self.snowflakes = []
        for _ in range(70):
            self.snowflakes.append(
                [
                    random.uniform(0, WIDTH),
                    random.uniform(0, HEIGHT),
                    random.uniform(0.5, 2.0),
                ]
            )

        # Title screen preview animation variables
        self.preview_ball = pygame.Rect(WIDTH / 2 - 10, HEIGHT / 2 - 10, 20, 20)
        self.preview_ball_dir = [3, 2]
        self.preview_paddle_a = pygame.Rect(80, HEIGHT / 2 - 50, 20, 100)
        self.preview_paddle_b = pygame.Rect(WIDTH - 100, HEIGHT / 2 - 50, 20, 100)

        self.init_game_variables()

    def init_game_variables(self):
        self.player_hearts = 2
        self.ai_hearts = 2
        self.max_hearts = 6

        self.game_mode = "CAMPAIGN"  # 'CAMPAIGN' or 'ENDLESS'
        self.boss_level = 1
        self.boss_hearts = 2
        self.max_boss_levels = 4
        self.endless_wave = 1
        self.is_boss_active = False

        self.speed_escalation_timer = 0
        self.current_base_speed = 2.5

        self.boss_ability_timer = 0
        self.active_projectiles = []
        self.arena_obstacle = None
        self.obstacle_timer = 0
        self.player_frozen_timer = 0

        self.pending_next_phase = "BOSS_START"
        self.current_perk_choices = []
        self.frame_count = 0

        # Ball and Paddles
        self.ball = pygame.Rect(WIDTH / 2 - 10, HEIGHT / 2 - 10, 20, 20)
        self.ball_dir = [self.current_base_speed, self.current_base_speed]

        self.paddle_a = pygame.Rect(30, HEIGHT / 2 - 50, 20, 100)
        self.paddle_b = pygame.Rect(WIDTH - 50, HEIGHT / 2 - 50, 20, 100)
        self.original_paddle_h = 100

        self.base_ai_speed = 2.7
        self.paddle_color = (
            int(random.uniform(75, 255)),
            int(random.uniform(75, 255)),
            int(random.uniform(75, 255)),
        )

        self.power_ups = []
        self.active_effect = None
        self.effect_timer = 0
        self.spawn_timer = 0
        self.victory_message = "YOU DEFEATED ALL BOSSES!"

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                self.handle_click(mx, my)

    def handle_click(self, mx, my):
        if self.state == "MENU":
            # Start Campaign (y: 250 to 295)
            if (WIDTH / 2 - 100 <= mx <= WIDTH / 2 + 100) and (
                250 <= my <= 295
            ):
                self.init_game_variables()
                self.game_mode = "CAMPAIGN"
                self.state = "PLAYING"
            # Endless Mode (y: 310 to 355)
            elif (WIDTH / 2 - 100 <= mx <= WIDTH / 2 + 100) and (
                310 <= my <= 355
            ):
                self.init_game_variables()
                self.game_mode = "ENDLESS"
                self.state = "PLAYING"
            # Quit (y: 370 to 415)
            elif (WIDTH / 2 - 100 <= mx <= WIDTH / 2 + 100) and (
                370 <= my <= 415
            ):
                pygame.quit()
                sys.exit()

        elif self.state == "PLAYING":
            # Pause button top right
            if (WIDTH - 90 <= mx <= WIDTH - 15) and (15 <= my <= 45):
                self.state = "PAUSED"

        elif self.state == "PAUSED":
            # Resume button (y: HEIGHT/2 - 30 to HEIGHT/2 + 15 -> 370 to 415)
            if (WIDTH / 2 - 100 <= mx <= WIDTH / 2 + 100) and (
                HEIGHT / 2 - 30 <= my <= HEIGHT / 2 + 15
            ):
                self.state = "COUNTDOWN"
                self.countdown_frames = 180
            # Quit to Menu button (y: HEIGHT/2 + 25 to HEIGHT/2 + 70 -> 425 to 470)
            elif (WIDTH / 2 - 100 <= mx <= WIDTH / 2 + 100) and (
                HEIGHT / 2 + 25 <= my <= HEIGHT / 2 + 70
            ):
                self.state = "MENU"
            # Exit Game button (y: HEIGHT/2 + 85 to HEIGHT/2 + 130 -> 485 to 530)
            elif (WIDTH / 2 - 100 <= mx <= WIDTH / 2 + 100) and (
                HEIGHT / 2 + 85 <= my <= HEIGHT / 2 + 130
            ):
                pygame.quit()
                sys.exit()

        elif self.state == "PERK_SELECT":
            card_w, card_h = 320, 80
            start_y = HEIGHT / 2 + 60
            for i, perk in enumerate(self.current_perk_choices):
                cy = start_y - (i * 100)
                if (WIDTH / 2 - card_w / 2 <= mx <= WIDTH / 2 + card_w / 2) and (
                    cy <= my <= cy + card_h
                ):
                    self.apply_perk(perk["title"])

        elif self.state in ["GAMEOVER", "VICTORY"]:
            # Restart button (y: HEIGHT/2 - 20 to HEIGHT/2 + 30 -> 380 to 430)
            if (WIDTH / 2 - 100 <= mx <= WIDTH / 2 + 100) and (
                HEIGHT / 2 - 20 <= my <= HEIGHT / 2 + 30
            ):
                self.init_game_variables()
                self.state = "PLAYING"
            # Quit to Menu button (y: HEIGHT/2 + 45 to HEIGHT/2 + 95 -> 445 to 495)
            elif (WIDTH / 2 - 100 <= mx <= WIDTH / 2 + 100) and (
                HEIGHT / 2 + 45 <= my <= HEIGHT / 2 + 95
            ):
                self.state = "MENU"

    def update(self):
        self.frame_count += 1

        if self.state == "MENU":
            self.preview_ball.x += self.preview_ball_dir[0]
            self.preview_ball.y += self.preview_ball_dir[1]

            if (
                self.preview_ball.y <= 50
                or self.preview_ball.y >= HEIGHT - 180
            ):
                self.preview_ball_dir[1] *= -1

            preview_paddle_b_center = (
                self.preview_paddle_b.y + self.preview_paddle_b.height / 2
            )
            if preview_paddle_b_center < self.preview_ball.y:
                self.preview_paddle_b.y += 2
            elif preview_paddle_b_center > self.preview_ball.y:
                self.preview_paddle_b.y -= 2

            self.preview_paddle_a.y = self.preview_ball.y - 50

            if self.preview_ball.colliderect(
                self.preview_paddle_a
            ) or self.preview_ball.colliderect(self.preview_paddle_b):
                self.preview_ball_dir[0] *= -1

            if self.preview_ball.x <= 0 or self.preview_ball.x >= WIDTH:
                self.preview_ball.x = WIDTH / 2 - 10
                self.preview_ball.y = HEIGHT / 2 - 10
                self.preview_ball_dir[0] *= -1

        # Continuous mouse tracking for player paddle
        if self.state == "PLAYING" and self.player_frozen_timer <= 0:
            mouse_pos = pygame.mouse.get_pos()
            if mouse_pos[0] < WIDTH / 2:
                self.paddle_a.y = mouse_pos[1] - (self.paddle_a.height / 2)
                self.paddle_a.y = max(
                    0, min(HEIGHT - self.paddle_a.height, self.paddle_a.y)
                )

        if self.state == "PLAYING":
            if self.player_frozen_timer > 0:
                self.player_frozen_timer -= 1

            # Ball Speed Escalation
            self.speed_escalation_timer += 1
            if self.speed_escalation_timer >= 600:
                self.speed_escalation_timer = 0
                self.current_base_speed *= 1.05
                if not self.active_effect:
                    curr_mag = math.hypot(
                        self.ball_dir[0], self.ball_dir[1]
                    )
                    if curr_mag > 0:
                        self.ball_dir[0] = (
                            self.ball_dir[0] / curr_mag
                        ) * self.current_base_speed
                        self.ball_dir[1] = (
                            self.ball_dir[1] / curr_mag
                        ) * self.current_base_speed

            # Boss Abilities Logic
            if self.is_boss_active:
                self.boss_ability_timer += 1
                # Level 1: Blue Boss - Ice Shards
                if self.boss_level == 1 and self.boss_ability_timer >= 300:
                    self.boss_ability_timer = 0
                    self.active_projectiles.append(
                        {
                            "rect": pygame.Rect(
                                self.paddle_b.x,
                                random.randint(
                                    int(HEIGHT * 0.2), int(HEIGHT * 0.8)
                                ),
                                20,
                                20,
                            ),
                            "type": "ice_shard",
                        }
                    )
                # Level 2: Green Boss - Shifting Barrier
                elif self.boss_level == 2:
                    self.obstacle_timer += 1
                    if self.arena_obstacle is None:
                        if self.obstacle_timer >= 180:
                            self.obstacle_timer = 0
                            rx = random.randint(
                                int(WIDTH * 0.35), int(WIDTH * 0.65)
                            )
                            ry = random.randint(100, int(HEIGHT - 200))
                            self.arena_obstacle = pygame.Rect(rx, ry, 20, 100)
                    else:
                        if self.obstacle_timer >= 600:
                            self.obstacle_timer = 0
                            self.arena_obstacle = None
                # Level 3: Yellow Boss - Speed Burst
                elif self.boss_level == 3 and self.boss_ability_timer >= 350:
                    self.boss_ability_timer = 0
                    self.ball_dir[0] *= 1.3
                    self.ball_dir[1] *= 1.3
                # Level 4: Red Boss - Horizontal Laser
                elif self.boss_level == 4 and self.boss_ability_timer >= 250:
                    self.boss_ability_timer = 0
                    rand_y = random.randint(80, int(HEIGHT - 120))
                    self.active_projectiles.append(
                        {
                            "rect": pygame.Rect(0, rand_y, WIDTH, 12),
                            "type": "laser",
                            "timer": 60,
                        }
                    )

            # Move Projectiles
            for proj in self.active_projectiles[:]:
                if proj["type"] == "ice_shard":
                    proj["rect"].x -= 4
                    if proj["rect"].colliderect(self.paddle_a):
                        self.player_frozen_timer = 90
                        self.active_projectiles.remove(proj)
                    elif proj["rect"].x < 0:
                        self.active_projectiles.remove(proj)
                elif proj["type"] == "laser":
                    proj["timer"] -= 1
                    if proj["timer"] <= 0:
                        if proj["rect"].colliderect(self.paddle_a):
                            self.player_hearts -= 1
                            if self.player_hearts <= 0:
                                self.state = "GAMEOVER"
                        self.active_projectiles.remove(proj)

            # Power-up expiration
            if self.active_effect:
                self.effect_timer -= 1
                if self.effect_timer <= 0:
                    self.remove_effect()

            # Power-up Spawning
            total_seconds = self.frame_count // 60
            minute_block = total_seconds // 60
            self.spawn_timer += 1
            spawn_interval = max(80, 300 - (minute_block * 45))
            if self.spawn_timer > spawn_interval:
                self.spawn_power_up()
                self.spawn_timer = 0

            for p in self.power_ups[:]:
                p["rect"].y -= 1.5
                p["lifetime"] -= 1
                if p["lifetime"] <= 0 or p["rect"].y < 0:
                    self.power_ups.remove(p)

            # Move Ball
            self.ball.x += self.ball_dir[0]
            self.ball.y += self.ball_dir[1]

            # Wall Collisions
            if self.ball.y <= 0:
                self.ball.y = 0
                self.ball_dir[1] *= -1
            elif self.ball.y >= HEIGHT - self.ball.height:
                self.ball.y = HEIGHT - self.ball.height
                self.ball_dir[1] *= -1

            # Obstacle Collision (Green Boss)
            if self.arena_obstacle and self.ball.colliderect(
                self.arena_obstacle
            ):
                self.ball_dir[0] *= -1

            # Paddle Collisions
            if self.ball.colliderect(self.paddle_a) and self.ball_dir[0] < 0:
                self.ball.x = self.paddle_a.right
                self.ball_dir[0] *= -1
            if self.ball.colliderect(self.paddle_b) and self.ball_dir[0] > 0:
                self.ball.x = self.paddle_b.left - self.ball.width
                self.ball_dir[0] *= -1

            # Scoring
            if self.ball.x <= 0:
                self.player_hearts -= 1
                if self.player_hearts <= 0:
                    self.state = "GAMEOVER"
                else:
                    self.reset_ball()
            elif self.ball.x >= WIDTH:
                if self.is_boss_active:
                    self.boss_hearts -= 1
                    if self.boss_hearts <= 0:
                        if (
                            self.game_mode == "CAMPAIGN"
                            and self.boss_level >= self.max_boss_levels
                        ):
                            self.victory_message = "YOU DEFEATED ALL BOSSES!"
                            self.state = "VICTORY"
                        else:
                            self.pending_next_phase = "NEXT_BOSS"
                            self.generate_perks()
                            self.state = "PERK_SELECT"
                    else:
                        self.reset_ball()
                else:
                    self.ai_hearts -= 1
                    if self.ai_hearts <= 0:
                        self.pending_next_phase = "BOSS_START"
                        self.generate_perks()
                        self.state = "PERK_SELECT"
                    else:
                        self.reset_ball()

            for p in self.power_ups[:]:
                if self.ball.colliderect(p["rect"]):
                    self.apply_effect(p["type"])
                    self.power_ups.remove(p)

            # AI / Boss Movement
            if self.is_boss_active:
                current_ai_speed = (
                    self.base_ai_speed + 1.2 + (self.boss_level * 1.8)
                )
                target_y = self.ball.y + (self.ball_dir[1] * 4)
            else:
                current_ai_speed = self.base_ai_speed
                target_y = self.ball.y + (self.ball_dir[1] * 1.5)

            paddle_b_center = self.paddle_b.y + (self.paddle_b.height / 2)
            if (
                paddle_b_center < target_y
                and self.paddle_b.y + self.paddle_b.height < HEIGHT
            ):
                self.paddle_b.y += current_ai_speed
            elif paddle_b_center > target_y and self.paddle_b.y > 0:
                self.paddle_b.y -= current_ai_speed

        elif self.state == "COUNTDOWN":
            self.countdown_frames -= 1
            if self.countdown_frames <= 0:
                self.state = "PLAYING"

    def draw(self):
        screen.fill((13, 26, 64))  # Deep blue background

        # Draw snow
        for flake in self.snowflakes:
            flake[1] -= flake[2]
            if flake[1] < 0:
                flake[1] = HEIGHT
                flake[0] = random.uniform(0, WIDTH)
            pygame.draw.rect(screen, (255, 255, 255), (flake[0], flake[1], 3, 3))

        if self.state == "MENU":
            self.draw_menu_screen()
        elif self.state in ["PLAYING", "PAUSED", "COUNTDOWN"]:
            self.draw_game_elements()
            if self.state == "PAUSED":
                self.draw_pause_overlay()
            elif self.state == "COUNTDOWN":
                self.draw_countdown_overlay()
        elif self.state == "PERK_SELECT":
            self.draw_perk_select_screen()
        elif self.state == "GAMEOVER":
            self.draw_game_over_screen()
        elif self.state == "VICTORY":
            self.draw_victory_screen()

        pygame.display.flip()

    def draw_rounded_paddle(self, rect_obj, color):
        pygame.draw.rect(screen, color, rect_obj, border_radius=10)

    def draw_menu_screen(self):
        title = FONT_XL.render("Pong Evolved", True, (255, 255, 255))
        screen.blit(title, (WIDTH / 2 - title.get_width() / 2, 120))

        # Draw title screen preview animation
        self.draw_rounded_paddle(self.preview_paddle_a, (75, 204, 255))
        self.draw_rounded_paddle(self.preview_paddle_b, (25, 102, 230))
        pygame.draw.ellipse(screen, (255, 255, 0), self.preview_ball)

        # Buttons
        btn_campaign = pygame.Rect(WIDTH / 2 - 100, 250, 200, 45)
        btn_endless = pygame.Rect(WIDTH / 2 - 100, 310, 200, 45)
        btn_quit = pygame.Rect(WIDTH / 2 - 100, 370, 200, 45)

        pygame.draw.rect(screen, (50, 200, 75), btn_campaign, border_radius=8)
        pygame.draw.rect(screen, (50, 120, 230), btn_endless, border_radius=8)
        pygame.draw.rect(screen, (200, 50, 50), btn_quit, border_radius=8)

        t1 = FONT_MD.render("START GAME", True, (255, 255, 255))
        t2 = FONT_MD.render("ENDLESS MODE", True, (255, 255, 255))
        t3 = FONT_MD.render("QUIT", True, (255, 255, 255))

        screen.blit(
            t1,
            (
                btn_campaign.centerx - t1.get_width() / 2,
                btn_campaign.centery - t1.get_height() / 2,
            ),
        )
        screen.blit(
            t2,
            (
                btn_endless.centerx - t2.get_width() / 2,
                btn_endless.centery - t2.get_height() / 2,
            ),
        )
        screen.blit(
            t3,
            (
                btn_quit.centerx - t3.get_width() / 2,
                btn_quit.centery - t3.get_height() / 2,
            ),
        )

    def draw_game_elements(self):
        total_seconds = self.frame_count // 60
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        time_str = f"{minutes:02d}:{seconds:02d}"

        p_hp_str = f"HP: {self.player_hearts}/{self.max_hearts}"
        boss_hp_val = self.boss_hearts if self.is_boss_active else self.ai_hearts
        e_hp_str = f"HP: {boss_hp_val}"

        txt_p = FONT_SM.render("PLAYER", True, (255, 50, 50))
        txt_ph = FONT_SM.render(p_hp_str, True, (255, 50, 50))
        screen.blit(txt_p, (100 - txt_p.get_width() / 2, HEIGHT - 755))
        screen.blit(txt_ph, (100 - txt_ph.get_width() / 2, HEIGHT - 732))

        enemy_title = (
            f"BOSS {self.boss_level}" if self.is_boss_active else "ENEMY AI"
        )
        txt_e = FONT_SM.render(enemy_title, True, (255, 50, 50))
        txt_eh = FONT_SM.render(e_hp_str, True, (255, 50, 50))
        screen.blit(txt_e, (WIDTH - 100 - txt_e.get_width() / 2, HEIGHT - 755))
        screen.blit(
            txt_eh, (WIDTH - 100 - txt_eh.get_width() / 2, HEIGHT - 732)
        )

        if self.is_boss_active:
            boss_names = ["BLUE BOSS", "GREEN BOSS", "YELLOW BOSS", "RED BOSS"]
            b_name = boss_names[(self.boss_level - 1) % len(boss_names)]
            wave_str = (
                f"[WAVE {self.endless_wave}] "
                if self.game_mode == "ENDLESS"
                else ""
            )
            txt_b = FONT_MD.render(
                f"⚠️ {wave_str}{b_name} ({time_str})", True, (255, 50, 50)
            )
            screen.blit(txt_b, (WIDTH / 2 - txt_b.get_width() / 2, HEIGHT - 695))
        else:
            txt_n = FONT_SM.render(
                f"Normal Round ({time_str})", True, (180, 200, 255)
            )
            screen.blit(txt_n, (WIDTH / 2 - txt_n.get_width() / 2, HEIGHT - 695))

        # Pause Button
        btn_pause = pygame.Rect(WIDTH - 90, 15, 75, 30)
        pygame.draw.rect(screen, (80, 80, 130), btn_pause, border_radius=5)
        ptxt = FONT_SM.render("PAUSE", True, (255, 255, 255))
        screen.blit(
            ptxt,
            (
                btn_pause.centerx - ptxt.get_width() / 2,
                btn_pause.centery - ptxt.get_height() / 2,
            ),
        )

        # Arena Obstacle (Green Boss)
        if self.arena_obstacle:
            pygame.draw.rect(
                screen, (30, 180, 80), self.arena_obstacle, border_radius=5
            )

        # Projectiles
        for proj in self.active_projectiles:
            if proj["type"] == "ice_shard":
                pygame.draw.ellipse(screen, (100, 200, 255), proj["rect"])
            elif proj["type"] == "laser":
                pygame.draw.rect(screen, (255, 30, 30), proj["rect"])

        # Power-ups
        for p in self.power_ups:
            pygame.draw.ellipse(screen, (200, 200, 50), p["rect"])
            ltxt = FONT_SM.render(p["label"], True, (0, 0, 0))
            screen.blit(
                ltxt,
                (
                    p["rect"].centerx - ltxt.get_width() / 2,
                    p["rect"].centery - ltxt.get_height() / 2,
                ),
            )

        # Player Paddle
        p_color = (
            (100, 200, 255) if self.player_frozen_timer > 0 else self.paddle_color
        )
        self.draw_rounded_paddle(self.paddle_a, p_color)

        # Boss/AI Paddle
        if self.is_boss_active:
            boss_colors = {
                1: (30, 100, 230),
                2: (30, 200, 50),
                3: (230, 230, 30),
                4: (230, 50, 50),
            }
            mapped_lvl = ((self.boss_level - 1) % 4) + 1
            b_col = boss_colors.get(mapped_lvl, (180, 0, 30))
            self.draw_rounded_paddle(self.paddle_b, b_col)
        else:
            self.draw_rounded_paddle(self.paddle_b, (255, 255, 255))

        # Ball
        pygame.draw.ellipse(screen, (255, 255, 0), self.ball)

    def generate_perks(self):
        pool = [
            {"title": "+1 Max Heart", "desc": "Gain a permanent heart container"},
            {
                "title": "Wider Paddle",
                "desc": "Permanently increase paddle size",
            },
            {"title": "Full Heal", "desc": "Restore all lost hearts"},
            {
                "title": "Kinetic Boost",
                "desc": "Permanent slight speed increase",
            },
        ]
        self.current_perk_choices = random.sample(pool, 3)

    def draw_perk_select_screen(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        title = FONT_LG.render("CHOOSE A PERK", True, (255, 255, 0))
        screen.blit(title, (WIDTH / 2 - title.get_width() / 2, HEIGHT - 680))

        card_w, card_h = 320, 80
        start_y = HEIGHT / 2 + 60

        for i, perk in enumerate(self.current_perk_choices):
            cy = start_y - (i * 100)
            card_rect = pygame.Rect(WIDTH / 2 - card_w / 2, cy, card_w, card_h)
            pygame.draw.rect(screen, (40, 65, 115), card_rect, border_radius=8)

            t_title = FONT_MD.render(perk["title"], True, (255, 255, 255))
            t_desc = FONT_SM.render(perk["desc"], True, (200, 220, 255))
            screen.blit(
                t_title, (WIDTH / 2 - t_title.get_width() / 2, cy + 20)
            )
            screen.blit(t_desc, (WIDTH / 2 - t_desc.get_width() / 2, cy + 48))

    def apply_perk(self, perk_title):
        if "+1 Max Heart" in perk_title:
            if self.player_hearts < self.max_hearts:
                self.player_hearts += 1
        elif "Wider Paddle" in perk_title:
            self.original_paddle_h += 20
            self.paddle_a.height = self.original_paddle_h
        elif "Full Heal" in perk_title:
            self.player_hearts = self.max_hearts
        elif "Kinetic Boost" in perk_title:
            self.current_base_speed *= 1.15

        if self.pending_next_phase == "BOSS_START":
            self.is_boss_active = True
            self.boss_level = 1
            self.boss_hearts = 2
        elif self.pending_next_phase == "NEXT_BOSS":
            self.boss_level += 1
            if self.game_mode == "ENDLESS" and self.boss_level > 4:
                self.endless_wave += 1
                self.boss_level = 1
            self.boss_hearts = 2 + ((self.endless_wave - 1) * 1)
            self.is_boss_active = True

        self.arena_obstacle = None
        self.obstacle_timer = 0
        self.reset_ball()
        self.state = "PLAYING"

    def draw_pause_overlay(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        title = FONT_XL.render("PAUSED", True, (255, 255, 255))
        screen.blit(title, (WIDTH / 2 - title.get_width() / 2, HEIGHT / 2 - 120))

        r_btn = pygame.Rect(WIDTH / 2 - 100, HEIGHT / 2 - 30, 200, 45)
        q_btn = pygame.Rect(WIDTH / 2 - 100, HEIGHT / 2 + 25, 200, 45)
        e_btn = pygame.Rect(WIDTH / 2 - 100, HEIGHT / 2 + 85, 200, 45)

        pygame.draw.rect(screen, (50, 200, 75), r_btn, border_radius=6)
        pygame.draw.rect(screen, (200, 130, 30), q_btn, border_radius=6)
        pygame.draw.rect(screen, (200, 50, 50), e_btn, border_radius=6)

        t1 = FONT_MD.render("RESUME", True, (255, 255, 255))
        t2 = FONT_MD.render("QUIT TO MENU", True, (255, 255, 255))
        t3 = FONT_MD.render("EXIT GAME", True, (255, 255, 255))

        screen.blit(
            t1,
            (
                r_btn.centerx - t1.get_width() / 2,
                r_btn.centery - t1.get_height() / 2,
            ),
        )
        screen.blit(
            t2,
            (
                q_btn.centerx - t2.get_width() / 2,
                q_btn.centery - t2.get_height() / 2,
            ),
        )
        screen.blit(
            t3,
            (
                e_btn.centerx - t3.get_width() / 2,
                e_btn.centery - t3.get_height() / 2,
            ),
        )

    def draw_countdown_overlay(self):
        current_num = (self.countdown_frames // 60) + 1
        num_surf = FONT_XL.render(str(current_num), True, (255, 255, 0))
        screen.blit(
            num_surf,
            (
                WIDTH / 2 - num_surf.get_width() / 2,
                HEIGHT / 2 - num_surf.get_height() / 2,
            ),
        )

    def draw_game_over_screen(self):
        title = FONT_XL.render("GAME OVER", True, (255, 50, 50))
        screen.blit(title, (WIDTH / 2 - title.get_width() / 2, HEIGHT / 2 - 120))

        r_btn = pygame.Rect(WIDTH / 2 - 100, HEIGHT / 2 - 20, 200, 50)
        q_btn = pygame.Rect(WIDTH / 2 - 100, HEIGHT / 2 + 45, 200, 50)

        pygame.draw.rect(screen, (50, 200, 75), r_btn, border_radius=6)
        pygame.draw.rect(screen, (200, 50, 50), q_btn, border_radius=6)

        t1 = FONT_MD.render("RESTART", True, (255, 255, 255))
        t2 = FONT_MD.render("QUIT TO MENU", True, (255, 255, 255))

        screen.blit(
            t1,
            (
                r_btn.centerx - t1.get_width() / 2,
                r_btn.centery - t1.get_height() / 2,
            ),
        )
        screen.blit(
            t2,
            (
                q_btn.centerx - t2.get_width() / 2,
                q_btn.centery - t2.get_height() / 2,
            ),
        )

    def draw_victory_screen(self):
        title = FONT_LG.render(self.victory_message, True, (50, 255, 50))
        screen.blit(title, (WIDTH / 2 - title.get_width() / 2, HEIGHT / 2 - 120))

        r_btn = pygame.Rect(WIDTH / 2 - 100, HEIGHT / 2 - 20, 200, 50)
        q_btn = pygame.Rect(WIDTH / 2 - 100, HEIGHT / 2 + 45, 200, 50)

        pygame.draw.rect(screen, (50, 200, 75), r_btn, border_radius=6)
        pygame.draw.rect(screen, (200, 50, 50), q_btn, border_radius=6)

        t1 = FONT_MD.render("RESTART", True, (255, 255, 255))
        t2 = FONT_MD.render("QUIT TO MENU", True, (255, 255, 255))

        screen.blit(
            t1,
            (
                r_btn.centerx - t1.get_width() / 2,
                r_btn.centery - t1.get_height() / 2,
            ),
        )
        screen.blit(
            t2,
            (
                q_btn.centerx - t2.get_width() / 2,
                q_btn.centery - t2.get_height() / 2,
            ),
        )

    def spawn_power_up(self):
        p_types = [
            "speed_up",
            "speed_down",
            "big_player",
            "big_ai",
            "extra_heart",
            "small_ai",
        ]
        chosen = random.choice(p_types)
        labels = {
            "speed_up": "S+",
            "speed_down": "S-",
            "big_player": "P+",
            "big_ai": "P-",
            "extra_heart": "+1",
            "small_ai": "AI-",
        }
        rx = random.randint(int(WIDTH * 0.3), int(WIDTH * 0.7))
        ry = int(HEIGHT - 100)

        p_rect = pygame.Rect(rx, ry, 30, 30)
        self.power_ups.append(
            {
                "rect": p_rect,
                "type": chosen,
                "label": labels[chosen],
                "lifetime": 600,
            }
        )

    def apply_effect(self, p_type):
        self.remove_effect()
        self.active_effect = p_type
        self.effect_timer = 600

        if p_type == "speed_up":
            self.ball_dir[0] *= 1.6
            self.ball_dir[1] *= 1.6
        elif p_type == "speed_down":
            self.ball_dir[0] *= 0.6
            self.ball_dir[1] *= 0.6
        elif p_type == "big_player":
            self.paddle_a.height = self.original_paddle_h * 2
        elif p_type == "big_ai":
            self.paddle_b.height = self.original_paddle_h * 2
        elif p_type == "extra_heart":
            if self.player_hearts < self.max_hearts:
                self.player_hearts += 1
            self.active_effect = None
        elif p_type == "small_ai":
            self.paddle_b.height = max(30, self.original_paddle_h // 2)

    def remove_effect(self):
        if not self.active_effect:
            return
        if self.active_effect in ["speed_up", "speed_down"]:
            sign_x = 1 if self.ball_dir[0] > 0 else -1
            sign_y = 1 if self.ball_dir[1] > 0 else -1
            curr_mag = math.hypot(self.ball_dir[0], self.ball_dir[1])
            if curr_mag > 0:
                self.ball_dir[0] = (
                    abs(self.ball_dir[0]) / curr_mag
                ) * self.current_base_speed * sign_x
                self.ball_dir[1] = (
                    abs(self.ball_dir[1]) / curr_mag
                ) * self.current_base_speed * sign_y
            else:
                self.ball_dir[0] = self.current_base_speed * sign_x
                self.ball_dir[1] = self.current_base_speed * sign_y
        elif self.active_effect == "big_player":
            self.paddle_a.height = self.original_paddle_h
        elif self.active_effect in ["big_ai", "small_ai"]:
            self.paddle_b.height = self.original_paddle_h
        self.active_effect = None

    def reset_ball(self):
        self.ball.x = WIDTH / 2 - 10
        self.ball.y = HEIGHT / 2 - 10
        sign_x = 1 if self.ball_dir[0] > 0 else -1
        sign_y = 1 if self.ball_dir[1] > 0 else -1
        curr_mag = math.hypot(self.ball_dir[0], self.ball_dir[1])
        if curr_mag > 0:
            self.ball_dir[0] = (
                abs(self.ball_dir[0]) / curr_mag
            ) * self.current_base_speed * sign_x
            self.ball_dir[1] = (
                abs(self.ball_dir[1]) / curr_mag
            ) * self.current_base_speed * sign_y
        else:
            self.ball_dir[0] = self.current_base_speed * sign_x
            self.ball_dir[1] = self.current_base_speed * sign_y


if __name__ == "__main__":
    game = PongGamePygame()
    game.run()
