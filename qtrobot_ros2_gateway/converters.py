"""
ROS2 ↔ ZMQ dict conversion helpers for the QTrobot gateway.

Wire protocol (ZMQ/msgpack side):
  RPC request:  {"name": <api_path>, "args": {<param>: <value>, ...}}
  RPC response: {"status": bool, "response": <payload>}
  Stream frame: plain dict {<field>: <value>, ...}  (msgpack-deserialized)
"""

import json
import importlib


# ---------------------------------------------------------------------------
# Name helper (mirrors scripts/ros2_interfaces_generator.py)
# ---------------------------------------------------------------------------

def path_to_classname(api_path: str) -> str:
    """
    /face/emotion/list       → FaceEmotionList
    /gesture/progress/stream:o → GestureProgressStream
    """
    clean = api_path.lstrip('/').split(':')[0]
    parts = []
    for segment in clean.split('/'):
        for word in segment.split('_'):
            if word:
                parts.append(word.capitalize())
    return ''.join(parts)


# ---------------------------------------------------------------------------
# Type coercion helper
# ---------------------------------------------------------------------------

def _coerce(value, ros2_type: str):
    """Coerce a value to the Python type expected by a ROS2 field."""
    if 'float' in ros2_type:
        return float(value)
    if 'int' in ros2_type or 'uint' in ros2_type:
        return int(value)
    if ros2_type == 'bool':
        return bool(value)
    return value


# ---------------------------------------------------------------------------
# Dynamic ROS2 class loaders
# ---------------------------------------------------------------------------

def get_srv_class(api_path: str):
    """Return the qtrobot_interfaces.srv class for an RPC API path."""
    class_name = path_to_classname(api_path)
    mod = importlib.import_module('qtrobot_interfaces.srv')
    return getattr(mod, class_name)


def get_msg_class(frame_type: str):
    """Return the qtrobot_interfaces.msg class for a frame type name."""
    mod = importlib.import_module('qtrobot_interfaces.msg')
    return getattr(mod, frame_type)


# ---------------------------------------------------------------------------
# RPC: ROS2 request → ZMQ args dict
# ---------------------------------------------------------------------------

# ROS2 "empty" defaults for each param type (mirrors the srv generator)
_EMPTY_DEFAULT = {
    'str':   '',
    'float': 0.0,
    'int':   0,
    'bool':  False,
    'list':  '',
    'dict':  '',
}


def ros2_request_to_args(request, params_def: dict) -> dict:
    """
    Convert a ROS2 service request object to a ZMQ args dict.

    Rules:
      - Required params: always included.
      - Optional params with api_default=None: included only when the field
        value differs from the ROS2 "empty" sentinel (0 / 0.0 / False / "").
      - Optional params with an explicit api_default: always included.
      - Params of type "list" or "dict" are JSON-decoded from the string field.
    """
    args = {}
    for param_name, param_info in params_def.items():
        param_type = param_info.get('type', 'str')
        required = param_info.get('required', True)
        api_default = param_info.get('default')

        field_val = getattr(request, param_name, None)
        if field_val is None:
            continue

        # For optional params whose api default is None, skip when the field
        # still holds its ROS2 "empty" sentinel value.
        if not required and api_default is None:
            empty = _EMPTY_DEFAULT.get(param_type, '')
            if field_val == empty:
                continue

        # Decode JSON-encoded list/dict params
        if param_type == 'list':
            try:
                args[param_name] = json.loads(field_val) if field_val else None
            except (json.JSONDecodeError, TypeError):
                args[param_name] = field_val
        elif param_type == 'dict':
            try:
                args[param_name] = json.loads(field_val) if field_val else None
            except (json.JSONDecodeError, TypeError):
                args[param_name] = field_val
        else:
            args[param_name] = field_val

        # Drop keys that decoded to None (absent optionals)
        if args.get(param_name) is None:
            args.pop(param_name, None)

    return args


# ---------------------------------------------------------------------------
# RPC: ZMQ response → ROS2 response
# ---------------------------------------------------------------------------

