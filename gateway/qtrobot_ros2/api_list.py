# ============================================================================
# QTrobot Service Hub API definition
#
# Derived from the qtrobot-service-hub node.cpp implementations.
#
# "rpc" entries — ZMQ request/reply services.
#   Each entry has:
#     params   : request parameters (name → {type, required, default?})
#     returns  : response payload type (used by the ROS2 interface generator)
#     transports: transport configuration
#
# "stream" entries — ZMQ pub/sub data streams.
#   Each entry has:
#     direction    : "in" (gateway→hub) or "out" (hub→gateway)
#     frame_type   : name of the ROS2 msg to generate for this stream
#     frame_fields : flat dict {field_name: ros2_type} for the msg body
#     sub_msgs     : optional nested sub-message definitions
#                    {MsgName: {field_name: ros2_type, ...}}
#                    Required when frame_fields references a MsgName[] array.
#     transports   : transport configuration
#
# ---- returns format --------------------------------------------------------
#   {"type": "bool"}          → bool result
#   {"type": "float64"}       → float64 result 0.0
#   {"type": "string"}        → string result ""
#   {"type": "string[]"}      → string[] result
#   {"type": "json"}          → string result "" (JSON-encoded complex value)
#   {"type": "msg_array",     → <item_msg>[] result  (also generates item_msg.msg)
#    "item_msg":  "MsgName",
#    "item_fields": {field: ros2_type, ...}}
# ============================================================================

