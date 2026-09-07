#include "Lidar.hpp"
#include <iostream>
#include <random>

Lidar::Lidar(const std::string& sensorName, double maxRange)
    : Sensor(sensorName), maxRange(maxRange), lastValue(0.0)
{
    std::cout << "  [Lidar]    생성자: 최대 " << maxRange << " m\n";
}

Lidar::~Lidar() {
    std::cout << "  [Lidar]    소멸자: " << name << "\n";
}

double Lidar::read() {
    static std::mt19937 gen(42);
    std::uniform_real_distribution<double> dist(0.1, maxRange);
    lastValue = dist(gen);
    return lastValue;
}

std::string Lidar::type() const {
    return "Lidar";
}