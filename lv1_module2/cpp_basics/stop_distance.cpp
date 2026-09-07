#include <iostream>
#include <iomanip>

int main() {
    const double g = 9.81; // 중력가속도 (m/s^2)

    double v = 0.0;   // 속도 (m/s)
    double mu = 0.0;  // 마찰계수

    std::cout << "속도(m/s)를 입력하세요: ";
    if (!(std::cin >> v)) {
        std::cerr << "잘못된 입력입니다.\n";
        return 1;
    }

    std::cout << "마찰계수(mu)를 입력하세요: ";
    if (!(std::cin >> mu)) {
        std::cerr << "잘못된 입력입니다.\n";
        return 1;
    }

    if (v < 0.0) {
        std::cerr << "속도는 음수가 될 수 없습니다.\n";
        return 1;
    }
    if (mu <= 0.0) {
        std::cerr << "마찰계수는 0보다 커야 합니다.\n";
        return 1;
    }

    double distance = (v * v) / (2.0 * mu * g);

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "예상 제동 거리: " << distance << " m\n";

    return 0;
}