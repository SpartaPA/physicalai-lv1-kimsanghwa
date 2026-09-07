#ifndef LIDAR_HPP
#define LIDAR_HPP

#include "sensor.hpp"

class Lidar : public Sensor {
private:
    double maxRange;   // 최대 측정 거리 (m)
    double lastValue;

public:
    Lidar(const std::string& sensorName, double maxRange);
    ~Lidar() override;

    double read() override;              // 가상 소멸자 구현
    std::string type() const override;
};

#endif // LIDAR_HPP