import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32


class DistanceWatcher(Node):

    def __init__(self):
        super().__init__('distance_watcher')

        self.declare_parameter('threshold', 15.0) #임계값 3.0으로 설정, 임계값 변경 필요시 숫자 변경

        self._sub = self.create_subscription(
            Float32, '/turtle_distance', self._distance_callback, 10) #10Hz로 발행

    def _distance_callback(self, msg: Float32) -> None:
        threshold = self.get_parameter('threshold').value
        if msg.data > threshold:
            self.get_logger().warn(
                f'거리 {msg.data:.3f} m가 임계값 {threshold:.3f} m를 초과했습니다') #3.0초과시 경고문구 출력


def main(args=None):
    rclpy.init(args=args)
    node = DistanceWatcher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
