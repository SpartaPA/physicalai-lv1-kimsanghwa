# 문제 2-1. C++ 빌드 체계 세우기 — g++ 다중 파일 빌드와 CMake 전환

## 수동 2단계 빌드 명령(터미널 입력)

### 1단계 — 컴파일 (링크하지 않고 컴파일만)
g++ -std=c++17 -Wall -c motor.cpp -o motor.o -> -c 옵션을 붙여 컴파일만 하도록 한다.
g++ -std=c++17 -Wall -c main.cpp  -o main.o -> -c 옵션을 붙여 컴파일만 하도록 한다.

### 2단계 — 링크 (.o들을 묶어 실행파일 생성)
g++ motor.o main.o -o motor_program

## undefined reference 에러 메시지(출력)
링크 단계에서 motor.o를 빼고 빌드하여 undefined reference에러를 구현한다.
```bash
pa16@pa16-Legion-Pro-5-16IAX10:~/lv1_module2_김상화/cpp_basics$ g++ build/main.o -o build/motor_program
```

```bash
/usr/bin/ld: build/main.o: in function `main':
main.cpp:(.text+0x56): undefined reference to `Motor::Motor(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&, int)'
/usr/bin/ld: main.cpp:(.text+0x7a): undefined reference to `Motor::start()'
/usr/bin/ld: main.cpp:(.text+0x8b): undefined reference to `Motor::accelerate(int)'
/usr/bin/ld: main.cpp:(.text+0x97): undefined reference to `Motor::printStatus() const'
/usr/bin/ld: main.cpp:(.text+0xa3): undefined reference to `Motor::stop()'
collect2: error: ld returned 1 exit status
```

컴파일 에러는 컴파일러가 코드를 읽는중에 발생하는 에러이기 때문에 문법에 맞지 않는다면 에러가 발생한 줄을 명시하며 이곳을 고쳐야 한다고 알려준다. 하지만 링크과정에서 문제가 생겼다면 터미널에서는 /usr/bin/id로 시작하는 디렉토리 주소를 알려주는것을 알 수 있다. 이것은 링크가 제대로 이루어지지 않았음을 알려준다.

## CMake 빌드 출력
```bash
pa16@pa16-Legion-Pro-5-16IAX10:~/lv1_module2_김상화/ros2_ws/src/turtle_cpp$ cd ~/lv1_module2_김상화/cpp_basics/
pa16@pa16-Legion-Pro-5-16IAX10:~/lv1_module2_김상화/cpp_basics$ mkdir -p build
pa16@pa16-Legion-Pro-5-16IAX10:~/lv1_module2_김상화/cpp_basics$ cd build
pa16@pa16-Legion-Pro-5-16IAX10:~/lv1_module2_김상화/cpp_basics/build$ cmake ..
-- The CXX compiler identification is GNU 11.4.0
-- Detecting CXX compiler ABI info
-- Detecting CXX compiler ABI info - done
-- Check for working CXX compiler: /usr/bin/c++ - skipped
-- Detecting CXX compile features
-- Detecting CXX compile features - done
-- Configuring done
-- Generating done
-- Build files have been written to: /home/pa16/lv1_module2_김상화/cpp_basics/build
pa16@pa16-Legion-Pro-5-16IAX10:~/lv1_module2_김상화/cpp_basics/build$ cmake --build
Usage: cmake --build <dir>             [options] [-- [native-options]]
       cmake --build --preset <preset> [options] [-- [native-options]]
Options:
  <dir>          = Project binary directory to be built.
  --preset <preset>, --preset=<preset>
                 = Specify a build preset.
  --list-presets
                 = List available build presets.
  --parallel [<jobs>], -j [<jobs>]
                 = Build in parallel using the given number of jobs. 
                   If <jobs> is omitted the native build tool's 
                   default number is used.
                   The CMAKE_BUILD_PARALLEL_LEVEL environment variable
                   specifies a default parallel level when this option
                   is not given.
  --target <tgt>..., -t <tgt>... 
                 = Build <tgt> instead of default targets.
  --config <cfg> = For multi-configuration tools, choose <cfg>.
  --clean-first  = Build target 'clean' first, then build.
                   (To clean only, use --target 'clean'.)
  --verbose, -v  = Enable verbose output - if supported - including
                   the build commands to be executed. 
  --             = Pass remaining options to the native tool.

```

