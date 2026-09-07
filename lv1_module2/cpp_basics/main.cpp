#include "motor.hpp"

int main() {
    Motor motor("MyMotor", 1000);
    motor.start();
    motor.accelerate(50);
    motor.printStatus();
    motor.stop();

    return 0;
}