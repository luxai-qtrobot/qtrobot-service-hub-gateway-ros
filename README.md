# QTrobot ROS2 Gateway

A ROS2 gateway that bridges the **LuxAI QTrobot v3** service hub to standard ROS2 services and topics.
The gateway translates between the robot's internal ZMQ/magpie transport and the ROS2 interface layer, exposing all robot capabilities as ROS2 services and topics that any ROS2 node can consume.

---

## Architecture

```
 Your ROS2 Nodes
       │
  ROS2 services / topics  (qtrobot_interfaces)
       │
 qtrobot_ros2_gateway     (this repo)
       │  ZMQ / magpie
 QTrobot service hub      (running on the robot)
```

- **`qtrobot_interfaces`** — ROS2 message and service definitions (built via colcon).
- **`qtrobot_ros2_gateway`** — Plain Python package that runs as a ROS2 node; no colcon build required.

---

## Prerequisites

| Requirement | Version |
|---|---|
| ROS2 | Jazzy |
| Python | 3.12 |
| Network access to QTrobot | TCP ports 505xx |

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/luxai-qtrobot/qtrobot-service-hub-gateway-ros.git
cd qtrobot-service-hub-gateway-ros
```

### 2. Create a Python virtual environment and install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Set up a ROS2 workspace and build the interfaces package

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws

# Symlink only the interfaces package — the gateway does not need colcon
ln -s /path/to/qtrobot-service-hub-gateway-ros/qtrobot_interfaces src/qtrobot_interfaces

source /opt/ros/jazzy/setup.bash
colcon build --packages-select qtrobot_interfaces
```

---

## Running the Gateway

Every new terminal session requires the following setup:

```bash
# 1. Activate the virtual environment
source /path/to/qtrobot-service-hub-gateway-ros/.venv/bin/activate

# 2. Source ROS2 and the built interfaces
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash

# 3. Run the gateway from the repo root
cd /path/to/qtrobot-service-hub-gateway-ros
python -m qtrobot_ros2_gateway.main --ros-args -p robot_ip:=<ROBOT_IP> -r __ns:=/qtrobot
```

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `robot_ip` | string | `127.0.0.1` | IP address of the QTrobot service hub or service hub gateway|
| `rpc_timeout` | float | `30.0` | Service call timeout in seconds |


All examples below assume the `/qtrobot` namespace.

---

## ROS2 Services

All robot capabilities are exposed as ROS2 services. The service name mirrors the robot API path.

### Face

| Service | Description | Key Parameters |
|---|---|---|
| `/qtrobot/face/emotion/list` | List available emotion names | — |
| `/qtrobot/face/emotion/show` | Display an emotion | `emotion` (string, required), `speed` (float, optional) |
| `/qtrobot/face/emotion/stop` | Stop current emotion animation | — |
| `/qtrobot/face/look` | Move eye gaze | `l_eye`, `r_eye` (JSON list, required), `duration` (float) |

### Text-to-Speech

| Service | Description | Key Parameters |
|---|---|---|
| `/qtrobot/tts/engine/say/text` | Speak plain text | `text` (required), `lang`, `voice`, `pitch`, `rate`, `volume`, `style`, `engine` |
| `/qtrobot/tts/engine/say/ssml` | Speak SSML markup | `ssml` (required), `engine` |
| `/qtrobot/tts/engine/cancel` | Cancel ongoing speech | `engine` (optional) |
| `/qtrobot/tts/engines/list` | List available TTS engines | — |
| `/qtrobot/tts/engine/voices/get` | List voices for an engine | `engine` (optional) |
| `/qtrobot/tts/engine/languages/get` | List supported languages | `engine` (optional) |
| `/qtrobot/tts/default_engine/get` | Get current default engine | — |
| `/qtrobot/tts/default_engine/set` | Set default engine | `engine` (required) |
| `/qtrobot/tts/engine/configure/get` | Get engine configuration | `engine` (optional) |
| `/qtrobot/tts/engine/configure/set` | Set engine configuration | `config` (JSON dict, required), `engine` (optional) |
| `/qtrobot/tts/engine/supports/ssml` | Check SSML support | `engine` (optional) |

