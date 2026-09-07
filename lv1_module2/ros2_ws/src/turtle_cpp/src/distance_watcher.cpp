#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/float32.hpp"

using std::placeholders::_1;

class DistanceWatcher : public rclcpp::Node {
 public:
  DistanceWatcher() : Node("distance_watcher") {
    this->declare_parameter<double>("threshold", 3.0);

    sub_ = this->create_subscription<std_msgs::msg::Float32>(
        "/turtle_distance", 10,
        std::bind(&DistanceWatcher::distanceCallback, this, _1));
  }

 private:
  void distanceCallback(const std_msgs::msg::Float32::SharedPtr msg) {
    const double threshold = this->get_parameter("threshold").as_double();
    if (msg->data > threshold) {
      RCLCPP_WARN(this->get_logger(), "거리 %.3f m가 임계값 %.3f m를 초과했습니다",
                  msg->data, threshold);
    }
  }

  rclcpp::Subscription<std_msgs::msg::Float32>::SharedPtr sub_;
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<DistanceWatcher>());
  rclcpp::shutdown();
  return 0;
}
