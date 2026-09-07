import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from visualization_msgs.msg import Marker


class DrawPolygon(Node):

    LINEAR_SPEED = 1.5            # m/s
    PAUSE_DURATION = 0.5          # s  -> 코너에서 정지해 마커를 찍는 시간
    ANGULAR_SPEED = math.pi / 2   # rad/s
    PERIOD = 0.1                  # s  -> 10Hz
    RADIUS = 2.0                  # m  -> 도형의 외접원 반지름(창 중앙 기준 고정)

    def __init__(self, sides: int):
        super().__init__('draw_polygon')

        self._sides = sides

        # 변의 길이를 N과 무관하게 고정하면 외접원 반지름이 N에 비례해 커져
        # turtlesim 창을 벗어난다. 외접원 반지름(RADIUS)을 고정하고
        # 변의 길이 = 2 * R * sin(pi / N) 공식으로 역산해 항상 같은 크기 안에 들어오게 한다.
        side_length = 2 * self.RADIUS * math.sin(math.pi / sides)
        self._forward_duration = side_length / self.LINEAR_SPEED
        self._turn_duration = (2 * math.pi / sides) / self.ANGULAR_SPEED  # 외각 = 360/N도

        self._pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self._marker_pub = self.create_publisher(Marker, '/corner_markers', 10)

        self._latest_pose = None
        self._pose_sub = self.create_subscription(
            Pose, '/turtle1/pose', self._pose_callback, 10)

        self._phase = 'forward'   # 'forward' -> 'pause' -> 'turn' 순환
        self._elapsed = 0.0
        self._sides_done = 0
        self._corner_id = 0
        self._finished = False

        self._timer = self.create_timer(self.PERIOD, self._timer_callback)

    def _pose_callback(self, msg: Pose) -> None:
        self._latest_pose = msg

    def _publish_corner_marker(self) -> None:
        if self._latest_pose is None:
            return

        marker = Marker()
        marker.header.frame_id = 'world'
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = 'corners'
        marker.id = self._corner_id
        marker.type = Marker.SPHERE
        marker.action = Marker.ADD
        marker.pose.position.x = self._latest_pose.x
        marker.pose.position.y = self._latest_pose.y
        marker.pose.orientation.w = 1.0
        marker.scale.x = 0.5
        marker.scale.y = 0.5
        marker.scale.z = 0.5
        marker.color.b = 1.0
        marker.color.a = 1.0
        self._marker_pub.publish(marker)
        self._corner_id += 1

    def _timer_callback(self) -> None:
        if self._finished:
            return

        self._elapsed += self.PERIOD

        if self._phase == 'forward':
            msg = Twist()
            msg.linear.x = self.LINEAR_SPEED
            self._pub.publish(msg)
            if self._elapsed >= self._forward_duration:
                self._elapsed = 0.0
                self._phase = 'pause'
                self._pub.publish(Twist())      # 정지
                self._publish_corner_marker()   # 정지한 자리에 마커 찍기
            return

        if self._phase == 'pause':
            self._pub.publish(Twist())          # 계속 정지 상태 유지
            if self._elapsed >= self.PAUSE_DURATION:
                self._elapsed = 0.0
                self._phase = 'turn'
            return

        # self._phase == 'turn'
        msg = Twist()
        msg.angular.z = self.ANGULAR_SPEED
        self._pub.publish(msg)
        if self._elapsed < self._turn_duration:
            return

        self._elapsed = 0.0
        self._sides_done += 1
        self._phase = 'forward'

        if self._sides_done >= self._sides:
            self._finished = True
            self._pub.publish(Twist())  # 정지
            self.get_logger().info(f'{self._sides}각형 주행 완료')


def _read_sides() -> int:
    while True:
        raw = input('몇 각형을 그릴지 정수를 입력하세요 (3 이상): ')
        try:
            sides = int(raw)
        except ValueError:
            print('정수를 입력해주세요.')
            continue
        if sides < 3:
            print('변의 개수는 3 이상이어야 합니다.')
            continue
        return sides


def main(args=None):
    rclpy.init(args=args)
    sides = _read_sides()
    node = DrawPolygon(sides)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