### Gesture

| Service | Description | Key Parameters |
|---|---|---|
| `/qtrobot/gesture/file/list` | List available gesture files | — |
| `/qtrobot/gesture/file/play` | Play a gesture file | `gesture` (required), `speed_factor` (float) |
| `/qtrobot/gesture/play` | Play a keyframe trajectory | `keyframes` (JSON dict, required), `rate_hz`, `speed_factor`, `resample` |
| `/qtrobot/gesture/cancel` | Cancel current gesture | — |
| `/qtrobot/gesture/record/start` | Start gesture recording | `motors` (JSON list, required), `timeout_ms`, `release_motors`, ... |
| `/qtrobot/gesture/record/stop` | Stop gesture recording | — |
| `/qtrobot/gesture/record/store` | Save recorded gesture to file | `gesture` (required) |

### Motor

| Service | Description | Key Parameters |
|---|---|---|
| `/qtrobot/motor/list` | List motors and their properties | — |
| `/qtrobot/motor/on` | Enable torque on a motor | `motor` (required) |
| `/qtrobot/motor/on/all` | Enable torque on all motors | — |
| `/qtrobot/motor/off` | Disable torque on a motor | `motor` (required) |
| `/qtrobot/motor/off/all` | Disable torque on all motors | — |
| `/qtrobot/motor/move/home` | Move a motor to its home position | `motor` (required) |
| `/qtrobot/motor/move/home/all` | Move all motors to home | — |
| `/qtrobot/motor/velocity/set` | Set motor max velocity | `motor`, `velocity` (required) |
| `/qtrobot/motor/calib/set` | Set motor calibration parameters | `motor` (required), `offset`, `velocity_max`, `overload_threshold`, `store` |
| `/qtrobot/motor/calib/all` | Calibrate all motors | — |

### Media — Audio

| Service | Description | Key Parameters |
|---|---|---|
| `/qtrobot/media/audio/fg/file/play` | Play foreground audio file | `uri` (required) |
| `/qtrobot/media/audio/fg/file/pause` | Pause foreground audio | — |
| `/qtrobot/media/audio/fg/file/resume` | Resume foreground audio | — |
| `/qtrobot/media/audio/fg/file/cancel` | Cancel foreground audio | — |
| `/qtrobot/media/audio/fg/volume/get` | Get foreground audio volume | — |
| `/qtrobot/media/audio/fg/volume/set` | Set foreground audio volume | `value` (0.0–1.0) |
| `/qtrobot/media/audio/fg/stream/pause` | Pause foreground audio stream | — |
| `/qtrobot/media/audio/fg/stream/resume` | Resume foreground audio stream | — |
| `/qtrobot/media/audio/fg/stream/cancel` | Cancel foreground audio stream | — |
| `/qtrobot/media/audio/bg/*` | Background audio — same API as `fg` | — |
| `/qtrobot/speaker/volume/get` | Get speaker volume | — |
| `/qtrobot/speaker/volume/set` | Set speaker volume | `value` (0.0–1.0) |
| `/qtrobot/speaker/volume/mute` | Mute speaker | — |
| `/qtrobot/speaker/volume/unmute` | Unmute speaker | — |

### Media — Video

| Service | Description | Key Parameters |
|---|---|---|
| `/qtrobot/media/video/fg/file/play` | Play foreground video file | `uri` (required), `speed`, `with_audio` |
| `/qtrobot/media/video/fg/file/pause` | Pause foreground video | — |
| `/qtrobot/media/video/fg/file/resume` | Resume foreground video | — |
| `/qtrobot/media/video/fg/file/cancel` | Cancel foreground video | — |
| `/qtrobot/media/video/fg/set_alpha` | Set foreground video transparency | `value` (0.0–1.0) |
| `/qtrobot/media/video/fg/stream/pause` | Pause foreground video stream | — |
| `/qtrobot/media/video/fg/stream/resume` | Resume foreground video stream | — |
| `/qtrobot/media/video/fg/stream/cancel` | Cancel foreground video stream | — |
| `/qtrobot/media/video/bg/*` | Background video — same API as `fg` | — |

