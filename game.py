"""Dig Dug Lite Game.

A 2D arcade grid digging and enemy popping game implemented using Pygame.
Features subterranean tunneling, BFS enemy pathfinding, and inflation attacks.
"""
# pylint: disable=no-member

from collections import deque
import secrets
import pygame

rng = secrets.SystemRandom()

TILE, COLS, ROWS = 32, 20, 14
WIDTH, HEIGHT = COLS * TILE, ROWS * TILE + 36
DIRS = {
    pygame.K_UP: (-1, 0),
    pygame.K_DOWN: (1, 0),
    pygame.K_LEFT: (0, -1),
    pygame.K_RIGHT: (0, 1),
}
MOVE_DELAY, ENEMY_DELAY, PUMP_RANGE, DEFLATE_AFTER = 0.11, 0.35, 3, 1.5


def dirt_color(row):
    """Return an (r, g, b) colour for dirt in the given row.

    Provides distinct colored strata bands based on row depth.
    """
    band = row // 3
    r_val = max(60, 180 - band * 25)
    g_val = max(35, 120 - band * 20)
    b_val = max(20, 70 - band * 10)
    return (r_val, g_val, b_val)


def on_enemy_popped(enemy, score):
    """Handle enemy popped event; awards depth bonus points."""
    depth_bonus = enemy.cell[0] * 10
    return score + depth_bonus


def enemy_speed_multiplier(level):
    """Return a speed multiplier for enemies scaling with level."""
    return 1.0 + 0.08 * (level - 1)


def in_bounds(r, c):
    """Check if grid coordinates (r, c) are within the playing field."""
    return 0 <= r < ROWS and 0 <= c < COLS


def bfs_path(grid, start, goal):
    """Calculate the shortest path between start and goal using BFS."""
    queue, parents = deque([start]), {start: None}
    while queue:
        cell = queue.popleft()
        if cell == goal:
            break
        for dr, dc in DIRS.values():
            nxt = (cell[0] + dr, cell[1] + dc)
            if (
                in_bounds(*nxt)
                and not grid[nxt[0]][nxt[1]]
                and nxt not in parents
            ):
                parents[nxt] = cell
                queue.append(nxt)
    if goal not in parents:
        return []
    path, cell = [], goal
    while cell != start:
        path.append(cell)
        cell = parents[cell]
    return path[::-1]


class Enemy:  # pylint: disable=too-few-public-methods
    """Enemy character with pathfinding, inflation stages, and ghosting."""

    def __init__(self, cell):
        """Initialize enemy state and timers."""
        self.cell = cell
        self.stage = 0
        self.last_pump = 0.0
        self.step_timer = rng.uniform(0, ENEMY_DELAY)
        self.ghost_timer = rng.uniform(6, 10)
        self.ghost = False

    @property
    def locked(self):
        """Return True if the enemy is inflated and locked in place."""
        return self.stage > 0


