#!/usr/bin/env python3
""" INFO_USER_NODE 
Asks the player for their full name, username, and age in the terminal, 
validates them and publishes them on /user_information (GameUserMsg).

"""

import re
import rospy
from game_msgs.msg import GameUserMsg


class InfoUserNode:

    def __init__(self):
        
        rospy.init_node('info_user_node')

        # we set latch = True --> ROS keeps the last message and also delivers it to nodes that start (subscribe) after we published it.
        self.user_pub = rospy.Publisher('/user_information', GameUserMsg, queue_size=1, latch=True)


        self.name = ""
        self.username = ""
        self.age = 0

        rospy.loginfo("info_user_node started. Asking for player information...")

    
    def ask_name(self):

        while not rospy.is_shutdown():
            name = input("Enter your full name: ").strip()
            words = name.split()
            if len(words) >= 1 and all (w.replace("-", "").replace("'", "").isalpha() for w in words):
                return " ".join(words)

            print(" Invalid name. Use letters only, with optional hyphens or spaces).")

    def ask_username(self):
        
        while not rospy.is_shutdown():

            username = input("enter your username: ").strip()
            if re.fullmatch(r"\w{3,20}", username):
                return username
            print(" Invalid username, use 3-20 letters, numbers or _ (no spaces).)")

    def ask_age(self):

        while not rospy.is_shutdown():
            
            text = input("Enter your age: ").strip()
            if text.isdigit() and 1 <= int(text) <= 120:
                return int(text)
            print(" Invalid age, use a number between 1 and 120.")


    def collect_user_info(self):
        self.name = self.ask_name()
        self.username = self.ask_username()
        self.age = self.ask_age()

        rospy.loginfo(" Player information validated: %s (%s), %d years old", self.name, self.username, self.age)


    def publish_user_info(self):
        msg = GameUserMsg()
        msg.name = self.name 
        msg.username = self.username 
        msg.age = self.age 
        self.user_pub.publish(msg)
        rospy.loginfo("Player information published on /user_information")

    def run(self):
        self.collect_user_info()
        self.publish_user_info()
        rospy.loginfo("Done, keeping node alive so late subscribers get the data.")
        rospy.spin()

if __name__ == '__main__':

    try:
        node = InfoUserNode()
        node.run()
    except (rospy.ROSInterruptException, KeyboardInterrupt, EOFError):
        pass
        