## 증분 빌드시 재컴파일된 파일
```bash
stat motor.cpp
  파일: motor.cpp
  크기: 1371      	블록: 8          입출력 블록: 4096   일반 파일
Device: 10302h/66306d	Inode: 28576480    Links: 1
접근: (0664/-rw-rw-r--)  UID: ( 1000/    pa16)   GID: ( 1000/    pa16)
접근: 2026-09-01 15:37:17.040733839 +0900
수정: 2026-08-27 15:04:54.769832721 +0900
변경: 2026-08-27 15:04:54.769832721 +0900
생성: 2026-08-26 17:41:57.024825052 +0900

```

**판단근거**
파일이 수정된 이력을 볼 수 있는 터미널 명령어 stat을 이용하여 파일의 생성, 접근, 수정 이력을 모두 확인할 수 있다. 작성일인 9월1일 기준 Cmake로 증분빌드를 하면서 motor.cpp에 접근한 흔적이 남았다. 이를 근거로 이 파일은 재컴파일 되었음을 확인할 수 있다.


# 문제 2-2. 현대 C++로 센서 계층 구현 — RAII·다형성·STL

## 다형성 루프 + 가상 소멸자 유무 비교 (sensors/)

main.cpp에서 `std::vector<std::unique_ptr<Sensor>>`에 `Lidar`, `Imu` 두 센서를 담고 기반 포인터로 `read()`, `type()`을 호출하는 다형성 루프를 구현했다. `sensor.hpp`의 `Sensor` 소멸자는 `virtual`로 선언되어 있어, `unique_ptr<Sensor>`가 소멸될 때 실제 가리키던 파생 클래스(`Lidar`/`Imu`)의 소멸자부터 호출된 뒤 `Sensor`의 소멸자가 호출된다.



## 스택 객체와 힙 객체의 소멸 시점


`sensors/StackVsHeap.cpp`에서 같은 `Imu` 객체를 (A) 지역 변수로 스택에 직접 생성한 경우와 (B) `std::make_unique`로 힙에 생성해 `unique_ptr`로 소유한 경우로 나눠, 각 블록(`{ }`)을 빠져나갈 때 소멸자가 언제 호출되는지 관찰했다.

```
=== A. 지역 변수(스택)로 생성 ===
  [블록 탈출 직전]
  [Imu]      소멸자: STACK-IMU
  [Sensor]   소멸자: STACK-IMU
  [블록 탈출 완료]

=== B. std::make_unique로 생성 (힙) ===
  [블록 탈출 직전]
  [Imu]      소멸자: HEAP-IMU
  [Sensor]   소멸자: HEAP-IMU
  [블록 탈출 완료]
```

스택 객체(A)는 블록을 벗어나는 순간 컴파일러가 자동으로 소멸자를 호출한다. `make_unique`로 만든 힙 객체(B)는 그 객체를 소유한 `unique_ptr`가 블록을 벗어날 때 소멸되면서 내부적으로 `delete`를 호출해 소멸자를 부른다. 두 경우 모두 소멸 시점은 블록이 끝나는 지점으로 동일하게 관찰되었다.

## 가상 소멸자 유무 비교

`sensors/Compare.cpp`에서는 가상 소멸자 유무에 따른 차이를 직접 실험했다 (`WithVirtual` / `NoVirtual` 두 네임스페이스, 각각 `Lidar`/`Imu`가 `new[]`로 버퍼를 동적 할당). 컴파일 및 실행 결과:

```bash
g++ -std=c++17 -Wall -Wextra -o compare_test Compare.cpp
./compare_test
```

