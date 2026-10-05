# Cyber Defender - Robot Programming Assessment

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Library](https://img.shields.io/badge/library-Pygame-green.svg)](https://www.pygame.org/)
[![Course](https://img.shields.io/badge/course-Robot%20Programming-orange.svg)](https://www.uc3m.es/)
[![Institution](https://img.shields.io/badge/university-UC3M-purple.svg)](https://www.uc3m.es/)

**First Assessment • Robot Programming Course**  
**Universidad Carlos III de Madrid (UC3M)**  
**Professor:** Sofía Die-Pancorbo (`sdie@ing.uc3m.es`)  

---

## 📖 1. Project Overview

**Cyber Defender** is an arcade 2D space survival and robot defense game written in Python using **Pygame**. 

You control an advanced **Purple Defender Unit** navigating through cosmic hazard fields, neutralizing rogue combat drones, dodging tumbling asteroids, and collecting high-yield energy cores. The game features real-time procedural audio, a particle physics system, smooth 60 FPS animation, dynamic difficulty scaling, and a complete arcade state cycle (Welcome Screen, Active HUD, and Game Over Screen).

---

## 🎯 2. Course Assessment Compliance

This project fulfills all 11 technical requirements specified in the official assessment guidelines:

| # | Requirement | Implementation in `game.py` |
|---|---|---|
| **1** | **`game.py` in `Game` Branch** | The core application is packaged entirely within `game.py`. |
| **2** | **Welcome Screen** | Displays an intro screen showing controls, pilot showcase, and a pulsing prompt waiting for player input. |
| **3** | **Player Control** | Full omnidirectional movement using **Arrow Keys** or **W, A, S, D**, and firing with **Spacebar**. |
| **4** | **Obstacles or Enemies** | Rogue drones move with sine-wave motion and asteroids tumble downwards automatically. |
| **5** | **Collisions** | Collision system: losing lives upon contact with hazards, destroying enemies with lasers, and collecting power cores. |
| **6** | **Score System** | Points awarded for destroying enemies (+100 pts), collecting energy cores (+50 pts), and dodging obstacles (+10 pts). |
| **7** | **Current Score Display** | Live HUD showing **Score**, **Lives**, **Difficulty Multiplier**, and current **Level**. |
| **8** | **End Game Screen** | Displays Game Over banner, final score, best record, and options: `[R]` to replay or `[Q]/[ESC]` to exit. |
| **9** | **Increasing Difficulty** | Level increases every 400 points; enemy speed increases by +18% per level with faster spawn rates; capped at 60 FPS via `pygame.time.Clock()`. |
| **10** | **Player Visible in Purple** | The player is rendered with a distinct **Purple** cyber-craft design (`PLAYER_PURPLE = (168, 50, 240)`). |
| **11** | **Consistent Screen Size** | Standardized, fixed window size: **800 x 600 pixels**. |

---

## 🕹️ 3. How to Play & Controls

### Controls

| Key | Action |
|---|---|
| **`▲` / `W`** | Move Up |
| **`▼` / `S`** | Move Down |
| **`◄` / `A`** | Move Left |
| **`►` / `D`** | Move Right |
| **`SPACEBAR`** | Fire Twin Lasers (Tap or Hold) |
| **`R`** (on Game Over) | Restart / Play Again |
| **`Q` / `ESC`** | Exit Game |

### Scoring Matrix

- **Rogue Drone Destroyed**: `+100 Points`
- **Asteroid Destroyed**: `+50 Points`
- **Energy Core Collected**: `+50 Points`
- **Obstacle Dodged (Leaves Screen)**: `+10 Points`

### Lives & Shield System

- You start with **3 Lives** represented as hearts in the top right HUD.
- Colliding with an enemy or asteroid consumes 1 life and grants **1.5 seconds of invincibility** (indicated by ship blinking).
- If all 3 lives are lost, the system initiates the **End Game Screen**.

---

## 🚀 4. Installation & Running

### Prerequisites

- **Python 3.10+** (Tested on Python 3.13)
- **Pygame 2.5+**

### Step-by-Step Setup

1. **Clone the repository and switch to the `Game` branch**:
   ```bash
   git clone <YOUR_REPOSITORY_URL>
   cd <REPOSITORY_FOLDER>
   git checkout Game
   ```

2. **Install Pygame**:
   ```bash
   pip install pygame
   ```

3. **Run the Game**:
   ```bash
   python game.py
   ```

> [!NOTE]
> **No external sound files or asset folders required!**  
> All retro audio effects (laser chirps, explosions, item pickups, hit sounds, and game over sequences) are generated procedurally in memory via Python's standard `wave` and `math` libraries.

---

## 🗂️ 5. Repository Structure

```text
RP_Surname1_Surname2_Surname3_25/
├── .gitignore
├── README.md              # Project documentation and guide
├── game.py                # Main executable Python game
```

### Git Branch Structure
- **`main`**: Root production branch.
- **`Game`**: Contains `game.py` and `README.md` for this assessment.
- **`ROS`**: Reserved for robotics / ROS integration milestones.

---

## 👥 6. Academic Information

- **Course:** Robot Programming (Fourth Year)
- **Institution:** Universidad Carlos III de Madrid (UC3M)
- **Professor:** Prof. Sofía Die-Pancorbo (`sdie@ing.uc3m.es`)
- **Group Registration:** Aula Global