def fill_ros2_rpc_response(zmq_resp, ros_response, returns_def: dict) -> None:
    """
    Fill a ROS2 service response from a ZMQ RPC response.

    zmq_resp is expected to be {"status": bool, "response": <payload>}.
    Falls back gracefully if the structure differs.
    """
    if isinstance(zmq_resp, dict) and 'status' in zmq_resp:
        status = bool(zmq_resp.get('status', False))
        payload = zmq_resp.get('response')
    else:
        status = True
        payload = zmq_resp

    ros_response.status = status

    ret_type = returns_def.get('type', 'bool')

    if ret_type == 'bool':
        ros_response.result = bool(payload) if payload is not None else status

    elif ret_type == 'float64':
        try:
            ros_response.result = float(payload) if payload is not None else 0.0
        except (TypeError, ValueError):
            ros_response.result = 0.0

    elif ret_type == 'string':
        ros_response.result = str(payload) if payload is not None else ''

    elif ret_type == 'string[]':
        ros_response.result = list(payload) if isinstance(payload, (list, tuple)) else []

    elif ret_type == 'json':
        ros_response.result = json.dumps(payload) if payload is not None else ''

    elif ret_type == 'msg_array':
        item_msg_name = returns_def['item_msg']
        item_fields = returns_def['item_fields']
        mod = importlib.import_module('qtrobot_interfaces.msg')
        item_class = getattr(mod, item_msg_name)

        result = []
        if isinstance(payload, list):
            for item_dict in payload:
                if isinstance(item_dict, dict):
                    item = item_class()
                    for field_name, field_type in item_fields.items():
                        if field_name in item_dict:
                            try:
                                setattr(item, field_name,
                                        _coerce(item_dict[field_name], field_type))
                            except Exception:
                                pass
                    result.append(item)
        elif isinstance(payload, dict):
            # Dynamic-key dict: {name: {fields}} — key becomes the 'name' field
            for item_key, item_data in payload.items():
                if isinstance(item_data, dict):
                    item = item_class()
                    if hasattr(item, 'name'):
                        item.name = item_key
                    for field_name, field_type in item_fields.items():
                        if field_name != 'name' and field_name in item_data:
                            try:
                                setattr(item, field_name,
                                        _coerce(item_data[field_name], field_type))
                            except Exception:
                                pass
                    result.append(item)
        ros_response.result = result


# ---------------------------------------------------------------------------
# Stream: ZMQ dict → ROS2 msg
# ---------------------------------------------------------------------------

# Field-name mappings for built-in binary frames (magpie → ROS2 msg fields)
_AUDIO_FRAME_MAP = {
    'channels':    'channels',
    'sample_rate': 'sample_rate',
    'bit_depth':   'sample_width',   # magpie bit_depth → ros2 sample_width (raw value kept)
    # 'format' is not in the ROS2 msg
}
_IMAGE_FRAME_MAP = {
    'width':        'width',
    'height':       'height',
    'pixel_format': 'encoding',      # magpie pixel_format → ros2 encoding
    # 'format' / 'channels' are not in the ROS2 msg
}