```
########## A. 가상 소멸자 있음 ##########
[소멸]
    ~Lidar(LIDAR-01) 버퍼 해제
    ~Sensor(LIDAR-01)
    ~Imu(IMU-01) 버퍼 해제
    ~Sensor(IMU-01)

########## B. 가상 소멸자 없음 ##########
[소멸]
    ~Sensor(LIDAR-02)
    ~Sensor(IMU-02)
```

**관찰**: A(가상 소멸자 있음)는 `unique_ptr<Sensor>`를 통해 소멸시켜도 실제 타입인 `~Lidar`/`~Imu`가 먼저 호출되어 `scanBuffer`/`gyroBuffer`가 정상적으로 해제된다. 반면 B(가상 소멸자 없음)는 기반 클래스의 `~Sensor()`만 호출되고 파생 클래스 소멸자(`~Lidar`, `~Imu`)는 아예 실행되지 않는다 — 즉 `delete[] scanBuffer` / `delete[] gyroBuffer`가 실행되지 않아 **메모리 누수**가 발생한다.

이 동작은 C++ 표준상 정의되지 않은 동작(UB)이다: 기반 클래스 포인터로 파생 객체를 `delete`할 때 소멸자가 `virtual`이 아니면 어떤 일이 일어날지 표준이 보장하지 않으며, 위 결과는 GCC/libstdc++ 환경에서 관찰된 동작일 뿐이다. 실제로 `-Wnon-virtual-dtor` 옵션을 켜고 컴파일하면(`-Wall -Wextra`에는 기본 포함되지 않음) 아래와 같은 경고가 뜬다.

```
warning: 'class NoVirtual::Sensor' has virtual functions and accessible non-virtual destructor [-Wnon-virtual-dtor]
warning: base class 'class NoVirtual::Lidar' has virtual functions and accessible non-virtual destructor [-Wnon-virtual-dtor]
```

**결론**: 다형적으로 사용될 기반 클래스(가상 함수가 하나라도 있고, 파생 클래스를 기반 포인터로 소유/소멸시킬 가능성이 있는 클래스)는 소멸자를 반드시 `virtual`로 선언해야 한다. 그렇지 않으면 파생 클래스의 자원 해제 로직이 통째로 스킵되어 메모리 누수나 미정의 동작으로 이어진다.

`sensors/Compare.cpp`에서는 가상 소멸자 유무에 따른 차이를 직접 실험했다 (`WithVirtual` / `NoVirtual` 두 네임스페이스, 각각 `Lidar`/`Imu`가 `new[]`로 버퍼를 동적 할당). 컴파일 및 실행 결과:

```bash
g++ -std=c++17 -Wall -Wextra -o compare_test Compare.cpp
./compare_test
```

```
########## A. 가상 소멸자 있음 ##########
[소멸]
    ~Lidar(LIDAR-01) 버퍼 해제
    ~Sensor(LIDAR-01)
    ~Imu(IMU-01) 버퍼 해제
    ~Sensor(IMU-01)

########## B. 가상 소멸자 없음 ##########
[소멸]
    ~Sensor(LIDAR-02)
    ~Sensor(IMU-02)
```

**관찰**: A(가상 소멸자 있음)는 `unique_ptr<Sensor>`를 통해 소멸시켜도 실제 타입인 `~Lidar`/`~Imu`가 먼저 호출되어 `scanBuffer`/`gyroBuffer`가 정상적으로 해제된다. 반면 B(가상 소멸자 없음)는 기반 클래스의 `~Sensor()`만 호출되고 파생 클래스 소멸자(`~Lidar`, `~Imu`)는 아예 실행되지 않는다 — 즉 `delete[] scanBuffer` / `delete[] gyroBuffer`가 실행되지 않아 **메모리 누수**가 발생한다.

