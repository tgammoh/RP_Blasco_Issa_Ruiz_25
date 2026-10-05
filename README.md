# The Midnight Gospel: Clancy vs Prince Jam Roll

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Library](https://img.shields.io/badge/library-Pygame-green.svg)](https://www.pygame.org/)
[![Course](https://img.shields.io/badge/course-Robot%20Programming-orange.svg)](https://www.uc3m.es/)
[![Institution](https://img.shields.io/badge/university-UC3M-purple.svg)](https://www.uc3m.es/)

**First Assessment • Robot Programming Course**  
**Universidad Carlos III de Madrid (UC3M)**  
**Professor:** Sofía Die-Pancorbo (`sdie@ing.uc3m.es`)  

---

## 🌌 1. Project Overview

Inspired by Pendleton Ward's animated surrealist series ***The Midnight Gospel*** (specifically Episode 4: *"Blinded by My End"*), this arcade 2D Python game casts you as **Clancy Gilroy** exploring deep space.

Navigating the cosmos in his iconic **Purple Wizard Hat**, Clancy shoots magical **Heart Arrows** to blast through waves of the sinister **Prince Jam Roll**, dodge tumbling **Cosmic Geode Asteroids**, and collect pairs of the legendary **Multiverse Shoes** (rendered from a top-down upper point of view) for his shoe rack. Every 20 levels, Clancy enters through the **Multiverse Simulator Portal** which warps the background into progressively **deeper space sectors** (Known Cosmos -> Abyssal Violet Void -> Midnight Teal Abyss -> Crimson Singularity -> Event Horizon Void)!

---

## 🎯 2. Course Assessment Compliance

This project fulfills all 11 technical requirements specified in the official assessment guidelines:

| # | Requirement | Implementation in `game.py` |
|---|---|---|
| **1** | **`game.py` in `Game` Branch** | The core application is packaged entirely within `game.py`. |
| **2** | **Welcome Screen** | Displays an intro screen with Clancy, mission objectives, and a pulsing prompt waiting for any keypress. |
| **3** | **Player Control** | Full movement using **Arrow Keys** or **W, A, S, D**, and firing magical **Heart Arrows** with **Spacebar**. |
| **4** | **Obstacles or Enemies** | Animated **Prince Jam Roll** (webbed bat wings, consuming toothy mouth with fangs, imp claws, curved horns) and tumbling **Geode Asteroids** move automatically. |
| **5** | **Collisions** | Collision system: losing Clancy lives upon contact with hazards, defeating Prince Jam Roll with heart arrows, and collecting multiverse shoe pairs. |
| **6** | **Score System** | Points awarded for defeating Prince Jam Roll (+100 pts), blasting asteroids (+50 pts), collecting multiverse shoe pairs (+50 pts), and dodging hazards (+10 pts). |
| **7** | **Current Score Display** | Live HUD showing **Score**, **Dimension Level & Sector**, **👟 Shoes Collected (Pairs)**, and **Clancy Lives (Wizard Hats)**. |
| **8** | **End Game Screen** | Displays Simulator Shutdown banner, final score, shoes collected, best record, and options: `[R]` to respawn or `[Q]/[ESC]` to exit. |
| **9** | **Increasing Difficulty** | Dimension Level increases every 400 points; every 20 levels Clancy enters the **Multiverse Simulator Transition** to reach deeper space sectors; enemy speed increases by +18% per level with faster spawn rates; capped at 60 FPS via `pygame.time.Clock()`. |
| **10** | **Player Visible in Purple** | Clancy is rendered in his signature **Lilac Purple** (`CLANCY_PURPLE = (175, 80, 245)`) wearing his floppy purple wizard hat. |
| **11** | **Consistent Screen Size** | Standardized, fixed window size: **800 x 600 pixels**. |

---

## 🕹️ 3. How to Play & Controls

### Controls

| Key | Action |
|---|---|
| **`▲` / `W`** | Float Up |
| **`▼` / `S`** | Float Down |
| **`◄` / `A`** | Float Left |
| **`►` / `D`** | Float Right |
| **`SPACEBAR`** | Cast Magical Heart Arrows (Tap or Hold) |
| **`R`** (on Game Over) | Respawn in Simulator / Play Again |
| **`Q` / `ESC`** | Exit Game |

### Scoring Matrix

- **Prince Jam Roll Defeated**: `+100 Points`
- **Cosmic Asteroid Blasted**: `+50 Points`
- **Multiverse Shoe Pair Collected**: `+50 Points` *(Added to Clancy's Shoe Rack)*
- **Hazard Dodged (Leaves Screen)**: `+10 Points`
- **Level Completion**: Enter the Multiverse Simulator to warp to the next dimension!

---

## 🚀 4. Installation & Running

### Prerequisites

- **Python 3.10+**
- **Pygame 2.5+**

```bash
pip install pygame
python game.py
```

> [!NOTE]
> **No external sound files or asset folders required!**  
> All audio effects (magical star-beams, squishy monster hits, shoe pickups, and hurt sounds) are synthesized procedurally in memory via Python's standard `wave` and `math` libraries.

---

## 👥 5. Academic Information

- **Course:** Robot Programming (Fourth Year)
- **Institution:** Universidad Carlos III de Madrid (UC3M)
- **Professor:** Prof. Sofía Die-Pancorbo (`sdie@ing.uc3m.es`)
- **Group Registration:** Aula Global
