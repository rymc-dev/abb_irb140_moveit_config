#!/usr/bin/env python3
"""One-shot loader for a pre-built octomap into move_group's planning scene.

MoveIt's OccupancyMapMonitor has no launch-time "load this file at startup"
option -- the only way to get a pre-built octree into the planning scene's
octomap is the `load_map` service (moveit_msgs/srv/LoadMap) it advertises
once move_group is up. This node waits for that service, calls it once with
the `octomap_path` parameter, logs the result, and exits.

Note: MoveIt's OccupancyMapMonitor reads the octree with
octomap::AbstractOccupancyOcTree::readBinary(), which only understands the
binary `.bt` format -- pass the `.bt` counterpart of a `.ot` file here, not
the `.ot` itself (that full/XML octree format fails with "First line of
OcTree file header does not start with ...").
"""
import sys

import rclpy
from moveit_msgs.srv import LoadMap
from rclpy.node import Node


class StaticOctomapLoader(Node):
    def __init__(self):
        super().__init__("static_octomap_loader")
        self.declare_parameter("octomap_path", "")
        self.declare_parameter("service_wait_timeout_sec", 30.0)

    def load(self):
        octomap_path = self.get_parameter("octomap_path").value
        if not octomap_path:
            self.get_logger().error("octomap_path parameter not set; nothing to load.")
            return False

        timeout_sec = self.get_parameter("service_wait_timeout_sec").value
        client = self.create_client(LoadMap, "load_map")
        self.get_logger().info(f"Waiting for /load_map (move_group) to come up...")
        if not client.wait_for_service(timeout_sec=timeout_sec):
            self.get_logger().error(
                f"/load_map not available after {timeout_sec:.0f}s; is move_group running?"
            )
            return False

        request = LoadMap.Request(filename=octomap_path)
        future = client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        result = future.result()

        if result is None:
            self.get_logger().error(f"/load_map call failed: {future.exception()}")
            return False
        if not result.success:
            self.get_logger().error(f"move_group reported failure loading {octomap_path}")
            return False

        self.get_logger().info(f"Loaded static octomap into the planning scene from {octomap_path}")
        return True


def main():
    rclpy.init()
    node = StaticOctomapLoader()
    success = node.load()
    node.destroy_node()
    rclpy.shutdown()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
