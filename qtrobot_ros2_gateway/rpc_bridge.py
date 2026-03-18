"""
RPC bridge: creates one ROS2 service per RPC endpoint and proxies calls
to the ZMQ/magpie service hub via ZMQRpcRequester.

One ZMQRpcRequester is created per unique ZMQ endpoint (port), so all
RPC endpoints on the same port share a single DEALER socket.
"""

from luxai.magpie.transport.zmq.zmq_rpc_requester import ZMQRpcRequester
from luxai.magpie.transport.rpc_requester import AckTimeoutError, ReplyTimeoutError

from .converters import get_srv_class, ros2_request_to_args, fill_ros2_rpc_response


class RpcBridge:
    """
    Creates ROS2 services for every entry in API['rpc'] and bridges
    each service call to the qtrobot service hub via ZMQ RPC.
    """

    def __init__(self, node, api_rpc: dict, robot_ip: str,
                 rpc_timeout: float = 30.0):
        self._node = node
        self._rpc_timeout = rpc_timeout
        self._requesters: dict[str, ZMQRpcRequester] = {}  # endpoint → requester
        self._services: list = []

        self._setup(api_rpc, robot_ip)

    # ------------------------------------------------------------------

    def _endpoint(self, template: str, robot_ip: str) -> str:
        return template.replace('*', robot_ip)

    def _setup(self, api_rpc: dict, robot_ip: str) -> None:
        for api_path, info in api_rpc.items():
            endpoint = self._endpoint(
                info['transports']['zmq']['endpoint'], robot_ip
            )

            if endpoint not in self._requesters:
                self._requesters[endpoint] = ZMQRpcRequester(
                    endpoint=endpoint,
                    name=f'rpc:{endpoint}',
                )
                self._node.get_logger().debug(
                    f'RpcBridge: new ZMQRpcRequester → {endpoint}'
                )

            requester = self._requesters[endpoint]
            params_def = info.get('params', {})
            returns_def = info.get('returns', {'type': 'bool'})

            try:
                srv_class = get_srv_class(api_path)
            except AttributeError:
                self._node.get_logger().warning(
                    f'RpcBridge: no srv class for {api_path}, skipping'
                )
                continue

            callback = self._make_callback(
                requester, api_path, params_def, returns_def
            )
            svc = self._node.create_service(srv_class, api_path.lstrip('/'), callback)
            self._services.append(svc)
            self._node.get_logger().debug(
                f'RpcBridge: service {api_path} → {endpoint}'
            )

    def _make_callback(self, requester: ZMQRpcRequester,
                       api_path: str, params_def: dict, returns_def: dict):
        def callback(request, response):
            args = ros2_request_to_args(request, params_def)
            request_obj = {'name': api_path, 'args': args}
            try:
                zmq_resp = requester.call(request_obj, timeout=self._rpc_timeout)
                fill_ros2_rpc_response(zmq_resp, response, returns_def)
            except (AckTimeoutError, ReplyTimeoutError) as exc:
                self._node.get_logger().warning(
                    f'{api_path}: timeout — {exc}'
                )
                response.status = False
            except Exception as exc:
                self._node.get_logger().error(
                    f'{api_path}: error — {exc}'
                )
                response.status = False
            return response

        return callback

    # ------------------------------------------------------------------

    def close(self) -> None:
        for requester in self._requesters.values():
            try:
                requester.close()
            except BaseException:
                pass
        self._requesters.clear()
