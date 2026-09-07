#ifndef IMU_HPP
#define IMU_HPP

#include "sensor.hpp"

class Imu : public Sensor {
private:
    double bias;       // 센서 바이어스 (deg/s)
    double lastValue;

public:
    Imu(const std::string& sensorName, double bias);
    ~Imu() override;

    double read() override;              // 가상 소멸자 구현
    std::string type() const override;
};

#endif // IMU_HPP