이 동작은 C++ 표준상 정의되지 않은 동작(UB)이다: 기반 클래스 포인터로 파생 객체를 `delete`할 때 소멸자가 `virtual`이 아니면 어떤 일이 일어날지 표준이 보장하지 않으며, 위 결과는 GCC/libstdc++ 환경에서 관찰된 동작일 뿐이다. 실제로 `-Wnon-virtual-dtor` 옵션을 켜고 컴파일하면(`-Wall -Wextra`에는 기본 포함되지 않음) 아래와 같은 경고가 뜬다.

```
warning: 'class NoVirtual::Sensor' has virtual functions and accessible non-virtual destructor [-Wnon-virtual-dtor]
warning: base class 'class NoVirtual::Lidar' has virtual functions and accessible non-virtual destructor [-Wnon-virtual-dtor]
```

**결론**: 다형적으로 사용될 기반 클래스(가상 함수가 하나라도 있고, 파생 클래스를 기반 포인터로 소유/소멸시킬 가능성이 있는 클래스)는 소멸자를 반드시 `virtual`로 선언해야 한다. 그렇지 않으면 파생 클래스의 자원 해제 로직이 통째로 스킵되어 메모리 누수나 미정의 동작으로 이어진다.

## count_if 결과

`sensors/main.cpp`에서 LIDAR-01, IMU-01을 각 200번씩 읽어 총 400개 로그를 만들고, `std::count_if`로 "목표점 15.0 ± 0.5" 조건을 만족하는 기록 수는 총 **2개**가 나왔다.

- **LIDAR-01**: 0.1 ~ 30.0m 범위에서 균등하게 값이 나온다. 15.0 ± 0.5 구간(폭 1.0)은 전체 범위(약 29.9)의 약 3.3%밖에 안 되므로, 200개 중 이 구간에 들어올 확률적 기대값은 약 6~7개 정도다.

- **IMU-01**: 값이 항상 0 근처(평균 0.02, 표준편차 0.5)에서만 나오기 때문에 15.0 근처에 올 가능성이 사실상 없다. 그래서 IMU 쪽에서는 0개.
- 실제로 매칭된 기록은 LIDAR-01의 값 2개(14.5964, 15.2951)였고, 이는 위 확률(기대값 6~7개)보다 적지만 난수라서 나올 수 있는 정상적인 편차다.

**요약**: 목표점 근처(15.0)에 값이 나올 수 있는 센서는 넓은 범위를 갖는 LIDAR-01뿐이었고, 그마저도 좁은 허용 오차(±0.5) 구간에 실제로 걸린 표본이 200개 중 2개였기 때문에 count_if 결과가 2가 나왔다.

## 누수 검출 결과 -> 수정 후 결과

`sensors/LeakDemo.cpp`에서 `new Imu(...)`만 하고 `delete`를 하지 않는 루프(5회)를 만들어 누수를 재현하고, `std::make_unique`로 바꿔서 해결됐는지 ASan(AddressSanitizer)으로 비교했다. (실행 환경: 리눅스 + g++, `-fsanitize=address`)

**수정 전 (new, delete 없음) — 누수 검출됨**
```
==ERROR: LeakSanitizer: detected memory leaks
Direct leak of 280 byte(s) in 5 object(s) allocated from:
    #1 runLeaky LeakDemo.cpp:13
SUMMARY: AddressSanitizer: 280 byte(s) leaked in 5 allocation(s).
```
(종료 코드 1)

**수정 후 (std::make_unique로 교체) — 누수 없음**
```
(ASan 경고 없음, 정상 종료)
```
(종료 코드 0)

**요약**: `new`로 할당하고 `delete`를 빠뜨리면 ASan이 몇 줄에서, 몇 개, 몇 바이트가 새는지 정확히 잡아낸다. 같은 코드를 `std::make_unique`로만 바꾸면 반복문이 끝날 때마다 스마트 포인터가 자동으로 메모리를 해제해서 같은 검사에서 누수가 전혀 검출되지 않는다.

# 문제 2-3. rclpy 노드 작성 — 거북이 상태 발행자와 구독자