class Game:  # pylint: disable=too-many-instance-attributes
    """Main game controller managing state, player, enemies, and rendering."""

    def __init__(self):
        """Initialize all game attributes and resources."""
        self.font = pygame.font.Font(None, 26)
        self.level = 1
        self.score = 0
        self.lives = 3
        self.state = "play"
        self.grid = []
        self.player = (0, 0)
        self.facing = (0, 1)
        self.move_timer = 0.0
        self.time = 0.0
        self.pump_target = None
        self.enemies = []
        self.reset()

    def reset(self):
        """Reset match statistics and start a new level."""
        self.level, self.score, self.lives, self.state = 1, 0, 3, "play"
        self.start_level()

    def start_level(self):
        """Initialize or advance to a new level grid and spawn enemies."""
        self.grid = [[r > 0 for _ in range(COLS)] for r in range(ROWS)]
        self.player = (0, COLS // 2)
        self.facing = (0, 1)
        self.move_timer = 0.0
        self.time = 0.0
        self.pump_target = None
        self.enemies = []
        for _ in range(3 + self.level):
            r = rng.randint(4, ROWS - 2)
            c = rng.randint(1, COLS - 3)
            for dc in range(3):
                self.grid[r][c + dc] = False
            self.enemies.append(Enemy((r, c + rng.randint(0, 2))))

    def dig(self, cell):
        """Clear dirt at the given cell coordinates."""
        self.grid[cell[0]][cell[1]] = False

    def move_player(self, direction):
        """Update player facing and move into adjacent cell if in bounds."""
        self.facing = direction
        nr = self.player[0] + direction[0]
        nc = self.player[1] + direction[1]
        if in_bounds(nr, nc):
            self.player = (nr, nc)
            self.dig(self.player)

    def find_pump_target(self):
        """Find the nearest enemy within pump range in facing direction."""
        for step in range(1, PUMP_RANGE + 1):
            r = self.player[0] + self.facing[0] * step
            c = self.player[1] + self.facing[1] * step
            if not in_bounds(r, c) or self.grid[r][c]:
                return None
            for enemy in self.enemies:
                if enemy.cell == (r, c):
                    return enemy
        return None

    def pump(self):
        """Pump inflation into the targeted enemy or pop if max stage."""
        enemy = self.find_pump_target()
        self.pump_target = enemy
        if enemy is None:
            return
        enemy.stage += 1
        enemy.last_pump = self.time
        if enemy.stage >= 4:
            self.enemies.remove(enemy)
            self.score += 200 + 100 * (enemy.cell[0] // 4)
            self.pump_target = None
            self.score = on_enemy_popped(enemy, self.score)
            if not self.enemies:
                self.level += 1
                self.start_level()

    def hurt(self):
        """Handle player taking damage, losing life, or game over."""
        self.lives -= 1
        self.player = (0, COLS // 2)
        if self.lives <= 0:
            self.state = "lose"

    def update_enemy(self, enemy, dt):
        """Update single enemy inflation, ghost state, and path movement."""
        if enemy.locked:
            if self.time - enemy.last_pump > DEFLATE_AFTER:
                enemy.stage -= 1
                enemy.last_pump = self.time
            return
        enemy.ghost_timer -= dt
        if enemy.ghost_timer <= 0:
            enemy.ghost = not enemy.ghost
            enemy.ghost_timer = 4.0 if enemy.ghost else rng.uniform(6, 10)
            if not enemy.ghost:
                self.grid[enemy.cell[0]][enemy.cell[1]] = False
        enemy.step_timer -= dt
        if enemy.step_timer > 0:
            return
        speed_mult = enemy_speed_multiplier(self.level) or 1
        speed_factor = 1.6 if enemy.ghost else 1.0
        enemy.step_timer = (ENEMY_DELAY * speed_factor) / speed_mult
        if enemy.ghost:
            dr = self.player[0] - enemy.cell[0]
            dc = self.player[1] - enemy.cell[1]
            if abs(dr) >= abs(dc) and dr:
                step_r = 1 if dr > 0 else -1
                enemy.cell = (enemy.cell[0] + step_r, enemy.cell[1])
            elif dc:
                step_c = 1 if dc > 0 else -1
                enemy.cell = (enemy.cell[0], enemy.cell[1] + step_c)
            return
        path = bfs_path(self.grid, enemy.cell, self.player)
        if path:
            enemy.cell = path[0]

    def update(self, dt, keys):
        """Advance game simulation by dt seconds given keyboard inputs."""
        if self.state != "play":
            return
        self.time += dt
        self.move_timer -= dt
        if self.move_timer <= 0:
            for key, direction in DIRS.items():
                if keys[key]:
                    self.move_player(direction)
                    self.move_timer = MOVE_DELAY
                    break
        for enemy in self.enemies[:]:
            self.update_enemy(enemy, dt)
            if enemy.cell == self.player and not enemy.locked:
                self.hurt()
                break
        if self.pump_target and (
            self.pump_target not in self.enemies
            or not self.pump_target.locked
        ):
            self.pump_target = None

    def draw_tiles(self, screen):
        """Render sky, dirt layers, and excavated tunnels."""
        screen.fill((30, 30, 60))
        for r in range(ROWS):
            for c in range(COLS):
                rect = pygame.Rect(c * TILE, r * TILE, TILE, TILE)
                if r == 0:
                    pygame.draw.rect(screen, (90, 170, 230), rect)
                elif self.grid[r][c]:
                    shade = dirt_color(r) or (170 - r * 6, 110 - r * 4, 60)
                    pygame.draw.rect(screen, shade, rect)
                else:
                    pygame.draw.rect(screen, (20, 12, 10), rect)

    def draw_actors(self, screen):
        """Render enemies, player, and active pump line."""
        for enemy in self.enemies:
            x = enemy.cell[1] * TILE + TILE // 2
            y = enemy.cell[0] * TILE + TILE // 2
            radius = 10 + enemy.stage * 4
            color = (230, 230, 240) if enemy.ghost else (230, 70, 70)
            pygame.draw.circle(screen, color, (x, y), radius)
            pygame.draw.circle(screen, (255, 255, 255), (x - 4, y - 3), 3)
            pygame.draw.circle(screen, (255, 255, 255), (x + 4, y - 3), 3)
        px = self.player[1] * TILE + TILE // 2
        py = self.player[0] * TILE + TILE // 2
        pygame.draw.circle(screen, (250, 250, 250), (px, py), 12)
        pygame.draw.rect(screen, (60, 120, 230), (px - 8, py - 12, 16, 8))
        if self.pump_target:
            tx = self.pump_target.cell[1] * TILE + TILE // 2
            ty = self.pump_target.cell[0] * TILE + TILE // 2
            pygame.draw.line(screen, (255, 255, 120), (px, py), (tx, ty), 3)

    def draw_hud(self, screen):
        """Render score, lives, current level HUD, and game over overlay."""
        hud_text = (
            f"Score {self.score}  Lives {self.lives}  "
            f"Level {self.level}  R = reset"
        )
        hud = self.font.render(hud_text, True, (240, 240, 240))
        screen.blit(hud, (10, ROWS * TILE + 8))
        if self.state == "lose":
            label = self.font.render(
                "GAME OVER - Press R", True, (255, 255, 120)
            )
            screen.blit(
                label, label.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            )

    def draw(self, screen):
        """Render complete game scene to the display screen."""
        self.draw_tiles(screen)
        self.draw_actors(screen)
        self.draw_hud(screen)


def main():
    """Main loop initializing pygame and running event loop."""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Dig Dug")
    clock = pygame.time.Clock()
    game = Game()
    running = True
    while running:
        dt = min(clock.tick(60) / 1000, 0.05)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_SPACE
                and game.state == "play"
            ):
                game.pump()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                game.reset()
        game.update(dt, pygame.key.get_pressed())
        game.draw(screen)
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