### Microphone

| Service | Description | Key Parameters |
|---|---|---|
| `/qtrobot/microphone/int/tunning/get` | Get all ReSpeaker DSP parameters | — |
| `/qtrobot/microphone/int/tunning/set` | Set a ReSpeaker DSP parameter | `name`, `value` (required) |

---

## ROS2 Topics

### Published by the Gateway (robot → ROS2)

| Topic | Message Type | Rate | Description |
|---|---|---|---|
| `/qtrobot/motor/joints/state/stream` | `MotorJointsStateFrame` | 10 Hz | Per-joint position (deg), velocity (deg/s), effort (Nm), voltage (V), temperature (°C) |
| `/qtrobot/motor/joints/error/stream` | `MotorJointsErrorFrame` | on change | Per-joint error flags: overload, voltage limit, temperature limit, sensor failure |
| `/qtrobot/gesture/progress/stream` | `GestureProgressFrame` | streaming | Gesture playback progress percentage (0–100) and elapsed time in microseconds |
| `/qtrobot/mic/int/event/stream` | `MicEventFrame` | streaming | Voice activity (`activity: bool`) and direction of arrival (`direction`: 0–359°) |
| `/qtrobot/mic/int/audio/ch0/stream` | `AudioFrameRaw` | streaming | Internal mic — channel 0 (beamformed / processed) |
| `/qtrobot/mic/int/audio/ch1/stream` | `AudioFrameRaw` | streaming | Internal mic — channel 1 (raw) |
| `/qtrobot/mic/int/audio/ch2/stream` | `AudioFrameRaw` | streaming | Internal mic — channel 2 (raw) |
| `/qtrobot/mic/int/audio/ch3/stream` | `AudioFrameRaw` | streaming | Internal mic — channel 3 (raw) |
| `/qtrobot/mic/int/audio/ch4/stream` | `AudioFrameRaw` | streaming | Internal mic — channel 4 (raw) |
| `/qtrobot/mic/ext/audio/ch0/stream` | `AudioFrameRaw` | streaming | External mic — channel 0 |

### Subscribed by the Gateway (ROS2 → robot)

| Topic | Message Type | Description |
|---|---|---|
| `/qtrobot/motor/joints/command/stream` | `MotorJointsCommandFrame` | Send joint position/velocity commands to the robot |
| `/qtrobot/media/audio/fg/stream` | `AudioFrameRaw` | Stream raw PCM audio to the foreground audio player |
| `/qtrobot/media/audio/bg/stream` | `AudioFrameRaw` | Stream raw PCM audio to the background audio player |
| `/qtrobot/media/video/fg/stream` | `ImageFrameRaw` | Stream raw image frames to the foreground display |
| `/qtrobot/media/video/bg/stream` | `ImageFrameRaw` | Stream raw image frames to the background display |

All message types are in the `qtrobot_interfaces/msg` package.

---

## Usage Examples

### Text-to-Speech

```bash
# Say a sentence
ros2 service call /qtrobot/tts/engine/say/text qtrobot_interfaces/srv/TtsEngineSayText \
    "{text: 'Hello, I am QTrobot.'}"

# Say with a specific language and pitch
ros2 service call /qtrobot/tts/engine/say/text qtrobot_interfaces/srv/TtsEngineSayText \
    "{text: 'Bonjour', lang: 'fr-FR', pitch: 1.2}"

# Cancel ongoing speech
ros2 service call /qtrobot/tts/engine/cancel qtrobot_interfaces/srv/TtsEngineCancel "{}"

# List available TTS engines
ros2 service call /qtrobot/tts/engines/list qtrobot_interfaces/srv/TtsEnginesList "{}"
```

### Face Emotions

