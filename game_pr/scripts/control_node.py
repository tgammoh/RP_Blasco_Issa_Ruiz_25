#!/usr/bin/env python3
"""
CONTROL_NODE
Only responsible for keyboard input. Reads the arrow keys (and a few extra
keys) in the terminal and publishes the matching command on
/keyboard_control (std_msgs/String).
"""

import os
import select
import sys
import termios
import tty

import rospy
from std_msgs.msg import String


class ControlNode:
    # Key (what the terminal sends) -> command (what we publish)
    # Arrow keys send 3 characters: ESC + '[' + a letter
    KEY_BINDINGS = {
        '\x1b[A': 'UP',
        '\x1b[B': 'DOWN',
        '\x1b[C': 'RIGHT',
        '\x1b[D': 'LEFT',
        ' ': 'SHOOT',      # spacebar -> fire heart arrows
        '\n': 'START',     # Enter -> leave the welcome screen
        'r': 'RESTART',    # play again on the end screen
        'q': 'QUIT',       # exit the game
        '\x1b': 'QUIT',    # ESC -> exit the game
    }

    def __init__(self):
        rospy.init_node('control_node')
        self.control_pub = rospy.Publisher('/keyboard_control', String, queue_size=10)

        # Save the terminal settings so we can restore them when we exit
        self.fd = sys.stdin.fileno()
        self.old_settings = termios.tcgetattr(self.fd)

        rospy.loginfo("control_node started. Publishing commands on /keyboard_control")

    def get_key(self, timeout=0.1):
        """ return the key pressed, or '' if no keey was pressed within timeout seconds"""
        ready, _, _ = select.select([self.fd], [], [], timeout)
        if not ready:
            return ''
        key = os.read(self.fd, 1).decode(errors='ignore')
        if key == '\x1b':                       # start of an arrow-key sequence
            more, _, _ = select.select([self.fd], [], [], 0.05)
            if more:
                key += os.read(self.fd, 2).decode(errors='ignore')  # read the next two characters
        return key.lower() if len(key) == 1 else key

    def publish_command(self, command):
        self.control_pub.publish(String(data=command))
        rospy.loginfo("Command sent: %s", command)

    def print_instructions(self):
        print("")
        print("==============================================")
        print("  CONTROL NODE - keep THIS terminal selected")
        print("  Arrow keys : move (UP / DOWN / LEFT / RIGHT)")
        print("  Space      : SHOOT")
        print("  Enter      : START")
        print("  R          : RESTART      Q / Esc : QUIT")
        print("  Ctrl+C     : stop this node")
        print("==============================================")
        print("")

    def run(self):
        self.print_instructions()
        # cbreak mode: keys arrive immediately (no need to press Enter),
        # they are not printed, and Ctrl+C still works
        tty.setcbreak(self.fd)
        try:
            while not rospy.is_shutdown():
                key = self.get_key()
                command = self.KEY_BINDINGS.get(key)
                if command:
                    self.publish_command(command)
        finally:
            # Always give the terminal back in its normal state
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)
            rospy.loginfo("control_node stopped.")


if __name__ == '__main__':
    try:
        node = ControlNode()
        node.run()
    except rospy.ROSInterruptException:
        pass