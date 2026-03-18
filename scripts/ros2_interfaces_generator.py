#!/usr/bin/env python3
"""
ROS2 Interfaces Generator for qtrobot-service-hub-gateway-ros

Reads scripts/api_list.py and generates a complete qtrobot_interfaces ROS2
package (srv/, msg/, CMakeLists.txt, package.xml) in the project root.

Usage:
    python3 scripts/ros2_interfaces_generator.py [--output-dir <path>]

Re-run any time api_list.py is updated to regenerate the interfaces.

---- api_list.py "returns" types ----------------------------------------
  {"type": "bool"}        → bool result
  {"type": "float64"}     → float64 result 0.0
  {"type": "string"}      → string result ""
  {"type": "string[]"}    → string[] result
  {"type": "json"}        → string result ""  (JSON-encoded payload)
  {"type": "msg_array",   → <item_msg>[] result  (also creates item_msg.msg)
   "item_msg": "Name",
   "item_fields": {...}}

---- api_list.py stream frame types -------------------------------------
  frame_type + frame_fields (flat)       → <FrameType>.msg with those fields
  frame_type + frame_fields (array ref)  → <FrameType>.msg + sub-msg from sub_msgs
  frame_type only (no frame_fields)      → built-in definition used
"""

import os
import sys
import shutil
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from api_list import API

# ---------------------------------------------------------------------------
# Type helpers
# ---------------------------------------------------------------------------

# Python "type" string from params section → ROS2 request field type
PARAM_TYPE_MAP = {
    "str":   "string",
    "float": "float32",
    "int":   "int32",
    "bool":  "bool",
    "list":  "string",   # JSON-encoded
    "dict":  "string",   # JSON-encoded
}

# ROS2 type → "empty / not-set" default string for optional param fields
PARAM_EMPTY_DEFAULT = {
    "string":  '""',
    "float32": "0.0",
    "int32":   "0",
    "bool":    "false",
}

# "returns.type" → (ros2_field_decl)
#   None means the type is handled specially (msg_array)
RETURN_TYPE_MAP = {
    "bool":     "bool result",
    "float64":  "float64 result 0.0",
    "string":   'string result ""',
    "string[]": "string[] result",
    "json":     'string result ""',   # JSON-encoded payload
}

# Built-in msg definitions for binary (non-dict) frame types
BUILTIN_FRAME_DEFS: dict[str, str] = {
    "AudioFrameRaw": (
        "std_msgs/Header header\n"
        "uint32 sample_rate\n"
        "uint8 channels\n"
        "uint8 sample_width\n"
        "uint8[] data\n"
    ),
    "ImageFrameRaw": (
        "std_msgs/Header header\n"
        "uint32 width\n"
        "uint32 height\n"
        "string encoding\n"
        "uint8[] data\n"
    ),
}


# ---------------------------------------------------------------------------
# Name helpers
# ---------------------------------------------------------------------------

def path_to_classname(api_path: str) -> str:
    """
    /face/emotion/list          → FaceEmotionList
    /gesture/record/start       → GestureRecordStart
    /media/audio/bg/stream:i    → MediaAudioBgStream   (strips :i/:o)
    """
    clean = api_path.lstrip("/").split(":")[0]
    parts = []
    for segment in clean.split("/"):
        for word in segment.split("_"):
            if word:
                parts.append(word.capitalize())
    return "".join(parts)


def default_for_param(ros_type: str, api_default) -> str:
    """Return the ROS2 field default literal for an optional param."""
    if api_default is None:
        return PARAM_EMPTY_DEFAULT.get(ros_type, '""')
    if ros_type == "string":
        return f'"{api_default}"'
    if ros_type == "bool":
        return "true" if api_default else "false"
    if ros_type == "float32":
        return str(float(api_default))
    if ros_type == "int32":
        return str(int(api_default))
    return PARAM_EMPTY_DEFAULT.get(ros_type, '""')


# ---------------------------------------------------------------------------
# .srv generator
# ---------------------------------------------------------------------------

