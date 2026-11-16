#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Point
from geometry_msgs.msg import PoseWithCovarianceStamped
from nav2_msgs.msg import SpeedLimit
from visualization_msgs.msg import Marker


class SpeedLimiter(Node):

    def __init__(self):

        super().__init__('speed_limiter')

        # PARAMETERS

        self.declare_parameter('max_speed', 0.1)
        self.declare_parameter('polygon_x', [1.8, 1.8, 0.4, 0.4])
        self.declare_parameter('polygon_y', [0.6, -1.6, -1.6, 0.6])
        self.declare_parameter('pose_topic', '/amcl_pose')
        self.declare_parameter('speed_limit_topic', '/speed_limit')

        self.max_speed = self.get_parameter('max_speed').value
        polygon_x = self.get_parameter('polygon_x').value
        polygon_y = self.get_parameter('polygon_y').value

        self.polygon = []

        for i in range(len(polygon_x)):
            self.polygon.append([polygon_x[i], polygon_y[i]])

        self.get_logger().info(f"Max Speed: {self.max_speed}")
        self.get_logger().info(f"Polygon: {self.polygon}")

        # ROBOT POSITION

        self.robot_x = 0.0
        self.robot_y = 0.0
        self.have_pose = False
        self.inside = False

        # SUBSCRIBE ROBOT POSE (AMCL)

        self.pose_sub = self.create_subscription(
            PoseWithCovarianceStamped,
            self.get_parameter('pose_topic').value,
            self.pose_callback,
            10
        )

        # NAV2 SPEED LIMIT PUBLISHER

        self.limit_pub = self.create_publisher(
            SpeedLimit,
            self.get_parameter('speed_limit_topic').value,
            10
        )

        # RVIZ MARKER

        self.marker_pub = self.create_publisher(
            Marker,
            '/speed_zone_marker',
            10
        )

        self.marker_timer = self.create_timer(1.0, self.publish_marker)

        # re-send the current limit once a second so Nav2 never misses it
        self.limit_timer = self.create_timer(1.0, self.publish_limit)

        self.get_logger().info("Speed Limiter Started")

    # ROBOT POSITION

    def pose_callback(self, msg):

        self.robot_x = msg.pose.pose.position.x
        self.robot_y = msg.pose.pose.position.y
        self.have_pose = True

        now_inside = self.point_inside_polygon(self.robot_x, self.robot_y)

        if now_inside != self.inside:
            self.inside = now_inside

            if self.inside:
                self.get_logger().info(
                    f"Robot entered speed zone, limit {self.max_speed} m/s")
            else:
                self.get_logger().info(
                    "Robot left speed zone, limit removed")

            self.publish_limit()

    # SPEED LIMIT (Nav2: speed_limit 0.0 means "no limit")

    def publish_limit(self):

        if not self.have_pose:
            return

        msg = SpeedLimit()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "map"
        msg.percentage = False
        msg.speed_limit = float(self.max_speed) if self.inside else 0.0

        self.limit_pub.publish(msg)

    # POINT IN POLYGON

    def point_inside_polygon(self, x, y):

        inside = False
        n = len(self.polygon)

        px, py = zip(*self.polygon)

        j = n - 1

        for i in range(n):

            if ((py[i] > y) != (py[j] > y)) and \
                    (x < (px[j] - px[i]) * (y - py[i]) /
                     (py[j] - py[i]) + px[i]):

                inside = not inside

            j = i

        return inside

    # RVIZ ZONE

    def publish_marker(self):

        if len(self.polygon) == 0:
            return

        marker = Marker()

        marker.header.frame_id = "map"
        marker.header.stamp = self.get_clock().now().to_msg()

        marker.ns = "speed_zone"
        marker.id = 0
        marker.type = Marker.LINE_STRIP
        marker.action = Marker.ADD

        marker.scale.x = 0.05

        marker.color.r = 1.0
        marker.color.g = 0.0
        marker.color.b = 0.0
        marker.color.a = 1.0

        for p in self.polygon:

            pt = Point()
            pt.x = float(p[0])
            pt.y = float(p[1])
            pt.z = 0.0

            marker.points.append(pt)

        first = Point()
        first.x = float(self.polygon[0][0])
        first.y = float(self.polygon[0][1])
        first.z = 0.0

        marker.points.append(first)

        self.marker_pub.publish(marker)


def main(args=None):

    rclpy.init(args=args)

    node = SpeedLimiter()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()