## /turtle1/pose 필드 구성

```bash
x: 5.544444561004639
y: 5.544444561004639
theta: 0.0
linear_velocity: 0.0
angular_velocity: 0.0
---

```

| 필드 | 의미 |
|:---:|:---:|
  | `x` | 거북이의 x 좌표 (미터) |
  | `y` | 거북이의 y 좌표 (미터) |
  | `theta` | 거북이가 향하고 있는 방향(각도, 라디안). 0이면 +x 방향(오른쪽)을 바라보는 상태|
  | `linear_velocity` | 현재 직진 속도 (m/s).  |
  | `angular_velocity` | 현재 회전 속도 (rad/s).
  
## ros2 topic hz /turtle_distance 출력  
```bash
average rate: 19.987
	min: 0.009s max: 0.091s std dev: 0.04037s window: 22
average rate: 20.380
	min: 0.005s max: 0.096s std dev: 0.04060s window: 43
average rate: 19.999
	min: 0.005s max: 0.096s std dev: 0.04075s window: 64
average rate: 19.999
	min: 0.004s max: 0.096s std dev: 0.04095s window: 84
average rate: 20.155
	min: 0.004s max: 0.096s std dev: 0.04084s window: 105
average rate: 20.129
	min: 0.004s max: 0.096s std dev: 0.04083s window: 125
average rate: 20.000
	min: 0.004s max: 0.096s std dev: 0.04084s window: 146
```

## 구독자 경고 로그(터미널 출력)
```bash
[WARN] [1787885054.942755310] [distance_watcher]: 거리 7.841 m가 임계값 3.000 m를 초과했습니다
[WARN] [1787885055.033475265] [distance_watcher]: 거리 7.841 m가 임계값 3.000 m를 초과했습니다
[WARN] [1787885055.042879131] [distance_watcher]: 거리 7.841 m가 임계값 3.000 m를 초과했습니다
[WARN] [1787885055.133693026] [distance_watcher]: 거리 7.841 m가 임계값 3.000 m를 초과했습니다
[WARN] [1787885055.143008611] [distance_watcher]: 거리 7.841 m가 임계값 3.000 m를 초과했습니다
[WARN] [1787885055.233370642] [distance_watcher]: 거리 7.841 m가 임계값 3.000 m를 초과했습니다
[WARN] [1787885055.243146075] [distance_watcher]: 거리 7.841 m가 임계값 3.000 m를 초과했습니다

```

turtlesim_node를 실행하면 거북이의 원점의 위치가 7.841이기 때문에 임계값을 초과했다는 경고 메시지를 계속해서 출력한다.

