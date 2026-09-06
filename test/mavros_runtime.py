#!/usr/bin/env python3
import time
import unittest
import rospy
import rostest
from mavros_msgs.msg import State
from mavros_msgs.srv import CommandLong
from gazebo_msgs.srv import GetWorldProperties
class MavrosRuntime(unittest.TestCase):
    def test_two_connected_instances(self):
        states={}
        subs=[rospy.Subscriber('/%s/mavros/state'%name,State,lambda msg,name=name:states.update({name:msg})) for name in ['uav1','uav2']]
        deadline=time.monotonic()+70
        while time.monotonic()<deadline:
            if len(states)==2 and all(state.connected for state in states.values()): break
            time.sleep(.1)
        self.assertEqual(set(states),{'uav1','uav2'})
        self.assertTrue(all(state.connected for state in states.values()),states)
        self.assertTrue({'fs150_3','fs150_4'}.issubset(rospy.ServiceProxy('/gazebo/get_world_properties',GetWorldProperties)().model_names))
        for name in ['uav1','uav2']:
            service='/%s/mavros/cmd/command'%name
            rospy.wait_for_service(service,timeout=10)
            # Disarm already-unarmed disposable SITL; require actual FCU ACK.
            ack=rospy.ServiceProxy(service,CommandLong)(False,400,0,0,0,0,0,0,0,0)
            self.assertTrue(ack.success)
            self.assertEqual(ack.result,0)
        for sub in subs:sub.unregister()
if __name__=='__main__':
    rospy.init_node('mavros_runtime')
    rostest.rosrun('gazebo_sim_fs150_sitl','mavros_runtime',MavrosRuntime)
