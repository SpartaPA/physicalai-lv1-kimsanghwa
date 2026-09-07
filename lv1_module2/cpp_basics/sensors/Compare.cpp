#include <iostream>
#include <memory>
#include <vector>
#include <string>

// ============ A. 가상 소멸자 있음 ============
namespace WithVirtual {

class Sensor {
protected:
    std::string name;
public:
    Sensor(const std::string& n) : name(n) {}
    virtual ~Sensor() { std::cout << "    ~Sensor(" << name << ")\n"; }
    virtual double read() = 0;
    virtual std::string type() const = 0;
};

class Lidar : public Sensor {
    double* scanBuffer;              // 동적 할당 자원
public:
    Lidar(const std::string& n) : Sensor(n) {
        scanBuffer = new double[360];
        std::cout << "    Lidar(" << name << ") 버퍼 360개 할당\n";
    }
    ~Lidar() override {
        delete[] scanBuffer;
        std::cout << "    ~Lidar(" << name << ") 버퍼 해제\n";
    }
    double read() override { return 12.34; }
    std::string type() const override { return "Lidar"; }
};

class Imu : public Sensor {
    double* gyroBuffer;
public:
    Imu(const std::string& n) : Sensor(n) {
        gyroBuffer = new double[3];
        std::cout << "    Imu(" << name << ") 버퍼 3개 할당\n";
    }
    ~Imu() override {
        delete[] gyroBuffer;
        std::cout << "    ~Imu(" << name << ") 버퍼 해제\n";
    }
    double read() override { return -0.56; }
    std::string type() const override { return "Imu"; }
};

} // namespace WithVirtual

// ============ B. 가상 소멸자 없음 ============
namespace NoVirtual {

class Sensor {
protected:
    std::string name;
public:
    Sensor(const std::string& n) : name(n) {}
    ~Sensor() { std::cout << "    ~Sensor(" << name << ")\n"; }   // virtual 없음
    virtual double read() = 0;
    virtual std::string type() const = 0;
};

class Lidar : public Sensor {
    double* scanBuffer;
public:
    Lidar(const std::string& n) : Sensor(n) {
        scanBuffer = new double[360];
        std::cout << "    Lidar(" << name << ") 버퍼 360개 할당\n";
    }
    ~Lidar() {
        delete[] scanBuffer;
        std::cout << "    ~Lidar(" << name << ") 버퍼 해제\n";
    }
    double read() override { return 12.34; }
    std::string type() const override { return "Lidar"; }
};

class Imu : public Sensor {
    double* gyroBuffer;
public:
    Imu(const std::string& n) : Sensor(n) {
        gyroBuffer = new double[3];
        std::cout << "    Imu(" << name << ") 버퍼 3개 할당\n";
    }
    ~Imu() {
        delete[] gyroBuffer;
        std::cout << "    ~Imu(" << name << ") 버퍼 해제\n";
    }
    double read() override { return -0.56; }
    std::string type() const override { return "Imu"; }
};

} // namespace NoVirtual


int main() {
    std::cout << "########## A. 가상 소멸자 있음 ##########\n";
    {
        using namespace WithVirtual;
        std::cout << "\n[생성]\n";
        std::vector<std::unique_ptr<Sensor>> sensors;
        sensors.push_back(std::make_unique<Lidar>("LIDAR-01"));
        sensors.push_back(std::make_unique<Imu>("IMU-01"));

        std::cout << "\n[다형성 루프]\n";
        for (const auto& s : sensors)
            std::cout << "    " << s->type() << " read() = " << s->read() << "\n";

        std::cout << "\n[소멸]\n";
    }   // 여기서 vector 소멸

    std::cout << "\n\n########## B. 가상 소멸자 없음 ##########\n";
    {
        using namespace NoVirtual;
        std::cout << "\n[생성]\n";
        std::vector<std::unique_ptr<Sensor>> sensors;
        sensors.push_back(std::make_unique<Lidar>("LIDAR-02"));
        sensors.push_back(std::make_unique<Imu>("IMU-02"));

        std::cout << "\n[다형성 루프]\n";
        for (const auto& s : sensors)
            std::cout << "    " << s->type() << " read() = " << s->read() << "\n";

        std::cout << "\n[소멸]\n";
    }

    return 0;
}