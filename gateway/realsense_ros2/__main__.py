#!/usr/bin/env python3
"""Entry point: python -m gateway.realsense_ros2"""

import rclpy
from rclpy.executors import MultiThreadedExecutor

from .gateway_node import GatewayNode
from luxai.magpie.utils import Logger


def main(args=None):
    Logger.set_level("DEBUG")

    rclpy.init(args=args)
    node = GatewayNode()
    executor = MultiThreadedExecutor()
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.shutdown()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
