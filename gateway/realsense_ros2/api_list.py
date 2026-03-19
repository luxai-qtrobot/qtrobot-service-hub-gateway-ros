# ============================================================================
# QTrobot RealSense Camera Driver API definition
#
# Derived from qtrobot-realsense-driver node implementation.
#
# Default ZMQ base port: 50750
#   rpcPort         = base + 0  (50750)
#   rgbStreamPort   = base + 1  (50751)
#   depthStreamPort = base + 2  (50752)
#   imuStreamPort   = base + 3  (50753)
# ============================================================================

API = {
    "rpc": {

        # ---- camera intrinsics / scale ----------------------------------
        "/camera/color/intrinsics": {
            "params": {},
            # Returns CameraIntrinsics: {width, fx, fy, ppx, ppy, coef[5], model}
            # Note: driver has a bug — v["width"] is assigned twice so height is missing.
            "returns": {
                "type": "msg",
                "item_msg": "CameraIntrinsics",
                "item_fields": {
                    "width": "int32",
                    "fx":    "float64",
                    "fy":    "float64",
                    "ppx":   "float64",
                    "ppy":   "float64",
                    "coef":  "float64[]",
                    "model": "string"
                }
            },
            "transports": {
                "zmq": {"endpoint": "tcp://*:50750"}
            }
        },
        "/camera/depth/intrinsics": {
            "params": {},
            # Returns CameraIntrinsics: {width, fx, fy, ppx, ppy, coef[5], model}
            "returns": {
                "type": "msg",
                "item_msg": "CameraIntrinsics",
                "item_fields": {
                    "width": "int32",
                    "fx":    "float64",
                    "fy":    "float64",
                    "ppx":   "float64",
                    "ppy":   "float64",
                    "coef":  "float64[]",
                    "model": "string"
                }
            },
            "transports": {
                "zmq": {"endpoint": "tcp://*:50750"}
            }
        },
        "/camera/depth/scale": {
            "params": {},
            # Returns depth scale factor (meters per depth unit)
            "returns": {"type": "float64"},
            "transports": {
                "zmq": {"endpoint": "tcp://*:50750"}
            }
        },

    },  # end rpc

    # =========================================================================
    "stream": {

        # ---- RGB image ------------------------------------------------------
        "/camera/color/image": {
            "direction": "out",
            "frame_type": "ImageFrameRaw",
            "frame_fields": None,
            "transports": {
                "zmq": {
                    "endpoint": "tcp://*:50751",
                    "delivery": "latest",
                    "queue_size": 1
                }
            }
        },

        # ---- depth images ---------------------------------------------------
        "/camera/depth/image": {
            "direction": "out",
            "frame_type": "ImageFrameRaw",
            "frame_fields": None,
            "transports": {
                "zmq": {
                    "endpoint": "tcp://*:50752",
                    "delivery": "latest",
                    "queue_size": 1
                }
            }
        },
        "/camera/depth/aligned/image": {
            "direction": "out",
            "frame_type": "ImageFrameRaw",
            "frame_fields": None,
            "transports": {
                "zmq": {
                    "endpoint": "tcp://*:50752",
                    "delivery": "latest",
                    "queue_size": 1
                }
            }
        },
        "/camera/depth/color/image": {
            "direction": "out",
            "frame_type": "ImageFrameRaw",
            "frame_fields": None,
            "transports": {
                "zmq": {
                    "endpoint": "tcp://*:50752",
                    "delivery": "latest",
                    "queue_size": 1
                }
            }
        },

        # ---- IMU streams ----------------------------------------------------
        "/camera/gyro": {
            "direction": "out",
            # ListFrame: [x, y, z] in rad/s
            "frame_type": "ImuFrame",
            "frame_fields": None,
            "transports": {
                "zmq": {
                    "endpoint": "tcp://*:50753",
                    "delivery": "latest",
                    "queue_size": 1
                }
            }
        },
        "/camera/acceleration": {
            "direction": "out",
            # ListFrame: [x, y, z] in m/s²
            "frame_type": "ImuFrame",
            "frame_fields": None,
            "transports": {
                "zmq": {
                    "endpoint": "tcp://*:50753",
                    "delivery": "latest",
                    "queue_size": 1
                }
            }
        },

    }  # end stream
}