```bash
# List all available emotions
ros2 service call /qtrobot/face/emotion/list qtrobot_interfaces/srv/FaceEmotionList "{}"

# Show the 'happy' emotion
ros2 service call /qtrobot/face/emotion/show qtrobot_interfaces/srv/FaceEmotionShow \
    "{emotion: 'QT/happy'}"

# Show an emotion at half speed
ros2 service call /qtrobot/face/emotion/show qtrobot_interfaces/srv/FaceEmotionShow \
    "{emotion: 'QT/happy', speed: 0.7}"

# Stop the current emotion animation
ros2 service call /qtrobot/face/emotion/stop qtrobot_interfaces/srv/FaceEmotionStop "{}"
```

### Gestures

```bash
# List available gesture files
ros2 service call /qtrobot/gesture/file/list qtrobot_interfaces/srv/GestureFileList "{}"

# Play a gesture file
ros2 service call /qtrobot/gesture/file/play qtrobot_interfaces/srv/GestureFilePlay \
    "{gesture: 'QT/send_kiss'}"

# Cancel current gesture
ros2 service call /qtrobot/gesture/cancel qtrobot_interfaces/srv/GestureCancel "{}"
```

### Motors

```bash
# List all motors and their properties
ros2 service call /qtrobot/motor/list qtrobot_interfaces/srv/MotorList "{}"

# Enable torque on all motors and move to home position
ros2 service call /qtrobot/motor/on/all qtrobot_interfaces/srv/MotorOnAll "{}"
ros2 service call /qtrobot/motor/move/home/all qtrobot_interfaces/srv/MotorMoveHomeAll "{}"

# Set max velocity for a specific motor
ros2 service call /qtrobot/motor/velocity/set qtrobot_interfaces/srv/MotorVelocitySet \
    "{motor: 'HeadYaw', velocity: 50}"

# Disable torque on all motors
ros2 service call /qtrobot/motor/off/all qtrobot_interfaces/srv/MotorOffAll "{}"
```

### Motor Joint States (topic)

```bash
# Monitor joint states at 10 Hz
ros2 topic echo /qtrobot/motor/joints/state/stream
```

Example output:
```yaml
header:
  stamp: {sec: 1234567890, nanosec: 0}
  frame_id: ''
joints:
  - name: HeadYaw
    position: 0.44      # degrees
    velocity: 0.0       # deg/s
    effort: -2.0        # Nm
    voltage: 7.7        # V
    temperature: 24.0   # °C
  - name: HeadPitch
    position: 2.2
    ...
```

### Microphone Events (topic)

```bash
# Monitor voice activity and direction of arrival when user speak
ros2 topic echo /qtrobot/mic/int/event/stream
```

Example output:
```yaml
header:
  stamp: {sec: 1234567890, nanosec: 0}
  frame_id: ''
activity: true    # true = speech detected
direction: 270    # direction of arrival in degrees (0–359)
```

### Speaker Volume

```bash
# Get current speaker volume
ros2 service call /qtrobot/speaker/volume/get qtrobot_interfaces/srv/SpeakerVolumeGet "{}"

# Set speaker volume to 80%
ros2 service call /qtrobot/speaker/volume/set qtrobot_interfaces/srv/SpeakerVolumeSet \
    "{value: 0.8}"

# Mute and unmute
ros2 service call /qtrobot/speaker/volume/mute   qtrobot_interfaces/srv/SpeakerVolumeMute "{}"
ros2 service call /qtrobot/speaker/volume/unmute qtrobot_interfaces/srv/SpeakerVolumeUnmute "{}"
```

---

## Introspection

```bash
# List all QTrobot services
ros2 service list | grep qtrobot

# List all QTrobot topics
ros2 topic list | grep qtrobot

# Check topic publish rate
ros2 topic hz /qtrobot/motor/joints/state/stream

# Inspect a message or service interface
ros2 interface show qtrobot_interfaces/msg/MotorJointsStateFrame
ros2 interface show qtrobot_interfaces/srv/TtsEngineSayText
```

---

## License

Copyright © LuxAI S.A. All rights reserved.
