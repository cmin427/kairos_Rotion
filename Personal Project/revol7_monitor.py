import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

class Revolute7Monitor(Node):
    def __init__(self):
        super().__init__('revolute7_monitor')
        self.subscription = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            10)

    def joint_state_callback(self, msg):
        for i, name in enumerate(msg.name):
            if name == 'Revolute 7':
                position = msg.position[i]
                self.get_logger().info(f'Revolute 7 Position: {position:.4f}')
                return

def main(args=None):
    rclpy.init(args=args)
    revolute7_monitor = Revolute7Monitor()
    rclpy.spin(revolute7_monitor)
    revolute7_monitor.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()