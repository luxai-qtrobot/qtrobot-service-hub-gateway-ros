"""RealSense ROS2 gateway node."""

from ..core.gateway_node import GatewayNode as BaseGatewayNode
from .api_list import API


class GatewayNode(BaseGatewayNode):

    def __init__(self):
        super().__init__(
            node_name='realsense_ros2_gateway',
            ip_param='realsense_ip',
            api=API,
            interfaces_pkg='qtrobot_interfaces',
            default_ip='127.0.0.1',
        )
