#ifndef MOTOR_HPP
#define MOTOR_HPP
#include <string>

class Motor {
private:
    std::string name;
    int rpm;          // 현재 회전수
    int maxRpm;       // 최대 회전수
    bool isRunning;

public:
    Motor(const std::string& motorName, int maxRpm);

    void start();
    void stop();
    void setSpeed(int targetRpm);   // 절대값 설정
    void accelerate(int deltaRpm);  // 현재값에서 증가
    void printStatus() const;
};

#endif // MOTOR_HPP