cmake_minimum_required(VERSION 3.8)
project(qtrobot_interfaces)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)

set(msg_files
  "msg/AudioFrameRaw.msg"
  "msg/GestureProgressFrame.msg"
  "msg/ImageFrameRaw.msg"
  "msg/MicEventFrame.msg"
  "msg/MotorInfo.msg"
  "msg/MotorJointCommand.msg"
  "msg/MotorJointError.msg"
  "msg/MotorJointState.msg"
  "msg/MotorJointsCommandFrame.msg"
  "msg/MotorJointsErrorFrame.msg"
  "msg/MotorJointsStateFrame.msg"
  "msg/TtsVoiceInfo.msg"
)

set(srv_files
  "srv/FaceEmotionList.srv"
  "srv/FaceEmotionShow.srv"
  "srv/FaceEmotionStop.srv"
  "srv/FaceLook.srv"
  "srv/GestureCancel.srv"
  "srv/GestureFileList.srv"
  "srv/GestureFilePlay.srv"
  "srv/GesturePlay.srv"
  "srv/GestureRecordStart.srv"
  "srv/GestureRecordStop.srv"
  "srv/GestureRecordStore.srv"
  "srv/MediaAudioBgFileCancel.srv"
  "srv/MediaAudioBgFilePause.srv"
  "srv/MediaAudioBgFilePlay.srv"
  "srv/MediaAudioBgFileResume.srv"
  "srv/MediaAudioBgStreamCancel.srv"
  "srv/MediaAudioBgStreamPause.srv"
  "srv/MediaAudioBgStreamResume.srv"
  "srv/MediaAudioBgVolumeGet.srv"
  "srv/MediaAudioBgVolumeSet.srv"
  "srv/MediaAudioFgFileCancel.srv"
  "srv/MediaAudioFgFilePause.srv"
  "srv/MediaAudioFgFilePlay.srv"
  "srv/MediaAudioFgFileResume.srv"
  "srv/MediaAudioFgStreamCancel.srv"
  "srv/MediaAudioFgStreamPause.srv"
  "srv/MediaAudioFgStreamResume.srv"
  "srv/MediaAudioFgVolumeGet.srv"
  "srv/MediaAudioFgVolumeSet.srv"
  "srv/MediaVideoBgFileCancel.srv"
  "srv/MediaVideoBgFilePause.srv"
  "srv/MediaVideoBgFilePlay.srv"
  "srv/MediaVideoBgFileResume.srv"
  "srv/MediaVideoBgStreamCancel.srv"
  "srv/MediaVideoBgStreamPause.srv"
  "srv/MediaVideoBgStreamResume.srv"
  "srv/MediaVideoFgFileCancel.srv"
  "srv/MediaVideoFgFilePause.srv"
  "srv/MediaVideoFgFilePlay.srv"
  "srv/MediaVideoFgFileResume.srv"
  "srv/MediaVideoFgSetAlpha.srv"
  "srv/MediaVideoFgStreamCancel.srv"
  "srv/MediaVideoFgStreamPause.srv"
  "srv/MediaVideoFgStreamResume.srv"
  "srv/MicrophoneIntTunningGet.srv"
  "srv/MicrophoneIntTunningSet.srv"
  "srv/MotorCalibAll.srv"
  "srv/MotorCalibSet.srv"
  "srv/MotorList.srv"
  "srv/MotorMoveHome.srv"
  "srv/MotorMoveHomeAll.srv"
  "srv/MotorOff.srv"
  "srv/MotorOffAll.srv"
  "srv/MotorOn.srv"
  "srv/MotorOnAll.srv"
  "srv/MotorVelocitySet.srv"
  "srv/SpeakerVolumeGet.srv"
  "srv/SpeakerVolumeMute.srv"
  "srv/SpeakerVolumeSet.srv"
  "srv/SpeakerVolumeUnmute.srv"
  "srv/TtsDefaultEngineGet.srv"
  "srv/TtsDefaultEngineSet.srv"
  "srv/TtsEngineCancel.srv"
  "srv/TtsEngineConfigureGet.srv"
  "srv/TtsEngineConfigureSet.srv"
  "srv/TtsEngineLanguagesGet.srv"
  "srv/TtsEngineSaySsml.srv"
  "srv/TtsEngineSayText.srv"
  "srv/TtsEngineSupportsSsml.srv"
  "srv/TtsEngineVoicesGet.srv"
  "srv/TtsEnginesList.srv"
)

rosidl_generate_interfaces(${PROJECT_NAME}
  ${msg_files}
  ${srv_files}
  DEPENDENCIES std_msgs
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
