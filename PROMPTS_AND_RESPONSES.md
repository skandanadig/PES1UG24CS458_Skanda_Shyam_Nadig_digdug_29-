# LLM Prompts & Responses Log — Dig Dug Repair Lab

This document contains the iterative prompts and LLM responses used to analyze, debug, and implement the features for the Dig Dug Repair Lab (`game.py`).

---

## Task 1: Fix the Enemy Pathfinding Bug (`bfs_path`)

### Prompt 1
> In `game.py`, once a tunnel connects an enemy to the player, the enemy is supposed to take the shortest route through cleared cells using breadth-first search (`bfs_path`). Currently, enemies take long, winding routes instead of the shortest path, behaving like depth-first search (DFS) instead of breadth-first search (BFS). Here is `bfs_path`:
> ```python
> def bfs_path(grid, start, goal):
>     queue, parents = deque([start]), {start: None}
>     while queue:
>         cell = queue.pop()
>         if cell == goal:
>             break
>         for dr, dc in DIRS.values():
>             nxt = (cell[0] + dr, cell[1] + dc)
>             if in_bounds(*nxt) and not grid[nxt[0]][nxt[1]] and nxt not in parents:
>                 parents[nxt] = cell
>                 queue.append(nxt)
> ```
> What is causing this bug and how do we fix it?

### Response 1
**Root Cause:**
In Python's `collections.deque`, `queue.append(nxt)` adds elements to the **right** end of the deque, and `queue.pop()` also removes elements from the **right** end. This makes the data structure operate in Last-In, First-Out (LIFO) order—which is a stack, resulting in Depth-First Search (DFS) rather than Breadth-First Search (BFS).

**Fix:**
Change `cell = queue.pop()` to `cell = queue.popleft()` so that cells are removed from the **left** (front) of the queue in First-In, First-Out (FIFO) order. This guarantees that `bfs_path` explores nodes layer-by-layer and always finds the shortest path in an unweighted grid.

```python
def bfs_path(grid, start, goal):
    queue, parents = deque([start]), {start: None}
    while queue:
        cell = queue.popleft()
        if cell == goal:
            break
        for dr, dc in DIRS.values():
            nxt = (cell[0] + dr, cell[1] + dc)
            if in_bounds(*nxt) and not grid[nxt[0]][nxt[1]] and nxt not in parents:
                parents[nxt] = cell
                queue.append(nxt)
    if goal not in parents:
        return []
    path, cell = [], goal
    while cell != start:
        path.append(cell)
        cell = parents[cell]
    return path[::-1]
```

---

## Task 2: Implement `dirt_color(row)`

### Prompt 2
> Next, I need to implement `dirt_color(row)` in `game.py`. It is called once per dirt cell per frame in `draw()` as:
> `shade = dirt_color(r) or (170 - r * 6, 110 - r * 4, 60)`
> It receives the cell's row index `row` (where row `0` is the sky and rows `1` to `13` are dirt) and should return an `(r, g, b)` tuple so each horizontal strata band has a distinct classic Dig Dug color instead of a smooth gradient.

### Response 2
We can divide the underground rows (`1` to `ROWS - 1`) into 4 distinct horizontal strata bands (each 3 rows tall) with progressively darker, richer earth tones:

```python
def dirt_color(row):
    """Return an (r, g, b) colour for dirt in the given row, or None for the default gradient."""
    bands = [
        (210, 160, 90),   # Top soil (rows 1-3)
        (180, 115, 65),   # Mid clay (rows 4-6)
        (145, 80, 45),    # Deep earth (rows 7-9)
        (105, 55, 35),    # Bedrock layer (rows 10+)
    ]
    return bands[min((row - 1) // 3, len(bands) - 1)]
```

**Why this works well:**
- Using `(row - 1) // 3` groups rows `1–3`, `4–6`, `7–9`, and `10–13` into crisp horizontal bands.
- `min(..., len(bands) - 1)` safely clamps the index if `ROWS` is ever increased.
- The colors contrast clearly with the dug tunnel background `(20, 12, 10)`, the red/ghost enemies, and the player sprite.

---

## Task 3: Implement `on_enemy_popped(enemy, score)`

### Prompt 3
> Now let's implement `on_enemy_popped(enemy, score)`. It is called in `pump()` right after an enemy reaches inflation stage 4, is removed from `self.enemies`, and its points are added to `self.score`. How can we add a clean particle burst effect at `enemy.cell` when an enemy pops?

### Response 3
We can maintain a module-level `PARTICLES` list that stores active particles as dictionaries with position `(x, y)`, velocity `(vx, vy)`, remaining `life`, and `color`. When `on_enemy_popped(enemy, score)` is called, we convert `enemy.cell` into pixel coordinates at the center of that tile and spawn 16 particles flying outward in random directions:

```python
PARTICLES = []


def on_enemy_popped(enemy, score):
    """Called when an enemy is popped; add particles, bonus points, or a colour flash here."""
    cx = enemy.cell[1] * TILE + TILE // 2
    cy = enemy.cell[0] * TILE + TILE // 2
    for _ in range(16):
        PARTICLES.append({
            "x": float(cx),
            "y": float(cy),
            "vx": random.uniform(-120, 120),
            "vy": random.uniform(-120, 120),
            "life": random.uniform(0.3, 0.6),
            "color": random.choice([(255, 90, 90), (255, 220, 90), (255, 150, 60), (255, 255, 255)]),
        })
```

Then we update and expire particles each frame in `Game.update(self, dt, keys)`:
```python
        for p in PARTICLES[:]:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
            if p["life"] <= 0:
                PARTICLES.remove(p)
```
And draw them in `Game.draw(self, screen)` (plus clear `PARTICLES` on `Game.reset()`):
```python
        for p in PARTICLES:
            pygame.draw.circle(screen, p["color"], (int(p["x"]), int(p["y"])), 4)
```

---

## Task 4: Implement `enemy_speed_multiplier(level)`

### Prompt 4
> Finally, let's implement `enemy_speed_multiplier(level)`. It is called when setting `enemy.step_timer`:
> `enemy.step_timer = ENEMY_DELAY * (1.6 if enemy.ghost else 1) / (enemy_speed_multiplier(self.level) or 1)`
> It receives the current level number (`1`, `2`, `3`, ...) and should return a speed multiplier so enemies gradually move faster on deeper levels.

### Response 4
We can increase enemy speed by 10% per level using the formula `1 + 0.1 * level`:

```python
def enemy_speed_multiplier(level):
    """Return a speed multiplier for enemies at the given level, or None for the default speed."""
    return 1 + 0.1 * level
```

**Behavior across levels:**
- **Level 1:** `1.1x` speed (`step_timer` reduced from `0.35s` to `~0.318s`)
- **Level 2:** `1.2x` speed (`~0.292s` per step)
- **Level 5:** `1.5x` speed (`~0.233s` per step)
- **Level 10:** `2.0x` speed (`0.175s` per step, still slower than the player's `MOVE_DELAY = 0.11s` so the game remains fair and playable).
