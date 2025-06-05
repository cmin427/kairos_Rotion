import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import serial
import time

class JointStateToMultiServoZeroDebug(Node):
    def __init__(self):
        super().__init__('joint_state_to_multi_servo_zero_debug')
        self.subscription = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            10)
        try:
            self.serial_port = serial.Serial('/dev/ttyUSB0', 115200)
            self.get_logger().info(f'Serial port {self.serial_port.port} opened successfully.')
        except serial.SerialException as e:
            self.get_logger().error(f'Could not open serial port: {e}')
            self.serial_port = None
        self.joint_names_to_control = ['Revolute 2', 'Revolute 6', 'Revolute 7', 'Revolute 8']  # 제어할 4개 관절 이름 (실제 이름으로 변경)
        self.servo_zero_offsets = [90, 85, 90, 110]  # 각 서보의 영점 오프셋 (Servo1, Servo2, Servo3, Servo4 순서)
        self.servo_angle_multipliers = [180.0 / 3.14159] * 4 # 기본 변환 계수
        self.last_command_time = 0.0
        self.command_interval = 0.1

    def joint_state_callback(self, msg):
        current_time_ros = self.get_clock().now()
        current_time = current_time_ros.nanoseconds * 1e-9  # 나노초를 초로 변환

        if current_time - self.last_command_time >= self.command_interval:
            if self.serial_port and self.serial_port.is_open:
                try:
                    servo_angles_to_send = [0] * 4
                    joint_values = {}
                    for i, name in enumerate(msg.name):
                        if name in self.joint_names_to_control:
                            joint_values[name] = msg.position[i]

                    found_all_joints = True
                    angles_to_send_log = []
                    for i, target_joint_name in enumerate(self.joint_names_to_control):
                        if target_joint_name in joint_values:
                            angle_rad = joint_values[target_joint_name]
                            self.get_logger().info(f'Processing Joint: {target_joint_name}, Raw Radian: {angle_rad:.4f}') # 추가 로깅

                            if i == 1:  # Revolute 6 (Servo2)에 대한 별도 계산 (라디안 범위 -> 180 ~ 0)
                                # 라디안 범위: -1.7 ~ 1.7 (총 3.4) -> 각도 범위: 180 ~ 0 (총 -180)
                                # 기울기 (m) = (0 - 180) / (1.7 - (-1.7)) = -180 / 3.4
                                m = -180.0 / 3.4
                                # y - y1 = m(x - x1) => servo_angle - 180 = m(angle_rad - (-1.7))
                                servo_angle = int(m * (angle_rad + 1.7) + 180)
                            else:
                                servo_angle = self.servo_zero_offsets[i] if abs(angle_rad) < 0.001 else int(angle_rad * self.servo_angle_multipliers[i] + self.servo_zero_offsets[i])

                            servo_angle = max(0, min(180, servo_angle)) # 범위 제한
                            servo_angles_to_send[i] = servo_angle
                            angles_to_send_log.append(f'{target_joint_name}: {servo_angle}')
                        else:
                            self.get_logger().warn(f"Joint '{target_joint_name}' not found in /joint_states")
                            found_all_joints = False
                            break

                    if found_all_joints:
                        data_to_send = ",".join(map(str, servo_angles_to_send)) + "\n"
                        self.serial_port.write(data_to_send.encode('utf-8'))
                        self.last_command_time = current_time
                except serial.SerialException as e:
                    self.get_logger().error(f'Serial write error: {e}')
            else:
                self.get_logger().warn('Serial port is not open.')

def main(args=None):
    rclpy.init(args=args)
    joint_state_to_multi_servo_zero = JointStateToMultiServoZeroDebug()
    rclpy.spin(joint_state_to_multi_servo_zero)
    joint_state_to_multi_servo_zero.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()