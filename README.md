# The Midnight Gospel: Clancy vs Prince Jam Roll — ROS1 Edition

**Robot Programming · Final Assignment, Part I (ROS1 Publisher, Subscriber and Custom Message)**
Universidad Carlos III de Madrid (UC3M) · Professor: Sofía Die-Pancorbo
Group: Blasco · Issa · Ruiz

The game from the first assignment, rebuilt as **4 independent ROS1 nodes** that talk to each other through **3 topics** and **1 custom message**. One node asks for the player's data, one reads the keyboard, one runs the game, and one shows the final result.

---

## 1. Repository structure (`ROS` branch)

```
ROS branch
├── game_msgs/                 # Message package
│   ├── msg/
│   │   └── GameUserMsg.msg    # Custom message: player data
│   ├── CMakeLists.txt
│   └── package.xml
├── game_pr/                   # Python nodes package
│   ├── scripts/
│   │   ├── info_user_node.py      # Asks for and publishes the player data
│   │   ├── control_node.py        # Reads the keyboard, publishes commands
│   │   ├── game_node.py           # Main game (Welcome / Game / Final phases)
│   │   └── results_game_node.py   # Shows the final username and score
│   ├── CMakeLists.txt
│   └── package.xml
└── README.md
```

Both packages go inside the `src/` folder of a catkin workspace (structure **Option 2** of the assignment).

---

## 2. Requirements and dependencies

| Requirement | Version |
|---|---|
| Ubuntu | 20.04 (native or WSL2) |
| ROS | ROS1 **Noetic** |
| Python | 3.8 (included with Ubuntu 20.04) |
| Pygame | 2.x |

**Install ROS Noetic** (skip if already installed): follow the official guide at <https://wiki.ros.org/noetic/Installation/Ubuntu>, then load it in every terminal:

```bash
echo "source /opt/ros/noetic/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

**Install Pygame:**

```bash
sudo apt install -y python3-pip
pip3 install pygame
```

> **WSL users:** the game window needs WSLg (included in Windows 11). Sound may not work under WSL; the game detects this and keeps running without audio.

---

## 3. Build

```bash
# 1. Create a workspace (skip if you already have one)
mkdir -p ~/catkin_ws/src

# 2. Copy (or clone) the two packages into src/
cd ~/catkin_ws/src
git clone -b ROS https://github.com/tgammoh/RP_Blasco_Issa_Ruiz_25.git
cp -r RP_Blasco_Issa_Ruiz_25/game_msgs RP_Blasco_Issa_Ruiz_25/game_pr .
rm -rf RP_Blasco_Issa_Ruiz_25

# 3. Make the node scripts executable
chmod +x ~/catkin_ws/src/game_pr/scripts/*.py

# 4. Build and load the workspace
cd ~/catkin_ws
catkin_make
echo "source ~/catkin_ws/devel/setup.bash" >> ~/.bashrc
source ~/.bashrc

# 5. Check that ROS knows the custom message
rosmsg show game_msgs/GameUserMsg
```

The last command should print:

```
string name
string username
int64 age
```

---

## 4. Run

Open **5 terminals** and start them **in this order**:

| # | Command | What to do |
|---|---|---|
| 1 | `roscore` | ROS master — always first |
| 2 | `rosrun game_pr results_game_node.py` | Shows the final result at the end |
| 3 | `rosrun game_pr game_node.py` | The game window opens on the welcome screen |
| 4 | `rosrun game_pr info_user_node.py` | Type your full name, username and age |
| 5 | `rosrun game_pr control_node.py` | **Keep this terminal selected and play from here** |

### Controls (typed in the `control_node` terminal)

| Key | Command sent | Effect in the game |
|---|---|---|
| ↑ ↓ ← → | `UP` `DOWN` `LEFT` `RIGHT` | Move Clancy |
| Space | `SHOOT` | Fire heart arrows |
| Enter | `START` | Start the game from the welcome screen |
| R | `RESTART` | Play again from the end screen |
| Q / Esc | `QUIT` | End the game (during play) or close it (welcome / end screen) |
| Ctrl+C | — | Stop the node |

### Gameplay

Dodge **Prince Jam Roll** and the **cosmic asteroids**, shoot them with heart arrows and collect **multiverse shoes**. You have 3 lives.

| Action | Points |
|---|---|
| Defeat Prince Jam Roll | +100 |
| Destroy an asteroid | +50 |
| Collect a pair of shoes | +50 |
| Dodge an enemy or asteroid | +10 |

The level rises every 400 points and enemies get faster. Every 20 levels Clancy warps through the Multiverse Simulator into a deeper space sector.

---

## 5. Node-to-node communication

```
                 /user_information (game_msgs/GameUserMsg)
 info_user_node ─────────────────────────────┬──────────────────────► game_node
                                             │                          ▲    │
                                             └──► results_game_node     │    │
                                                        ▲               │    │
                 /keyboard_control (std_msgs/String)    │               │    │
 control_node ──────────────────────────────────────────┼───────────────┘    │
                                                        │                    │
                 /result_information (std_msgs/Int64)   │                    │
                 ◄──────────────────────────────────────┴────────────────────┘
```

### Topics

| Topic | Message type | Publisher | Subscribers |
|---|---|---|---|
| `/user_information` | `game_msgs/GameUserMsg` | `info_user_node` | `game_node`, `result_game_node` |
| `/keyboard_control` | `std_msgs/String` | `control_node` | `game_node` |
| `/result_information` | `std_msgs/Int64` | `game_node` | `result_game_node` |

### Custom message — `game_msgs/GameUserMsg`

```
string name
string username
int64 age
```

### Nodes

**`info_user_node`** (`info_user_node.py`)
Asks for the full name, username and age in the terminal and validates them (letters only for the name, 3–20 letters/numbers/`_` for the username, age 1–120). The data is stored inside the node's class and published once on `/user_information`. The publisher is *latched*, so nodes that start later still receive the data.

**`control_node`** (`control_node.py`)
Only handles keyboard input. It reads keys directly from its terminal (no Enter needed) and publishes one capital-letter command per key press on `/keyboard_control`.

**`game_node`** (`game_node.py`) — main node, split into three phase methods:
1. `welcome_phase()` — receives the player data, stores it in the class and greets the player by name. Waits for `START`.
2. `game_phase()` — runs the game and moves Clancy according to the commands received from `control_node`.
3. `final_phase()` — detects the end of the game, calculates the final score and publishes it on `/result_information`. Offers `RESTART` or `QUIT`.

It logs every phase change: `"Welcome phase started."`, `"Game phase started."`, `"Final phase reached, calculating score."`

**`result_game_node`** (`results_game_node.py`)
Subscribes to `/user_information` and `/result_information` and prints a final message with the player's username and score. The two messages can arrive in any order.

### Useful commands to inspect the system

```bash
rosnode list                         # the 4 running nodes
rostopic list                        # the 3 topics
rostopic echo /keyboard_control      # watch the commands live
rostopic echo /user_information      # watch the player data
rostopic echo /result_information    # watch the final score
rqt_graph                            # draw the node/topic graph
```

---

## 6. Design notes

- **Every node is a class in its own file**, and nothing uses global variables: publishers, subscribers, player data, score and state all live inside each class.
- **Thread safety:** ROS callbacks run in a separate thread from the Pygame loop, so `game_node` puts incoming commands in a thread-safe queue and reads them once per frame.
- **Smooth movement from discrete commands:** each movement command keeps Clancy moving for a few frames. Holding an arrow key makes the terminal repeat the command, so the movement continues while the key is held.
- **Logging:** every node uses `rospy.loginfo` to report what it is doing.