## 구독자 2개 동시 수신 확인
## 정사각형 주행 캡쳐
![](https://velog.velcdn.com/images/kimhwa0486/post/308307f8-3cdb-4b44-81a9-3adb865e022e/image.png)

정사각형 주행을 여러번 시도했지만 완전한 정사각형 모양을 그릴수는 없었다.

그 이유를 추정해보았다.

- 이동한 거리를 받아오는 노드와 발행하는 노드의 시간이 완전히 일치하지 않아서 생기는 지속적인 오차(타이머 지터)

- turtlesim이 자신의 현재 위치를 정확하게 추정할 수 없음.

- 서로의 타이머를 공유하지 않고 publisher와 watcher가 서로 각각 다른 타이머를 사용함 -> 서로 싱크가 맞지않아 정사각형 모양 틀어짐. 


# 문제 2-4. rclcpp 노드 작성 — C++ 발행자와 구독자

## colcon build 성공 출력
```bash
Starting >>> turtle_cpp
Finished <<< turtle_cpp [5.48s]                     

Summary: 1 package finished [5.71s]
```

## rclpy 발행에서 rclcpp 구독으로 이어진 로그
**turtle_py의 distance_publisher에서 발행로그**
```bash
pa16@pa16-Legion-Pro-5-16IAX10:~$ ros2 run turtle_py distance_publisher 

```
**turtle_cpp의 distance_watcher에서 구독로그**
```bash
pa16@pa16-Legion-Pro-5-16IAX10:~$ ros2 run turtle_cpp distance_watcher 
[WARN] [1788335921.855976863] [distance_watcher]: 거리 7.841 m가 임계값 3.000 m를 초과했습니다
[WARN] [1788335921.956023809] [distance_watcher]: 거리 7.841 m가 임계값 3.000 m를 초과했습니다
[WARN] [1788335922.055797698] [distance_watcher]: 거리 7.841 m가 임계값 3.000 m를 초과했습니다
[WARN] [1788335922.156003312] [distance_watcher]: 거리 7.841 m가 임계값 3.000 m를 초과했습니다
[WARN] [1788335922.255983664] [distance_watcher]: 거리 7.841 m가 임계값 3.000 m를 초과했습니다
[WARN] [1788335922.356022989] [distance_watcher]: 거리 7.841 m가 임계값 3.000 m를 초과했습니다
[WARN] [1788335922.455942564] [distance_watcher]: 거리 7.841 m가 임계값 3.000 m를 초과했습니다
[WARN] [1788335922.555950430] [distance_watcher]: 거리 7.841 m가 임계값 3.000 m를 초과했습니다
[WARN] [1788335922.655955341] [distance_watcher]: 거리 7.841 m가 임계값 3.000 m를 초과했습니다
[WARN] [1788335922.755992686] [distance_watcher]: 거리 7.841 m가 임계값 3.000 m를 초과했습니다
[WARN] [1788335922.855724089] [distance_watcher]: 거리 7.841 m가 임계값 3.000 m를 초과했습니다

```
## rclpy와 rclcpp 대응 관계표
| 항목 | `turtle_py/distance_publisher.py` (rclpy) | `turtle_cpp/distance_watcher.cpp` (rclcpp) | 대응 관계 |
|---|---|---|---|
| **노드 생성** | `super().__init__('turtle_distance_publisher')`로 노드 생성 → `create_subscription(Pose, '/turtle1/pose', ...)`으로 pose 구독 → `create_publisher(Float32, '/turtle_distance', 10)`으로 발행자 생성 | `Node("distance_watcher")`로 노드 생성 → `declare_parameter<double>("threshold", 3.0)`으로 파라미터 선언 → `create_subscription<Float32>("/turtle_distance", 10, std::bind(...))`으로 구독 생성 | 생성자에서 이름 등록 + 구독/발행 객체를 멤버로 만들어두는 구조는 동일. publisher는 발행자도 같이 만들고, watcher는 파라미터도 같이 선언한다는 점만 다름 |
| **타이머** | `create_timer(0.1, self._timer_callback)`로 10Hz 타이머 생성 — 구독 콜백은 값 저장만 하고 실제 발행은 타이머가 담당 | 없음 — 발행할 게 없어 타이머 불필요, 메시지 수신 즉시 반응하는 이벤트 구동 구조 | publisher만 타이머 보유. 타이머로 "수신 주기"와 "발행 주기"를 분리한 게 publisher 설계의 핵심 |
| **콜백** | `_pose_callback`: 최신 pose 저장만 함 / `_timer_callback`: 거리 계산 후 publish — 역할이 콜백 2개로 분리됨 | `distanceCallback`: 수신 즉시 threshold와 비교해 초과 시 `RCLCPP_WARN` 로그 — 콜백 1개가 판단+로그까지 전부 처리 | 둘 다 구독 콜백이 있다는 점은 같지만, publisher는 수신과 계산/발행을 분리(2단계), watcher는 수신 즉시 판단(1단계)으로 처리 흐름이 다름 |
| **종료** | `rclpy.init()` → `rclpy.spin(node)`를 try로 감싸 `KeyboardInterrupt` 처리 → `finally`에서 `node.destroy_node()` 명시적 호출 후 `rclpy.shutdown()` | `rclcpp::init()` → `rclcpp::spin(shared_ptr)` → 스코프 종료 시 `shared_ptr` 소멸자가 노드 자동 파괴 → `rclcpp::shutdown()` | init → spin → shutdown 골격은 동일하지만, 정리 방식이 다름: Python은 `destroy_node()` 수동 호출, C++은 `shared_ptr`의 RAII로 자동 파괴 |


# 문제 2-10. 시각화·기록·테스트로 검증하기

## rqt_graph 캡쳐
![](https://velog.velcdn.com/images/kimhwa0486/post/0bfc6e64-bcb2-49c7-8aab-3df019fd4758/image.png)

## 데이터 미수신시 진단 절차

**1단계 — 증상 구분**
실제로 실습중 통신에 문제가 생기는 경우는 크게 하기의 2가지 문제가 주요했다.

**토픽이 아예 뜨지 않는경우** 또는 **뜨긴 하지만 실시간으로 통신이 안되는 경우**

   ros2 topic list                     **# /turtle_py/distance_publisher or /turtle_cpp/distance_publisher가 실행되지 않았을 경우 이 명령어를 통해 node가 살아있고 topic을 발행중인지 확인해야 한다.** 
   ros2 topic hz /turtle_distance      **# 여기서 10Hz로 나온다고 "정상"이라고 단정지어서는 안된다. publisher와 watcher모두 실행시켜 실시간으로 통신을 하고있는지 확인해야한다.**

**2단계 — 값 자체를 확인(실시간성)**
   ros2 topic echo /turtle_distance    **# 값이 고정돼서 안 바뀌는지, 몇 초 텀을 두고 두 번 비교**

**3단계 — 상류(upstream) 토픽까지 거슬러 올라가며 확인**
   ros2 topic hz /turtle1/pose         **# 여기가 타임아웃되면 문제는 turtlesim(또는 그 위)에 있음**
   ros2 node list                      **# /turtlesim 노드가 실제로 살아있는지**

**4단계 — 노드 자체 생존 확인**
   ros2 node list | grep turtlesim
   ps aux | grep turtlesim_node        **# DDS에는 남아 보여도 프로세스는 죽어있는 경우 대비**

**5단계 — 연결 구조 확인 (rqt_graph 또는 CLI)**
   ros2 topic info /turtle1/pose -v    **# publisher count가 0이면 turtlesim이 발행을 멈춘 것**
   ros2 topic info /turtle_distance -v **# publisher/subscriber count로 양쪽 다 붙어있는지 확인**

**6단계 — 재현 및 재시작**
   turtlesim을 재시작해 /turtle1/pose가 다시 발행되는지, distance_publisher가 새 값으로
   갱신되는지 확인. 갱신 안 되면 distance_publisher 자체를 재시작 (구독 콜백이 최신 pose를
   못 받는 상태로 멈춰있을 수 있음)

### 결론: hz는 일정시간마다 topic을 발행하는가를 검증하는 도구라 노드가 실행되지 않은 경우에는 캐시된 값으로 계속 발행되는 노드에서는 잘못된 값을 받아오고 있지만 정상이라고 판정하는 현상을 발생시킨다. 그래서 진단할 때는 항상 hz(주기) + echo(값 변화) + 상위 노드 실행 여부를 종합적으로 확인해야 한다.


## RViz2 TF + 경유점 마커 캡처
![](https://velog.velcdn.com/images/kimhwa0486/post/f97670c8-0a2c-4592-9a64-620659c6909a/image.png)

**먼저 world와 turtle1마커를 생성한다.**

![](https://velog.velcdn.com/images/kimhwa0486/post/4a1c9b3f-1880-4228-bb98-93fa728aee7f/image.png)

**그 후 square_driver를 실행하여 전진후 방향을 돌리기전 waypoint(경유점)을 표시하도록 함수를 추가하였다. 그 결과 멈추는 꼭짓점마다 waypoint가 생성되는것을 확인할 수 있었다.**


