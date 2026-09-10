# lv1 과제 제출 레포지토리

계층구조트리

```
physicalai-lv1-kimsanghwa/
├── .gitignore
├── README.md
├── requirements.txt
├── lv1_module1/                     # 리눅스/센서 관련 과제
│   ├── report.md
│   ├── images/                      # 스크린샷 4장
│   └── rules/
│       └── 99-robot-sensor.rules
├── lv1_module2/                     # ROS2 실습 (C++, Python)
│   ├── report.md
│   ├── bags/
│   ├── screenshots/                 # 스크린샷 12장
│   ├── cpp_basics/                  # C++ 기초 예제 (motor, sensor 등)
│   │   ├── CMakeLists.txt
│   │   ├── main.cpp, motor.cpp/hpp, stop_distance.cpp
│   │   └── sensors/                 # Imu, Lidar, Compare 등
│   └── ros2_ws/                     # ROS2 워크스페이스
│       └── src/
│           ├── turtle_cpp/          # C++ 패키지 (distance_publisher 등)
│           ├── turtle_py/           # Python 패키지 (tf_broadcaster 등)
│           ├── turtle_interfaces/   # msg/srv/action 정의
│           └── turtle_examples/     # 예제 노드 모음 (ex03~ex07)
├── lv1_module3/                     # 좌표변환/회전 수학
│   ├── README.md, requirements.txt
│   ├── notebooks/                   # 01_vectors ~ 06_chain (jupyter)
│   ├── src/                         # vectors, rotation, transform, coordinate_chain
│   └── tests/                       # pytest 테스트
└── lv1_module4/                     # 포즈 추정/쿼터니언/궤적
    ├── README.md, pytest.ini, requirements.txt, demo.gif
    ├── notebooks/                   # 01_pipeline ~ 03_pose_estimation
    ├── src/                         # quaternion, pose_pipeline, pose_estimation, trajectory 등
    └── tests/                       # pytest 테스트
```