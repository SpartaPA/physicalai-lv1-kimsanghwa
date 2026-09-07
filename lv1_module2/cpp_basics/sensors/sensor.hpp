#ifndef SENSOR_HPP
#define SENSOR_HPP

#include <string>

// 추상 기반 클래스
class Sensor {
protected:
    std::string name;

public:
    Sensor(const std::string& sensorName);

    // 가상 소멸자 센서
    virtual ~Sensor();

    // 순수 가상 함수 - 파생 클래스 구현필요
    virtual double read() = 0;

    // 일반 가상 함수 - 재정의 가능
    virtual std::string type() const;

    // 비가상 함수 - 모든 파생 클래스가 공유
    const std::string& getName() const;
};

#endif // SENSOR_HPP