API = {
    "rpc": {

      # ---- face -------------------------------------------------------
      "/face/emotion/list": {
        "params": {},
        "returns": {"type": "string[]"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50520"}
        }
      },
      "/face/emotion/show": {
        "params": {
          "emotion": {"required": True,  "type": "str"},
          "speed":   {"required": False, "type": "float", "default": None}
        },
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50520"}
        }
      },
      "/face/emotion/stop": {
        "params": {},
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50520"}
        }
      },
      "/face/look": {
        "params": {
          "l_eye":    {"required": True,  "type": "list"},
          "r_eye":    {"required": True,  "type": "list"},
          "duration": {"required": False, "type": "float", "default": 0}
        },
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50520"}
        }
      },

      # ---- gesture ----------------------------------------------------
      "/gesture/cancel": {
        "params": {},
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50540"}
        }
      },
      "/gesture/file/list": {
        "params": {},
        "returns": {"type": "string[]"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50540"}
        }
      },
      "/gesture/file/play": {
        "params": {
          "gesture":      {"required": True,  "type": "str"},
          "speed_factor": {"required": False, "type": "float", "default": 1}
        },
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50540"}
        }
      },
      "/gesture/play": {
        "params": {
          "keyframes":    {"required": True,  "type": "dict"},
          "resample":     {"required": False, "type": "bool",  "default": True},
          "rate_hz":      {"required": False, "type": "float", "default": 100},
          "speed_factor": {"required": False, "type": "float", "default": 1}
        },
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50540"}
        }
      },
      "/gesture/record/start": {
        "params": {
          "motors":              {"required": True,  "type": "list"},
          "delay_start_ms":      {"required": False, "type": "int",   "default": 0},
          "keyframe_max_gap_us": {"required": False, "type": "int",   "default": 100000},
          "keyframe_pos_eps":    {"required": False, "type": "float", "default": 0.75},
          "refine_keyframe":     {"required": False, "type": "bool",  "default": True},
          "release_motors":      {"required": False, "type": "bool",  "default": False},
          "timeout_ms":          {"required": False, "type": "int",   "default": 60000}
        },
        # Returns recorded trajectory: {meta:{time_unit,position_unit,joints[]},
        #                               points:[{time_us,joints:{name:{position}}}]}
        "returns": {"type": "json"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50540"}
        }
      },
      "/gesture/record/stop": {
        "params": {},
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50540"}
        }
      },
      "/gesture/record/store": {
        "params": {
          "gesture": {"required": True, "type": "str"}
        },
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50540"}
        }
      },

      # ---- media / audio / fg -----------------------------------------
      "/media/audio/fg/file/cancel": {
        "params": {},
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50510"}
        }
      },
      "/media/audio/fg/file/pause": {
        "params": {},
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50510"}
        }
      },
      "/media/audio/fg/file/play": {
        "params": {
          "uri": {"required": True, "type": "str"}
        },
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50510"}
        }
      },
      "/media/audio/fg/file/resume": {
        "params": {},
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50510"}
        }
      },
      "/media/audio/fg/stream/cancel": {
        "params": {},
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50510"}
        }
      },
      "/media/audio/fg/stream/pause": {
        "params": {},
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50510"}
        }
      },
      "/media/audio/fg/stream/resume": {
        "params": {},
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50510"}
        }
      },
      "/media/audio/fg/volume/get": {
        "params": {},
        "returns": {"type": "float64"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50510"}
        }
      },
      "/media/audio/fg/volume/set": {
        "params": {
          "value": {"required": True, "type": "float"}
        },
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50510"}
        }
      },

      # ---- media / audio / bg -----------------------------------------
      "/media/audio/bg/file/cancel": {
        "params": {},
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50510"}
        }
      },
      "/media/audio/bg/file/pause": {
        "params": {},
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50510"}
        }
      },
      "/media/audio/bg/file/play": {
        "params": {
          "uri": {"required": True, "type": "str"}
        },
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50510"}
        }
      },
      "/media/audio/bg/file/resume": {
        "params": {},
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50510"}
        }
      },
      "/media/audio/bg/stream/cancel": {
        "params": {},
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50510"}
        }
      },
      "/media/audio/bg/stream/pause": {
        "params": {},
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50510"}
        }
      },
      "/media/audio/bg/stream/resume": {
        "params": {},
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50510"}
        }
      },
      "/media/audio/bg/volume/get": {
        "params": {},
        "returns": {"type": "float64"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50510"}
        }
      },
      "/media/audio/bg/volume/set": {
        "params": {
          "value": {"required": True, "type": "float"}
        },
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50510"}
        }
      },

      # ---- media / video / fg -----------------------------------------
      "/media/video/fg/file/cancel": {
        "params": {},
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50510"}
        }
      },
      "/media/video/fg/file/pause": {
        "params": {},
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50510"}
        }
      },
      "/media/video/fg/file/play": {
        "params": {
          "uri":        {"required": True,  "type": "str"},
          "speed":      {"required": False, "type": "float", "default": 1},
          "with_audio": {"required": False, "type": "bool",  "default": False}
        },
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50510"}
        }
      },
      "/media/video/fg/file/resume": {
        "params": {},
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50510"}
        }
      },
      "/media/video/fg/set_alpha": {
        "params": {
          "value": {"required": True, "type": "float"}
        },
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50510"}
        }
      },
      "/media/video/fg/stream/cancel": {
        "params": {},
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50510"}
        }
      },
      "/media/video/fg/stream/pause": {
        "params": {},
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50510"}
        }
      },
      "/media/video/fg/stream/resume": {
        "params": {},
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50510"}
        }
      },

      # ---- media / video / bg -----------------------------------------
      "/media/video/bg/file/cancel": {
        "params": {},
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50510"}
        }
      },
      "/media/video/bg/file/pause": {
        "params": {},
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50510"}
        }
      },
      "/media/video/bg/file/play": {
        "params": {
          "uri":        {"required": True,  "type": "str"},
          "speed":      {"required": False, "type": "float", "default": 1},
          "with_audio": {"required": False, "type": "bool",  "default": False}
        },
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50510"}
        }
      },
      "/media/video/bg/file/resume": {
        "params": {},
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50510"}
        }
      },
      "/media/video/bg/stream/cancel": {
        "params": {},
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50510"}
        }
      },
      "/media/video/bg/stream/pause": {
        "params": {},
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50510"}
        }
      },
      "/media/video/bg/stream/resume": {
        "params": {},
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50510"}
        }
      },

      # ---- microphone -------------------------------------------------
      "/microphone/int/tunning/get": {
        "params": {},
        # Returns dict of all readable respeaker parameters: {param_name: float_value}
        # Params include: AECFREEZEONOFF, AECNORM, AECPATHCHANGE, RT60, HPFONOFF,
        # RT60ONOFF, AECSILENCELEVEL, AECSILENCEMODE, AGCONOFF, AGCMAXGAIN,
        # AGCDESIREDLEVEL, AGCGAIN, AGCTIME, CNIONOFF, FREEZEONOFF, STATNOISEONOFF,
        # GAMMA_NS, MIN_NS, NONSTATNOISEONOFF, GAMMA_NN, MIN_NN, ECHOONOFF,
        # GAMMA_E, GAMMA_ETAIL, GAMMA_ENL, NLATTENONOFF, NLAEC_MODE,
        # SPEECHDETECTED, FSBUPDATED, FSBPATHCHANGE, TRANSIENTONOFF, VOICEACTIVITY,
        # STATNOISEONOFF_SR, NONSTATNOISEONOFF_SR, GAMMA_NS_SR, GAMMA_NN_SR,
        # MIN_NS_SR, MIN_NN_SR, GAMMAVAD_SR, DOAANGLE
        "returns": {"type": "json"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50550"}
        }
      },
      "/microphone/int/tunning/set": {
        "params": {
          "name":  {"required": True, "type": "str"},
          "value": {"required": True, "type": "float"}
        },
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50550"}
        }
      },

      # ---- motor ------------------------------------------------------
      "/motor/calib/all": {
        "params": {},
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50540"}
        }
      },
      "/motor/calib/set": {
        "params": {
          "motor":               {"required": True,  "type": "str"},
          "offset":              {"required": False, "type": "float", "default": None},
          "overload_threshold":  {"required": False, "type": "int",   "default": None},
          "store":               {"required": False, "type": "bool",  "default": False},
          "velocity_max":        {"required": False, "type": "int",   "default": None}
        },
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50540"}
        }
      },
      "/motor/list": {
        "params": {},
        # Returns array of motor descriptors; dynamic keys = motor names.
        # Each motor: {part, position_min, position_max, position_home,
        #              velocity_max, calibration_offset, overload_threshold}
        "returns": {
          "type": "msg_array",
          "item_msg": "MotorInfo",
          "item_fields": {
            "name":                "string",
            "part":                "string",
            "position_min":        "float64",
            "position_max":        "float64",
            "position_home":       "float64",
            "velocity_max":        "float64",
            "calibration_offset":  "float64",
            "overload_threshold":  "int32"
          }
        },
        "transports": {
          "zmq": {"endpoint": "tcp://*:50540"}
        }
      },
      "/motor/move/home": {
        "params": {
          "motor": {"required": True, "type": "str"}
        },
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50540"}
        }
      },
      "/motor/move/home/all": {
        "params": {},
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50540"}
        }
      },
      "/motor/off": {
        "params": {
          "motor": {"required": True, "type": "str"}
        },
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50540"}
        }
      },
      "/motor/off/all": {
        "params": {},
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50540"}
        }
      },
      "/motor/on": {
        "params": {
          "motor": {"required": True, "type": "str"}
        },
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50540"}
        }
      },
      "/motor/on/all": {
        "params": {},
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50540"}
        }
      },
      "/motor/velocity/set": {
        "params": {
          "motor":    {"required": True, "type": "str"},
          "velocity": {"required": True, "type": "int"}
        },
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50540"}
        }
      },

      # ---- speaker ----------------------------------------------------
      "/speaker/volume/get": {
        "params": {},
        "returns": {"type": "float64"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50510"}
        }
      },
      "/speaker/volume/mute": {
        "params": {},
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50510"}
        }
      },
      "/speaker/volume/set": {
        "params": {
          "value": {"required": True, "type": "float"}
        },
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50510"}
        }
      },
      "/speaker/volume/unmute": {
        "params": {},
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50510"}
        }
      },

      # ---- tts --------------------------------------------------------
      "/tts/default_engine/get": {
        "params": {},
        "returns": {"type": "string"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50530"}
        }
      },
      "/tts/default_engine/set": {
        "params": {
          "engine": {"required": True, "type": "str"}
        },
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50530"}
        }
      },
      "/tts/engine/cancel": {
        "params": {
          "engine": {"required": False, "type": "str", "default": None}
        },
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50530"}
        }
      },
      "/tts/engine/configure/get": {
        "params": {
          "engine": {"required": False, "type": "str", "default": None}
        },
        # Engine-specific configuration dict; structure varies per engine
        "returns": {"type": "json"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50530"}
        }
      },
      "/tts/engine/configure/set": {
        "params": {
          "config": {"required": True,  "type": "dict"},
          "engine": {"required": False, "type": "str", "default": None}
        },
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50530"}
        }
      },
      "/tts/engine/languages/get": {
        "params": {
          "engine": {"required": False, "type": "str", "default": None}
        },
        "returns": {"type": "string[]"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50530"}
        }
      },
      "/tts/engine/say/ssml": {
        "params": {
          "ssml":   {"required": True,  "type": "str"},
          "engine": {"required": False, "type": "str", "default": None}
        },
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50530"}
        }
      },
      "/tts/engine/say/text": {
        "params": {
          "text":   {"required": True,  "type": "str"},
          "engine": {"required": False, "type": "str",   "default": None},
          "lang":   {"required": False, "type": "str",   "default": None},
          "pitch":  {"required": False, "type": "float", "default": None},
          "rate":   {"required": False, "type": "float", "default": None},
          "style":  {"required": False, "type": "str",   "default": None},
          "voice":  {"required": False, "type": "str",   "default": None},
          "volume": {"required": False, "type": "float", "default": None}
        },
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50530"}
        }
      },
      "/tts/engine/supports/ssml": {
        "params": {
          "engine": {"required": False, "type": "str", "default": None}
        },
        "returns": {"type": "bool"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50530"}
        }
      },
      "/tts/engine/voices/get": {
        "params": {
          "engine": {"required": False, "type": "str", "default": None}
        },
        # Returns list of voice descriptors with known fixed fields
        "returns": {
          "type": "msg_array",
          "item_msg": "TtsVoiceInfo",
          "item_fields": {
            "id":              "string",
            "lang":            "string",
            "lang_name":       "string",
            "gender":          "string",
            "is_child":        "bool",
            "is_multilingual": "bool",
            "display_name":    "string"
          }
        },
        "transports": {
          "zmq": {"endpoint": "tcp://*:50530"}
        }
      },
      "/tts/engines/list": {
        "params": {},
        "returns": {"type": "string[]"},
        "transports": {
          "zmq": {"endpoint": "tcp://*:50530"}
        }
      }

    },  # end rpc

    # =========================================================================
    "stream": {

      # ---- gesture progress -----------------------------------------------
      "/gesture/progress/stream:o": {
        "direction": "out",
        # flat DictFrame: percentage (0-100) and elapsed time in microseconds
        "frame_type": "GestureProgressFrame",
        "frame_fields": {
          "percentage": "float64",
          "time_us":    "int64"
        },
        "transports": {
          "zmq": {
            "delivery": "latest",
            "endpoint": "tcp://*:50541",
            "queue_size": 2
          }
        }
      },

      # ---- audio streams (binary, not dict-based) -------------------------
      "/media/audio/bg/stream:i": {
        "direction": "in",
        "frame_type": "AudioFrameRaw",
        "transports": {
          "zmq": {
            "delivery": "reliable",
            "endpoint": "tcp://*:50512",
            "queue_size": 10
          }
        }
      },
      "/media/audio/fg/stream:i": {
        "direction": "in",
        "frame_type": "AudioFrameRaw",
        "transports": {
          "zmq": {
            "delivery": "reliable",
            "endpoint": "tcp://*:50511",
            "queue_size": 10
          }
        }
      },

      # ---- video streams (binary, not dict-based) -------------------------
      "/media/video/bg/stream:i": {
        "direction": "in",
        "frame_type": "ImageFrameRaw",
        "transports": {
          "zmq": {
            "delivery": "latest",
            "endpoint": "tcp://*:50514",
            "queue_size": 0
          }
        }
      },
      "/media/video/fg/stream:i": {
        "direction": "in",
        "frame_type": "ImageFrameRaw",
        "transports": {
          "zmq": {
            "delivery": "latest",
            "endpoint": "tcp://*:50513",
            "queue_size": 0
          }
        }
      },

      # ---- microphone streams (binary audio + event dict) -----------------
      "/mic/ext/audio/ch0/stream:o": {
        "direction": "out",
        "frame_type": "AudioFrameRaw",
        "transports": {
          "zmq": {
            "delivery": "reliable",
            "endpoint": "tcp://*:50557",
            "queue_size": 10
          }
        }
      },
      "/mic/int/audio/ch0/stream:o": {
        "direction": "out",
        "frame_type": "AudioFrameRaw",
        "transports": {
          "zmq": {
            "delivery": "reliable",
            "endpoint": "tcp://*:50551",
            "queue_size": 10
          }
        }
      },
      "/mic/int/audio/ch1/stream:o": {
        "direction": "out",
        "frame_type": "AudioFrameRaw",
        "transports": {
          "zmq": {
            "delivery": "reliable",
            "endpoint": "tcp://*:50552",
            "queue_size": 10
          }
        }
      },
      "/mic/int/audio/ch2/stream:o": {
        "direction": "out",
        "frame_type": "AudioFrameRaw",
        "transports": {
          "zmq": {
            "delivery": "reliable",
            "endpoint": "tcp://*:50553",
            "queue_size": 10
          }
        }
      },
      "/mic/int/audio/ch3/stream:o": {
        "direction": "out",
        "frame_type": "AudioFrameRaw",
        "transports": {
          "zmq": {
            "delivery": "reliable",
            "endpoint": "tcp://*:50554",
            "queue_size": 10
          }
        }
      },
      "/mic/int/audio/ch4/stream:o": {
        "direction": "out",
        "frame_type": "AudioFrameRaw",
        "transports": {
          "zmq": {
            "delivery": "reliable",
            "endpoint": "tcp://*:50555",
            "queue_size": 10
          }
        }
      },
      "/mic/int/event/stream:o": {
        "direction": "out",
        # DictFrame: voice-activity detection result + direction-of-arrival angle
        "frame_type": "MicEventFrame",
        "frame_fields": {
          "activity":  "bool",
          "direction": "int32"
        },
        "transports": {
          "zmq": {
            "delivery": "latest",
            "endpoint": "tcp://*:50556",
            "queue_size": 2
          }
        }
      },

      # ---- motor streams --------------------------------------------------
      "/motor/joints/command/stream:i": {
        "direction": "in",
        # DictFrame: {motor_name: {position, velocity}} for each commanded joint
        # Represented as array of MotorJointCommand sub-messages (dynamic keys → array)
        "frame_type": "MotorJointsCommandFrame",
        "frame_fields": {
          "joints": "MotorJointCommand[]"
        },
        "sub_msgs": {
          "MotorJointCommand": {
            "name":     "string",
            "position": "float64",
            "velocity": "float64"
          }
        },
        "transports": {
          "zmq": {
            "delivery": "reliable",
            "endpoint": "tcp://*:50542",
            "queue_size": 10
          }
        }
      },
      "/motor/joints/error/stream:o": {
        "direction": "out",
        # DictFrame: {motor_name: {error_flags}} for motors with active errors.
        # All flag fields default to false; only set when the error is active.
        "frame_type": "MotorJointsErrorFrame",
        "frame_fields": {
          "joints": "MotorJointError[]"
        },
        "sub_msgs": {
          "MotorJointError": {
            "name":               "string",
            "overload_limit":     "bool",
            "voltage_limit":      "bool",
            "temperature_limit":  "bool",
            "sensor_failure":     "bool"
          }
        },
        "transports": {
          "zmq": {
            "delivery": "latest",
            "endpoint": "tcp://*:50541",
            "queue_size": 2
          }
        }
      },
      "/motor/joints/state/stream:o": {
        "direction": "out",
        # DictFrame: {motor_name: {position, velocity, effort, voltage, temperature}}
        # Published at feedback_freq_hz (default 10 Hz).
        # position/velocity in degrees / deg·s⁻¹; effort in Nm; voltage in V; temp in °C
        "frame_type": "MotorJointsStateFrame",
        "frame_fields": {
          "joints": "MotorJointState[]"
        },
        "sub_msgs": {
          "MotorJointState": {
            "name":        "string",
            "position":    "float64",
            "velocity":    "float64",
            "effort":      "float64",
            "voltage":     "float64",
            "temperature": "float64"
          }
        },
        "transports": {
          "zmq": {
            "delivery": "latest",
            "endpoint": "tcp://*:50541",
            "queue_size": 2
          }
        }
      }

    }  # end stream
}
