"""
Stream bridge: bridges ZMQ PUB/SUB streams to/from ROS2 topics.

  "out" streams (hub → gateway):
    ZMQSubscriber.read() → dict → ROS2 publisher.publish(msg)

  "in" streams (gateway → hub):
    ROS2 subscriber callback → dict → ZMQPublisher.write(dict, topic)

Topic naming convention:
  The api_path (e.g. /gesture/progress/stream:o) is used as the ZMQ
  topic filter.  The ROS2 topic name is the same path with the :i/:o
  direction suffix stripped.
"""

import threading

from luxai.magpie.transport.zmq.zmq_subscriber import ZMQSubscriber
from luxai.magpie.transport.zmq.zmq_publisher import ZMQPublisher

from .converters import get_msg_class, dict_to_ros2_msg, ros2_msg_to_dict


def _ros2_topic(api_path: str) -> str:
    """Strip :i/:o direction suffix → ROS2 topic name (relative, no leading /)."""
    return api_path.split(':')[0].lstrip('/')


class StreamBridge:
    """
    Manages all ZMQ ↔ ROS2 stream bridges (both directions).
    """

    def __init__(self, node, api_stream: dict, robot_ip: str):
        self._node = node
        self._subscribers: list[ZMQSubscriber] = []
        self._publishers: list[ZMQPublisher] = []
        self._threads: list[threading.Thread] = []
        self._running = threading.Event()
        self._running.set()

        self._setup(api_stream, robot_ip)

    # ------------------------------------------------------------------

    def _endpoint(self, template: str, robot_ip: str) -> str:
        return template.replace('*', robot_ip)

    def _setup(self, api_stream: dict, robot_ip: str) -> None:
        for api_path, info in api_stream.items():
            direction   = info['direction']
            frame_type  = info['frame_type']
            frame_fields = info.get('frame_fields')        # None for binary frames
            sub_msgs_def = info.get('sub_msgs', {})
            zmq_cfg      = info['transports']['zmq']
            endpoint     = self._endpoint(zmq_cfg['endpoint'], robot_ip)
            delivery     = zmq_cfg.get('delivery', 'reliable')
            queue_size   = zmq_cfg.get('queue_size', 10)
            ros_topic    = _ros2_topic(api_path)

            try:
                msg_class = get_msg_class(frame_type)
            except AttributeError:
                self._node.get_logger().warning(
                    f'StreamBridge: no msg class for {frame_type}, skipping {api_path}'
                )
                continue

            if direction == 'out':
                self._setup_out(api_path, endpoint, ros_topic, msg_class,
                                frame_type, frame_fields, sub_msgs_def,
                                delivery, queue_size)
            else:  # 'in'
                self._setup_in(api_path, endpoint, ros_topic, msg_class,
                               frame_type, frame_fields, sub_msgs_def,
                               delivery, queue_size)

    # ------------------------------------------------------------------
    # "out": ZMQ subscriber → ROS2 publisher
    # ------------------------------------------------------------------

    def _setup_out(self, api_path, endpoint, ros_topic, msg_class,
                   frame_type, frame_fields, sub_msgs_def, delivery, queue_size):
        ros2_pub = self._node.create_publisher(msg_class, ros_topic, 10)

        sub = ZMQSubscriber(
            endpoint=endpoint,
            topic=api_path,          # ZMQ topic filter = full api_path
            queue_size=max(queue_size, 1),
            delivery=delivery,
        )
        self._subscribers.append(sub)

        clock = self._node.get_clock()

        def reader():
            while self._running.is_set():
                try:
                    result = sub.read(timeout=1.0)
                    if result is None:
                        continue
                    data_dict, _topic = result
                    if not isinstance(data_dict, dict):
                        continue

                    # Unwrap magpie frame envelope {gid, id, name, timestamp, value}
                    if 'value' in data_dict and isinstance(data_dict['value'], dict):
                        data_dict = data_dict['value']

                    ros_msg = msg_class()
                    dict_to_ros2_msg(
                        data_dict=data_dict,
                        frame_type=frame_type,
                        frame_fields=frame_fields,
                        sub_msgs_def=sub_msgs_def,
                        ros2_msg=ros_msg,
                        clock=clock,
                    )
                    ros2_pub.publish(ros_msg)
                except TimeoutError:
                    continue
                except Exception as exc:
                    if self._running.is_set():
                        self._node.get_logger().warning(
                            f'Out stream {api_path}: {exc}'
                        )

        t = threading.Thread(target=reader, name=f'out:{api_path}', daemon=True)
        self._threads.append(t)
        t.start()
        self._node.get_logger().debug(
            f'StreamBridge out: {api_path} ({endpoint}) → {ros_topic}'
        )

    # ------------------------------------------------------------------
    # "in": ROS2 subscriber → ZMQ publisher
    # ------------------------------------------------------------------

    def _setup_in(self, api_path, endpoint, ros_topic, msg_class,
                  frame_type, frame_fields, sub_msgs_def, delivery, queue_size):
        pub = ZMQPublisher(
            endpoint=endpoint,
            queue_size=max(queue_size, 1),
            bind=False,      # gateway connects to the hub's SUB socket
            delivery=delivery,
        )
        self._publishers.append(pub)

        def ros_callback(ros_msg):
            try:
                data_dict = ros2_msg_to_dict(
                    ros2_msg=ros_msg,
                    frame_type=frame_type,
                    frame_fields=frame_fields,
                    sub_msgs_def=sub_msgs_def,
                )
                pub.write(data_dict, topic=api_path)
            except Exception as exc:
                self._node.get_logger().warning(
                    f'In stream {api_path}: {exc}'
                )

        self._node.create_subscription(msg_class, ros_topic, ros_callback, 10)
        self._node.get_logger().debug(
            f'StreamBridge in: {ros_topic} → {api_path} ({endpoint})'
        )

    # ------------------------------------------------------------------

    def close(self) -> None:
        self._running.clear()
        for t in self._threads:
            t.join(timeout=2.0)
        for sub in self._subscribers:
            try:
                sub.close()
            except Exception:
                pass
        for pub in self._publishers:
            try:
                pub.close()
            except Exception:
                pass
