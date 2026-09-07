#include "sensor.hpp"
#include <iostream>

Sensor::Sensor(const std::string& sensorName) : name(sensorName) {
    std::cout << "  [Sensor]   생성자: " << name << "\n";
}

Sensor::~Sensor() {
    std::cout << "  [Sensor]   소멸자: " << name << "\n";
}

std::string Sensor::type() const {
    return "Sensor";
}

const std::string& Sensor::getName() const {
    return name;
}