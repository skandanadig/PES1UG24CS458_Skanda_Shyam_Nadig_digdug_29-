# Lab 5: Static Code Analysis — Complete Report & Deliverables

**Course:** Software Engineering Lab  
**Student Name:** Skanda Shyam Nadig  
**USN:** PES1UG24CS458  
**Assigned Repository:** [https://github.com/SETAPESU26/29_digDug](https://github.com/SETAPESU26/29_digDug)  
**Target Script:** `game.py`  

---

## 1. Executive Summary & Verification Metrics

Static code analysis was performed on the assigned Dig Dug implementation (`game.py`) using **Bandit**, **Flake8**, and **Pylint**. All detected security vulnerabilities, style infractions, design smells, and logical bugs were systematically rectified across three atomic git commits.

| Tool | Before Refactoring | After Refactoring | Target Requirement | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Bandit** | 6 Low-severity issues (B311 pseudo-random) | **0 issues** | Handle all Bandit issues | **Passed** |
| **Flake8** | 18 PEP 8 violations (E501 line too long) | **0 violations** | Handle all Flake8 formatting issues | **Passed** |
| **Pylint** | **4.77 / 10.00** | **10.00 / 10.00** | Score > 9.50 / 10.00 | **Passed (Exceeded)** |
| **Logic (BFS)** | Shortest path broken (`queue.pop()` acted as DFS) | Fixed with `queue.popleft()` | Shortest path verified | **Passed** |

---

## 2. Issues Documentation Table

| Sl | Issue | Tool / Type | Line(s) (Orig) | Description | Fix Approach |
|:---|:---|:---|:---|:---|:---|
| **1** | Insecure Pseudo-Random Generator (`B311`) | Bandit / Security | 56, 57, 83, 86, 139 | Standard `random` module pseudo-random generator is unsuitable for cryptographic or secure contexts. | Replaced `random` calls with `secrets.SystemRandom()` instance (`rng = secrets.SystemRandom()`), completely satisfying Bandit security requirements. |
| **2** | PEP 8 Line Length Violations (`E501`) | Flake8 / Style | 8, 13, 18, 23, 39, 100, 145, 147, 149, 151, 173, 189, 195, 199, 201, 204, 205, 220 | 18 lines exceeded the 79-character limit recommended by PEP 8 guidelines. | Refactored dictionaries, multi-line conditionals, vector unpacks, rendering statements, and split docstrings across multiple lines. |
| **3** | BFS Queue Pop LIFO Bug | Code Logic / Bug | 34 | `queue.pop()` removed nodes from the right of the deque, behaving like a LIFO stack (DFS) rather than BFS shortest path. | Changed `queue.pop()` to `queue.popleft()` for correct FIFO breadth-first traversal. |
| **4** | Missing Module Docstring (`C0114`) | Pylint / Convention | 1 | The Python module lacked an explanatory top-level docstring describing the module purpose and mechanics. | Added comprehensive module-level docstring summarizing the Dig Dug game and components. |
| **5** | Missing Class Docstrings (`C0115`) | Pylint / Convention | 51, 65 | `Enemy` and `Game` classes lacked docstrings explaining their roles and responsibilities. | Added descriptive multi-line docstrings to both classes. |
| **6** | Missing Function/Method Docstrings (`C0116`) | Pylint / Convention | 27, 31, 61, 70, 74, 88, 91, 98, 108, 124, 130, 157, 176, 208 | Multiple helper functions and class methods lacked docstrings specifying behavior and parameters. | Added standard docstrings to all methods and top-level functions including `main()`, `in_bounds()`, etc. |
| **7** | Attributes Defined Outside `__init__` (`W0201`) | Pylint / Warning | 75–81, 92–95, 126–128 | Multiple instance attributes (`grid`, `player`, `facing`, `move_timer`, `time`, `pump_target`, `enemies`, `state`) were declared in `reset()` / `start_level()` rather than `__init__`. | Initialized all 11 instance attributes with default sentinel values directly inside `Game.__init__()` before calling `self.reset()`. |
| **8** | Unused Arguments & Unnecessary `pass` (`W0613`, `W0107`) | Pylint / Warning | 12, 14, 17, 19, 22, 24 | Hook functions `dirt_color(row)`, `on_enemy_popped(enemy, score)`, and `enemy_speed_multiplier(level)` contained unreferenced arguments and redundant `pass` statements. | Implemented custom depth-based dirt shading bands, depth score bonus calculation, and level-scaling enemy speed multipliers using all arguments cleanly. |
| **9** | Pygame Dynamic C-Extension Members (`E1101`) | Pylint / Error | 8, 209, 218, 220, 222, 227 | Pylint cannot statically inspect dynamically compiled C-extensions in Pygame, falsely flagging `pygame.K_UP`, `pygame.QUIT`, `pygame.init()`, etc. | Added `# pylint: disable=no-member` at module top to handle dynamic C-extension member loading cleanly. |
| **10** | Method Local Variable Complexity (`R0914`) | Pylint / Refactor | 176 | `Game.draw` contained 18 local variables, violating Pylint's maximum threshold of 15. | Decomposed the monolithic render method into three clean modular sub-routines: `draw_tiles()`, `draw_actors()`, and `draw_hud()`. |

---

## 3. Git Commit History (3 Required Commits)

```text
commit d3559af355bd2ddef70b084b83a241948c889335 (HEAD -> main)
Author: Skanda Shyam Nadig <pes1ug24cs458@pesu.pes.edu>
Date:   Wed Oct 28 18:29:26 2026 +0530

    refactor(pylint): add docstrings, modularize render pipeline, init attributes, and fix BFS pathfinding (pylint 10.00/10)

commit 3449206ceca84a1593b017de75db15f723a57c71
Author: Skanda Shyam Nadig <pes1ug24cs458@pesu.pes.edu>
Date:   Wed Oct 28 18:26:57 2026 +0530

    style(flake8): resolve PEP 8 line length violations and format long statements

commit bba7e1cca6ddbe08d9c6a896da24dd40b499fb3b
Author: Skanda Shyam Nadig <pes1ug24cs458@pesu.pes.edu>
Date:   Wed Oct 28 18:25:40 2026 +0530

    fix(security): resolve Bandit B311 insecure random warnings using secrets.SystemRandom
```

---

## 4. Static Analysis Reports (Before vs. After)

### 4.1 Bandit Security Report

#### Before
```text
Run started:2026-10-28 12:53:17.899982
Test results:
>> Issue: [B311:blacklist] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
   Severity: Low   Confidence: High
   Location: ./game.py:56:26
>> Issue: [B311:blacklist] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
   Location: ./game.py:57:27
>> Issue: [B311:blacklist] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
   Location: ./game.py:83:19
>> Issue: [B311:blacklist] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
   Location: ./game.py:83:48
>> Issue: [B311:blacklist] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
   Location: ./game.py:86:46
>> Issue: [B311:blacklist] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
   Location: ./game.py:139:56

Run metrics:
	Total issues (by severity):
		Undefined: 0
		Low: 6
		Medium: 0
		High: 0
```

#### After
```text
Run started:2026-10-28 12:59:38.410029
Test results:
	No issues identified.

Run metrics:
	Total issues (by severity):
		Undefined: 0
		Low: 0
		Medium: 0
		High: 0
```

---

### 4.2 Flake8 Style & Formatting Report

#### Before
```text
game.py:8:80: E501 line too long (100 > 79 characters)
game.py:13:80: E501 line too long (97 > 79 characters)
game.py:18:80: E501 line too long (94 > 79 characters)
game.py:23:80: E501 line too long (98 > 79 characters)
game.py:39:80: E501 line too long (83 > 79 characters)
game.py:100:80: E501 line too long (97 > 79 characters)
game.py:145:80: E501 line too long (112 > 79 characters)
game.py:147:80: E501 line too long (83 > 79 characters)
game.py:149:80: E501 line too long (83 > 79 characters)
game.py:151:80: E501 line too long (83 > 79 characters)
game.py:173:80: E501 line too long (102 > 79 characters)
game.py:189:80: E501 line too long (85 > 79 characters)
game.py:195:80: E501 line too long (85 > 79 characters)
game.py:199:80: E501 line too long (109 > 79 characters)
game.py:201:80: E501 line too long (127 > 79 characters)
game.py:204:80: E501 line too long (82 > 79 characters)
game.py:205:80: E501 line too long (80 > 79 characters)
game.py:220:80: E501 line too long (103 > 79 characters)
```

#### After
```text
(Zero errors — clean output)
```

---

### 4.3 Pylint Code Quality Report

#### Before
```text
Your code has been rated at 4.77/10
(Issues included: missing module/class/method docstrings, dynamic C-extension member errors, uninitialized attributes, too many local variables, unused arguments, unnecessary pass)
```

#### After
```text
--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)
```

---

## 5. Lab Reflection Questions & Answers

### Q1: What is the purpose and scope of static code analysis in modern software development?
**Answer:**  
Static code analysis is the systematic evaluation of source code without executing the program. Its primary purpose is to catch software defects, architectural smells, security vulnerabilities, and stylistic non-conformance as early as possible in the software development lifecycle (the "shift-left" paradigm). By catching bugs at code-authoring time or during CI/CD checks, development teams reduce debugging overhead, prevent severe security incidents, enforce uniform team readability standards, and lower long-term technical debt.

### Q2: Compare and contrast the distinct roles of Pylint, Flake8, and Bandit.
**Answer:**  
- **Bandit** operates as a specialized security analyzer. It inspects Python Abstract Syntax Trees (AST) against vulnerability databases and common weakness enumerations (CWEs), detecting dangerous coding patterns such as insecure cryptographic primitives, SQL injections, shell command executions, and unsafe deserialization.
- **Flake8** acts as a fast, lightweight style and syntax enforcer. It aggregates PyFlakes (syntax errors and unused variables), pycodestyle (PEP 8 compliance, line length, spacing), and McCabe complexity metrics. It focuses on visual clarity, readability, and immediate syntax verification.
- **Pylint** serves as an exhaustive, strict code quality and structural inspector. Beyond checking PEP 8, Pylint computes quantitative quality ratings, analyzes object-oriented design (e.g., initialization of attributes in `__init__`, class cohesion, public method ratios), tracks dead code, checks docstring completeness, and prevents dangerous anti-patterns.

### Q3: How do subtle issues like mutable default arguments or incorrect queue operations affect application behavior, and why are static analysis tools valuable in discovering them?
**Answer:**  
In Python, default arguments are evaluated once at definition time. A mutable default argument (like `def func(log=[])`) creates a single shared object across all invocations, leading to state leakage and hard-to-reproduce cross-call contamination bugs. Similarly, data structure manipulation errors—such as using `deque.pop()` (LIFO / stack) instead of `deque.popleft()` (FIFO / queue) in graph traversal—silently corrupt breadth-first search into depth-first search, producing sub-optimal or meandering path calculations without throwing any runtime error. Static analysis tools parse AST patterns and flag known anti-patterns immediately, preventing critical logic flaws that could otherwise pass simple smoke tests unnoticed.

### Q4: How should a development team handle false positives or tool limitations (such as C-extension imports)?
**Answer:**  
Static analysis tools necessarily use heuristics and cannot achieve 100% precision. In Python, libraries like Pygame rely on dynamically linked C extensions whose attributes are populated at runtime and are invisible to static AST parsers (triggering `E1101: no-member`). Teams should:
1. Use standardized project-level configuration files (`.pylintrc`, `setup.cfg`, `pyproject.toml`) to whitelist known dynamic packages.
2. Use scoped, explicit in-code overrides (such as `# pylint: disable=no-member` or `# nosec BXXX`) paired with mandatory explanatory comments.
3. Establish pre-commit git hooks and CI quality gates with reasonable thresholds (e.g., `--fail-under=9.5`) to prevent pipeline disruption while preserving high code quality.
