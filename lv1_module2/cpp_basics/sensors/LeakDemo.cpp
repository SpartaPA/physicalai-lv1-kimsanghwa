#include "Imu.hpp"

#include <iostream>
#include <memory>
#include <string>

namespace {

// (A) new 로 할당하고 delete 하지 않는 루프 -> 메모리 누수 재현
void runLeaky() {
    std::cout << "--- (A) new 할당, delete 없음 (누수) ---\n";
    for (int i = 0; i < 5; ++i) {
        Imu* p = new Imu("LEAK-IMU-" + std::to_string(i), 0.1); // delete 의도적으로 생략
        std::cout << "  read() = " << p->read() << "\n";
    }
}

// (B) 같은 루프를 std::make_unique 로 교체 -> 스코프를 벗어나면 자동 해제
void runFixed() {
    std::cout << "--- (B) std::make_unique (자동 해제) ---\n";
    for (int i = 0; i < 5; ++i) {
        auto p = std::make_unique<Imu>("FIX-IMU-" + std::to_string(i), 0.1);
        std::cout << "  read() = " << p->read() << "\n";
    } // 매 반복 끝에서 unique_ptr 소멸자가 delete 호출
}

} // namespace

int main(int argc, char** argv) {
    const std::string mode = (argc > 1) ? argv[1] : "leak";
    if (mode == "fixed") {
        runFixed();
    } else {
        runLeaky();
    }
    return 0;
}