def generate_srv(params: dict, returns: dict, sub_msgs: dict) -> str:
    """
    Generate .srv content.

    Request section: typed fields derived from params.
    Response section: typed fields derived from returns.
    sub_msgs: accumulated dict updated in-place when returns.type == msg_array.
    """
    # ---- request section --------------------------------------------------
    required_lines = []
    optional_lines = []
    for param_name, param_info in sorted(params.items()):
        ros_type = PARAM_TYPE_MAP.get(param_info.get("type", "str"), "string")
        if param_info.get("required", True):
            required_lines.append(f"{ros_type} {param_name}")
        else:
            default_val = default_for_param(ros_type, param_info.get("default"))
            optional_lines.append(f"{ros_type} {param_name} {default_val}")

    request_lines = required_lines + optional_lines
    if not request_lines:
        request_lines = ["# no parameters"]

    # ---- response section -------------------------------------------------
    ret_type = returns.get("type", "bool")
    response_lines = ["bool status"]

    if ret_type in RETURN_TYPE_MAP:
        response_lines.append(RETURN_TYPE_MAP[ret_type])
    elif ret_type == "msg_array":
        item_msg = returns["item_msg"]
        # Register sub-msg (will be written as a .msg file)
        sub_msgs[item_msg] = returns["item_fields"]
        response_lines.append(f"qtrobot_interfaces/{item_msg}[] result")
    else:
        # Unknown type — fall back to JSON string
        response_lines.append('string result ""')

    lines = request_lines + ["---"] + response_lines
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# .msg generator
# ---------------------------------------------------------------------------

def generate_msg_from_fields(frame_fields: dict) -> str:
    """
    Generate a .msg file from a flat field dict  {field_name: ros2_type}.
    Always prepends std_msgs/Header header.
    """
    lines = ["std_msgs/Header header"]
    for field_name, ros2_type in frame_fields.items():
        # Handle array-of-sub-msgs references: "MotorJointState[]"
        # These are already fully-qualified names, emit as-is.
        if ros2_type.endswith("[]") and not ros2_type.startswith("std_msgs"):
            # Local package sub-msg array
            base = ros2_type[:-2]
            lines.append(f"qtrobot_interfaces/{base}[] {field_name}")
        else:
            lines.append(f"{ros2_type} {field_name}")
    return "\n".join(lines) + "\n"


def generate_sub_msg_from_fields(fields: dict) -> str:
    """Generate a plain .msg file for a sub-message (no Header)."""
    lines = []
    for field_name, ros2_type in fields.items():
        lines.append(f"{ros2_type} {field_name}")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# CMakeLists.txt / package.xml generators
# ---------------------------------------------------------------------------

def generate_cmake(srv_names: list[str], msg_names: list[str]) -> str:
    srv_entries = "\n".join(f'  "srv/{n}.srv"' for n in sorted(srv_names))
    msg_entries = "\n".join(f'  "msg/{n}.msg"' for n in sorted(msg_names))

    lines = [
        "cmake_minimum_required(VERSION 3.8)",
        "project(qtrobot_interfaces)",
        "",
        "if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES \"Clang\")",
        "  add_compile_options(-Wall -Wextra -Wpedantic)",
        "endif()",
        "",
        "# find dependencies",
        "find_package(ament_cmake REQUIRED)",
        "find_package(rosidl_default_generators REQUIRED)",
        "find_package(std_msgs REQUIRED)",
        "",
        "set(msg_files",
        msg_entries,
        ")",
        "",
        "set(srv_files",
        srv_entries,
        ")",
        "",
        "rosidl_generate_interfaces(${PROJECT_NAME}",
        "  ${msg_files}",
        "  ${srv_files}",
        "  DEPENDENCIES std_msgs",
        ")",
        "",
        "if(BUILD_TESTING)",
        "  find_package(ament_lint_auto REQUIRED)",
        "  set(ament_cmake_copyright_FOUND TRUE)",
        "  set(ament_cmake_cpplint_FOUND TRUE)",
        "  ament_lint_auto_find_test_dependencies()",
        "endif()",
        "",
        "ament_package()",
        "",
    ]
    return "\n".join(lines)


