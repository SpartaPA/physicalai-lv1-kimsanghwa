# CMake 최소 요구 버전
cmake_minimum_required(VERSION 3.10)

# 프로젝트 이름과 사용 언어
project(MotorProject VERSION 1.0 LANGUAGES CXX)

# C++ 표준 지정
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 실행 파일 정의: 이름 + 소스 파일 목록
add_executable(motor_program
    main.cpp
    motor.cpp
)

# 컴파일 경고 옵션
target_compile_options(motor_program PRIVATE -Wall -Wextra)