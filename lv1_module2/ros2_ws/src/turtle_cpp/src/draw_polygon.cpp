#include <chrono>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <memory>

#include "geometry_msgs/msg/twist.hpp"
#include "rclcpp/rclcpp.hpp"

class DrawPolygon : public rclcpp::Node {
 public:
  explicit DrawPolygon(int sides) : Node("draw_polygon"), sides_(sides) {
    pub_ = this->create_publisher<geometry_msgs::msg::Twist>("/turtle1/cmd_vel", 10);

    // 변의 길이를 N과 무관하게 고정하면 외접원 반지름이 N에 비례해 커져
    // turtlesim 창을 벗어난다. 외접원 반지름(kRadius)을 고정하고
    // 변의 길이 = 2 * R * sin(pi / N) 공식으로 역산해 항상 같은 크기 안에 들어오게 한다.
    const double side_length = 2.0 * kRadius * std::sin(M_PI / sides_);
    forward_duration_ = side_length / kLinearSpeed;
    turn_duration_ = (2.0 * M_PI / sides_) / kAngularSpeed;  // 외각 = 360/N도

    timer_ = this->create_wall_timer(
        std::chrono::milliseconds(kPeriodMs),
        std::bind(&DrawPolygon::timerCallback, this));
  }

 private:
  static constexpr int kPeriodMs = 100;               // 10Hz
  static constexpr double kLinearSpeed = 1.5;          // m/s
  static constexpr double kAngularSpeed = M_PI / 2.0;  // rad/s
  static constexpr double kRadius = 2.0;               // m -> 도형의 외접원 반지름(창 중앙 기준 고정)

  void timerCallback() {
    if (finished_) {
      return;
    }

    elapsed_ += kPeriodMs / 1000.0;

    geometry_msgs::msg::Twist msg;
    double duration;
    if (moving_forward_) {
      duration = forward_duration_;
      msg.linear.x = kLinearSpeed;
    } else {
      duration = turn_duration_;
      msg.angular.z = kAngularSpeed;
    }
    pub_->publish(msg);

    if (elapsed_ < duration) {
      return;
    }

    // 현재 구간 종료 -> 다음 구간으로 전환
    elapsed_ = 0.0;
    if (!moving_forward_) {
      ++sides_done_;
    }
    moving_forward_ = !moving_forward_;

    if (sides_done_ >= sides_) {
      finished_ = true;
      pub_->publish(geometry_msgs::msg::Twist());  // 정지
      RCLCPP_INFO(this->get_logger(), "%d각형 주행 완료", sides_);
    }
  }

  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr pub_;
  rclcpp::TimerBase::SharedPtr timer_;

  int sides_;
  double forward_duration_ = 0.0;
  double turn_duration_ = 0.0;

  bool moving_forward_ = true;
  double elapsed_ = 0.0;
  int sides_done_ = 0;
  bool finished_ = false;
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);

  int sides = 0;
  if (argc >= 2) {
    sides = std::atoi(argv[1]);
  } else {
    std::cout << "몇 각형을 그릴지 정수를 입력하세요 (3 이상): ";
    std::cin >> sides;
  }

  if (sides < 3) {
    std::cerr << "변의 개수는 3 이상이어야 합니다." << std::endl;
    rclcpp::shutdown();
    return 1;
  }

  rclcpp::spin(std::make_shared<DrawPolygon>(sides));
  rclcpp::shutdown();
  return 0;
}
