#include "Imu.hpp"
#include <iostream>
#include <random>

Imu::Imu(const std::string& sensorName, double bias)
    : Sensor(sensorName), bias(bias), lastValue(0.0)
{
    std::cout << "  [Imu]      생성자: 바이어스 " << bias << " deg/s\n";
}

Imu::~Imu() {
    std::cout << "  [Imu]      소멸자: " << name << "\n";
}

double Imu::read() {
    static std::mt19937 gen(7);
    std::normal_distribution<double> dist(0.0, 0.5);
    lastValue = dist(gen) + bias;
    return lastValue;
}

std::string Imu::type() const {
    return "Imu";
}