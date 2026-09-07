#include "sensor.hpp"
#include "Lidar.hpp"
#include "Imu.hpp"

#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <memory>
#include <string>
#include <unordered_map>
#include <vector>

// 측정 로그 한 건: 어느 센서에서, 어떤 값이 나왔는지
struct LogEntry {
    std::string sensorName;
    double value;
};

int main() {
    // Sensor s("test");   // 컴파일 에러 - 추상 클래스는 객체 생성 불가

    std::cout << "=== 1. 객체 생성 ===\n";
    std::vector<std::unique_ptr<Sensor>> sensors;
    sensors.push_back(std::make_unique<Lidar>("LIDAR-01", 30.0));
    sensors.push_back(std::make_unique<Imu>("IMU-01", 0.02));

    std::cout << "\n=== 2. 다형성 - 반복 측정 (unordered_map + 로그 vector 채우기) ===\n";
    std::cout << std::fixed << std::setprecision(4);

    std::unordered_map<std::string, double> latestValue; // 센서 이름 -> 최근 측정값
    std::vector<LogEntry> log;                            // 전체 측정 로그(시계열)

    const int kNumSamples = 200;
    for (int i = 0; i < kNumSamples; ++i) {
        for (const auto& s : sensors) {
            const double v = s->read();
            latestValue[s->getName()] = v;    // 기반 포인터로 호출해도 실제 타입의 read()가 실행됨
            log.push_back({s->getName(), v});
        }
    }

    for (const auto& s : sensors) {
        std::cout << "  " << std::setw(6) << s->type()
                  << " | " << s->getName()
                  << " | 최근 측정값 = " << latestValue[s->getName()] << "\n";
    }
    std::cout << "  로그 총 개수 = " << log.size() << "\n";

    std::cout << "\n=== 3. count_if - 목표점 근접 기록 세기 ===\n";
    const double target = 15.0;   // 목표점 (예: LIDAR-01 기준 목표 거리, m)
    const double tolerance = 0.5; // 허용 오차

    const long nearCount = std::count_if(
        log.begin(), log.end(),
        [target, tolerance](const LogEntry& e) {
            return std::abs(e.value - target) <= tolerance;
        });

    std::cout << "  목표점(" << target << ") ± " << tolerance
              << " 이내 기록 개수 = " << nearCount << " / " << log.size() << "\n";

    std::cout << "\n=== 4. 소멸 (역순) ===\n";
    return 0;   // unique_ptr 소멸 -> 가상 소멸자 재귀 동작
}