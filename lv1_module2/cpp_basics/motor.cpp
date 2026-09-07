#include "motor.hpp"
#include <iostream>
#include <algorithm>

Motor::Motor(const std::string& motorName, int maxRpm)
    : name(motorName), rpm(0), maxRpm(maxRpm), isRunning(false)
{
    std::cout << "[Motor] '" << name << "' 생성됨 (최대 " << maxRpm << " RPM)\n";
}

void Motor::start() {
    isRunning = true;
    std::cout << "[Motor] '" << name << "' 시작됨\n";
}

void Motor::stop() {
    isRunning = false;
    rpm = 0;
    std::cout << "[Motor] '" << name << "' 정지 완료\n";
}

void Motor::setSpeed(int targetRpm) {
    if (!isRunning) {
        std::cout << "[Motor] 경고: 모터가 꺼져있어 속도를 설정할 수 없습니다\n";
        return;
    }
    rpm = std::clamp(targetRpm, 0, maxRpm);
    std::cout << "[Motor] '" << name << "' 속도 설정: " << rpm << " RPM\n";
}

void Motor::accelerate(int deltaRpm) {
    if (!isRunning) {
        std::cout << "[Motor] 경고: 모터가 꺼져있어 가속할 수 없습니다\n";
        return;
    }
    int before = rpm;
    rpm = std::clamp(rpm + deltaRpm, 0, maxRpm);
    std::cout << "[Motor] '" << name << "' 가속: "
              << before << " -> " << rpm << " RPM\n";
}

void Motor::printStatus() const {
    std::cout << "[Motor] " << name
              << " | 상태: " << (isRunning ? "구동중" : "정지")
              << " | RPM: " << rpm << " / " << maxRpm << "\n";
}