def generate_package_xml() -> str:
    return (
        '<?xml version="1.0"?>\n'
        '<?xml-model href="http://download.ros.org/schema/package_format3.xsd"'
        ' schematypens="http://www.w3.org/2001/XMLSchema"?>\n'
        '<package format="3">\n'
        '  <name>qtrobot_interfaces</name>\n'
        '  <version>1.0.0</version>\n'
        '  <description>QTrobot ROS2 interface messages and services'
        ' (auto-generated from api_list.py)</description>\n'
        '  <maintainer email="support@luxai.com">LuxAI</maintainer>\n'
        '  <license>LuxAI S.A.</license>\n'
        '\n'
        '  <buildtool_depend>ament_cmake</buildtool_depend>\n'
        '  <buildtool_depend>rosidl_default_generators</buildtool_depend>\n'
        '  <exec_depend>rosidl_default_runtime</exec_depend>\n'
        '  <member_of_group>rosidl_interface_packages</member_of_group>\n'
        '\n'
        '  <test_depend>ament_lint_auto</test_depend>\n'
        '  <test_depend>ament_lint_common</test_depend>\n'
        '\n'
        '  <export>\n'
        '    <build_type>ament_cmake</build_type>\n'
        '  </export>\n'
        '</package>\n'
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_out = os.path.join(project_root, "qtrobot_interfaces")
    parser.add_argument("--output-dir", default=default_out, metavar="PATH",
                        help=f"Destination package directory (default: {default_out})")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print plan without writing files")
    args = parser.parse_args()

    output_dir = args.output_dir
    srv_dir = os.path.join(output_dir, "srv")
    msg_dir = os.path.join(output_dir, "msg")

    # Collected outputs
    srv_files: dict[str, str] = {}          # classname  → content
    msg_files: dict[str, str] = {}          # frame/msg name → content
    shared_sub_msgs: dict[str, dict] = {}   # sub-msg name → field dict
                                            # (populated by generate_srv for msg_array returns)

    # ------------------------------------------------------------------
    # RPC → .srv files
    # ------------------------------------------------------------------
    print("RPC endpoints → srv/")
    for api_path, info in API["rpc"].items():
        class_name = path_to_classname(api_path)
        returns = info.get("returns", {"type": "bool"})
        content = generate_srv(info.get("params", {}), returns, shared_sub_msgs)
        srv_files[class_name] = content
        ret_label = returns.get("type", "?")
        if ret_label == "msg_array":
            ret_label = f"msg_array({returns['item_msg']}[])"
        print(f"  {api_path:52s} → {class_name}.srv  [{ret_label}]")

    # ------------------------------------------------------------------
    # Sub-msgs from RPC msg_array returns  (e.g. MotorInfo, TtsVoiceInfo)
    # ------------------------------------------------------------------
    if shared_sub_msgs:
        print("\nSub-messages from RPC msg_array returns → msg/")
        for msg_name, fields in shared_sub_msgs.items():
            content = generate_sub_msg_from_fields(fields)
            msg_files[msg_name] = content
            print(f"  {msg_name}.msg  ({', '.join(fields.keys())})")

    # ------------------------------------------------------------------
    # Streams → .msg files
    # ------------------------------------------------------------------
    print("\nStream frames → msg/")
    for api_path, info in API["stream"].items():
        frame_type = info["frame_type"]
        frame_fields = info.get("frame_fields")
        sub_msgs = info.get("sub_msgs", {})

        if frame_fields:
            # Generate sub-msgs first (for array-of-structs frames)
            for sub_name, sub_fields in sub_msgs.items():
                if sub_name not in msg_files:
                    msg_files[sub_name] = generate_sub_msg_from_fields(sub_fields)
                    print(f"  {sub_name}.msg  (sub-msg for {frame_type})")

            # Generate the frame msg itself
            if frame_type not in msg_files:
                msg_files[frame_type] = generate_msg_from_fields(frame_fields)
                print(f"  {frame_type}.msg  ← {api_path}")
        else:
            # Use built-in definition
            if frame_type not in msg_files:
                if frame_type in BUILTIN_FRAME_DEFS:
                    msg_files[frame_type] = BUILTIN_FRAME_DEFS[frame_type]
                    print(f"  {frame_type}.msg  (built-in, used by {api_path})")
                else:
                    # Unknown type — emit a minimal placeholder
                    msg_files[frame_type] = "std_msgs/Header header\nstring data\n"
                    print(f"  {frame_type}.msg  (UNKNOWN built-in, placeholder)")

    # ------------------------------------------------------------------
    # Write files
    # ------------------------------------------------------------------
    if args.dry_run:
        print(f"\n[dry-run] Would write to: {output_dir}")
        print(f"  {len(srv_files)} srv files, {len(msg_files)} msg files")
        return

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        print(f"\nRemoved existing: {output_dir}")
    os.makedirs(srv_dir)
    os.makedirs(msg_dir)

    for name, content in srv_files.items():
        with open(os.path.join(srv_dir, f"{name}.srv"), "w") as f:
            f.write(content)

    for name, content in msg_files.items():
        with open(os.path.join(msg_dir, f"{name}.msg"), "w") as f:
            f.write(content)

    with open(os.path.join(output_dir, "CMakeLists.txt"), "w") as f:
        f.write(generate_cmake(list(srv_files.keys()), list(msg_files.keys())))

    with open(os.path.join(output_dir, "package.xml"), "w") as f:
        f.write(generate_package_xml())

    print(f"\nGenerated:")
    print(f"  {len(srv_files):3d} srv files  → {srv_dir}/")
    print(f"  {len(msg_files):3d} msg files  → {msg_dir}/")
    print(f"        CMakeLists.txt → {output_dir}/")
    print(f"        package.xml    → {output_dir}/")
    print(f"\nDone. Package: {output_dir}")


if __name__ == "__main__":
    main()
