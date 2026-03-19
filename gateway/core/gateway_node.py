"""
Base GatewayNode: ROS2 node that bridges a ZMQ/magpie backend to ROS2
services and topics.

Subclasses provide:
  - node_name      : ROS2 node name
  - ip_param       : name of the IP address parameter (e.g. 'robot_ip')
  - api            : API dict with 'rpc' and 'stream' keys
  - interfaces_pkg : Python package name for ROS2 msg/srv types
  - default_ip     : default value for the IP parameter
"""

from rclpy.node import Node

from .rpc_bridge import RpcBridge
from .stream_bridge import StreamBridge


class GatewayNode(Node):

    def __init__(self, node_name: str, ip_param: str, api: dict,
                 interfaces_pkg: str, default_ip: str = '127.0.0.1'):
        super().__init__(node_name)

        self.declare_parameter(ip_param, default_ip)
        self.declare_parameter('rpc_timeout', 30.0)

        ip = self.get_parameter(ip_param).get_parameter_value().string_value
        rpc_timeout = self.get_parameter('rpc_timeout').get_parameter_value().double_value

        self.get_logger().info(f'{node_name} starting ({ip_param}={ip})')

        self._rpc_bridge = RpcBridge(
            node=self,
            api_rpc=api.get('rpc', {}),
            robot_ip=ip,
            rpc_timeout=rpc_timeout,
            interfaces_pkg=interfaces_pkg,
        )

        self._stream_bridge = StreamBridge(
            node=self,
            api_stream=api.get('stream', {}),
            robot_ip=ip,
            interfaces_pkg=interfaces_pkg,
        )

        self.get_logger().info(f'{node_name} ready.')

    def shutdown(self) -> None:
        self.get_logger().info('Gateway shutting down.')
        self._stream_bridge.close()
        self._rpc_bridge.close()
