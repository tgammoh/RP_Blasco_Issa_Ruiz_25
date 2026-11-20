#!/usr/bin/env python3
"""
RESULTS_GAME_NODE
Subscribes to /user_information (GameUserMsg) and /result_information (std_msgs/Int64)
and shows a final message with username and score.

"""

import rospy
from std_msgs.msg import Int64
from game_msgs.msg import GameUserMsg


class ResultsGameNode:

    def __init__(self):

        rospy.init_node('result_game_node')

        self.username = None
        self.age = None
        self.final_score = None 

        rospy.Subscriber('/user_information', GameUserMsg, self.user_callback)
        rospy.Subscriber('/result_information', Int64, self.score_callback)

        rospy.loginfo("result_game_node started. Waiting for player info and final score...")


    def user_callback(self, msg):
        self.username = msg.username 
        self.age = msg.age 
        rospy.loginfo("Player information received: username=%s, age=%d", self.username, self.age)
        self.show_result()


    def score_callback(self, msg):

        self.final_score = msg.data
        rospy.loginfo("Final score received: %d", self.final_score)
        self.show_result()

    def show_result(self):

        # Messages can arrive in any order: wait until we have both

        if self.username is None or self.final_score is None:
            return
        print("")
        print("=" * 40)
        print("          GAME OVER")
        print(" Player: %s " % self.username)
        print(" Score : %d " % self.final_score)
        print("=" * 40)
        rospy.loginfo(" Final result displayed for %s", self.username)

    
    def run(self):
        rospy.spin()


if __name__ == '__main__':

    try:
        node = ResultsGameNode()
        node.run()

    except rospy.ROSInterruptException:
        pass



