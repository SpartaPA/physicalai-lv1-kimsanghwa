#include "Imu.hpp"

#include <iostream>
#include <memory>

// 스택 객체 vs make_unique(힙) 객체의 소멸 시점을 비교하는 실험
int main() {
    std::cout << "=== A. 지역 변수(스택)로 생성 ===\n";
    {
        std::cout << "  [블록 진입]\n";
        Imu localImu("STACK-IMU", 0.1);   // 스택에 직접 생성
        std::cout << "  블록 안에서 사용: read() = " << localImu.read() << "\n";
        std::cout << "  [블록 탈출 직전]\n";
    }   // <- 여기서 localImu 소멸자가 자동 호출됨
    std::cout << "  [블록 탈출 완료]\n\n";

    std::cout << "=== B. std::make_unique로 생성 (힙) ===\n";
    {
        std::cout << "  [블록 진입]\n";
        auto heapImu = std::make_unique<Imu>("HEAP-IMU", 0.1);   // 힙에 생성, unique_ptr가 소유
        std::cout << "  블록 안에서 사용: read() = " << heapImu->read() << "\n";
        std::cout << "  [블록 탈출 직전]\n";
    }   // <- 여기서 unique_ptr 소멸자가 호출되며 내부적으로 delete 실행 -> Imu 소멸자 호출
    std::cout << "  [블록 탈출 완료]\n";

    return 0;
}
