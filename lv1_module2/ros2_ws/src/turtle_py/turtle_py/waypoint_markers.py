import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
from visualization_msgs.msg import Marker

# square_driver가 그리는 한 변 3m 정사각형의 꼭짓점 (turtle1 시작 위치 기준)
WAYPOINTS = [
    (5.544, 5.544),
    (8.544, 5.544),
    (8.544, 8.544),
    (5.544, 8.544),
    (5.544, 5.544),  # 시작점으로 되돌아와 사각형을 닫음
]


class WaypointMarkerPublisher(Node):

    def __init__(self):
        super().__init__('waypoint_marker_publisher')

        self._pub = self.create_publisher(Marker, '/waypoint_markers', 10)
        self._timer = self.create_timer(1.0, self._timer_callback)  # 1Hz로 계속 재발행

    def _timer_callback(self) -> None:
        now = self.get_clock().now().to_msg()

        points_marker = Marker()
        points_marker.header.frame_id = 'world'
        points_marker.header.stamp = now
        points_marker.ns = 'waypoints'
        points_marker.id = 0
        points_marker.type = Marker.SPHERE_LIST
        points_marker.action = Marker.ADD
        points_marker.scale.x = 0.6
        points_marker.scale.y = 0.6
        points_marker.scale.z = 0.6
        points_marker.color.r = 1.0
        points_marker.color.g = 0.0
        points_marker.color.b = 0.0
        points_marker.color.a = 1.0
        points_marker.points = [Point(x=x, y=y, z=0.0) for x, y in WAYPOINTS]
        self._pub.publish(points_marker)

        line_marker = Marker()
        line_marker.header.frame_id = 'world'
        line_marker.header.stamp = now
        line_marker.ns = 'waypoints'
        line_marker.id = 1
        line_marker.type = Marker.LINE_STRIP
        line_marker.action = Marker.ADD
        line_marker.scale.x = 0.1
        line_marker.color.g = 1.0
        line_marker.color.a = 1.0
        line_marker.points = [Point(x=x, y=y, z=0.0) for x, y in WAYPOINTS]
        self._pub.publish(line_marker)


def main(args=None):
    rclpy.init(args=args)
    node = WaypointMarkerPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
