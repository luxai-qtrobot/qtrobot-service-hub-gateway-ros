"""
QTrobot ROS2 Gateway Node.

Bridges the qtrobot-service-hub ZMQ/magpie interfaces to ROS2 services
and topics.  The API is read from api_list.py (co-located in this package).

ROS2 parameters
---------------
robot_ip    (string, default "192.168.1.1")
    IP address of the robot running qtrobot-service-hub.

rpc_timeout (float, default 30.0)
    Maximum seconds to wait for an RPC reply before returning status=false.
"""

import rclpy
from rclpy.node import Node

from .api_list import API

from .rpc_bridge import RpcBridge
from .stream_bridge import StreamBridge


# ---------------------------------------------------------------------------

class GatewayNode(Node):

    def __init__(self):
        super().__init__('qtrobot_ros2_gateway')

        self.declare_parameter('robot_ip',   '127.0.0.1')
        self.declare_parameter('rpc_timeout', 30.0)

        robot_ip    = self.get_parameter('robot_ip').get_parameter_value().string_value
        rpc_timeout = self.get_parameter('rpc_timeout').get_parameter_value().double_value

        self.get_logger().info(f'QTrobot gateway starting (robot_ip={robot_ip})')

        self._rpc_bridge = RpcBridge(
            node=self,
            api_rpc=API['rpc'],
            robot_ip=robot_ip,
            rpc_timeout=rpc_timeout,
        )

        self._stream_bridge = StreamBridge(
            node=self,
            api_stream=API['stream'],
            robot_ip=robot_ip,
        )

        self.get_logger().info('QTrobot gateway ready.')

    def shutdown(self) -> None:
        self.get_logger().info('QTrobot gateway shutting down.')
        self._stream_bridge.close()
        self._rpc_bridge.close()
