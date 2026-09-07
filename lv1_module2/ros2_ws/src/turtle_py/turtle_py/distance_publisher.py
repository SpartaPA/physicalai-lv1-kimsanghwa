import math

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from turtlesim.msg import Pose


class TurtleDistancePublisher(Node):

    def __init__(self):
        super().__init__('turtle_distance_publisher')

        self._latest_pose = None

        self._pose_sub = self.create_subscription(
            Pose, '/turtle1/pose', self._pose_callback, 10)

        self._distance_pub = self.create_publisher(Float32, '/turtle_distance', 10)

        self._timer = self.create_timer(0.1, self._timer_callback)  # 10Hz

    def _pose_callback(self, msg: Pose) -> None:
        # 구독 콜백: 최신 자세만 저장하고 발행은 하지 않음
        self._latest_pose = msg

    def _timer_callback(self) -> None:
        if self._latest_pose is None:
            return

        distance = math.sqrt(self._latest_pose.x ** 2 + self._latest_pose.y ** 2)

        msg = Float32()
        msg.data = distance
        self._distance_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = TurtleDistancePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
