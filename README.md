# Dig Dug Repair Lab

This project is a single-file Dig Dug-lite clone using **Pygame**. It introduces students to grid digging, breadth-first pathfinding, and multi-stage enemy state using a small, readable object-oriented codebase.

---

## What's Provided

A working Dig Dug-lite game with:

- A player that digs through dirt as they move, leaving permanent tunnels behind them
- Enemies that path toward the player through cleared tunnels using breadth-first search, and can turn "ghost" to phase through dirt briefly
- A pump attack that inflates an enemy through four stages before popping it
- Levels, lives, and scoring

It has **one deliberate bug** and **three optional features** left as empty functions. You are expected to **analyze**, **interact with an AI assistant**, and **complete/fix** the game to make it fully functional and more interesting.

### **Use an LLM (e.g. ChatGPT or Claude) as your debugging and pair-programming partner for this lab.**

---

## Getting Started

### Setup

1. Make sure you have Python 3.10+ installed.
2. Install dependencies:

```bash
pip install pygame
```

3. Run the game:

```bash
python game.py
```

**Controls:** Arrow keys to dig/move, Space to pump, `R` to reset.

---

## Tasks to Complete

Each task must be completed using an iterative process involving LLM suggestions and your critical code review.

### Task 1: Fix the enemy pathfinding bug

> Once a tunnel connects an enemy to the player, the enemy is supposed to take the *shortest* route through cleared cells, using breadth-first search. In the current build, enemies do eventually reach the player, but along long, winding routes instead of the shortest one — the search behaves like depth-first search rather than breadth-first. Look at which end of the `deque` the search removes cells from in `bfs_path`.

### Task 2: Implement `dirt_color(row)`

> Called once per dirt cell per frame in `draw`, as `shade = dirt_color(row) or (170 - row * 6, 110 - row * 4, 60)`. It receives the cell's row index and should return an `(r, g, b)` color, or `None` to keep the default gradient (which darkens with depth). Idea: give each row band a distinct color instead of a smooth gradient.

### Task 3: Implement `on_enemy_popped(enemy, score)`

> Called from `pump()` right after an enemy reaches its fourth inflation stage, is removed from play, and its points are added. It receives the `Enemy` that popped and the score after its points were added. Its return value is ignored. Idea: a particle burst at `enemy.cell`, or extra points for popping an enemy deep underground.

### Task 4: Implement `enemy_speed_multiplier(level)`

> Called every time a non-locked enemy finishes a step, as part of `enemy.step_timer = ENEMY_DELAY * (1.6 if enemy.ghost else 1) / (enemy_speed_multiplier(self.level) or 1)`. It receives the current level number and should return a speed multiplier, or `None` for the default speed (1x). A higher multiplier makes enemies move more often (shorter delay between steps). Idea: return `1 + 0.1 * level` so enemies get gradually faster on deeper levels.

---

## Expected Behavior

- Moving the player clears dirt in the cells they move into
- A pumped enemy can't move, and slowly deflates back down if you stop pumping it before it pops
- Enemies path through cleared tunnels toward the player using short routes; while "ghosting" they move in straight lines through dirt instead
- Popping every enemy on a level advances to the next, larger level
- Touching a non-locked enemy costs a life; the game ends when lives reach zero

---

## Folder Structure

```
dig_dug/
├── game.py
└── README.md
```

---

## Submission Checklist

Submission is only the following three things:

- [x] A 10-second video of gameplay **before** your changes, showing the bug/broken behavior (`before_changes.mp4`)
- [x] A 10-second video of gameplay **after** your changes, showing the bug fixed and the new features working (`after_changes.mp4`)
- [x] The Chat/LLM used page link, with the complete chat history (`PROMPTS_AND_RESPONSES.md`)