def dict_to_ros2_msg(data_dict: dict, frame_type: str, frame_fields: dict,
                     sub_msgs_def: dict, ros2_msg, clock=None) -> None:
    """
    Fill a ROS2 message from a plain dict received from ZMQ.

    Handles three cases:
      1. Typed flat-field frames (frame_fields provided, no array-of-structs).
      2. Array-of-structs frames (field value references a sub-msg array type).
      3. Built-in binary frames AudioFrameRaw / ImageFrameRaw.
    """
    from std_msgs.msg import Header

    # Always stamp the header if present
    if hasattr(ros2_msg, 'header'):
        header = Header()
        if clock is not None:
            header.stamp = clock.now().to_msg()
        ros2_msg.header = header

    if frame_fields is None:
        # Built-in binary frame — use explicit field mapping
        if frame_type == 'AudioFrameRaw':
            for src, dst in _AUDIO_FRAME_MAP.items():
                if src in data_dict and hasattr(ros2_msg, dst):
                    setattr(ros2_msg, dst, data_dict[src])
            raw = data_dict.get('data', b'')
            ros2_msg.data = list(raw) if isinstance(raw, (bytes, bytearray)) else raw

        elif frame_type == 'ImageFrameRaw':
            for src, dst in _IMAGE_FRAME_MAP.items():
                if src in data_dict and hasattr(ros2_msg, dst):
                    setattr(ros2_msg, dst, data_dict[src])
            raw = data_dict.get('data', b'')
            ros2_msg.data = list(raw) if isinstance(raw, (bytes, bytearray)) else raw

        else:
            # Generic fallback: copy all matching fields
            for key, val in data_dict.items():
                if hasattr(ros2_msg, key):
                    try:
                        setattr(ros2_msg, key, val)
                    except Exception:
                        pass
        return

    # Typed frame with known fields
    mod = importlib.import_module('qtrobot_interfaces.msg')

    for field_name, ros2_type in frame_fields.items():
        val = data_dict.get(field_name)
        if val is None:
            # The entire frame may be the array-of-structs (e.g. motor joints:
            # ZMQ sends {motor_name: {fields}} with no wrapper key)
            if ros2_type.endswith('[]') and not ros2_type.startswith('std_msgs'):
                val = data_dict
            else:
                continue

        if ros2_type.endswith('[]') and not ros2_type.startswith('std_msgs'):
            # Array-of-structs field
            sub_msg_name = ros2_type[:-2]
            sub_fields = sub_msgs_def.get(sub_msg_name, {})
            sub_class = getattr(mod, sub_msg_name)

            if isinstance(val, dict):
                # Dynamic-key dict: {motor_name: {position: ..., ...}}
                # The sub-msg has a 'name' field to hold the key.
                items = []
                for item_key, item_data in val.items():
                    sub = sub_class()
                    if hasattr(sub, 'name'):
                        sub.name = item_key
                    if isinstance(item_data, dict):
                        for sf in sub_fields:
                            if sf != 'name' and sf in item_data:
                                try:
                                    setattr(sub, sf, item_data[sf])
                                except Exception:
                                    pass
                    items.append(sub)
                setattr(ros2_msg, field_name, items)

            elif isinstance(val, list):
                items = []
                for item_data in val:
                    sub = sub_class()
                    if isinstance(item_data, dict):
                        for sf in sub_fields:
                            if sf in item_data:
                                try:
                                    setattr(sub, sf, item_data[sf])
                                except Exception:
                                    pass
                    items.append(sub)
                setattr(ros2_msg, field_name, items)

        else:
            # Scalar field
            try:
                setattr(ros2_msg, field_name, val)
            except Exception:
                pass


# ---------------------------------------------------------------------------
# Stream: ROS2 msg → ZMQ dict
# ---------------------------------------------------------------------------

def ros2_msg_to_dict(ros2_msg, frame_type: str, frame_fields: dict,
                     sub_msgs_def: dict) -> dict:
    """
    Convert a ROS2 message to a plain dict for ZMQ publishing (stream "in").
    """
    if frame_fields is None:
        # Built-in binary frame
        if frame_type == 'AudioFrameRaw':
            raw = bytes(ros2_msg.data) if ros2_msg.data else b''
            return {
                'sample_rate': ros2_msg.sample_rate,
                'channels':    ros2_msg.channels,
                'bit_depth':   ros2_msg.sample_width,
                'format':      'PCM',
                'data':        raw,
            }
        elif frame_type == 'ImageFrameRaw':
            raw = bytes(ros2_msg.data) if ros2_msg.data else b''
            return {
                'width':        ros2_msg.width,
                'height':       ros2_msg.height,
                'pixel_format': ros2_msg.encoding,
                'format':       'raw',
                'data':         raw,
            }
        else:
            # Generic: copy all non-header fields
            d = {}
            for field in ros2_msg.get_fields_and_field_types():
                if field == 'header':
                    continue
                val = getattr(ros2_msg, field, None)
                if val is not None:
                    d[field] = val
            return d

    d = {}
    for field_name, ros2_type in frame_fields.items():
        val = getattr(ros2_msg, field_name, None)
        if val is None:
            continue

        if ros2_type.endswith('[]') and not ros2_type.startswith('std_msgs'):
            # Array-of-structs → dynamic-key dict {name: {fields}}
            sub_fields = sub_msgs_def.get(ros2_type[:-2], {})
            result = {}
            for item in val:
                item_name = getattr(item, 'name', None)
                if item_name is not None:
                    item_dict = {}
                    for sf in sub_fields:
                        if sf != 'name' and hasattr(item, sf):
                            item_dict[sf] = getattr(item, sf)
                    result[item_name] = item_dict
            d[field_name] = result
        else:
            d[field_name] = val

    return d
