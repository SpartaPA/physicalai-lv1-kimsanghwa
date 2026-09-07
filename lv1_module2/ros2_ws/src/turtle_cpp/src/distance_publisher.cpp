#include <chrono>
#include <cmath>
#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/float32.hpp"
#include "turtlesim/msg/pose.hpp"

using std::placeholders::_1;

class DistancePublisher : public rclcpp::Node {
 public:
  DistancePublisher() : Node("distance_publisher") {
    pose_sub_ = this->create_subscription<turtlesim::msg::Pose>(
        "/turtle1/pose", 10,
        std::bind(&DistancePublisher::poseCallback, this, _1));

    distance_pub_ =
        this->create_publisher<std_msgs::msg::Float32>("/turtle_distance", 10);

    timer_ = this->create_wall_timer(
        std::chrono::milliseconds(100),
        std::bind(&DistancePublisher::timerCallback, this));  // 10Hz
  }

 private:
  void poseCallback(const turtlesim::msg::Pose::SharedPtr msg) {
    latest_pose_ = msg;  // 구독 콜백: 최신 자세만 저장, 발행은 하지 않음
  }

  void timerCallback() {
    if (!latest_pose_) {
      return;
    }

    const double distance = std::sqrt(latest_pose_->x * latest_pose_->x +
                                       latest_pose_->y * latest_pose_->y);

    std_msgs::msg::Float32 msg;
    msg.data = static_cast<float>(distance);
    distance_pub_->publish(msg);
  }

  rclcpp::Subscription<turtlesim::msg::Pose>::SharedPtr pose_sub_;
  rclcpp::Publisher<std_msgs::msg::Float32>::SharedPtr distance_pub_;
  rclcpp::TimerBase::SharedPtr timer_;
  turtlesim::msg::Pose::SharedPtr latest_pose_;
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<DistancePublisher>());
  rclcpp::shutdown();
  return 0;
}
